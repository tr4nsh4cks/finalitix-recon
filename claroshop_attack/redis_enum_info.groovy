def redisCmd(host, port, password, commands) {
    def script = "#!/bin/bash\n"
    script += "exec 3<>/dev/tcp/${host}/${port} 2>/dev/null\n"
    script += "if [ \$? -ne 0 ]; then echo 'CONN_FAIL'; exit 1; fi\n"
    script += "echo -e 'AUTH ${password}\\r' >&3\n"
    script += "read -t 2 auth_resp <&3\n"
    script += "echo \"AUTH_RESP: \$auth_resp\"\n"
    commands.each { cmd ->
        script += "echo -e '${cmd}\\r' >&3\n"
        script += "sleep 0.3\n"
    }
    script += "sleep 1\n"
    script += "cat <&3 &\n"
    script += "CAT_PID=\$!\n"
    script += "sleep 2\n"
    script += "kill \$CAT_PID 2>/dev/null\n"
    script += "exec 3>&-\n"
    
    def proc = ['bash', '-c', script].execute()
    proc.waitForOrKill(15000)
    return proc.text + (proc.err?.text ?: '')
}

def redisCliCmd(host, port, password, cmd) {
    def fullCmd = "redis-cli -h ${host} -p ${port} -a '${password}' --no-auth-warning ${cmd} 2>&1"
    def proc = ['bash', '-c', fullCmd].execute()
    proc.waitForOrKill(10000)
    return proc.text.trim()
}

def checkTool = "which redis-cli 2>&1".execute()
checkTool.waitForOrKill(5000)
def hasRedisCli = checkTool.exitValue() == 0
println "=== REDIS-CLI AVAILABLE: ${hasRedisCli} ==="
if (hasRedisCli) println "PATH: ${checkTool.text.trim()}"

def targets = [
    [name: "DEV-DIRECT",  host: "172.27.140.151", port: "6379", pass: "@st0rAg3K3Y"],
    [name: "PROD-DNS",    host: "redis-storage-ng.claroshop-services.io", port: "6379", pass: "nBZxDxL2XxYwAEYyttme"],
    [name: "DEV-DNS",     host: "redis-storage-ng.dev.claroshop-services.io", port: "6379", pass: "@st0rAg3K3Y"],
]

targets.each { t ->
    println "\n${'='*60}"
    println "TARGET: ${t.name} (${t.host}:${t.port})"
    println "${'='*60}"
    
    if (hasRedisCli) {
        println "\n--- INFO SERVER ---"
        println redisCliCmd(t.host, t.port, t.pass, "INFO server")
        
        println "\n--- INFO KEYSPACE ---"
        println redisCliCmd(t.host, t.port, t.pass, "INFO keyspace")
        
        println "\n--- INFO CLIENTS ---"
        println redisCliCmd(t.host, t.port, t.pass, "INFO clients")
        
        println "\n--- INFO MEMORY ---"
        println redisCliCmd(t.host, t.port, t.pass, "INFO memory")
        
        println "\n--- INFO REPLICATION ---"
        println redisCliCmd(t.host, t.port, t.pass, "INFO replication")
        
        println "\n--- DBSIZE ---"
        println redisCliCmd(t.host, t.port, t.pass, "DBSIZE")
    } else {
        println redisCmd(t.host, t.port, t.pass, ["INFO server", "INFO keyspace", "INFO clients", "INFO memory", "INFO replication", "DBSIZE"])
    }
}

println "\n=== DONE ==="
