def run(cmd) {
    try {
        def proc = ['bash', '-c', cmd].execute()
        proc.waitFor()
        return proc.text.trim()
    } catch (e) { return "ERR:${e.message}" }
}
println "=== SSH TUNNEL DETAILS ==="
println "--- SSH process cmdline ---"
println run("cat /proc/32561/cmdline 2>/dev/null | tr '\\0' ' '")
println ""
println "--- All SSH processes ---"
println run("ps aux | grep ssh | grep -v grep")
println ""
println "--- Jenkins jobs XML with DB refs ---"
println run("grep -rl 'jdbc\\|mysql\\|13306\\|13307\\|13308\\|dbasears\\|3308' /var/jenkins_home/jobs/ 2>/dev/null | head -10")
println ""
println "--- Jenkins config with tunnel refs ---"
println run("grep -r '13306\\|13307\\|13308\\|tunnel\\|LocalForward\\|portForward' /var/jenkins_home/ 2>/dev/null | grep -v '.log' | head -20")
println ""
println "--- SSH config ---"
println run("cat /var/jenkins_home/.ssh/config 2>/dev/null || cat ~/.ssh/config 2>/dev/null || echo NOCONF")
println ""
println "--- OpenShift target ---"
println run("timeout 2 bash -c 'echo > /dev/tcp/172.26.127.196/8443' && echo OPEN || echo CLOSED")
println ""
println "--- Redis test ---"
println run("timeout 2 bash -c 'exec 3<>/dev/tcp/172.27.140.151/6379; echo PING >&3; cat <&3' 2>/dev/null | head -3")
println ""
println "=== END ==="
