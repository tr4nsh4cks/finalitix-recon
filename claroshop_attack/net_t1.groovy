def run(cmd) {
    try {
        def proc = ['bash', '-c', cmd].execute()
        proc.waitFor()
        return proc.text.trim()
    } catch (e) { return "ERR" }
}
println "=== TUNNELS ==="
println run("ss -tnp | head -30")
println "---BANNERS---"
println run("timeout 2 bash -c 'exec 3<>/dev/tcp/127.0.0.1/13306; cat <&3' 2>/dev/null | strings | head -3")
println "---"
println run("timeout 2 bash -c 'exec 3<>/dev/tcp/127.0.0.1/13307; cat <&3' 2>/dev/null | strings | head -3")
println "---"
println run("timeout 2 bash -c 'exec 3<>/dev/tcp/127.0.0.1/13308; cat <&3' 2>/dev/null | strings | head -3")
println "---ENV---"
println run("env | grep -iE 'db|mysql|jdbc|host' | head -10")
println "---SSH---"
println run("cat /root/.ssh/known_hosts 2>/dev/null; cat ~/.ssh/known_hosts 2>/dev/null; cat /var/jenkins_home/.ssh/known_hosts 2>/dev/null")
