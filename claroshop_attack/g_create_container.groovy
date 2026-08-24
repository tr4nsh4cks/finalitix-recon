// Create pivot04 container (host network) + verify connectivity from it
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

// 1) List images (names only)
println "=== IMAGES ==="
def imgs = httpGet(dockerApi + "/images/json")
if (imgs.code == 200) {
    def arr = new groovy.json.JsonSlurper().parseText(imgs.body)
    arr.each { img ->
        def tags = img.RepoTags ? img.RepoTags.join(",") : "<none>"
        println img.Id.substring(7,19) + " | " + tags
    }
}

// 2) Check if pivot04 already exists
def existing = httpGet(dockerApi + "/containers/json?all=true")
def already = false
if (existing.code == 200) {
    def arr = new groovy.json.JsonSlurper().parseText(existing.body)
    arr.each { c -> if (c.Names.toString().contains("pivot04")) already = true }
}
println ""
println "pivot04 exists already: " + already

if (!already) {
    // 3) Create container with host network (image already local -> no pull)
    def createJson = '{"Image":"docker-registry.nexus.dev.claroshop.com/ubi7-php72:latest","Cmd":["/bin/bash","-c","while true; do sleep 60; done"],"HostConfig":{"NetworkMode":"host"},"Labels":{"Description":"CS MSA builder","Vendor":"Dragoon MSA"}}'
    def rc = httpPost(dockerApi + "/containers/create?name=pivot04", createJson)
    println "CREATE HTTP " + rc.code + ": " + rc.body
    if (rc.code == 201) {
        def newId = new groovy.json.JsonSlurper().parseText(rc.body).Id
        def rs = httpPost(dockerApi + "/containers/" + newId + "/start", null)
        println "START HTTP " + rs.code + (rs.body ? ": " + rs.body : "")
    }
} else {
    println "Reusing existing pivot04"
}

// 4) Verify: probe T1Pagos MySQL from pivot04
println ""
println "=== VERIFY FROM pivot04 ==="
println execIn("pivot04", 'timeout 4 bash -c "exec 3<>/dev/tcp/172.27.141.6/3310" && echo "PIVOT04 -> 172.27.141.6:3310 OK" || echo "PIVOT04 FAIL"; php -v 2>/dev/null | head -1')
