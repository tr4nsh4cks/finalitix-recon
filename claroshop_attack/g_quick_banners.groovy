// Lectura rápida de banners locales y /proc/net
println "=== LOCAL PORT BANNERS 13306/13307/13308 ==="
[13306, 13307, 13308, 23456].each { port ->
    try {
        def socket = new Socket("127.0.0.1", port)
        socket.soTimeout = 2000
        def stream = socket.inputStream
        def banner = new byte[200]
        def len = stream.read(banner, 0, 200)
        socket.close()
        if (len > 0) {
            def bannerStr = new String(banner, 0, len).replaceAll('[^\\x20-\\x7E]', '.')
            println "PORT ${port} (${len}b): ${bannerStr.take(200)}"
            // MySQL version
            if (len > 10) {
                def versionEnd = -1
                for (int i = 5; i < Math.min(40, len); i++) {
                    if (banner[i] == 0) { versionEnd = i; break }
                }
                if (versionEnd > 5) println "  MySQL: ${new String(banner, 5, versionEnd-5)}"
            }
        }
    } catch(e) { println "PORT ${port}: ${e.message}" }
}

println "\n=== /proc/net/tcp entries (local listening) ==="
try {
    def content = new File("/proc/net/tcp").text
    content.split("\n").drop(1).each { line ->
        def parts = line.trim().split("\\s+")
        if (parts.length >= 4 && parts[3] == "0A") { // LISTEN state = 0A
            def localAddr = parts[1]
            def addrParts = localAddr.split(":")
            if (addrParts.length == 2) {
                def ip = Integer.parseInt(addrParts[0].substring(6, 8), 16).toString() + "." +
                         Integer.parseInt(addrParts[0].substring(4, 6), 16).toString() + "." +
                         Integer.parseInt(addrParts[0].substring(2, 4), 16).toString() + "." +
                         Integer.parseInt(addrParts[0].substring(0, 2), 16).toString()
                def portN = Integer.parseInt(addrParts[1], 16)
                println "  LISTEN: ${ip}:${portN} (hex:${addrParts[1]})"
            }
        }
    }
} catch(e) { println "proc/net/tcp: ${e.message}" }

println "\n=== ESTABLISHED CONNECTIONS ==="
try {
    def content = new File("/proc/net/tcp").text
    content.split("\n").drop(1).each { line ->
        def parts = line.trim().split("\\s+")
        if (parts.length >= 4 && parts[3] == "01") { // ESTABLISHED
            def localParts = parts[1].split(":")
            def remoteParts = parts[2].split(":")
            if (localParts.length == 2 && remoteParts.length == 2) {
                def remoteIp = Integer.parseInt(remoteParts[0].substring(6, 8), 16).toString() + "." +
                               Integer.parseInt(remoteParts[0].substring(4, 6), 16).toString() + "." +
                               Integer.parseInt(remoteParts[0].substring(2, 4), 16).toString() + "." +
                               Integer.parseInt(remoteParts[0].substring(0, 2), 16).toString()
                def remotePort = Integer.parseInt(remoteParts[1], 16)
                def localPort = Integer.parseInt(localParts[1], 16)
                // Only show interesting connections
                if (remoteIp.startsWith("172.27") || remotePort == 3306 || remotePort == 3308 || 
                    remotePort == 22 || remotePort == 3310 || localPort > 13000) {
                    println "  ESTAB: local:${localPort} -> ${remoteIp}:${remotePort}"
                }
            }
        }
    }
} catch(e) { println "connections: ${e.message}" }

println "\n=== WORKSPACE LISTING ==="
def wsDir = new File("/var/jenkins_home/workspace")
if (wsDir.exists()) {
    wsDir.listFiles()?.sort()?.each { f ->
        println "  WS: ${f.name}"
    }
}

println "\n=== BUILD ENV VARS FROM LAST BUILDS ==="
// Check last build envVars 
try {
    jenkins.model.Jenkins.getInstance().getAllItems().findAll { it.class.simpleName in ["WorkflowJob", "FreeStyleProject"] }.take(5).each { job ->
        def lastBuild = job.lastBuild
        if (lastBuild) {
            println "JOB: ${job.fullName} - Build #${lastBuild.number}"
            def envVarsAction = lastBuild.getAction(org.jenkinsci.plugins.workflow.cps.EnvActionImpl)
            if (envVarsAction) {
                envVarsAction.getEnvironment()?.each { k, v ->
                    if (k.toLowerCase().contains("db") || k.toLowerCase().contains("mysql") || 
                        k.toLowerCase().contains("pass") || k.toLowerCase().contains("host")) {
                        println "  ENV: ${k}=${v}"
                    }
                }
            }
        }
    }
} catch(e) { println "env vars: ${e.message}" }
