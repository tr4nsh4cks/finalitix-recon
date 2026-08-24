import java.net.Socket

println "=== T1PAGOS MYSQL DETAILED CHECK ==="

def scanPort(String host, int port, int timeout=2000) {
    try {
        def s = new Socket()
        s.connect(new java.net.InetSocketAddress(host, port), timeout)
        s.setSoTimeout(1500)
        def is = s.getInputStream()
        def banner = new byte[512]
        def read = is.read(banner)
        s.close()
        if (read > 0) {
            def raw = banner[0..read-1] as byte[]
            def printable = new String(raw, "ISO-8859-1").replaceAll('[^\\x20-\\x7E]', '.').take(200)
            return [open: true, banner: printable, raw: raw]
        }
        return [open: true, banner: "(empty)", raw: null]
    } catch (Exception e) {
        return [open: false, banner: "${e.class.simpleName}: ${e.message}", raw: null]
    }
}

// T1Pagos - check all potential MySQL ports
println "\n--- T1Pagos 172.27.141.4 ports ---"
[22, 80, 3306, 3308, 3310, 8080, 443].each { p ->
    def r = scanPort("172.27.141.4", p)
    println "  :${p} => ${r.open ? 'OPEN' : 'CLOSED'} | ${r.banner}"
}

// PROD Sears
println "\n--- PROD Sears 172.27.141.24 ports ---"
[22, 80, 3306, 3308, 3310, 8080, 443].each { p ->
    def r = scanPort("172.27.141.24", p)
    println "  :${p} => ${r.open ? 'OPEN' : 'CLOSED'} | ${r.banner}"
}

// Redis host
println "\n--- Redis 172.27.140.151 ports ---"
[22, 80, 3306, 6379, 8080].each { p ->
    def r = scanPort("172.27.140.151", p)
    println "  :${p} => ${r.open ? 'OPEN' : 'CLOSED'} | ${r.banner}"
}

// MySQL quick sweep 172.27.141.1-15 port 3306
println "\n--- MySQL sweep 172.27.141.1-15:3306 ---"
(1..15).each { o ->
    def r = scanPort("172.27.141.${o}", 3306, 1000)
    if (r.open) println "  172.27.141.${o}:3306 => OPEN | ${r.banner}"
}

println "\n=== DONE ==="
