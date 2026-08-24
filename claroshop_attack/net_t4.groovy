def run(cmd) {
    try {
        def proc = ['bash', '-c', cmd].execute()
        proc.waitFor()
        return proc.text.trim()
    } catch (e) { return "ERR" }
}
println "=== JENKINS DB CONFIG ==="
println run("find /var/jenkins_home -maxdepth 2 -name '*.xml' | xargs grep -l 'jdbc\\|dbasears\\|13306\\|3308' 2>/dev/null | head -5")
println "---"
println run("cat /var/jenkins_home/.ssh/config 2>/dev/null || echo NOCONF")
println "---"
println run("ls -la /var/jenkins_home/.ssh/ 2>/dev/null")
println "---"
println run("env | grep -iE 'JAVA_OPTS|JENKINS' | head -5")
