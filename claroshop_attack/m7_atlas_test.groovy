def probe = { host, port ->
    try {
        def s = new Socket()
        s.connect(new InetSocketAddress(host, port), 6000)
        s.close()
        return "OK"
    } catch (Exception e) {
        return e.getMessage()
    }
}
println "=== Atlas shards desde JENKINS MASTER ==="
["t1envios-shard-00-00.kqoop.mongodb.net","t1envios-shard-00-01.kqoop.mongodb.net","t1envios-shard-00-02.kqoop.mongodb.net","t1envios-shard-00-03.kqoop.mongodb.net"].each { h ->
    def ip = "?"
    try { ip = InetAddress.getByName(h).getHostAddress() } catch (Exception e) { ip = "DNS_FAIL: " + e.getMessage() }
    println "${h} -> ${ip} :27017 -> " + probe(h, 27017)
}
println "=== Puertos extra en hosts internos clave (desde Jenkins) ==="
[["172.27.141.24",[27017,27018,3306,3308,22,443,8080,8443]],
 ["172.27.141.4",[3310,3306,22,443,27017]],
 ["172.26.84.132",[27017,27020,27021,22,443]]
].each { h, ports ->
    ports.each { p ->
        def r = probe(h, p)
        if (r == "OK" || !r.contains("timed out")) println "${h}:${p} -> ${r}"
    }
}
println "DONE"
