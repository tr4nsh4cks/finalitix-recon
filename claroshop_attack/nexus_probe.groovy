// Probe Nexus registry from inside the network
def auth = "Basic " + "jenkins-ng.dev.claroshop.com:dtvV50vwfGq5CO9".bytes.encodeBase64().toString()

def tryUrl = { String u ->
    try {
        def c = new URL(u).openConnection()
        c.setConnectTimeout(8000)
        c.setReadTimeout(8000)
        c.setRequestProperty("Authorization", auth)
        c.setInstanceFollowRedirects(false)
        def code = c.getResponseCode()
        def body = ""
        try { body = c.getInputStream().getText("UTF-8") } catch (e) { body = c.getErrorStream()?.getText("UTF-8") ?: "" }
        return "URL=${u} CODE=${code} BODY=${body.take(500)}"
    } catch (Exception e) {
        return "URL=${u} ERROR=${e.getMessage()}"
    }
}

// DNS resolution
try {
    def addr = InetAddress.getAllByName("docker-registry.nexus.dev.claroshop.com")
    addr.each { println "DNS docker-registry => ${it.getHostAddress()}" }
} catch (e) { println "DNS docker-registry FAIL: ${e.message}" }
try {
    def addr2 = InetAddress.getAllByName("nexus.dev.claroshop.com")
    addr2.each { println "DNS nexus => ${it.getHostAddress()}" }
} catch (e) { println "DNS nexus FAIL: ${e.message}" }

// Try registry endpoints
println tryUrl("http://docker-registry.nexus.dev.claroshop.com/v2/_catalog")
println tryUrl("http://docker-registry.nexus.dev.claroshop.com:8082/v2/_catalog")
println tryUrl("http://docker-registry.nexus.dev.claroshop.com:8083/v2/_catalog")
println tryUrl("http://docker-registry.nexus.dev.claroshop.com:5000/v2/_catalog")
println tryUrl("http://nexus.dev.claroshop.com/service/rest/v1/repositories")
println tryUrl("http://nexus.dev.claroshop.com:8081/service/rest/v1/repositories")
