import groovy.json.JsonSlurper
import groovy.json.JsonOutput

def dHost = "172.27.140.148"
def dPort = 4243
def cid = "5b32e909c295"

def phpB64 = java.util.Base64.encoder.encodeToString('''<?php
$c=new mysqli("172.27.141.6","app_t1","wUt22Us2CUh#+M=","payment_t1",3310);
if($c->connect_error){die("FAIL:".$c->connect_error);}

echo "=== transaction date range ===\n";
$r=$c->query("SELECT MIN(creation_date) as mn, MAX(creation_date) as mx, COUNT(*) as tot FROM transaction");
while($row=$r->fetch_assoc()){echo "min=$row[mn] max=$row[mx] total=$row[tot]\n";}

echo "\n=== last 10 transactions ===\n";
$r2=$c->query("SELECT id_transaction,id_authorization,id_order,status,code,decision,creation_date,LEFT(response,200) as resp FROM transaction ORDER BY creation_date DESC LIMIT 10");
if($r2){
    while($row=$r2->fetch_assoc()){
        echo "{$row[id_transaction]}|{$row[id_authorization]}|{$row[id_order]}|{$row[status]}|{$row[code]}|{$row[decision]}|{$row[creation_date]}|{$row[resp]}\n";
    }
}

echo "\n=== transactions per year ===\n";
$r3=$c->query("SELECT YEAR(creation_date) as yr, COUNT(*) as cnt FROM transaction GROUP BY YEAR(creation_date) ORDER BY yr DESC");
if($r3){while($row=$r3->fetch_assoc()){echo "$row[yr]: $row[cnt]\n";}}

$c->close();
?>'''.getBytes("UTF-8"))

def url1 = new URL("http://${dHost}:${dPort}/containers/${cid}/exec")
def c1 = url1.openConnection()
c1.setRequestMethod("POST")
c1.setDoOutput(true)
c1.setRequestProperty("Content-Type", "application/json")
c1.setConnectTimeout(5000)
c1.setReadTimeout(30000)
def b1 = JsonOutput.toJson([AttachStdout: true, AttachStderr: true, Cmd: ["bash", "-c", "echo ${phpB64} | base64 -d > /tmp/t1dates.php && php /tmp/t1dates.php"]])
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
