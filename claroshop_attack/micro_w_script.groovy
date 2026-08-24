// MICRO-W: Extract pipeline lines with key commands
def run = { cmd ->
    def p = ["bash", "-c", cmd].execute()
    def out = new StringBuffer(); def err = new StringBuffer()
    p.consumeProcessOutput(out, err)
    p.waitForOrKill(15000)
    out.toString().take(6000)
}

def cfgPath = "/var/jenkins_home/jobs/cs_legacy_front/jobs/cs_legacy_pipe_build_caja-api/config.xml"

// Check line count and find script tag position
println "=== LINE COUNT + SCRIPT TAG ==="
println run("wc -l '${cfgPath}' && grep -n '<script\\|</script' '${cfgPath}' | head -5")

// Look for PROD environment deploy commands
println "\n=== KEY DEPLOY LINES (oc, ssh, rsync, GIT_PROJECT, PROD) ==="
println run("grep -n 'GIT_PROJECT\\|oc \\|kubectl\\|ssh \\|scp \\|rsync\\|PROD\\|prod\\|mrc-services\\|claroshop-services.io\\|172\\.27\\.' '${cfgPath}' | head -60 | sed \"s/&apos;/'/g; s/&quot;/\\\"/g; s/&lt;/</g; s/&gt;/>/g\"")

// Also look at the SSH/deploy server info
println "\n=== CAJA-API FULL LINE 160-230 ==="
println run("sed -n '160,230p' '${cfgPath}' | sed \"s/&apos;/'/g; s/&quot;/\\\"/g; s/&lt;/</g; s/&gt;/>/g; s/&#xd;/\\n/g\"")

// Also check if perl is available
println "\n=== PERL AVAILABLE? ==="
println run("perl -e 'print \"yes\"' 2>&1")

// If perl available, extract full script
println "\n=== FULL SCRIPT VIA PERL ==="
println run("perl -0777 -ne 'if(/<script>(.*?)<\\/script>/s){print \$1}' '${cfgPath}' | sed \"s/&apos;/'/g; s/&quot;/\\\"/g; s/&lt;/</g; s/&gt;/>/g\" | head -300")

println "\n=== DONE MICRO-W ==="
