// MICRO-S: Find the actual USERVAR values from build parameters
def run = { cmd ->
    def p = ["bash", "-c", cmd].execute()
    def out = new StringBuffer(); def err = new StringBuffer()
    p.consumeProcessOutput(out, err)
    p.waitForOrKill(20000)
    out.toString().take(6000)
}

// Jenkins build parameters are stored in build.xml files as <parameters>
println "=== BUILD.XML parameters for caja-api (last build) ==="
println run("cat /var/jenkins_home/jobs/cs_legacy_front/jobs/cs_legacy_pipe_build_caja-api/builds/889/build.xml 2>/dev/null")

// Also check if there's a parameters folder or env inject file
println "\n=== CAJA-API build 889 files ==="
println run("ls -la /var/jenkins_home/jobs/cs_legacy_front/jobs/cs_legacy_pipe_build_caja-api/builds/889/ 2>/dev/null")

// Check for EnvInject plugin data
println "\n=== EnvInject data in caja-api build ==="
println run("find /var/jenkins_home/jobs/cs_legacy_front/jobs/cs_legacy_pipe_build_caja-api -name 'injectedEnvVars.txt' -o -name 'envVars.properties' 2>/dev/null | head -5 | xargs cat 2>/dev/null | head -50")

// Check for env file in build artifacts
println "\n=== Tienda last build.xml ==="
println run("find /var/jenkins_home/jobs/cs_legacy_front/jobs/cs_legacy_pipe_build_tienda/builds -name 'build.xml' 2>/dev/null | sort -V | tail -1 | xargs cat 2>/dev/null | head -100")

// Check if there's a 'withEnv' value stored in pipeline node data
println "\n=== caja-api workflow node 49 ==="
println run("find /var/jenkins_home/jobs/cs_legacy_front/jobs/cs_legacy_pipe_build_caja-api/builds/889/workflow -name '*.xml' 2>/dev/null | head -5")
println run("cat /var/jenkins_home/jobs/cs_legacy_front/jobs/cs_legacy_pipe_build_caja-api/builds/889/workflow/49.xml 2>/dev/null")

println "\n=== DONE MICRO-S ==="
