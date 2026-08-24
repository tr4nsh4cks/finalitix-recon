def run(cmd) {
    try {
        def proc = ['bash', '-c', cmd].execute()
        proc.waitFor()
        return proc.text.trim()
    } catch (e) {
        return "ERROR: ${e.message}"
    }
}

println "=== SUBNET SCAN FROM JENKINS MASTER ==="
println "=== ${new Date()} ==="
println ""

def ports = [22, 80, 443, 3306, 3308, 3310, 5432, 6379, 8080, 8443, 9090, 27017, 4243, 2375, 5000, 9200, 11211]
def results = []

println "--- FULL SCAN 172.27.141.0/24 (all hosts, key ports) ---"
(1..254).each { i ->
    def ip = "172.27.141.${i}"
    def openPorts = []
    ports.each { port ->
        def r = run("timeout 1 bash -c 'echo > /dev/tcp/${ip}/${port}' 2>/dev/null && echo OPEN || echo CLOSED")
        if (r == "OPEN") openPorts << port
    }
    if (openPorts) {
        results << [ip: ip, ports: openPorts]
        println "${ip} => ${openPorts}"
    }
}
println ""

println "--- SCAN 172.27.140.0/24 (key hosts) ---"
def results140 = []
(1..254).each { i ->
    def ip = "172.27.140.${i}"
    def openPorts = []
    [22, 80, 443, 3306, 4243, 2375, 8080, 6379, 9090, 5000].each { port ->
        def r = run("timeout 1 bash -c 'echo > /dev/tcp/${ip}/${port}' 2>/dev/null && echo OPEN || echo CLOSED")
        if (r == "OPEN") openPorts << port
    }
    if (openPorts) {
        results140 << [ip: ip, ports: openPorts]
        println "${ip} => ${openPorts}"
    }
}
println ""

println "--- SCAN 172.26.84.0/24 (key hosts) ---"
def results2684 = []
(1..254).each { i ->
    def ip = "172.26.84.${i}"
    def openPorts = []
    [22, 80, 443, 3306, 3308, 8080, 6379, 9090, 4243].each { port ->
        def r = run("timeout 1 bash -c 'echo > /dev/tcp/${ip}/${port}' 2>/dev/null && echo OPEN || echo CLOSED")
        if (r == "OPEN") openPorts << port
    }
    if (openPorts) {
        results2684 << [ip: ip, ports: openPorts]
        println "${ip} => ${openPorts}"
    }
}
println ""

println "--- ADDITIONAL DNS LOOKUPS ---"
def dnsTargets = [
    "dbasears.mrc-services.io",
    "appdb.claroshop-services.net",
    "dbst1envios.t1envios-services.io",
    "jenkins-ng.dev.claroshop.com",
    "nexus.dev.claroshop.com",
    "sonarqube.dev.sia.gsanborns.com.mx",
    "gitlab.dev.claroshop.com",
    "registry.dev.claroshop.com"
]
dnsTargets.each { host ->
    println "${host}: ${run("getent hosts ${host} 2>/dev/null || nslookup ${host} 2>/dev/null | grep -A1 'Name:' || host ${host} 2>/dev/null || echo UNRESOLVED")}"
}
println ""

println "--- GATEWAY / BRIDGE CHECK ---"
println run("ip route show | grep default")
println run("cat /proc/net/route | head -20")
println ""

println "=== SUMMARY ==="
println "172.27.141.x alive: ${results.size()} hosts"
println "172.27.140.x alive: ${results140.size()} hosts"
println "172.26.84.x alive: ${results2684.size()} hosts"
println "=== END SUBNET SCAN ==="
