// MICRO-FIX: Use consumeProcessOutput to avoid Stream closed
def run = { args ->
    def p = args instanceof List ? args.execute() : ["bash", "-c", args].execute()
    def out = new StringBuffer()
    def err = new StringBuffer()
    p.consumeProcessOutput(out, err)
    p.waitForOrKill(15000)
    out.toString().take(2000)
}

// GitLab auth via HTTPS (follow redirect)
println "=== SESSION API (HTTPS -L) ==="
println run('curl -sk -L -X POST "https://172.27.140.134/api/v4/session" -H "Content-Type: application/json" -d \'{"login":"jenkins","password":"e6LBqIkOI$PR1XX2oia"}\' --max-time 8')

println "\n=== BASIC AUTH projects (HTTPS) ==="
println run('curl -sk -u "jenkins:e6LBqIkOI\$PR1XX2oia" "https://172.27.140.134/api/v4/projects?per_page=10&simple=true" --max-time 8')

println "\n=== maria.policarpo SESSION ==="
println run('curl -sk -L -X POST "https://172.27.140.134/api/v4/session" -H "Content-Type: application/json" -d \'{"login":"maria.policarpo","password":"FtMRl4fDXzIDY4Yj"}\' --max-time 8')

println "\n=== HTTP response code check ==="
println run('curl -sk -o /dev/null -w "%{http_code} -> %{redirect_url}" "http://172.27.140.134/api/v4/projects" --max-time 5')

println "\n=== Try hostname gitlab.dev.claroshop.com ==="
println run('curl -sk -u "jenkins:e6LBqIkOI\$PR1XX2oia" "https://gitlab.dev.claroshop.com/api/v4/projects?per_page=5&simple=true" --max-time 10')

println "\n=== DONE MICRO-FIX ==="
