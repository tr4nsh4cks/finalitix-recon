def pyCode = """
import socket, struct, hashlib, sys
HOST='172.27.141.6'
PORT=3308
USER='apifincadodev'
PASS='1q2w3e4r5t6y'
DB='tienda'
PHONE='5558455777'

queries = [
    ("credcliente", "SELECT id_cc_credcliente, id_cliente, telefono, credito_disponible, limite_credito, saldo_credito, saldo_ws, numero_cuenta, fecha_alta, estatus FROM credito_clarotel_credcliente WHERE telefono LIKE '%" + PHONE + "%'"),
    ("lineac", "SELECT id_cc_linea, id_cliente, telefono, monto_total, limite_cred_tel, saldo_cred_tel, saldo_sanborns, saldo_sears, saldo_claro, estado_linea FROM credito_clarotel_lineac WHERE telefono LIKE '%" + PHONE + "%'"),
]

def rp(s):
    h=b""
    while len(h)<4: h+=s.recv(4-len(h))
    l=struct.unpack("<I",h[:3]+b"\\x00")[0]
    sq=struct.unpack("B",h[3:4])[0]
    d=b""
    while len(d)<l: d+=s.recv(l-len(d))
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
    if fb==0xff:
        print("  ERR:"+d[9:].decode("latin1"))
        return
    if fb==0x00:
        print("  NO RESULTS")
        return
    nc=fb if fb<251 else struct.unpack("<H",d[1:3])[0]
    for _ in range(nc): sq,_=rp(s)
    sq,_=rp(s)
    count=0
    while True:
        sq,rd=rp(s)
        if struct.unpack("B",rd[0:1])[0]==0xfe and len(rd)<9: break
        if struct.unpack("B",rd[0:1])[0]==0xff:
            print("  ERR:"+rd[9:].decode("latin1"))
            break
        pos=0
        cols=[]
        for _ in range(nc):
            b=struct.unpack("B",rd[pos:pos+1])[0]
            if b==0xfb: cols.append("NULL");pos+=1;continue
            if b<251: ln=b;pos+=1
            elif b==252: ln=struct.unpack("<H",rd[pos+1:pos+3])[0];pos+=3
            elif b==253: ln=struct.unpack("<I",rd[pos+1:pos+4]+b"\\x00")[0];pos+=4
            else: ln=struct.unpack("<Q",rd[pos+1:pos+9])[0];pos+=9
            cols.append(rd[pos:pos+ln].decode("latin1"))
            pos+=ln
        print("|".join(cols))
        count+=1
    if count==0: print("  NO ROWS")

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
    if struct.unpack("B",r[0:1])[0]==0xff:
        print("AUTH_FAIL:"+r[9:].decode("latin1"))
        sys.exit(1)
    print("AUTH_OK")
    for label,q in queries:
        print("=== "+label+" ===")
        do_query(s,q)
        print("")
    s.close()
except Exception as e:
    print("ERROR:"+str(e))
"""

new File('/tmp/tlook.py').text = pyCode
def proc = "python /tmp/tlook.py".execute()
def out = new StringBuilder()
def err = new StringBuilder()
proc.consumeProcessOutput(out, err)
proc.waitForOrKill(15000)
println out.toString()
if (err) println "STDERR: " + err.toString()
