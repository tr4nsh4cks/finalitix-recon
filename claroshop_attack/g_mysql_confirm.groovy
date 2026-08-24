// Port sweep + MySQL auth confirmation via PHP PDO in pivot02
dockerApi = "http://172.27.140.148:4243"

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

def execIn(String containerId, String cmd) {
    def createBody = '{"AttachStdout":true,"AttachStderr":true,"Tty":true,"Cmd":["/bin/bash","-c",' + groovy.json.JsonOutput.toJson(cmd) + ']}'
    def r1 = httpPost(dockerApi + "/containers/" + containerId + "/exec", createBody)
    if (r1.code != 201) { return "EXEC_CREATE_FAIL HTTP " + r1.code + ": " + r1.body }
    def execId = new groovy.json.JsonSlurper().parseText(r1.body).Id
    def r2 = httpPost(dockerApi + "/exec/" + execId + "/start", '{"Detach":false,"Tty":true}')
    return r2.body
}

// 1) Port sweep on key hosts
def sweepCmd = '''
sweep() {
  local host=$1; shift
  for port in "$@"; do
    timeout 2 bash -c "exec 3<>/dev/tcp/$host/$port" 2>/dev/null && echo "OPEN|$host|$port" || echo "CLOSED|$host|$port"
  done
}
echo "### SWEEP 172.27.141.24 (PROD Sears) ###"
sweep 172.27.141.24 3306 3308 3310 3307 33060 33061 5432 1433 1521 27017 6379 22 80 443
echo "### SWEEP 172.27.141.4 (T1Pagos) ###"
sweep 172.27.141.4 3306 3308 3310 3307 33060 22 80 443
echo "### SWEEP 172.27.141.15 (QA) ###"
sweep 172.27.141.15 3306 3308 3310 22
echo "### DONE ###"
'''
println "########## PORT SWEEPS (pivot02) ##########"
println execIn("5b32e909c295", sweepCmd)
