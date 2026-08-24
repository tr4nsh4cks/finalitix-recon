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

# Query 1: List T1Pagos config archive files
print("=" * 60)
print("QUERY 1: T1Pagos config archive files")
print("=" * 60)
q1 = '''
def r = ["bash","-c","find /var/jenkins_home/jobs/cs_new_front/jobs/cs_new_pipe_build_t1pagos-api-config/builds -path '*/archive*' -type f 2>/dev/null | sort -t/ -k9 -n | tail -15"].execute().text
println r
'''
print(run_groovy(q1))

# Query 2: Read the latest T1Pagos properties
print("=" * 60)
print("QUERY 2: Latest T1Pagos config file contents")
print("=" * 60)
q2 = '''
def r = ["bash","-c","ls /var/jenkins_home/jobs/cs_new_front/jobs/cs_new_pipe_build_t1pagos-api-config/builds/ 2>/dev/null | sort -n | tail -3"].execute().text
def builds = r.trim().split("\\n")
builds.each { b ->
    if (b.trim()) {
        def path = "/var/jenkins_home/jobs/cs_new_front/jobs/cs_new_pipe_build_t1pagos-api-config/builds/" + b.trim() + "/archive"
        def files = ["bash","-c","find " + path + " -type f 2>/dev/null"].execute().text
        println "--- Build " + b.trim() + " ---"
        println files
        files.trim().split("\\n").each { f ->
            if (f.trim() && (f.contains(".properties") || f.contains(".env") || f.contains(".yml"))) {
                println "\\n>>> " + f.trim()
                def content = ["bash","-c","cat '" + f.trim() + "'"].execute().text
                println content
            }
        }
    }
}
'''
print(run_groovy(q2))
