def run(cmd) {
    try {
        def proc = ['bash', '-c', cmd].execute()
        proc.waitFor()
        return proc.text.trim()
    } catch (e) {
        return "ERROR: ${e.message}"
    }
}

println "=== TARGETED PORT SCAN ==="
println ""

def targets = [
    "172.27.141.1", "172.27.141.2", "172.27.141.3", "172.27.141.4", "172.27.141.5",
    "172.27.141.6", "172.27.141.12", "172.27.141.19", "172.27.141.21",
    "172.27.141.24", "172.27.141.25", "172.27.141.26", "172.27.141.36",
    "172.27.141.44", "172.27.140.130", "172.27.140.131", "172.27.140.132",
    "172.27.140.134", "172.27.140.143", "172.27.140.148", "172.27.140.149",
    "172.27.140.150", "172.27.140.151", "172.27.140.162"
]

def ports = [22, 80, 443, 3306, 3308, 3310, 5432, 6379, 8080, 8443, 9090, 9000, 27017, 4243, 2375, 5000, 9200, 11211, 5601, 50000, 8888, 10250, 2379]

println "Scanning ${targets.size()} hosts x ${ports.size()} ports..."
println ""

targets.each { ip ->
    def cmd = "for p in ${ports.join(' ')}; do timeout 0.5 bash -c \"echo > /dev/tcp/${ip}/\$p\" 2>/dev/null && echo \"OPEN \$p\"; done"
    def result = run(cmd)
    if (result && result.contains("OPEN")) {
        println "${ip}: ${result.replaceAll('\n', ', ')}"
    }
}
println ""

println "--- EXTRA: 10.252.x.x subnet (ens161) ---"
["10.252.0.1", "10.252.0.2", "10.252.0.3", "10.252.255.252"].each { ip ->
    def cmd = "for p in 22 80 443 8080 3306 6379 9090; do timeout 0.5 bash -c \"echo > /dev/tcp/${ip}/\$p\" 2>/dev/null && echo \"OPEN \$p\"; done"
    def result = run(cmd)
    if (result && result.contains("OPEN")) {
        println "${ip}: ${result.replaceAll('\n', ', ')}"
    }
}
println ""

println "--- EXTRA: 10.242.x.x subnet (ens256) ---"
["10.242.0.1", "10.242.0.2", "10.242.0.3", "10.242.8.216", "10.242.0.222"].each { ip ->
    def cmd = "for p in 22 80 443 8080 3306 6379 9090 8443 4243; do timeout 0.5 bash -c \"echo > /dev/tcp/${ip}/\$p\" 2>/dev/null && echo \"OPEN \$p\"; done"
    def result = run(cmd)
    if (result && result.contains("OPEN")) {
        println "${ip}: ${result.replaceAll('\n', ', ')}"
    }
}
println ""

println "=== END TARGETED SCAN ==="
