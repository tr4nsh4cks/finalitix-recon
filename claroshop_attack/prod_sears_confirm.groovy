def pyScript = '''
import socket, struct, hashlib, sys
reload(sys)
sys.setdefaultencoding("utf-8")

HOST="127.0.0.1"
PORT=13308
USER="apifincadob"
PASS="nNzy]Ku2Ah=u%y1I"
DB="tienda"

queries = [
    ("CONNECTION_TEST", "SELECT 1"),
    ("CURRENT_USER", "SELECT CURRENT_USER()"),
    ("DATABASE", "SELECT DATABASE()"),
    ("PEDIDOS_COUNT", "SELECT COUNT(*) FROM tienda.pedidos"),
    ("PEDIDOS_MAX_DATE", "SELECT MAX(fecha) FROM tienda.pedidos"),
    ("DATOSTARJETA_COUNT", "SELECT COUNT(*) FROM tienda.datostarjeta"),
    ("CLIENTES_COUNT", "SELECT COUNT(*) FROM tienda.clientes"),
    ("SHOW_TABLES", "SHOW TABLES FROM tienda"),
    ("ALL_DBS", "SHOW DATABASES"),
]

def rp(s):
    h=""
    while len(h)<4: h+=s.recv(4-len(h))
    l=struct.unpack("<I",h[:3]+"\\x00")[0]
    sq=struct.unpack("B",h[3])[0]
    d=""
    while len(d)<l: d+=s.recv(l-len(d))
    return sq,d

def auth(u,p,salt,db,sq):
    h1=hashlib.sha1(p).digest()
    h2=hashlib.sha1(h1).digest()
    h3=hashlib.sha1(salt+h2).digest()
    sc="".join(chr(ord(a)^ord(b)) for a,b in zip(h3,h1))
    cap=0x0003f7cf
    pl=struct.pack("<IIB",cap,16777216,33)+"\\x00"*23
    pl+=u+"\\x00"+chr(len(sc))+sc+(db if db else "")+"\\x00"+"mysql_native_password\\x00"
    return struct.pack("<I",len(pl))[:3]+chr(sq)+pl

def do_query(s,q):
    pl="\\x03"+q
    s.sendall(struct.pack("<I",len(pl))[:3]+"\\x00"+pl)
    sq,d=rp(s)
    fb=ord(d[0])
    if fb==0xff:
        print "  ERR:"+d[9:]
        return
    if fb==0x00:
        print "  OK"
        return
    nc=fb if fb<251 else struct.unpack("<H",d[1:3])[0]
    for _ in range(nc): sq,_=rp(s)
    sq,_=rp(s)
    count=0
    while True:
        sq,rd=rp(s)
        if ord(rd[0])==0xfe and len(rd)<9: break
        if ord(rd[0])==0xff:
            print "  ERR:"+rd[9:]
            break
        pos=0
        cols=[]
        for _ in range(nc):
            b=ord(rd[pos])
            if b==0xfb: cols.append("NULL");pos+=1;continue
            if b<251: ln=b;pos+=1
            elif b==252: ln=struct.unpack("<H",rd[pos+1:pos+3])[0];pos+=3
            elif b==253: ln=struct.unpack("<I",rd[pos+1:pos+4]+"\\x00")[0];pos+=4
            else: ln=struct.unpack("<Q",rd[pos+1:pos+9])[0];pos+=9
            cols.append(rd[pos:pos+ln])
            pos+=ln
        print "|".join(cols)
        count+=1
    print "  ROWS="+str(count)

try:
    s=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    s.settimeout(10)
    s.connect((HOST,PORT))
    sq,g=rp(s)
    salt=g[4:12]
    nul=g.find("\\x00",4)
    rest=g[nul+1+18:]
    salt+=rest[:rest.find("\\x00")]
    s.sendall(auth(USER,PASS,salt,DB,sq+1))
    sq,r=rp(s)
    if ord(r[0])==0xff:
        print "AUTH_FAIL:"+r[9:]
        sys.exit(1)
    print "AUTH_OK to PROD Sears via SSH tunnel"
    for label,q in queries:
        print "\\n=== "+label+" ==="
        do_query(s,q)
    s.close()
except Exception as e:
    print "ERROR:"+str(e)
'''

def encoded = pyScript.bytes.encodeBase64().toString()
def cmd = ["bash", "-c", "echo '${encoded}' | base64 -d > /tmp/prodsears.py && python /tmp/prodsears.py 2>&1"]
def proc = cmd.execute()
def out = new StringBuilder()
proc.consumeProcessOutput(out, new StringBuilder())
proc.waitForOrKill(30000)
println out.toString()
