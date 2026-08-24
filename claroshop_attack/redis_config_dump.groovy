def redisCliCmd(host, port, password, cmd) {
    def fullCmd = "redis-cli -h ${host} -p ${port} -a '${password}' --no-auth-warning ${cmd} 2>&1"
    def proc = ['bash', '-c', fullCmd].execute()
    proc.waitForOrKill(15000)
    return proc.text.trim()
}

def redisPipe(host, port, password, cmds) {
    def script = "#!/bin/bash\n"
    cmds.each { c ->
        script += "redis-cli -h ${host} -p ${port} -a '${password}' --no-auth-warning ${c} 2>/dev/null\n"
        script += "echo '---SEPARATOR---'\n"
    }
    def proc = ['bash', '-c', script].execute()
    proc.waitForOrKill(30000)
    return proc.text.trim()
}

def targets = [
    [name: "DEV-DIRECT",  host: "172.27.140.151", port: "6379", pass: "@st0rAg3K3Y"],
    [name: "PROD-DNS",    host: "redis-storage-ng.claroshop-services.io", port: "6379", pass: "nBZxDxL2XxYwAEYyttme"],
    [name: "DEV-DNS",     host: "redis-storage-ng.dev.claroshop-services.io", port: "6379", pass: "@st0rAg3K3Y"],
]

targets.each { t ->
    println "\n${'='*60}"
    println "CONFIG DUMP: ${t.name} (${t.host}:${t.port})"
    println "${'='*60}"
    
    println "\n--- CONFIG GET dir ---"
    println redisCliCmd(t.host, t.port, t.pass, "CONFIG GET dir")
    
    println "\n--- CONFIG GET dbfilename ---"
    println redisCliCmd(t.host, t.port, t.pass, "CONFIG GET dbfilename")
    
    println "\n--- CONFIG GET requirepass ---"
    println redisCliCmd(t.host, t.port, t.pass, "CONFIG GET requirepass")
    
    println "\n--- CONFIG GET bind ---"
    println redisCliCmd(t.host, t.port, t.pass, "CONFIG GET bind")
    
    println "\n--- CONFIG GET protected-mode ---"
    println redisCliCmd(t.host, t.port, t.pass, "CONFIG GET protected-mode")
    
    println "\n--- CONFIG GET loadmodule ---"
    println redisCliCmd(t.host, t.port, t.pass, "CONFIG GET loadmodule")
    
    println "\n--- CONFIG GET slaveof ---"
    println redisCliCmd(t.host, t.port, t.pass, "CONFIG GET slaveof")
    
    println "\n--- CONFIG GET rename-command ---"
    println redisCliCmd(t.host, t.port, t.pass, "CONFIG GET rename-command")
    
    println "\n--- CONFIG GET save ---"
    println redisCliCmd(t.host, t.port, t.pass, "CONFIG GET save")
    
    println "\n--- CONFIG GET logfile ---"
    println redisCliCmd(t.host, t.port, t.pass, "CONFIG GET logfile")
    
    println "\n--- CONFIG GET maxmemory ---"
    println redisCliCmd(t.host, t.port, t.pass, "CONFIG GET maxmemory")
    
    println "\n--- CONFIG GET maxmemory-policy ---"
    println redisCliCmd(t.host, t.port, t.pass, "CONFIG GET maxmemory-policy")
    
    println "\n--- MODULE LIST ---"
    println redisCliCmd(t.host, t.port, t.pass, "MODULE LIST")
    
    println "\n--- ACL LIST ---"
    println redisCliCmd(t.host, t.port, t.pass, "ACL LIST")
    
    println "\n--- CLIENT LIST (first 10) ---"
    def clients = redisCliCmd(t.host, t.port, t.pass, "CLIENT LIST")
    def lines = clients.split('\n')
    lines.take(10).each { println it }
    println "(total clients: ${lines.size()})"
}

println "\n=== CONFIG DUMP DONE ==="
