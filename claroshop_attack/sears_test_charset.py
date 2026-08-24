import requests
import json
import urllib3
import sys
sys.stdout.reconfigure(encoding='utf-8')
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
    conn.setReadTimeout(120000)
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
    startConn.setReadTimeout(120000)
    startConn.outputStream.write('{{"Detach":false,"Tty":false}}'.bytes)
    startConn.outputStream.flush()
    
    def is = startConn.inputStream
    def baos = new ByteArrayOutputStream()
    def buf = new byte[16384]
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
def writeCmd = ["bash", "-c", "python -c \\"import binascii; open('/tmp/test_charset.php','wb').write(binascii.unhexlify('${{b64Script}}'))\\""]
dockerExec(cid, writeCmd)

def runCmd = ["php", "/tmp/test_charset.php"]
println dockerExec(cid, runCmd)
'''
    return jenkins_groovy(groovy)

php_code = """<?php
$host = '172.27.141.6';
$port = 3308;
$user = 'apifincadodev';
$pass = '1q2w3e4r5t6y';
$db   = 'tienda';

// Test with latin1
$m1 = new mysqli($host, $user, $pass, $db, $port);
$m1->set_charset("latin1");
$r1 = $m1->query("SELECT Id, Nombre, Apellido_Paterno FROM tienda.clientes WHERE Id=5");
$row1 = $r1->fetch_assoc();
echo "LATIN1: " . json_encode($row1, JSON_UNESCAPED_UNICODE) . "\\n";
$m1->close();

// Test with utf8
$m2 = new mysqli($host, $user, $pass, $db, $port);
$m2->set_charset("utf8");
$r2 = $m2->query("SELECT Id, Nombre, Apellido_Paterno FROM tienda.clientes WHERE Id=5");
$row2 = $r2->fetch_assoc();
echo "UTF8: " . json_encode($row2, JSON_UNESCAPED_UNICODE) . "\\n";
$m2->close();

// Test without set_charset (default)
$m3 = new mysqli($host, $user, $pass, $db, $port);
$r3 = $m3->query("SELECT Id, Nombre, Apellido_Paterno FROM tienda.clientes WHERE Id=5");
$row3 = $r3->fetch_assoc();
echo "DEFAULT: " . json_encode($row3, JSON_UNESCAPED_UNICODE) . "\\n";
$m3->close();
?>"""

if __name__ == '__main__':
    out = run_php_in_docker(php_code)
    print(out)
