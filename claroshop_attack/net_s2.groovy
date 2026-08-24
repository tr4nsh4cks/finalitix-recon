def run(cmd) {
    try {
        def proc = ['bash', '-c', cmd].execute()
        proc.waitFor()
        return proc.text.trim()
    } catch (e) { return "ERR" }
}
println "=== SCAN BATCH 2: .140 subnet + extras ==="
def hosts = ["172.27.140.130", "172.27.140.131", "172.27.140.132", "172.27.140.134", "172.27.140.143", "172.27.140.149", "172.27.140.150", "172.27.140.151", "172.27.140.162"]
def ports = "22 80 443 3306 8080 4243 6379 9090"
hosts.each { ip ->
    println "${ip}: ${run("for p in ${ports}; do timeout 0.3 bash -c \"echo > /dev/tcp/${ip}/\$p\" 2>/dev/null && printf \"\$p \"; done")}"
}
println "---"
println "=== .141 extras ==="
["172.27.141.1","172.27.141.2","172.27.141.3","172.27.141.5","172.27.141.6","172.27.141.12","172.27.141.19","172.27.141.26","172.27.141.36","172.27.141.44"].each { ip ->
    println "${ip}: ${run("for p in 22 80 443 3306 8080 9090; do timeout 0.3 bash -c \"echo > /dev/tcp/${ip}/\$p\" 2>/dev/null && printf \"\$p \"; done")}"
}
