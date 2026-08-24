def run(cmd) {
    try {
        def proc = ['bash', '-c', cmd].execute()
        proc.waitFor()
        return proc.text.trim()
    } catch (e) { return "ERR" }
}
println "=== SSH TUNNEL DETAIL ==="
println run("cat /proc/32561/cmdline 2>/dev/null | tr '\\0' ' ' || echo 'PID_GONE'")
println "---"
println run("ps aux | grep -E 'ssh|tunnel' | grep -v grep")
println "---REDIS---"
println run("timeout 2 bash -c 'exec 3<>/dev/tcp/172.27.140.151/6379; echo \"PING\" >&3; timeout 1 cat <&3'")
println "---OCP---"
println run("timeout 1 bash -c 'echo > /dev/tcp/172.26.127.196/8443' 2>/dev/null && echo OPEN || echo CLOSED")
