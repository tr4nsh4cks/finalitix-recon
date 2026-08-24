import java.net.Socket
import java.net.InetSocketAddress
import java.security.MessageDigest

def mysqlTry = { String host, int port, String user, String pass, List queries ->
  def out = new StringBuilder()
  def sock = new Socket()
  try {
    sock.connect(new InetSocketAddress(host, port), 6000)
    sock.setSoTimeout(12000)
    def ins = new DataInputStream(new BufferedInputStream(sock.getInputStream()))
    def outs = new BufferedOutputStream(sock.getOutputStream())
    def readPacket = {
      int b0 = ins.readUnsignedByte(); int b1 = ins.readUnsignedByte(); int b2 = ins.readUnsignedByte()
      int len = b0 | (b1 << 8) | (b2 << 16); int seq = ins.readUnsignedByte()
      byte[] pl = new byte[len]; ins.readFully(pl)
      [seq: seq, pl: pl]
    }
    def writePacket = { int seq, byte[] pl ->
      int len = pl.length
      outs.write(len & 0xFF); outs.write((len >> 8) & 0xFF); outs.write((len >> 16) & 0xFF); outs.write(seq & 0xFF)
      outs.write(pl); outs.flush()
    }
    def hs = readPacket()
    def p = hs.pl
    if ((p[0] & 0xFF) != 10) { out.append("BAD_PROTO\n"); return out.toString() }
    int i = 1
    def sb = new StringBuilder()
    while (p[i] != 0) { sb.append((char) (p[i] & 0xFF)); i++ }
    def serverVer = sb.toString(); i++
    i += 4
    byte[] salt1 = new byte[8]; System.arraycopy(p, i, salt1, 0, 8); i += 8
    i++
    i += 2; i++; i += 2; i += 2
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
    def baos = new ByteArrayOutputStream()
    baos.write(clientCaps & 0xFF); baos.write((clientCaps >> 8) & 0xFF); baos.write((clientCaps >> 16) & 0xFF); baos.write((clientCaps >> 24) & 0xFF)
    baos.write(0); baos.write(0); baos.write(0); baos.write(1)
    baos.write(33)
    baos.write(new byte[23])
    baos.write(user.getBytes('UTF-8')); baos.write(0)
    baos.write(token.length); baos.write(token)
    baos.write('mysql_native_password'.getBytes('UTF-8')); baos.write(0)
    writePacket(1, baos.toByteArray())
    def ap = readPacket().pl
    int at = ap[0] & 0xFF
    if (at == 0xFF) {
      int code = (ap[1] & 0xFF) | ((ap[2] & 0xFF) << 8)
      out.append("AUTH_ERROR " + code + ": " + new String(ap, 3, ap.length - 3, 'UTF-8') + "\n")
      return out.toString()
    }
    if (at == 0xFE) { out.append("AUTH_SWITCH\n"); return out.toString() }
    out.append("AUTH_OK server=" + serverVer + "\n")

    // lenenc helpers
    def lenencInt
    lenencInt = { byte[] d, int[] pos ->
      int b = d[pos[0]] & 0xFF; pos[0]++
      if (b < 0xFB) return (long) b
      if (b == 0xFC) { long v = (d[pos[0]] & 0xFF) | ((d[pos[0]+1] & 0xFF) << 8); pos[0] += 2; return v }
      if (b == 0xFD) { long v = (d[pos[0]] & 0xFF) | ((d[pos[0]+1] & 0xFF) << 8) | ((d[pos[0]+2] & 0xFF) << 16); pos[0] += 3; return v }
      if (b == 0xFE) { long v = 0; for (int k = 0; k < 8; k++) { v |= ((long) (d[pos[0]+k] & 0xFF)) << (8 * k) }; pos[0] += 8; return v }
      return -1L
    }
    def doQuery = { String q ->
      def qb = new ByteArrayOutputStream()
      qb.write(0x03); qb.write(q.getBytes('UTF-8'))
      writePacket(0, qb.toByteArray())
      def rp = readPacket().pl
      int b0 = rp[0] & 0xFF
      if (b0 == 0xFF) {
        int code = (rp[1] & 0xFF) | ((rp[2] & 0xFF) << 8)
        return "ERR " + code + ": " + new String(rp, 3, rp.length - 3, 'UTF-8')
      }
      if (b0 == 0x00) return "OK"
      int[] pos = [0]
      long colCount = lenencInt(rp, pos)
      def colNames = []
      for (int ci = 0; ci < colCount; ci++) {
        def cp = readPacket().pl
        int[] cp2 = [0]
        for (int skip = 0; skip < 4; skip++) { long l = lenencInt(cp, cp2); cp2[0] += (int) l }
        long nl = lenencInt(cp, cp2)
        colNames.add(new String(cp, cp2[0], (int) nl, 'UTF-8'))
      }
      readPacket()
      def rows = []
      int guard = 0
      while (guard++ < 300) {
        def rp2 = readPacket().pl
        int rb = rp2[0] & 0xFF
        if (rb == 0xFE && rp2.length < 9) break
        if (rb == 0xFF) { rows.add(["ROWERR"]); break }
        int[] rp3 = [0]
        def vals = []
        for (int ci = 0; ci < colCount; ci++) {
          int fb = rp2[rp3[0]] & 0xFF
          if (fb == 0xFB) { rp3[0]++; vals.add("NULL") }
          else { long l = lenencInt(rp2, rp3); vals.add(new String(rp2, rp3[0], (int) l, 'UTF-8')); rp3[0] += (int) l }
        }
        rows.add(vals)
      }
      def res = new StringBuilder()
      res.append("COLS[" + colNames.join("|") + "]")
      rows.each { res.append(" ROW[" + it.join("|") + "]") }
      return res.toString()
    }
    queries.each { q ->
      try { out.append("Q[" + q + "] => " + doQuery(q) + "\n") }
      catch (Exception e) { out.append("Q[" + q + "] => EX: " + e.message + "\n") }
    }
  } catch (Exception e) {
    out.append("CONN_EX: " + e.class.simpleName + ": " + e.message + "\n")
  } finally {
    try { sock.close() } catch (ignored) {}
  }
  return out.toString()
}

def queries = [
  "SELECT VERSION(), CURRENT_USER(), @@hostname",
  "SHOW DATABASES",
]

println("### 172.27.141.26 app_t1 ###")
println(mysqlTry('172.27.141.26', 3306, 'app_t1', 'pySY8}7>ftpPz9S', queries))
println("### 172.27.141.4 app_t1 ###")
println(mysqlTry('172.27.141.4', 3306, 'app_t1', 'pySY8}7>ftpPz9S', queries))
println("MYSQL_AUTH_DONE")
