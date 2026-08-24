import java.net.Socket
import java.net.InetSocketAddress
import java.security.MessageDigest

def host='172.27.141.4'; int port=3306
def user='apifincadob'; def pass='nNzy]Ku2Ah=u%y1I'

def sock=new Socket()
sock.connect(new InetSocketAddress(host,port),8000)
sock.setSoTimeout(15000)
def ins=new DataInputStream(new BufferedInputStream(sock.getInputStream()))
def outs=new BufferedOutputStream(sock.getOutputStream())

def readPacket={
  int b0=ins.readUnsignedByte(); int b1=ins.readUnsignedByte(); int b2=ins.readUnsignedByte()
  int len=b0|(b1<<8)|(b2<<16); int seq=ins.readUnsignedByte()
  byte[] pl=new byte[len]; ins.readFully(pl)
  [seq:seq,pl:pl]
}
def writePacket={ int seq, byte[] pl ->
  int len=pl.length
  outs.write(len & 0xFF); outs.write((len>>8)&0xFF); outs.write((len>>16)&0xFF); outs.write(seq & 0xFF)
  outs.write(pl); outs.flush()
}

// --- handshake ---
def hs=readPacket()
def p=hs.pl
if((p[0]&0xFF)==0xFF){ println("CONNECT_ERR: "+new String(p,3,p.length-3,'UTF-8')); return }
if((p[0]&0xFF)!=10){ println("BAD_PROTOCOL "+(p[0]&0xFF)); return }
int i=1
def sb=new StringBuilder()
while(p[i]!=0){ sb.append((char)(p[i]&0xFF)); i++ }
def serverVer=sb.toString(); i++
i+=4
byte[] salt1=new byte[8]; System.arraycopy(p,i,salt1,0,8); i+=8
i++
int capLow=(p[i]&0xFF)|((p[i+1]&0xFF)<<8); i+=2
i++; i+=2
int capHigh=(p[i]&0xFF)|((p[i+1]&0xFF)<<8); i+=2
int authLen=(p[i]&0xFF); i++
i+=10
int salt2Len=Math.max(13, authLen-8)
def salt2List=[]
int avail=p.length-i
for(int k=0;k<Math.min(salt2Len,avail);k++){ if(p[i+k]!=0) salt2List.add(p[i+k]) }
byte[] seed=new byte[8+salt2List.size()]
System.arraycopy(salt1,0,seed,0,8)
for(int k=0;k<salt2List.size();k++) seed[8+k]=(byte)salt2List[k]
println("SERVER="+serverVer+" seedLen="+seed.length)

// --- token mysql_native_password ---
def md=MessageDigest.getInstance('SHA-1')
byte[] s1=md.digest(pass.getBytes('UTF-8'))
byte[] s2=md.digest(s1)
md.reset(); md.update(seed); md.update(s2)
byte[] s3=md.digest()
byte[] token=new byte[20]
for(int j=0;j<20;j++) token[j]=(byte)((s1[j]^s3[j])&0xFF)

// --- login packet ---
int clientCaps=0x1|0x200|0x2000|0x8000|0x80000|0x20000
def baos=new ByteArrayOutputStream()
baos.write(clientCaps&0xFF); baos.write((clientCaps>>8)&0xFF); baos.write((clientCaps>>16)&0xFF); baos.write((clientCaps>>24)&0xFF)
baos.write(0); baos.write(0); baos.write(0); baos.write(1)
baos.write(33)
baos.write(new byte[23])
baos.write(user.getBytes('UTF-8')); baos.write(0)
baos.write(token.length); baos.write(token)
baos.write('mysql_native_password'.getBytes('UTF-8')); baos.write(0)
writePacket(1, baos.toByteArray())

def authResp=readPacket()
def ap=authResp.pl
int at=ap[0]&0xFF
if(at==0xFF){
  int code=(ap[1]&0xFF)|((ap[2]&0xFF)<<8)
  println("AUTH_ERROR code="+code+" msg="+new String(ap,3,ap.length-3,'UTF-8'))
  return
} else if(at==0xFE){
  println("AUTH_SWITCH: "+new String(ap,1,ap.length-1,'UTF-8'))
  return
}
println("AUTH_OK user="+user)

// --- helpers lenenc ---
class Cur { byte[] d; int i=0 }
def lenencInt={ Cur c ->
  int b=c.d[c.i]&0xFF; c.i++
  if(b<0xFB) return (long)b
  if(b==0xFC){ long v=(c.d[c.i]&0xFF)|((c.d[c.i+1]&0xFF)<<8); c.i+=2; return v }
  if(b==0xFD){ long v=(c.d[c.i]&0xFF)|((c.d[c.i+1]&0xFF)<<8)|((c.d[c.i+2]&0xFF)<<16); c.i+=3; return v }
  if(b==0xFE){ long v=0; for(int k=0;k<8;k++){ v|=((long)(c.d[c.i+k]&0xFF))<<(8*k) }; c.i+=8; return v }
  return -1L
}

// --- query function ---
def doQuery={ String q ->
  def qb=new ByteArrayOutputStream()
  qb.write(0x03); qb.write(q.getBytes('UTF-8'))
  writePacket(0, qb.toByteArray())
  def rp=readPacket().pl
  int b0=rp[0]&0xFF
  if(b0==0xFF){
    int code=(rp[1]&0xFF)|((rp[2]&0xFF)<<8)
    return "ERR "+code+": "+new String(rp,3,rp.length-3,'UTF-8')
  }
  if(b0==0x00){ return "OK affected=0" }
  def c0=new Cur(d:rp)
  long colCount=lenencInt(c0)
  def colNames=[]
  for(int ci=0; ci<colCount; ci++){
    def cp=readPacket().pl
    def cc=new Cur(d:cp)
    for(int skip=0; skip<4; skip++){ long l=lenencInt(cc); cc.i+=(int)l }
    long nl=lenencInt(cc)
    colNames.add(new String(cc.d, cc.i, (int)nl, 'UTF-8'))
  }
  readPacket() // EOF
  def rows=[]
  int guard=0
  while(guard++<500){
    def rp2=readPacket().pl
    int rb=rp2[0]&0xFF
    if(rb==0xFE && rp2.length<9) break
    if(rb==0xFF){ rows.add(["ROWERR "+new String(rp2,3,rp2.length-3,'UTF-8')]); break }
    def rc=new Cur(d:rp2)
    def vals=[]
    for(int ci=0; ci<colCount; ci++){
      int fb=rc.d[rc.i]&0xFF
      if(fb==0xFB){ rc.i++; vals.add("NULL") }
      else { long l=lenencInt(rc); vals.add(new String(rc.d, rc.i, (int)l, 'UTF-8')); rc.i+=(int)l }
    }
    rows.add(vals)
  }
  def out=new StringBuilder()
  out.append("COLS="+colNames.join("|"))
  rows.each { out.append(" ;; ROW="+it.join("|")) }
  return out.toString()
}

println("Q1 version: " + doQuery("SELECT VERSION(), CURRENT_USER(), @@hostname"))
println("Q2 databases: " + doQuery("SHOW DATABASES"))
println("Q3 tienda.pedidos: " + doQuery("SELECT COUNT(*) FROM tienda.pedidos"))
println("Q4 user hosts: " + doQuery("SELECT user,host FROM mysql.user LIMIT 20"))
try { sock.close() } catch (ignored) {}
println("MYSQL_CLIENT_DONE")
