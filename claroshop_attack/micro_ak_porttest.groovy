// MICRO-AK: Fast connectivity tests only (no hanging DB connects)
def run = { cmd ->
    def p = ["bash", "-c", cmd].execute()
    def out = new StringBuffer()
    def err = new StringBuffer()
    p.consumeProcessOutput(out, err)
    p.waitForOrKill(8000)
    out.toString().take(2000)
}

println "=== /dev/tcp REACHABILITY ==="
[
    "appdb.claroshop-services.net/3306",
    "dbps.claroshop-services.net/3310",
    "172.27.141.4/3310",
    "172.27.141.24/3308",
    "172.27.141.25/8081",
    "172.27.141.25/3306",
    "nexus.dev.claroshop.com/8081",
    "nexus.dev.claroshop.com/80",
].each { hostport ->
    def (host, port) = hostport.split('/')
    def r = run("timeout 2 bash -c 'cat < /dev/null > /dev/tcp/${host}/${port}' 2>&1 && echo OPEN || echo CLOSED")
    println "  ${hostport}: ${r.trim().take(20)}"
}

println "=== DONE MICRO-AK ==="
