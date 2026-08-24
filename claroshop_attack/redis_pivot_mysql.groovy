import java.net.Socket

println "=== MYSQL + PORT SCAN T1PAGOS + SEARS ==="

def scanPort(String host, int port, int timeout=3000) {
    try {
        def s = new Socket()
        s.connect(new java.net.InetSocketAddress(host, port), timeout)
        s.setSoTimeout(2000)
        def is = s.getInputStream()
        def banner = new byte[256]
        def read = -1
        try { read = is.read(banner) } catch(Exception e) {}
        def bannerStr = read > 0 ? new String(banner, 0, read, "ISO-8859-1").replaceAll('[^\\x20-\\x7E]', '.').take(80) : "(no banner)"
        s.close()
        return "OPEN | ${bannerStr}"
    } catch (java.net.ConnectException e) {
        return "REFUSED"
    } catch (java.net.SocketTimeoutException e) {
        return "TIMEOUT"
    } catch (java.net.NoRouteToHostException e) {
        return "NO_ROUTE"
    } catch (Exception e) {
        return "${e.class.simpleName}"
    }
}

// T1Pagos host
println "\n--- 172.27.141.4 (T1Pagos) ---"
[22, 80, 443, 3306, 3307, 3308, 3309, 3310, 3311, 5432, 6379, 8080, 8443, 9090, 9200, 27017, 33060].each { port ->
    def r = scanPort("172.27.141.4", port, 2000)
    if (r != "TIMEOUT" && r != "NO_ROUTE") println "  :${port} => ${r}"
}

// PROD Sears host
println "\n--- 172.27.141.24 (PROD Sears) ---"
[22, 80, 443, 3306, 3307, 3308, 3309, 3310, 3311, 5432, 6379, 8080, 8443, 9090, 9200, 27017, 33060].each { port ->
    def r = scanPort("172.27.141.24", port, 2000)
    if (r != "TIMEOUT" && r != "NO_ROUTE") println "  :${port} => ${r}"
}

// Redis host
println "\n--- 172.27.140.151 (Redis host) ---"
[22, 80, 443, 3306, 5432, 6379, 8080, 9200, 27017].each { port ->
    def r = scanPort("172.27.140.151", port, 2000)
    if (r != "TIMEOUT" && r != "NO_ROUTE") println "  :${port} => ${r}"
}

// Quick sweep of 172.27.141.x:3306 to find more MySQL
println "\n--- MYSQL DISCOVERY 172.27.141.x:3306 ---"
(1..30).each { octet ->
    def r = scanPort("172.27.141.${octet}", 3306, 1500)
    if (r.startsWith("OPEN")) println "  172.27.141.${octet}:3306 => ${r}"
}

// Quick sweep of 172.27.140.x common ports
println "\n--- HOST DISCOVERY 172.27.140.x (port 22) ---"
(140..160).each { octet ->
    def r = scanPort("172.27.140.${octet}", 22, 1000)
    if (r.startsWith("OPEN")) println "  172.27.140.${octet}:22 => ${r}"
}

println "\n=== PORT SCAN DONE ==="
