import groovy.json.JsonSlurper
import groovy.json.JsonOutput

def dHost = "172.27.140.148"
def dPort = 4243
def cid = "5b32e909c295"

def phpB64 = java.util.Base64.encoder.encodeToString('''<?php
$c=new mysqli("187.191.91.37","adaxxidb","JTQ6PrkecY3y1kVN","tienda",3306);
if($c->connect_error){die("FAIL:".$c->connect_error);}

// Check date ranges across key tables on THIS server (187.191.91.37)
$tables = [
    ["credito_clarotel_credcliente","fecha_alta"],
    ["credito_clarotel_credcliente","fecha_modificacion"],
    ["credito_clarotel_lineac","fecha_alta"],
    ["credito_clarotel_lineac","fecha_modificacion"],
    ["credito_clarotel_login","fecha_alta"],
    ["credito_clarotel_login","fecha_modificacion"],
    ["credito_clarotel_datos_facturacion","fecha_alta"],
    ["credito_clarotel_datos_facturacion","fecha_modificacion"],
    ["credito_clarotel_pedidos_conciliados","fecha_alta"],
    ["credito_clarotel_pedidos_conciliados","fecha_modificacion"],
    ["credito_clarotel_movimientos","fecha_alta"],
    ["credito_clarotel_movimientos","fecha_modificacion"],
    ["credito_clarotel_antifraude","fecha_alta"],
    ["credito_clarotel_validacion_ip","fecha_alta"],
    ["telmex_ws_login","fecha"],
    ["telmex_ws_lineacredito","fecha"],
    ["telmex_ws_os","fecha"],
    ["pedidos","fecha"],
    ["datos_pedido","fecha"],
    ["datostarjeta","fecha"],
    ["datos_clientes","fecha"],
    ["clientes","fecha"],
];

echo "schema|table|date_col|min_date|max_date|total\n";
foreach($tables as $t){
    $tbl=$t[0];$col=$t[1];
    // Verify column exists
    $chk=$c->query("SHOW COLUMNS FROM $tbl LIKE '$col'");
    if(!$chk || $chk->num_rows==0){
        echo "tienda|$tbl|$col|COL_NOT_EXISTS||\n";
        continue;
    }
    $r=$c->query("SELECT MIN($col) as mn, MAX($col) as mx, COUNT(*) as tot FROM $tbl WHERE $col IS NOT NULL AND $col > '2000-01-01'");
    if($r){
        $row=$r->fetch_row();
        echo "tienda|$tbl|$col|".($row[0]?$row[0]:"NULL")."|".($row[1]?$row[1]:"NULL")."|$row[2]\n";
    }else{
        echo "tienda|$tbl|$col|ERR:".$c->error."\n";
    }
}

// Also check dbgomezt_test dates
echo "\n=== dbgomezt_test dates ===\n";
$tbls2=[["credito_clarotel_login","fecha_alta"],["credito_clarotel_lineac","fecha_alta"],["credito_clarotel_antifraude","fecha_alta"]];
foreach($tbls2 as $t){
    $tbl=$t[0];$col=$t[1];
    $chk=$c->query("SHOW COLUMNS FROM dbgomezt_test.$tbl LIKE '$col'");
    if(!$chk || $chk->num_rows==0){
        echo "dbgomezt_test|$tbl|$col|COL_NOT_EXISTS||\n";
        continue;
    }
    $r=$c->query("SELECT MIN($col),MAX($col),COUNT(*) FROM dbgomezt_test.$tbl WHERE $col IS NOT NULL AND $col > '2000-01-01'");
    if($r){
        $row=$r->fetch_row();
        echo "dbgomezt_test|$tbl|$col|".($row[0]?$row[0]:"NULL")."|".($row[1]?$row[1]:"NULL")."|$row[2]\n";
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
def b1 = JsonOutput.toJson([AttachStdout: true, AttachStderr: true, Cmd: ["bash", "-c", "echo ${phpB64} | base64 -d > /tmp/tqdates.php && php /tmp/tqdates.php"]])
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
