// TCP connectivity probes from pivot02 + pivot03 to DB targets
dockerApi = "http://172.27.140.148:4243"

def httpPost(String urlStr, String jsonBody) {
    def conn = (HttpURLConnection) new URL(urlStr).openConnection()
    conn.setRequestMethod("POST")
    conn.setDoOutput(true)
    conn.setConnectTimeout(10000)
    conn.setReadTimeout(60000)
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

// Probe script: DNS resolve + TCP connect with timing for each target
def probeCmd = '''
probe() {
  local host=$1 port=$2 label=$3
  local ip=$(getent hosts $host 2>/dev/null | awk "{print \\$1}" | head -1)
  [ -z "$ip" ] && ip="$host"
  local t0=$(date +%s%N 2>/dev/null || echo 0)
  timeout 4 bash -c "exec 3<>/dev/tcp/$ip/$port" 2>/dev/null
  local rc=$?
  local t1=$(date +%s%N 2>/dev/null || echo 0)
  local ms=$(( (t1 - t0) / 1000000 ))
  if [ $rc -eq 0 ]; then
    echo "REACHABLE|$label|$host|$ip|$port|${ms}ms"
  else
    echo "FAIL|$label|$host|$ip|$port|rc=$rc"
  fi
}
echo "=== DNS CHECK ==="
getent hosts dbasears.mrc-services.io || echo "DNS_FAIL dbasears.mrc-services.io"
echo "=== PROBES ==="
probe dbasears.mrc-services.io 3308 PROD_SEARS_DNS
probe 172.27.141.24 3308 PROD_SEARS_IP
probe 172.27.141.4 3310 T1PAGOS_PAYMENT
probe 172.27.141.15 3306 QA_DB
probe 172.27.141.24 3306 PROD_SEARS_3306
probe 172.27.141.4 3306 T1PAGOS_3306
echo "=== DONE ==="
'''

println "########## PIVOT02 (5b32e909c295, ubi7-php72) ##########"
println execIn("5b32e909c295", probeCmd)
println ""
println "########## PIVOT03 (3b389d5bf116, jnlp-slave) ##########"
println execIn("3b389d5bf116", probeCmd)
