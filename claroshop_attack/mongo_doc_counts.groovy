import groovy.json.JsonSlurper
import groovy.json.JsonOutput

def dHost = "172.27.140.148"
def dPort = 4243
def cid = "5b32e909c295"

def phpB64 = java.util.Base64.encoder.encodeToString('''<?php
$m=new MongoDB\\Driver\\Manager("mongodb://172.26.84.132:27020");

$dbs = ["credito-claroshop","singlepages","sso","t1pagos","users-t1pay","tienda","t1_envios","t1fullfilment","tracking","reviews","shipping_ms","marketing","carga_productos_sears","credito_claroshop_stores","sso_sanborns","carts_db","carts_db_claroshop","carts_db_sanborns","wishlist_db","shein_ms","sms-notifications","repst1","guias_masivas","peticiones_api","addressms","cartms","categories","clarolive","clarolive_sears","claroshop","config","dbpixel","dbpixel_cs","dbpixel_se","indexado_db","myprueba","reviews_sanborns","reviews_sears","reviews_test","sanborns","sanborns_categories","sanborns_shipping","sears","sears_categories","sears_shipping","shipping","sif","sistema_trace","tracking_cs","productos_xml_sears","api_products","dbshipping_cost","marketing_sanborns","marketing_sears","marketing_wl","t1fullfilment_prueba"];

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
                $cmd2=new MongoDB\\Driver\\Command(["count"=>$cname]);
                $r2=$m->executeCommand($db,$cmd2);
                $r2->setTypeMap(["root"=>"array","array"=>"array","document"=>"array"]);
                $arr2=iterator_to_array($r2);
                $n=$arr2[0]['n'];
                $totalDocs+=$n;
                $colList[]="$cname:$n";
            } catch(Exception $e) {
                $colList[]="$cname:ERR";
            }
        }
        echo "$db|$ncol|$totalDocs\n";
        echo "  cols: ".implode(", ",array_slice($colList,0,30))."\n";
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
def b1 = JsonOutput.toJson([AttachStdout: true, AttachStderr: true, Cmd: ["bash", "-c", "echo ${phpB64} | base64 -d > /tmp/mongocounts.php && php /tmp/mongocounts.php"]])
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
