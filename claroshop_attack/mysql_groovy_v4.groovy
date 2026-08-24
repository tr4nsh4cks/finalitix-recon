// MySQL Groovy v4 - CLIENT_CONNECT_WITH_DB + queries reales T1Pagos + PROD Sears
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
    int r = 0
    while (r < 4) r += ins.read(hdr, r, 4-r)
    int len = (hdr[0] & 0xFF) | ((hdr[1] & 0xFF) << 8) | ((hdr[2] & 0xFF) << 16)
    def body = new byte[len]
    r = 0
    while (r < len) r += ins.read(body, r, len-r)
    return [seq: hdr[3] & 0xFF, body: body]
}

def writePacket = { java.io.OutputStream outs, int seq, byte[] data ->
    int len = data.length
    outs.write(len & 0xFF); outs.write((len >> 8) & 0xFF); outs.write((len >> 16) & 0xFF)
    outs.write(seq & 0xFF)
    outs.write(data)
    outs.flush()
}

def sha1 = { byte[] data ->
    MessageDigest.getInstance("SHA-1").digest(data)
}

def nativeHash = { String pwd, byte[] scramble ->
    def h1 = sha1(pwd.getBytes("UTF-8"))
    def h2 = sha1(h1)
    def md = MessageDigest.getInstance("SHA-1")
    md.update(scramble, 0, 20)
    md.update(h2)
    def r = md.digest()
    for (int i = 0; i < r.length; i++) r[i] = (byte)(r[i] ^ h1[i])
    r
}

def mysqlQuery = { String host, int port, String user, String pass, String db, String sql ->
    def sock = new java.net.Socket()
    sock.connect(new java.net.InetSocketAddress(host, port), 8000)
    sock.setSoTimeout(15000)
    def ins = sock.inputStream
    def outs = sock.outputStream
    
    def greeting = readPacket(ins)
    def body = greeting.body
    
    // Parse greeting - find scramble
    int i = 1
    while (i < body.length && body[i] != 0) i++
    def serverVer = new String(body, 1, i-1, "UTF-8")
    i += 5 // skip null + thread_id
    def s1 = new byte[8]
    System.arraycopy(body, i, s1, 0, 8)
    i += 9 // 8 bytes + filler
    i += 2 + 1 + 2 + 2 + 1 + 10 // caps + charset + status + caps_high + auth_data_len + reserved
    def s2 = new byte[12]
    if (i + 12 <= body.length) System.arraycopy(body, i, s2, 0, 12)
    def scramble = concat(s1, s2)
    
    def pwdHash = pass ? nativeHash(pass, scramble) : new byte[0]
    
    // CLIENT flags including CONNECT_WITH_DB (bit3=8)
    int flags = 0x000FA68D  // 0x000FA685 | 0x8 (CONNECT_WITH_DB)
    
    def userB = (user + "\u0000").getBytes("UTF-8")
    def dbB = (db + "\u0000").getBytes("UTF-8")
    def plugin = "mysql_native_password\u0000".getBytes("UTF-8")
    def authResp = concat([(byte)pwdHash.length] as byte[], pwdHash)
    
    def hs = concat(le4(flags), le4(16777216), [0x21 as byte] as byte[], new byte[23],
                    userB, authResp, dbB, plugin)
    writePacket(outs, 1, hs)
    
    def authPkt = readPacket(ins)
    def ar = authPkt.body
    
    if ((ar[0] & 0xFF) == 0xFE) {
        // Auth switch
        int pi = 1; while (pi < ar.length && ar[pi] != 0) pi++
        def ns = new byte[20]
        if (ar.length > pi + 1) System.arraycopy(ar, pi+1, ns, 0, Math.min(20, ar.length-pi-1))
        def sw = pass ? nativeHash(pass, ns) : new byte[0]
        writePacket(outs, authPkt.seq + 1, sw)
        def swPkt = readPacket(ins)
        ar = swPkt.body
    }
    
    if ((ar[0] & 0xFF) == 0xFF) {
        int ec = (ar[1] & 0xFF) | ((ar[2] & 0xFF) << 8)
        sock.close()
        return "AUTH_ERR[" + ec + "] " + new String(ar, 9, Math.min(ar.length-9, 200), "UTF-8")
    }
    if (ar[0] != 0x00) { sock.close(); return "UNEXPECTED 0x" + String.format("%02X", ar[0]) }
    
    // Query
    def queryPkt = concat([0x03 as byte] as byte[], sql.getBytes("UTF-8"))
    writePacket(outs, 0, queryPkt)
    
    def rPkt = readPacket(ins)
    def rb = rPkt.body
    
    if ((rb[0] & 0xFF) == 0xFF) {
        int ec = (rb[1] & 0xFF) | ((rb[2] & 0xFF) << 8)
        sock.close()
        return "QUERY_ERR[" + ec + "] " + new String(rb, 9, Math.min(rb.length-9, 200), "UTF-8")
    }
    if (rb[0] == 0x00) {
        int affected = rb[1] & 0xFF
        sock.close()
        return "OK (affected=" + affected + ") [SERVER:" + serverVer + "]"
    }
    
    int numCols = rb[0] & 0xFF
    def cols = []
    numCols.times {
        def cp = readPacket(ins).body
        int ci = 0
        4.times { int len = cp[ci]&0xFF; ci += 1+len } // catalog/schema/table/org_table
        if (ci < cp.length) {
            int nl = cp[ci]&0xFF; ci++
            cols << new String(cp, ci, nl, "UTF-8")
        }
    }
    readPacket(ins) // EOF
    
    def rows = []
    while (rows.size() < 100) {
        def rowP = readPacket(ins)
        def rw = rowP.body
        if ((rw[0] & 0xFF) == 0xFE && rw.length < 9) break
        if ((rw[0] & 0xFF) == 0xFF) break
        def row = []
        int ri = 0
        numCols.times {
            if (ri < rw.length) {
                if ((rw[ri] & 0xFF) == 0xFB) { row << "NULL"; ri++ }
                else {
                    int rl = rw[ri] & 0xFF; ri++
                    if (rl < 0xFB) {
                        row << new String(rw, ri, rl, "UTF-8"); ri += rl
                    } else { row << "(blob)"; ri++ }
                }
            }
        }
        rows << row
    }
    sock.close()
    
    def out = "[" + serverVer + "] " + cols.join(" | ") + "\n"
    rows.each { row -> out += "  " + row.join(" | ") + "\n" }
    out + "  (" + rows.size() + " rows)"
}

