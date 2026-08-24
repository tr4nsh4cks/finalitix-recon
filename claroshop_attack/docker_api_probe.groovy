// Test reachability of Docker API host and Nexus from Jenkins
def probe = { String u ->
    try {
        def c = new URL(u).openConnection()
        c.setConnectTimeout(6000)
        c.setReadTimeout(6000)
        def code = c.getResponseCode()
        def body = ""
        try { body = c.getInputStream().getText("UTF-8") } catch (e) { body = c.getErrorStream()?.getText("UTF-8") ?: "" }
        return "URL=${u} CODE=${code} BODY=${body.take(400)}"
    } catch (Exception e) {
        return "URL=${u} ERROR=${e.getMessage()}"
    }
}

println probe("http://172.27.140.148:4243/version")
println probe("http://172.27.140.148:4243/images/json?all=1")

// Also check local network interfaces of Jenkins host
try {
    NetworkInterface.getNetworkInterfaces().each { ni ->
        if (ni.isUp() && !ni.isLoopback()) {
            ni.getInetAddresses().each { addr ->
                println "IFACE ${ni.getName()} => ${addr.getHostAddress()}"
            }
        }
    }
} catch (e) { println "IFACE ERR: ${e.message}" }
