def run(cmd) {
    try {
        def proc = ['bash', '-c', cmd].execute()
        proc.waitFor()
        return proc.text.trim()
    } catch (e) {
        return "ERROR: ${e.message}"
    }
}

println "=== JENKINS MASTER BASIC RECON ==="
println "Timestamp: ${new Date()}"
println ""

println "--- HOSTNAME ---"
println run("hostname -f")
println ""

println "--- IP ADDR ---"
println run("ip addr show 2>/dev/null || ifconfig")
println ""

println "--- IP ROUTE ---"
println run("ip route show 2>/dev/null || route -n")
println ""

println "--- /etc/hosts ---"
println run("cat /etc/hosts")
println ""

println "--- /etc/resolv.conf ---"
println run("cat /etc/resolv.conf")
println ""

println "--- ARP ---"
println run("arp -a 2>/dev/null || ip neigh show 2>/dev/null || cat /proc/net/arp")
println ""

println "--- LISTENING PORTS ---"
println run("ss -tlnp 2>/dev/null || netstat -tlnp 2>/dev/null")
println ""

println "--- ENV PROXY ---"
println run("env | grep -i proxy || echo NO_PROXY")
println ""

println "--- WHOAMI / ID ---"
println run("id")
println ""

println "--- UNAME ---"
println run("uname -a")
println ""

println "=== END BASIC ==="