println "=== T1PAGOS DB 172.27.141.26:3306 ==="
try { println mysqlQuery("172.27.141.26", 3306, "app_t1", "pySY8}7>ftpPz9S", "payment_t1", "SHOW TABLES") } catch(e) { println "ERR: $e.message" }

println "\n--- COUNT transactions en payment_t1 ---"
try { println mysqlQuery("172.27.141.26", 3306, "app_t1", "pySY8}7>ftpPz9S", "payment_t1", "SELECT COUNT(*) FROM payment_t1.transactions") } catch(e) { println "ERR: $e.message" }

println "\n--- SAMPLE transactions (5 rows) ---"
try { println mysqlQuery("172.27.141.26", 3306, "app_t1", "pySY8}7>ftpPz9S", "payment_t1", "SELECT id,amount,status,created_at FROM payment_t1.transactions ORDER BY id DESC LIMIT 5") } catch(e) { println "ERR: $e.message" }

println "\n--- SHOW TABLES FROM payment_t1 ---"
try { println mysqlQuery("172.27.141.26", 3306, "app_t1", "pySY8}7>ftpPz9S", "payment_t1", "SHOW TABLES FROM payment_t1") } catch(e) { println "ERR: $e.message" }

println "\n=== PROD SEARS dbpsears.claroshop-services.net:3312 ==="
try { println mysqlQuery("dbpsears.claroshop-services.net", 3312, "apsearsats", "7g4kktCAEuOV9CX", "tienda", "SHOW TABLES") } catch(e) { println "ERR: $e.message" }

println "\n--- SELECT COUNT(*) FROM tienda.pedidos ---"
try { println mysqlQuery("dbpsears.claroshop-services.net", 3312, "apsearsats", "7g4kktCAEuOV9CX", "tienda", "SELECT COUNT(*) FROM tienda.pedidos") } catch(e) { println "ERR: $e.message" }

println "\n--- SHOW DATABASES ---"
try { println mysqlQuery("dbpsears.claroshop-services.net", 3312, "apsearsats", "7g4kktCAEuOV9CX", "tienda", "SHOW DATABASES") } catch(e) { println "ERR: $e.message" }

println "\n--- Probe apifincadob en dbpsears ---"
try { println mysqlQuery("dbpsears.claroshop-services.net", 3312, "apifincadob", "nNzy]Ku2Ah=u%y1I", "tienda", "SELECT COUNT(*) FROM tienda.pedidos") } catch(e) { println "ERR: $e.message" }

println "\n=== FIN ==="
