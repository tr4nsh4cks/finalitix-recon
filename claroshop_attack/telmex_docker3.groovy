import groovy.json.JsonSlurper
import groovy.json.JsonOutput

def dockerHost = "172.27.140.148"
def dockerPort = 4243
def cid = "5b32e909c295"

def dockerExec(String containerId, List cmd) {
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

// Step 1: Check available tools
println "=== TOOLS ==="
println dockerExec(cid, ["bash", "-c", "which php && which python && which python2 && hostname && cat /etc/redhat-release 2>/dev/null || true"])

// Step 2: Write PHP query script
def phpCode = '<?php $c=new mysqli("172.27.141.6","apifincadodev","1q2w3e4r5t6y","tienda",3308);if($c->connect_error){die("FAIL:".$c->connect_error);}echo "OK\\n";$r=$c->query("SELECT id_cc_credcliente,id_cliente,telefono,credito_disponible,limite_credito,saldo_credito,numero_cuenta,estatus FROM credito_clarotel_credcliente WHERE telefono LIKE \\"%5558455777%\\"");echo "=== credcliente ===\\n";if($r&&$r->num_rows>0){while($row=$r->fetch_assoc()){echo implode("|",$row)."\\n";}}else{echo "NO_ROWS err:".$c->error."\\n";}$r2=$c->query("SELECT id_cc_linea,id_cliente,telefono,monto_total,limite_cred_tel,saldo_cred_tel,estado_linea FROM credito_clarotel_lineac WHERE telefono LIKE \\"%5558455777%\\"");echo "=== lineac ===\\n";if($r2&&$r2->num_rows>0){while($row=$r2->fetch_assoc()){echo implode("|",$row)."\\n";}}else{echo "NO_ROWS err:".$c->error."\\n";}$c->close();?>'

println "\n=== WRITE ==="
println dockerExec(cid, ["bash", "-c", "echo '${phpCode}' > /tmp/tq.php && echo DONE"])

println "\n=== EXECUTE ==="
println dockerExec(cid, ["php", "/tmp/tq.php"])
