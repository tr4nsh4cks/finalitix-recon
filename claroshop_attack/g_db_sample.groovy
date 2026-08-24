// Sample data from payment_t1 (read-only, LIMIT 3) + schema
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

def php = '''<?php
error_reporting(0);
$pdo = new PDO("mysql:host=172.27.141.6;port=3310;dbname=payment_t1", "app_t1", "wUt22Us2CUh#+M=", array(PDO::ATTR_TIMEOUT => 8, PDO::ATTR_ERRMODE => PDO::ERRMODE_EXCEPTION));
echo "=== SCHEMA client ===\\n";
foreach ($pdo->query("DESCRIBE client") as $r) { echo $r[0]." | ".$r[1]."\\n"; }
echo "=== SCHEMA transaction ===\\n";
foreach ($pdo->query("DESCRIBE `transaction`") as $r) { echo $r[0]." | ".$r[1]."\\n"; }
echo "=== SAMPLE client (3) ===\\n";
foreach ($pdo->query("SELECT * FROM client LIMIT 3") as $r) { echo json_encode($r, JSON_UNESCAPED_UNICODE)."\\n"; }
echo "=== SAMPLE transaction (3, mas recientes) ===\\n";
foreach ($pdo->query("SELECT * FROM `transaction` ORDER BY 1 DESC LIMIT 3") as $r) { echo json_encode($r, JSON_UNESCAPED_UNICODE)."\\n"; }
echo "PHP_DONE\\n";
'''

def b64 = php.getBytes("UTF-8").encodeBase64().toString()
def cmd = "echo " + b64 + " | base64 -d > /tmp/s.php && php /tmp/s.php; rm -f /tmp/s.php"

println "########## payment_t1 SAMPLE DATA ##########"
println execIn("5b32e909c295", cmd)
