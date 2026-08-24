def run(cmd) {
    try {
        def proc = ['bash', '-c', cmd].execute()
        proc.waitFor()
        return proc.text.trim()
    } catch (e) { return "ERR" }
}
println "=== SCAN BATCH 1: .24 .4 .21 .25 ==="
def hosts = ["172.27.141.24", "172.27.141.4", "172.27.141.21", "172.27.141.25"]
def ports = "22 80 443 3306 3308 3310 5432 6379 8080 9090 27017 4243 9000 50000"
hosts.each { ip ->
    println "${ip}: ${run("for p in ${ports}; do timeout 0.3 bash -c \"echo > /dev/tcp/${ip}/\$p\" 2>/dev/null && printf \"\$p \"; done")}"
}
