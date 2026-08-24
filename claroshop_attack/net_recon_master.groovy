def run(cmd) {
    try {
        def proc = ['bash', '-c', cmd].execute()
        proc.waitFor()
        return proc.text.trim()
    } catch (e) {
        return "ERROR: ${e.message}"
    }
}

println "=== JENKINS MASTER NETWORK RECON ==="
println "=== Timestamp: ${new Date()} ==="
println ""

println "--- [1] HOSTNAME ---"
println run("hostname -f")
println ""

println "--- [2] IP ADDR SHOW ---"
println run("ip addr show 2>/dev/null || ifconfig")
println ""

println "--- [3] IP ROUTE ---"
println run("ip route show 2>/dev/null || route -n")
println ""

println "--- [4] /etc/hosts ---"
println run("cat /etc/hosts")
println ""

println "--- [5] /etc/resolv.conf ---"
println run("cat /etc/resolv.conf")
println ""

println "--- [6] ARP TABLE ---"
println run("arp -a 2>/dev/null || ip neigh show")
println ""

println "--- [7] LISTENING PORTS ---"
println run("ss -tlnp 2>/dev/null || netstat -tlnp 2>/dev/null")
println ""

println "--- [8] ENV PROXY ---"
println run("env | grep -i proxy || echo 'NO_PROXY_VARS'")
println ""

println "--- [9] DNS RESOLV TARGETS ---"
println run("nslookup dbasears.mrc-services.io 2>/dev/null || host dbasears.mrc-services.io 2>/dev/null || dig dbasears.mrc-services.io +short 2>/dev/null || echo 'NO_DNS_TOOLS'")
println ""
println run("nslookup appdb.claroshop-services.net 2>/dev/null || host appdb.claroshop-services.net 2>/dev/null || echo 'FAILED'")
println ""
println run("nslookup dbst1envios.t1envios-services.io 2>/dev/null || host dbst1envios.t1envios-services.io 2>/dev/null || echo 'FAILED'")
println ""

println "--- [10] TRACEROUTE 172.27.141.24 (PROD SEARS) ---"
println run("traceroute -n -m 10 -w 2 172.27.141.24 2>/dev/null || tracepath 172.27.141.24 2>/dev/null || echo 'NO_TRACEROUTE'")
println ""

println "--- [11] TRACEROUTE 172.27.141.4 (T1Pagos) ---"
println run("traceroute -n -m 10 -w 2 172.27.141.4 2>/dev/null || tracepath 172.27.141.4 2>/dev/null || echo 'NO_TRACEROUTE'")
println ""

println "--- [12] QUICK PING SWEEP 172.27.141.0/24 ---"
def alive141 = []
(1..254).each { i ->
    def ip = "172.27.141.${i}"
    def r = run("timeout 1 bash -c 'echo > /dev/tcp/${ip}/22 2>/dev/null && echo OPEN22' || echo CLOSED")
    if (r.contains("OPEN")) alive141 << "${ip}:22"
}
println "SSH alive on 172.27.141.x: ${alive141}"
println ""

println "--- [13] TCP SCAN KEY PORTS 172.27.141.x ---"
def targets141 = [1, 4, 5, 6, 7, 8, 10, 15, 20, 21, 22, 23, 24, 25, 30, 40, 50, 100, 148, 200, 254]
def ports = [22, 80, 443, 3306, 3308, 3310, 6379, 8080, 9090, 27017, 4243, 5432]
def results141 = []
targets141.each { host ->
    ports.each { port ->
        def ip = "172.27.141.${host}"
        def r = run("timeout 1 bash -c 'echo > /dev/tcp/${ip}/${port}' 2>/dev/null && echo OPEN || echo CLOSED")
        if (r == "OPEN") results141 << "${ip}:${port}"
    }
}
println "Open ports 172.27.141.x: ${results141}"
println ""

println "=== END JENKINS MASTER RECON ==="
