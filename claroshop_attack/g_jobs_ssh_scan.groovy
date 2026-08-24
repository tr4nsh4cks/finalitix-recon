// Escanea TODOS los config.xml buscando:
// - SSH publishers (jenkins-publish-over-ssh)
// - IPs internas: 172.27.141.x, 172.26.x.x, dbasears, t1envios, t1pagos
// - credentialId references

import jenkins.model.Jenkins
import groovy.xml.XmlSlurper

def TARGETS = ["172.27.141", "172.26.", "dbasears", "t1envios", "t1pagos", "mrc-services", "t1pago", "sears"]
def results = []
def jobsWithSSH = []
def jobsWithTargetIPs = []

Jenkins.getInstance().getAllItems().each { job ->
    if (job instanceof jenkins.model.Jenkins.MasterComputer) return
    
    // Build path to config.xml
    def configPath = "/var/jenkins_home/jobs/" + job.fullName.replace("/", "/jobs/") + "/config.xml"
    def configFile = new File(configPath)
    if (!configFile.exists()) return
    
    def content = configFile.text
    
    // Check for SSH publishers
    def hasSSH = content.contains("jenkins.plugins.publish_over_ssh") || 
                 content.contains("BapSshPublisher") ||
                 content.contains("publish-over-ssh") ||
                 content.contains("sshPublisher")
    
    // Check for target IPs/hosts
    def hasTarget = TARGETS.any { t -> content.toLowerCase().contains(t.toLowerCase()) }
    
    if (hasSSH || hasTarget) {
        def info = [
            job: job.fullName,
            type: job.class.simpleName,
            hasSSH: hasSSH,
            hasTargetIPs: hasTarget,
            matches: []
        ]
        
        // Extract SSH publisher details
        if (hasSSH) {
            def sshMatches = (content =~ /(?i)<hostname>([^<]+)<\/hostname>/)
            sshMatches.each { m -> info.matches << "SSH_HOST: ${m[1]}" }
            
            def userMatches = (content =~ /(?i)<username>([^<]+)<\/username>/)
            userMatches.each { m -> info.matches << "SSH_USER: ${m[1]}" }
            
            def remoteDir = (content =~ /(?i)<remoteDirectory>([^<]+)<\/remoteDirectory>/)
            remoteDir.each { m -> info.matches << "REMOTE_DIR: ${m[1]}" }
            
            def credId = (content =~ /(?i)<credentialsId>([^<]+)<\/credentialsId>/)
            credId.each { m -> info.matches << "CRED_ID: ${m[1]}" }
        }
        
        // Extract target IP lines
        if (hasTarget) {
            content.split("\n").each { line ->
                TARGETS.each { t ->
                    if (line.toLowerCase().contains(t.toLowerCase())) {
                        info.matches << "TARGET_LINE: ${line.trim().take(200)}"
                    }
                }
            }
        }
        
        // Dedup matches
        info.matches = info.matches.unique()
        
        results << info
        if (hasSSH) jobsWithSSH << job.fullName
        if (hasTarget) jobsWithTargetIPs << job.fullName
    }
}

println "=" * 70
println "JOBS WITH SSH PUBLISHERS: ${jobsWithSSH.size()}"
println "JOBS WITH TARGET IPs: ${jobsWithTargetIPs.size()}"
println "TOTAL INTERESTING: ${results.size()}"
println "=" * 70

results.each { r ->
    println "\nJOB: ${r.job}"
    println "Type: ${r.type} | SSH: ${r.hasSSH} | TargetIPs: ${r.hasTargetIPs}"
    r.matches.unique().each { m ->
        println "  >> ${m}"
    }
    println "-" * 50
}

println "\n=== JOBS WITH SSH ONLY ==="
jobsWithSSH.each { println it }

println "\n=== JOBS WITH TARGET IPs ONLY ==="
jobsWithTargetIPs.each { println it }
