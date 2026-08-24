def run(cmd) {
    try {
        def proc = ['bash', '-c', cmd].execute()
        proc.waitFor()
        return proc.text.trim()
    } catch (e) { return "ERR" }
}
println "=== SCAN 10.x SUBNETS + OCP ==="
def hosts10 = ["10.252.0.1","10.252.0.2","10.252.0.3","10.252.255.252","10.242.0.1","10.242.0.2","10.242.0.3","10.242.8.216","10.242.0.222","172.26.127.196"]
hosts10.each { ip ->
    println "${ip}: ${run("for p in 22 80 443 8080 8443 3306 6379 9090; do timeout 0.3 bash -c \"echo > /dev/tcp/${ip}/\$p\" 2>/dev/null && printf \"\$p \"; done")}"
}
println ""
println "=== EXTRA MySQL hosts deeper ==="
["172.27.141.6","172.27.141.26","172.27.140.143","172.27.140.151"].each { ip ->
    println "${ip}: ${run("for p in 3306 3307 3308 3309 3310 3311 3312 6379 27017 9200; do timeout 0.3 bash -c \"echo > /dev/tcp/${ip}/\$p\" 2>/dev/null && printf \"\$p \"; done")}"
}
