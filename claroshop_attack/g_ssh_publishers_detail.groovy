// Extrae hostname exacto de todos los SSH publishers en config.xml
// Además lee los Groovy scripts del repo de t1pagos/t1envios buscando DB creds

import jenkins.model.Jenkins

println "=== SSH PUBLISHER HOSTS DETAIL ==="

def sshHostMap = [:]
def interesting = []

Jenkins.getInstance().getAllItems().each { job ->
    def configPath = "/var/jenkins_home/jobs/" + job.fullName.replace("/", "/jobs/") + "/config.xml"
    def configFile = new File(configPath)
    if (!configFile.exists()) return
    
    def content = configFile.text
    
    if (!content.contains("BapSshPublisher") && !content.contains("SSHLauncher") && 
        !content.contains("jenkins.plugins.publish_over_ssh") && !content.contains("sshPublisher")) return
    
    // Extract hostname from publish-over-ssh
    def hostMatches = (content =~ /<configName>([^<]+)<\/configName>/)
    def hostnames = (content =~ /<hostname>([^<]+)<\/hostname>/)
    
    hostMatches.each { m ->
        def cfg = m[1]
        if (!sshHostMap.containsKey(cfg)) sshHostMap[cfg] = []
        sshHostMap[cfg] << job.fullName
    }
    
    hostnames.each { m ->
        def h = m[1]
        if (!sshHostMap.containsKey(h)) sshHostMap[h] = []
        sshHostMap[h] << job.fullName
    }
    
    // Check for DB strings and interesting jobs
    def hasDB = content.contains("DB_HOST") || content.contains("DATABASE_HOST") || 
                content.contains("MYSQL_HOST") || content.contains("dbasears") ||
                content.contains("DB_PASSWORD") || content.contains("172.27.141.24") ||
                content.contains("172.27.141.4:")
    
    if (hasDB) {
        interesting << [job: job.fullName, content: content.take(3000)]
    }
}

println "\n--- SSH Config Names / Hostnames Seen ---"
sshHostMap.each { host, jobs ->
    println "HOST: ${host}"
    jobs.unique().take(5).each { j -> println "  JOB: ${j}" }
}

println "\n--- JOBS WITH DB CONNECTIONS ---"
interesting.each { i ->
    println "\n=== JOB: ${i.job} ==="
    println i.content
    println "-" * 50
}

println "\n=== JENKINS GLOBAL SSH CONFIG ==="
// Read jenkins.plugins.publish_over_ssh.BapSshPublisherPlugin.xml if exists
["jenkins.plugins.publish_over_ssh.BapSshPublisherPlugin.xml",
 "com.cloudbees.jenkins.plugins.sshcredentials.impl.BasicSSHUserPrivateKey.xml",
 "ssh.xml",
 "publish-over-ssh.xml"].each { fname ->
    def f = new File("/var/jenkins_home/${fname}")
    if (f.exists()) {
        println "=== FILE: ${fname} ==="
        println f.text.take(5000)
    }
}

// Also check the plugin config
def pluginConf = new File("/var/jenkins_home/jenkins.plugins.publish_over_ssh.BapSshPublisherPlugin.xml")
if (pluginConf.exists()) {
    println "\n=== PUBLISH OVER SSH PLUGIN CONFIG ==="
    println pluginConf.text
}

// List all xml files in jenkins_home
println "\n=== ALL XML FILES IN JENKINS_HOME (root) ==="
new File("/var/jenkins_home").listFiles().findAll { it.name.endsWith(".xml") && !it.name.equals("credentials.xml") }.each {
    println "${it.name} (${it.length()} bytes)"
}
