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

def b64Script = "{php_code.encode('utf-8').hex()}"
def writeCmd = ["bash", "-c", "python -c \\"import binascii; open('/tmp/probe2.php','wb').write(binascii.unhexlify('${{b64Script}}'))\\""]
dockerExec(cid, writeCmd)

def runCmd = ["php", "/tmp/probe2.php"]
println dockerExec(cid, runCmd)
'''
    return jenkins_groovy(groovy)

php_test = """<?php
$host = '172.27.141.6';
$port = 3308;
$user = 'apifincadodev';
$pass = '1q2w3e4r5t6y';
$db   = 'tienda';

$m = new mysqli($host, $user, $pass, $db, $port);
$m->set_charset("utf8");

echo "=== DATES IN datos_clientes ===\\n";
$r = $m->query("SELECT MAX(Fecha_Inicio) as max_fi, MIN(Fecha_Inicio) as min_fi FROM tienda.datos_clientes");
if ($r) {
    $row = $r->fetch_assoc();
    echo "datos_clientes.Fecha_Inicio: MIN=" . $row['min_fi'] . " MAX=" . $row['max_fi'] . "\\n";
}

$r = $m->query("SELECT COUNT(*) as orphan FROM tienda.datos_clientes WHERE Cliente NOT IN (SELECT Id FROM tienda.clientes)");
$row = $r->fetch_assoc();
echo "Orphan datos_clientes: " . $row['orphan'] . "\\n";

$r = $m->query("SELECT COUNT(DISTINCT Cliente) as distinct_c FROM tienda.datos_clientes");
$row = $r->fetch_assoc();
echo "Distinct Cliente in datos_clientes: " . $row['distinct_c'] . "\\n";

$m->close();
?>"""

if __name__ == '__main__':
    out = run_php_in_docker(php_test)
    print(out)
