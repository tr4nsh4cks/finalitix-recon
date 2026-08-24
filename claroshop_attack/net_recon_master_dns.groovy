def run(cmd) {
    try {
        def proc = ['bash', '-c', cmd].execute()
        proc.waitFor()
        return proc.text.trim()
    } catch (e) {
        return "ERROR: ${e.message}"
    }
}

println "=== DNS RESOLUTION + TRACEROUTE ==="
println ""

def targets = [
    "dbasears.mrc-services.io",
    "appdb.claroshop-services.net",
    "dbst1envios.t1envios-services.io",
    "jenkins-ng.dev.claroshop.com",
    "nexus.dev.claroshop.com",
    "sonarqube.dev.sia.gsanborns.com.mx",
    "gitlab.dev.claroshop.com",
    "registry.dev.claroshop.com",
    "t1pagos.com",
    "dev.claroshop.com",
    "mrc-services.io",
    "claroshop-services.net"
]

targets.each { h ->
    println "${h}:"
    println "  ${run("getent hosts ${h} 2>/dev/null || echo UNRESOLVED")}"
}
println ""

println "--- TRACEROUTE 172.27.141.24 ---"
println run("traceroute -n -m 5 -w 1 172.27.141.24 2>/dev/null || tracepath -n 172.27.141.24 2>/dev/null || echo NO_TRACEROUTE")
println ""

println "--- TRACEROUTE 172.27.141.4 ---"
println run("traceroute -n -m 5 -w 1 172.27.141.4 2>/dev/null || tracepath -n 172.27.141.4 2>/dev/null || echo NO_TRACEROUTE")
println ""

println "--- PING TEST KEY HOSTS ---"
["172.27.141.24", "172.27.141.4", "172.27.140.148", "172.27.141.1", "172.26.84.1"].each { ip ->
    println "${ip}: ${run("ping -c 1 -W 1 ${ip} 2>/dev/null && echo ALIVE || echo DEAD")}"
}
println ""

println "=== END DNS ==="
