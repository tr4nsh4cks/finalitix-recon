def probe = { host, port ->
    try {
        def s = new Socket()
        s.connect(new InetSocketAddress(host, port), 5000)
        s.close()
        return "OK"
    } catch (Exception e) {
        return e.getMessage()
    }
}
println "=== TCP desde JENKINS MASTER ==="
println "jenkins hostname: " + java.net.InetAddress.getLocalHost().getHostName()
try {
    def pb = "hostname; ip addr 2>/dev/null | grep 'inet ' | head -5".execute()
    pb.waitFor(); println pb.text
} catch(e) { println "shell err: " + e.getMessage() }

[["PUBLIC_MONGO","3.231.83.29",27017],
 ["INTERNAL_MONGO","172.26.84.132",27021],
 ["ATLAS_SRV_HOST","t1envios.kqoop.mongodb.net",27017],
 ["PROD_SEARS_DNS","dbasears.mrc-services.io",3308],
 ["PROD_SEARS_IP","172.27.141.24",3308],
 ["T1PAGOS","172.27.141.4",3310],
 ["DOCKER_HOST","172.27.140.148",4243]
].each { n,h,p ->
    println String.format("%-20s %s:%d -> %s", n, h, p, probe(h,p))
}

// DNS resolution checks
["t1envios.kqoop.mongodb.net","dbasears.mrc-services.io","172.26.84.132"].each { h ->
    try {
        def addr = InetAddress.getByName(h)
        println "DNS ${h} -> ${addr.getHostAddress()}"
    } catch (Exception e) {
        println "DNS ${h} -> FAIL: " + e.getMessage()
    }
}
