import groovy.json.JsonSlurper, groovy.json.JsonOutput

def dockerHost = "172.27.140.148"
def dockerPort = 4243
def cid = "5b32e909c295"  // pivot02 - php container

def dockerExec(String containerId, List cmd) {
    // Create exec
    def url = new URL("http://${dockerHost}:${dockerPort}/containers/${containerId}/exec")
    def conn = url.openConnection()
    conn.setRequestMethod("POST")
    conn.setDoOutput(true)
    conn.setRequestProperty("Content-Type", "application/json")
    conn.setConnectTimeout(5000)
    conn.setReadTimeout(20000)
    def body = JsonOutput.toJson([AttachStdout: true, AttachStderr: true, Cmd: cmd])
    conn.outputStream.write(body.bytes)
    conn.outputStream.flush()
    def execResp = conn.inputStream.text
    def execData = new JsonSlurper().parseText(execResp)
    def execId = execData.Id

    // Start exec
    def startUrl = new URL("http://${dockerHost}:${dockerPort}/exec/${execId}/start")
    def startConn = startUrl.openConnection()
    startConn.setRequestMethod("POST")
    startConn.setDoOutput(true)
    startConn.setRequestProperty("Content-Type", "application/json")
    startConn.setConnectTimeout(5000)
    startConn.setReadTimeout(20000)
    startConn.outputStream.write('{"Detach":false,"Tty":true}'.bytes)
    startConn.outputStream.flush()
    return startConn.inputStream.text
}

// Test: check what's available
println "=== TEST CONNECTIVITY ==="
println dockerExec(cid, ["bash", "-c", "hostname && which python && which python2 && which php && ip addr show eth0 | grep inet"])

// Write a small PHP script to query MySQL
def phpScript = '''<?php
\$h="172.27.141.6";
\$u="apifincadodev";
\$p="1q2w3e4r5t6y";
\$d="tienda";
\$port=3308;
\$phone="5558455777";
\$c=new mysqli(\$h,\$u,\$p,\$d,\$port);
if(\$c->connect_error){echo "CONN_FAIL:".\$c->connect_error;exit(1);}
echo "CONNECTED\\n";
\$r=\$c->query("SELECT id_cc_credcliente,id_cliente,telefono,credito_disponible,limite_credito,saldo_credito,numero_cuenta,estatus FROM credito_clarotel_credcliente WHERE telefono LIKE '%\$phone%'");
echo "=== credcliente ===\\n";
if(\$r && \$r->num_rows>0){while(\$row=\$r->fetch_assoc()){echo implode("|",\$row)."\\n";}}else{echo "NO_ROWS\\n";}
\$r2=\$c->query("SELECT id_cc_linea,id_cliente,telefono,monto_total,limite_cred_tel,saldo_cred_tel,estado_linea FROM credito_clarotel_lineac WHERE telefono LIKE '%\$phone%'");
echo "=== lineac ===\\n";
if(\$r2 && \$r2->num_rows>0){while(\$row=\$r2->fetch_assoc()){echo implode("|",\$row)."\\n";}}else{echo "NO_ROWS\\n";}
\$c->close();
?>'''

println "\n=== WRITING PHP SCRIPT ==="
println dockerExec(cid, ["bash", "-c", "cat > /tmp/tquery.php << 'PHPEOF'\n${phpScript}\nPHPEOF\necho WRITTEN"])

println "\n=== EXECUTING QUERY ==="
println dockerExec(cid, ["php", "/tmp/tquery.php"])
