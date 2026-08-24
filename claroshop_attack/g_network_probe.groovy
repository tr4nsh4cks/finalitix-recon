// Prueba conectividad de red desde Jenkins hacia IPs objetivo
// Testea: 172.27.141.24 (dbasears), 172.27.141.4 (T1Pagos), CSDEV01-2

def TARGET_IPS = [
    "172.27.141.24": "dbasears.mrc-services.io (PROD Sears DB)",
    "172.27.141.4": "T1Pagos DB",
    "172.27.141.5": "GitLab TMX",
    "172.27.141.25": "Proxy server",
    "172.27.141.12": "DNS server",
    "172.27.140.134": "GitLab dev (claroshop)",
    "172.27.140.148": "CSDEVBLD01-1",
    "172.27.140.162": "Syslog server"
]

def APP_SERVERS = [
    "CSDEV01-2.dev.claroshop.com",
    "CSDEV02-2.dev.claroshop.com",
    "CSQAAPP01-1.dev.claroshop.com",
    "CSQAAPP03-1.dev.claroshop.com"
]

println "=== NETWORK CONNECTIVITY TEST FROM JENKINS ==="
println "Jenkins hostname: ${InetAddress.localHost.hostName}"
println "Jenkins IP: ${InetAddress.localHost.hostAddress}"
println "Time: ${new Date()}"
println ""

// Test IPs via InetAddress.isReachable (ICMP)
println "--- ICMP Reachability Test ---"
TARGET_IPS.each { ip, desc ->
    try {
        def addr = InetAddress.getByName(ip)
        def reachable = addr.isReachable(3000)
        println "${ip} (${desc}): ${reachable ? 'REACHABLE' : 'NOT REACHABLE'}"
    } catch(e) {
        println "${ip} (${desc}): ERROR - ${e.message}"
    }
}

// Test TCP ports (important services)
println "\n--- TCP Port Test ---"
def PORT_TESTS = [
    ["172.27.141.24", 3308, "dbasears MySQL"],
    ["172.27.141.24", 22, "dbasears SSH"],
    ["172.27.141.24", 3306, "dbasears MySQL alt"],
    ["172.27.141.4", 3310, "T1Pagos DB port"],
    ["172.27.141.4", 3306, "T1Pagos MySQL"],
    ["172.27.141.4", 22, "T1Pagos SSH"],
    ["172.27.141.25", 8080, "Proxy"],
    ["172.27.141.12", 53, "DNS"],
    ["172.27.140.134", 22, "GitLab SSH"],
    ["172.27.140.134", 80, "GitLab HTTP"],
    ["172.27.140.148", 22, "CSDEVBLD01 SSH"]
]

PORT_TESTS.each { ip, port, desc ->
    try {
        def socket = new Socket()
        socket.connect(new InetSocketAddress(ip, port), 3000)
        socket.close()
        println "OPEN: ${ip}:${port} (${desc})"
    } catch(e) {
        def reason = e.class.simpleName
        println "CLOSED/FILTERED: ${ip}:${port} (${desc}) - ${reason}"
    }
}

// Try DNS resolution
println "\n--- DNS Resolution ---"
APP_SERVERS.each { hostname ->
    try {
        def addrs = InetAddress.getAllByName(hostname)
        addrs.each { a -> println "RESOLVED: ${hostname} -> ${a.hostAddress}" }
    } catch(e) {
        println "FAILED: ${hostname} - ${e.message}"
    }
}

// Try hostname resolution for dbasears
["dbasears.mrc-services.io", "t1pagos.api.claroshop-services.io", "t1pagos.api.mrc-services.io"].each { hostname ->
    try {
        def addr = InetAddress.getByName(hostname)
        println "RESOLVED: ${hostname} -> ${addr.hostAddress}"
    } catch(e) {
        println "FAILED: ${hostname} - ${e.message}"
    }
}

println "\n=== RUNNING 'ss -tuln' TO SEE LOCAL PORTS ==="
try {
    def proc = ["ss", "-tuln"].execute()
    proc.waitFor()
    println proc.text
} catch(e) {
    try {
        def proc2 = ["netstat", "-tuln"].execute()
        proc2.waitFor()
        println proc2.text
    } catch(e2) {
        println "netstat/ss unavailable"
    }
}

println "\n=== IP ROUTE ==="
try {
    def proc = ["ip", "route"].execute()
    proc.waitFor()
    println proc.text
} catch(e) {
    println "ip route failed: ${e.message}"
}

println "\n=== IP ADDR ==="
try {
    def proc = ["ip", "addr"].execute()
    proc.waitFor()
    println proc.text
} catch(e) {
    println "ip addr failed: ${e.message}"
}
