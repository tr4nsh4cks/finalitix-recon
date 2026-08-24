import java.net.Socket
import java.io.BufferedReader
import java.io.InputStreamReader

// === PART 1: MySQL T1Pagos connectivity + auth test ===
println "=== MYSQL T1PAGOS + PROD SEARS PIVOT ==="

// Test MySQL connectivity and extract banner details
def testMySQL(String host, int port, String desc) {
    println "\n--- ${desc} (${host}:${port}) ---"
    try {
        def s = new Socket()
        s.connect(new java.net.InetSocketAddress(host, port), 5000)
        s.setSoTimeout(3000)
        def is = s.getInputStream()
        def banner = new byte[512]
        def read = is.read(banner)
        if (read > 0) {
            def raw = new String(banner, 0, read, "ISO-8859-1")
            def printable = raw.replaceAll('[^\\x20-\\x7E]', '.')
            println "Banner (${read} bytes): ${printable}"
            
            // Extract MySQL version from greeting
            def versionEnd = raw.indexOf('\0', 4)
            if (versionEnd > 4) {
                def version = raw.substring(5, versionEnd)
                println "MySQL Version: ${version}"
            }
        }
        s.close()
        return true
    } catch (Exception e) {
        println "ERROR: ${e.class.simpleName}: ${e.message}"
        return false
    }
}

testMySQL("172.27.141.4", 3306, "T1Pagos MySQL (3306)")
testMySQL("172.27.141.4", 3310, "T1Pagos MySQL (3310)")
testMySQL("172.27.141.24", 3306, "PROD Sears MySQL (3306)")
testMySQL("172.27.141.24", 3308, "PROD Sears MySQL (3308)")

// Scan more MySQL-like ports on both hosts
[3307, 3309, 3311, 3312, 33060, 33306, 8080, 80, 443, 8443, 9090, 5432].each { port ->
    ["172.27.141.4", "172.27.141.24"].each { host ->
        try {
            def s = new Socket()
            s.connect(new java.net.InetSocketAddress(host, port), 2000)
            s.setSoTimeout(1000)
            def is = s.getInputStream()
            def banner = new byte[256]
            def read = -1
            try { read = is.read(banner) } catch(Exception e) {}
            def bannerStr = read > 0 ? new String(banner, 0, read).replaceAll('[^\\x20-\\x7E]', '.') : "(no banner)"
            println "  OPEN: ${host}:${port} | ${bannerStr}"
            s.close()
        } catch (Exception e) {
            // not open
        }
    }
}

// === PART 2: Try MySQL auth via raw protocol ===
println "\n--- ATTEMPTING MYSQL AUTH (raw) ---"

def tryMySQLAuth(String host, int port, String user, String desc) {
    println "\nTrying ${user}@${host}:${port} (${desc})..."
    try {
        def s = new Socket()
        s.connect(new java.net.InetSocketAddress(host, port), 5000)
        s.setSoTimeout(3000)
        def is = s.getInputStream()
        def os = s.getOutputStream()
        
        // Read greeting
        def greeting = new byte[512]
        def gLen = is.read(greeting)
        if (gLen <= 0) { println "No greeting"; s.close(); return }
        
        // Extract auth challenge (salt)
        def greetStr = new String(greeting, 0, gLen, "ISO-8859-1").replaceAll('[^\\x20-\\x7E]', '.')
        println "Greeting: ${greetStr.take(100)}"
        
        // Send COM_QUIT (for now, just test reachability)
        def quit = [(byte)0x01, (byte)0x00, (byte)0x00, (byte)0x00, (byte)0x01] as byte[]
        os.write(quit)
        os.flush()
        
        s.close()
        println "Connection OK - MySQL responds"
    } catch (Exception e) {
        println "ERROR: ${e.message}"
    }
}

// Test basic reachability with user strings
tryMySQLAuth("172.27.141.4", 3306, "root", "T1Pagos root")

// === PART 3: Network discovery - what else is on 172.27.141.x and 172.27.140.x ===
println "\n--- NETWORK DISCOVERY: 172.27.140-141.x ---"

// Key ports to check
def ports = [22, 80, 443, 3306, 3308, 5432, 6379, 8080, 8443, 9200, 9300, 27017]

// Scan 172.27.140.x range (140-155) 
println "\n  Subnet 172.27.140.x (140-160):"
(140..160).each { octet ->
    def host = "172.27.140.${octet}"
    [22, 80, 3306, 6379, 8080].each { port ->
        try {
            def s = new Socket()
            s.connect(new java.net.InetSocketAddress(host, port), 1000)
            s.setSoTimeout(500)
            def is = s.getInputStream()
            def banner = new byte[128]
            def read = -1
            try { read = is.read(banner) } catch(Exception e) {}
            def b = read > 0 ? new String(banner, 0, read).replaceAll('[^\\x20-\\x7E]', '.').take(60) : ""
            println "    OPEN: ${host}:${port} ${b}"
            s.close()
        } catch (Exception e) {
            // closed
        }
    }
}

// Scan 172.27.141.x range
println "\n  Subnet 172.27.141.x (1-30):"
(1..30).each { octet ->
    def host = "172.27.141.${octet}"
    [22, 80, 3306, 3308, 3310, 6379, 8080].each { port ->
        try {
            def s = new Socket()
            s.connect(new java.net.InetSocketAddress(host, port), 1000)
            s.setSoTimeout(500)
            def is = s.getInputStream()
            def banner = new byte[128]
            def read = -1
            try { read = is.read(banner) } catch(Exception e) {}
            def b = read > 0 ? new String(banner, 0, read).replaceAll('[^\\x20-\\x7E]', '.').take(60) : ""
            println "    OPEN: ${host}:${port} ${b}"
            s.close()
        } catch (Exception e) {
            // closed
        }
    }
}

println "\n=== PIVOT SCAN DONE ==="
