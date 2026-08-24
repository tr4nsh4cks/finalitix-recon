def run(cmd) {
    try {
        def proc = ['bash', '-c', cmd].execute()
        proc.waitFor()
        return proc.text.trim()
    } catch (e) {
        return "ERROR: ${e.message}"
    }
}

println "=== TUNNEL & CONNECTION ANALYSIS ==="
println ""

println "--- LOCAL LISTENING (full detail) ---"
println run("ss -tlnp")
println ""

println "--- ESTABLISHED CONNECTIONS (who are tunnels talking to?) ---"
println run("ss -tnp | grep -E '1330[678]|23456'")
println ""

println "--- ALL ESTABLISHED (remote IPs) ---"
println run("ss -tn state established | sort | uniq -c | sort -rn | head -30")
println ""

println "--- JAVA PROCESS CONNECTIONS ---"
println run("ss -tnp | grep java | head -40")
println ""

println "--- /proc/net/tcp (full - decode later) ---"
println run("cat /proc/net/tcp | head -40")
println ""

println "--- MySQL client test on tunnels ---"
println run("mysql -h 127.0.0.1 -P 13306 -u root --connect-timeout=3 -e 'SELECT 1' 2>&1 || echo 'NO_MYSQL_CLIENT_OR_AUTH_FAIL'")
println run("mysql -h 127.0.0.1 -P 13307 -u root --connect-timeout=3 -e 'SELECT 1' 2>&1 || echo 'NO_MYSQL_CLIENT_OR_AUTH_FAIL'")
println run("mysql -h 127.0.0.1 -P 13308 -u root --connect-timeout=3 -e 'SELECT 1' 2>&1 || echo 'NO_MYSQL_CLIENT_OR_AUTH_FAIL'")
println ""

println "--- Banner grab tunnels (raw) ---"
println run("timeout 2 bash -c 'exec 3<>/dev/tcp/127.0.0.1/13306; cat <&3' 2>/dev/null | strings | head -5 || echo NOBANNER")
println run("timeout 2 bash -c 'exec 3<>/dev/tcp/127.0.0.1/13307; cat <&3' 2>/dev/null | strings | head -5 || echo NOBANNER")
println run("timeout 2 bash -c 'exec 3<>/dev/tcp/127.0.0.1/13308; cat <&3' 2>/dev/null | strings | head -5 || echo NOBANNER")
println ""

println "--- Jenkins config files (DB connections) ---"
println run("find /var/jenkins_home -name '*.xml' -exec grep -l 'jdbc\\|mysql\\|3306\\|3308\\|3310\\|dbasears\\|t1pagos\\|t1envios' {} \\; 2>/dev/null | head -20")
println ""

println "--- ENV vars with DB refs ---"
println run("env | grep -iE 'db|mysql|jdbc|host|port|pass|user' | grep -v PATH || echo 'NONE'")
println ""

println "--- SSH config/known_hosts ---"
println run("cat ~/.ssh/config 2>/dev/null || echo 'NO_SSH_CONFIG'")
println run("cat ~/.ssh/known_hosts 2>/dev/null | head -20 || echo 'NO_KNOWN_HOSTS'")
println ""

println "=== END TUNNELS ==="
