// Probe PROD Sears + Nexus from Jenkins master JVM
def probe = { String host, int port ->
    try {
        def s = new Socket()
        s.connect(new InetSocketAddress(host, port), 5000)
        s.close()
        return "OPEN ${host}:${port}"
    } catch (Exception e) {
        return "closed ${host}:${port} (${e.getMessage()})"
    }
}
// PROD Sears
println probe("172.27.141.24", 3308)
println probe("172.27.141.24", 3306)
println probe("dbasears.mrc-services.io", 3308)
// Nexus
println probe("172.27.141.25", 443)
println probe("172.27.141.25", 8081)
println probe("172.27.141.25", 8082)
println probe("172.27.141.25", 5000)
// T1Pagos
println probe("172.27.141.4", 3310)
// Mongo internal
println probe("172.26.84.132", 27021)
