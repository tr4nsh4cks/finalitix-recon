import groovy.json.JsonSlurper
import groovy.json.JsonOutput

def dHost = "172.27.140.148"
def dPort = 4243
def cid = "5b32e909c295"

def shCmd = 'if [ -f /tmp/m6_done ]; then echo STATUS=DONE; else echo STATUS=RUNNING; fi; wc -l /tmp/m6_out.txt 2>/dev/null; tail -5 /tmp/m6_out.txt 2>/dev/null'
def b64 = java.util.Base64.encoder.encodeToString(shCmd.getBytes("UTF-8"))
def url = new URL("http://${dHost}:${dPort}/containers/${cid}/exec")
def conn = url.openConnection()
conn.setRequestMethod("POST"); conn.setDoOutput(true)
conn.setRequestProperty("Content-Type", "application/json")
def body = JsonOutput.toJson([AttachStdout:true, AttachStderr:true, Cmd:["bash","-c",'echo ' + b64 + ' | base64 -d | bash']])
conn.outputStream.write(body.bytes); conn.outputStream.flush()
def r = new JsonSlurper().parseText(conn.inputStream.text)
def eid = r.Id
def su = new URL("http://${dHost}:${dPort}/exec/${eid}/start").openConnection()
su.setRequestMethod("POST"); su.setDoOutput(true)
su.setRequestProperty("Content-Type", "application/json")
su.outputStream.write('{"Detach":false,"Tty":true}'.bytes); su.outputStream.flush()
println su.inputStream.text
