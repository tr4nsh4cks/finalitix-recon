def run(cmd) {
    try {
        def proc = ['bash', '-c', cmd].execute()
        proc.waitFor()
        return proc.text.trim()
    } catch (e) {
        return "ERROR: ${e.message}"
    }
}

println "=== FULL PORT SCAN 172.27.141.0/24 ==="
println "From: Jenkins master (172.17.0.2 → gw 172.17.0.1)"
println ""

def ports = [22, 80, 443, 3306, 3308, 3310, 5432, 6379, 8080, 8443, 9090, 9000, 27017, 4243, 2375, 5000, 9200, 11211, 5601, 50000]

println "--- BATCH SCAN (bash /dev/tcp) ---"
def script = new StringBuilder()
script.append('for i in $(seq 1 254); do\n')
script.append('  ip="172.27.141.$i"\n')
script.append('  open=""\n')
ports.each { p ->
    script.append("  timeout 0.5 bash -c \"echo > /dev/tcp/\$ip/${p}\" 2>/dev/null && open=\"\$open ${p}\"\n")
}
script.append('  [ -n "$open" ] && echo "$ip:$open"\n')
script.append('done\n')

println run(script.toString())
println ""

println "--- SCAN 172.27.140.0/24 (quick) ---"
def script2 = new StringBuilder()
script2.append('for i in $(seq 1 254); do\n')
script2.append('  ip="172.27.140.$i"\n')
script2.append('  open=""\n')
[22, 80, 443, 3306, 4243, 2375, 8080, 6379, 9090, 5000, 8443, 9200].each { p ->
    script2.append("  timeout 0.5 bash -c \"echo > /dev/tcp/\$ip/${p}\" 2>/dev/null && open=\"\$open ${p}\"\n")
}
script2.append('  [ -n "$open" ] && echo "$ip:$open"\n')
script2.append('done\n')

println run(script2.toString())
println ""

println "=== LOCAL TUNNELS CHECK ==="
println run("ss -tlnp | grep -E '133[0-9]{2}'")
println ""
println "--- CONNECT TO LOCAL TUNNELS ---"
println run("timeout 2 bash -c 'echo > /dev/tcp/127.0.0.1/13306' 2>/dev/null && echo '13306 OPEN' || echo '13306 CLOSED'")
println run("timeout 2 bash -c 'echo > /dev/tcp/127.0.0.1/13307' 2>/dev/null && echo '13307 OPEN' || echo '13307 CLOSED'")
println run("timeout 2 bash -c 'echo > /dev/tcp/127.0.0.1/13308' 2>/dev/null && echo '13308 OPEN' || echo '13308 CLOSED'")
println run("timeout 2 bash -c 'echo > /dev/tcp/127.0.0.1/23456' 2>/dev/null && echo '23456 OPEN' || echo '23456 CLOSED'")
println ""

println "--- MySQL BANNER GRAB ON TUNNELS ---"
println run("timeout 2 bash -c 'cat < /dev/tcp/127.0.0.1/13306' 2>/dev/null | head -1 | strings || echo NOBANNER")
println run("timeout 2 bash -c 'cat < /dev/tcp/127.0.0.1/13307' 2>/dev/null | head -1 | strings || echo NOBANNER")
println run("timeout 2 bash -c 'cat < /dev/tcp/127.0.0.1/13308' 2>/dev/null | head -1 | strings || echo NOBANNER")
println ""

println "=== END SCAN ==="
