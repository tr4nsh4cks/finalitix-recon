// Escanea TODOS los config.xml buscando SSH publishers e IPs target
// Sin XmlSlurper - puro regex/string

import jenkins.model.Jenkins

def TARGETS = ["172.27.141", "172.26.", "dbasears", "t1envios", "t1pagos", "mrc-services", "t1pago", "sears.mrc", "t1pay"]
def results = []

Jenkins.getInstance().getAllItems().each { job ->
    def configPath = "/var/jenkins_home/jobs/" + job.fullName.replace("/", "/jobs/") + "/config.xml"
    def configFile = new File(configPath)
    if (!configFile.exists()) return
    
    def content = configFile.text
    
    def hasSSH = content.contains("BapSshPublisher") ||
                 content.contains("publish_over_ssh") ||
                 content.contains("sshPublisher") ||
                 content.contains("jenkins.plugins.publish_over_ssh") ||
                 content.contains("SSHLauncher")
    
    def hasTarget = TARGETS.any { t -> content.toLowerCase().contains(t.toLowerCase()) }
    
    if (!hasSSH && !hasTarget) return
    
    def info = [
        job: job.fullName,
        type: job.class.simpleName,
        hasSSH: hasSSH,
        hasTargetIPs: hasTarget,
        matches: []
    ]
    
    // Extract SSH publisher hostnames
    (content =~ /<hostname>([^<]+)<\/hostname>/).each { m -> info.matches << "SSH_HOST: ${m[1]}" }
    (content =~ /<username>([^<]+)<\/username>/).each { m -> info.matches << "SSH_USER: ${m[1]}" }
    (content =~ /<remoteDirectory>([^<]+)<\/remoteDirectory>/).each { m -> info.matches << "REMOTE_DIR: ${m[1]}" }
    (content =~ /<credentialsId>([^<]+)<\/credentialsId>/).each { m -> info.matches << "CRED_ID: ${m[1]}" }
    (content =~ /<configVersion>([^<]+)<\/configVersion>/).each { m -> info.matches << "CONFIG_VER: ${m[1]}" }
    
    // Extract lines with target IPs/hosts
    content.split("\n").eachWithIndex { line, i ->
        TARGETS.each { t ->
            if (line.toLowerCase().contains(t.toLowerCase())) {
                def trimmed = line.trim().take(200)
                if (!info.matches.contains("TARGET: ${trimmed}")) {
                    info.matches << "TARGET: ${trimmed}"
                }
            }
        }
    }
    
    results << info
}

println "=" * 70
println "TOTAL INTERESTING JOBS: ${results.size()}"
println "WITH SSH: ${results.count { it.hasSSH }}"
println "WITH TARGET IPs: ${results.count { it.hasTargetIPs }}"
println "=" * 70

results.each { r ->
    println "\nJOB: ${r.job}"
    println "Type: ${r.type} | SSH: ${r.hasSSH} | TargetIPs: ${r.hasTargetIPs}"
    r.matches.unique().each { m -> println "  >> ${m}" }
    println "-" * 50
}
