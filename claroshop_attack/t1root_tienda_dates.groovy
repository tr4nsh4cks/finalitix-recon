import groovy.json.JsonSlurper
import groovy.json.JsonOutput

def dHost = "172.27.140.148"
def dPort = 4243
def cid = "5b32e909c295"

def phpB64 = java.util.Base64.encoder.encodeToString('''<?php
$c=new mysqli("172.27.141.4","root","password","tienda",3306);
if($c->connect_error){die("FAIL:".$c->connect_error);}

$checks = [
    ["clientes","fecha_creacion"],
    ["clientes","fecha_modificacion"],
    ["pedidos","fecha"],
    ["pedidos","Fecha_Inicio"],
    ["datos_clientes","Fecha_Inicio"],
    ["datos_pedido","Fecha_Inicio"],
    ["comentarios_pedidos","fecha"],
    ["comercio_pedidos","fecha"],
    ["relacion_pedidos","fecha"],
    ["datostarjeta","fecha"],
    ["datos_pedido","fecha"],
];

echo "table|date_col|min_date|max_date|total\n";
foreach($checks as $t){
    $tbl=$t[0];$col=$t[1];
    $chk=$c->query("SHOW COLUMNS FROM $tbl LIKE '$col'");
    if(!$chk || $chk->num_rows==0){
        echo "$tbl|$col|COL_NOT_EXISTS||\n";
        continue;
    }
    $r=$c->query("SELECT MIN($col) as mn, MAX($col) as mx, COUNT(*) as tot FROM $tbl WHERE $col IS NOT NULL AND $col > '2000-01-01'");
    if($r){
        $row=$r->fetch_row();
        echo "$tbl|$col|".($row[0]?$row[0]:"NULL")."|".($row[1]?$row[1]:"NULL")."|$row[2]\n";
    }
}

echo "\n=== DESCRIBE clientes (key cols) ===\n";
$r2=$c->query("DESCRIBE clientes");
if($r2){while($col=$r2->fetch_row()){echo "$col[0]|$col[1]\n";}}

echo "\n=== DESCRIBE pedidos (key cols) ===\n";
$r3=$c->query("DESCRIBE pedidos");
if($r3){while($col=$r3->fetch_row()){echo "$col[0]|$col[1]\n";}}

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
