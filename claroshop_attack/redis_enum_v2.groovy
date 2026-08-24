import java.net.Socket
import java.io.BufferedReader
import java.io.InputStreamReader
import java.io.OutputStream

def redisExec(String host, int port, String password, List<String> commands) {
    def results = [:]
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
        def authResp = readResp(br)
        results['AUTH'] = authResp
        
        if (!authResp.contains('+OK')) {
            results['ERROR'] = 'AUTH FAILED'
            return results
        }
        
        commands.each { cmd ->
            os.write("${cmd}\r\n".getBytes())
            os.flush()
            Thread.sleep(200)
            results[cmd] = readResp(br)
        }
    } catch (Exception e) {
        results['CONN_ERROR'] = "${e.class.simpleName}: ${e.message}"
    } finally {
        try { sock?.close() } catch(Exception e) {}
    }
    return results
}

def readResp(BufferedReader br) {
    def sb = new StringBuilder()
    try {
        while (br.ready()) {
            def line = br.readLine()
            if (line == null) break
            sb.append(line).append('\n')
        }
        if (sb.length() == 0) {
            Thread.sleep(500)
            while (br.ready()) {
                def line = br.readLine()
                if (line == null) break
                sb.append(line).append('\n')
            }
        }
    } catch (java.net.SocketTimeoutException e) {
        // expected
    }
    return sb.toString().trim()
}

def targets = [
    [name: "DEV-DIRECT",  host: "172.27.140.151", port: 6379, pass: "@st0rAg3K3Y"],
    [name: "PROD-DNS",    host: "redis-storage-ng.claroshop-services.io", port: 6379, pass: "nBZxDxL2XxYwAEYyttme"],
    [name: "DEV-DNS",     host: "redis-storage-ng.dev.claroshop-services.io", port: 6379, pass: "@st0rAg3K3Y"],
]

def infoCommands = ["INFO server", "INFO keyspace", "INFO clients", "INFO memory", "INFO replication", "DBSIZE"]

targets.each { t ->
    println "\n${'='*70}"
    println "TARGET: ${t.name} (${t.host}:${t.port})"
    println "${'='*70}"
    
    def results = redisExec(t.host, t.port, t.pass, infoCommands)
    results.each { k, v ->
        println "\n--- ${k} ---"
        println v
    }
}

println "\n=== ENUM DONE ==="
