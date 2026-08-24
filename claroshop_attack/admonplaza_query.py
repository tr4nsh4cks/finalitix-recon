#!/usr/bin/env python3
# admonplaza_query.py — Ejecuta un script PHP dentro del container PHP (5b32e909c295)
# via Jenkins Groovy -> bash -> Docker API 172.27.140.148:4243 -> docker exec
# Uso: python admonplaza_query.py <script.php> [timeout]
import urllib.request, base64, json, urllib.parse, ssl, http.cookiejar, sys

sys.stdout.reconfigure(errors='replace')

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE
AUTH = base64.b64encode(b'eduardo.cruz:xwMyIxfkZZaDNkFg').decode()
BASE = 'https://jenkins-ng.dev.claroshop.com'
DOCKER = 'http://172.27.140.148:4243'
CONTAINER = '5b32e909c295'


def jenkins_exec(script, timeout=300):
    cj = http.cookiejar.CookieJar()
    opener = urllib.request.build_opener(
        urllib.request.HTTPCookieProcessor(cj),
        urllib.request.HTTPSHandler(context=ctx))
    req = urllib.request.Request(BASE + '/crumbIssuer/api/json',
                                 headers={'Authorization': 'Basic ' + AUTH})
    crumb = json.loads(opener.open(req, timeout=20).read().decode())
    data = urllib.parse.urlencode({'script': script}).encode()
    req2 = urllib.request.Request(BASE + '/scriptText', data=data,
                                  headers={'Authorization': 'Basic ' + AUTH,
                                           crumb['crumbRequestField']: crumb['crumb']})
    return opener.open(req2, timeout=timeout).read().decode(errors='replace')


def run_php_in_container(php_code, timeout=300):
    php_b64 = base64.b64encode(php_code.encode()).decode()
    inner = "echo %s | base64 -d > /tmp/q_tr4.php && php /tmp/q_tr4.php" % php_b64
    payload = json.dumps({
        "Cmd": ["sh", "-c", inner],
        "AttachStdout": True,
        "AttachStderr": True,
    })
    bash_script = (
        "EXEC_ID=$(curl -s -X POST %s/containers/%s/exec "
        "-H 'Content-Type: application/json' "
        "-d '%s' | python -c \"import sys,json;print json.load(sys.stdin)['Id']\")\n"
        "echo \"EXEC_ID=$EXEC_ID\"\n"
        "curl -s -X POST %s/exec/$EXEC_ID/start "
        "-H 'Content-Type: application/json' "
        "-d '{\"Detach\":false,\"Tty\":false}'\n"
    ) % (DOCKER, CONTAINER, payload, DOCKER)
    bash_b64 = base64.b64encode(bash_script.encode()).decode()
    groovy = 'def r = ["bash","-c","echo %s | base64 -d | bash"].execute().text\nprintln r\n' % bash_b64
    return jenkins_exec(groovy, timeout=timeout)


if __name__ == '__main__':
    php_file = sys.argv[1]
    timeout = int(sys.argv[2]) if len(sys.argv) > 2 else 300
    php_code = open(php_file, encoding='utf-8').read()
    out = run_php_in_container(php_code, timeout=timeout)
    print(out)
