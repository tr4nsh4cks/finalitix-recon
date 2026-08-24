import groovy.json.JsonOutput
import groovy.json.JsonSlurper

def dockerExec(String cmd) {
    def create = new URL("http://172.27.140.148:4243/containers/5b32e909c295/exec").openConnection()
    create.setRequestMethod("POST")
    create.setDoOutput(true)
    create.setConnectTimeout(10000)
    create.setReadTimeout(30000)
    create.setRequestProperty("Content-Type", "application/json")
    def body = JsonOutput.toJson([AttachStdout:true, AttachStderr:true, Tty:true, Cmd:["sh","-c",cmd]])
    create.getOutputStream().write(body.getBytes("UTF-8"))
    def respCode = create.getResponseCode()
    def respText = create.getInputStream().getText("UTF-8")
    def resp = new JsonSlurper().parseText(respText)
    def execId = resp.Id

    def start = new URL("http://172.27.140.148:4243/exec/${execId}/start").openConnection()
    start.setRequestMethod("POST")
    start.setDoOutput(true)
    start.setConnectTimeout(10000)
    start.setReadTimeout(60000)
    start.setRequestProperty("Content-Type", "application/json")
    def startBody = JsonOutput.toJson([Detach:false, Tty:true])
    start.getOutputStream().write(startBody.getBytes("UTF-8"))
    return start.getInputStream().getText("UTF-8")
}

try {
    println "=== PROBE START ==="
    println dockerExec("id; php -v 2>&1 | head -2; php -m 2>&1 | grep -i mysql")
    println "=== PROBE END ==="
} catch (Exception e) {
    println "ERROR: " + e.getMessage()
    e.printStackTrace()
}
