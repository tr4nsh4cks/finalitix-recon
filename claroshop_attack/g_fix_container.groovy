// Debug pivot04 exit + recreate with entrypoint override
dockerApi = "http://172.27.140.148:4243"

def httpGet(String urlStr) {
    def conn = (HttpURLConnection) new URL(urlStr).openConnection()
    conn.setRequestMethod("GET")
    conn.setConnectTimeout(10000)
    conn.setReadTimeout(30000)
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
    conn.setReadTimeout(60000)
    conn.setRequestProperty("Content-Type", "application/json")
    if (jsonBody != null) conn.getOutputStream().write(jsonBody.getBytes("UTF-8"))
    def code = conn.getResponseCode()
    def body = (code >= 400 ? conn.getErrorStream()?.getText("UTF-8") : conn.getInputStream().getText("UTF-8"))
    conn.disconnect()
    return [code: code, body: body]
}

def httpDelete(String urlStr) {
    def conn = (HttpURLConnection) new URL(urlStr).openConnection()
    conn.setRequestMethod("DELETE")
    conn.setConnectTimeout(10000)
    conn.setReadTimeout(30000)
    def code = conn.getResponseCode()
    def body = (code >= 400 ? conn.getErrorStream()?.getText("UTF-8") : (conn.getInputStream() ? conn.getInputStream().getText("UTF-8") : ""))
    conn.disconnect()
    return [code: code, body: body]
}

// Logs of exited pivot04
println "=== PIVOT04 LOGS ==="
def logs = httpGet(dockerApi + "/containers/pivot04/logs?stdout=true&stderr=true")
println "HTTP " + logs.code
println logs.body

// Image config: entrypoint?
println "=== IMAGE CONFIG ubi7-php72 ==="
def img = httpGet(dockerApi + "/images/docker-registry.nexus.dev.claroshop.com/ubi7-php72:latest/json")
if (img.code == 200) {
    def j = new groovy.json.JsonSlurper().parseText(img.body)
    println "Entrypoint: " + j.Config?.Entrypoint
    println "Cmd: " + j.Config?.Cmd
    println "User: " + j.Config?.User
    println "WorkingDir: " + j.Config?.WorkingDir
}

// Compare with pivot02 config (running OK)
println "=== PIVOT02 CONFIG (the one that works) ==="
def p2 = httpGet(dockerApi + "/containers/5b32e909c295/json")
if (p2.code == 200) {
    def j = new groovy.json.JsonSlurper().parseText(p2.body)
    println "Entrypoint: " + j.Config?.Entrypoint
    println "Cmd: " + j.Config?.Cmd
    println "User: " + j.Config?.User
    println "HostConfig.NetworkMode: " + j.HostConfig?.NetworkMode
    println "HostConfig.Privileged: " + j.HostConfig?.Privileged
    println "HostConfig.Binds: " + j.HostConfig?.Binds
}

// Remove failed pivot04, recreate matching pivot02 config
println "=== RECREATE pivot04 ==="
def del = httpDelete(dockerApi + "/containers/pivot04?force=true")
println "DELETE HTTP " + del.code

def createJson = '{"Image":"docker-registry.nexus.dev.claroshop.com/ubi7-php72:latest","Entrypoint":["/bin/bash"],"Cmd":["-c","while true; do sleep 60; done"],"HostConfig":{"NetworkMode":"host"}}'
def rc = httpPost(dockerApi + "/containers/create?name=pivot04", createJson)
println "CREATE HTTP " + rc.code + ": " + rc.body
if (rc.code == 201) {
    def newId = new groovy.json.JsonSlurper().parseText(rc.body).Id
    def rs = httpPost(dockerApi + "/containers/" + newId + "/start", null)
    println "START HTTP " + rs.code + (rs.body ? ": " + rs.body : "")
    Thread.sleep(2000)
    def st = httpGet(dockerApi + "/containers/pivot04/json")
    if (st.code == 200) {
        def sj = new groovy.json.JsonSlurper().parseText(st.body)
        println "STATE: " + sj.State.Status + " | Running: " + sj.State.Running + " | ExitCode: " + sj.State.ExitCode
    }
}
