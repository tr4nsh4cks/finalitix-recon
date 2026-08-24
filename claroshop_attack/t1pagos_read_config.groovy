// Leer config PHP de t1pagos-api + cat directo de archivos de configuracion
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

println "=== LECTURA CONFIG t1pagos-api ==="

println "\n--- t1pagos config/ directory ---"
println sshExec("ls -la /var/www/sites/t1pagos-api.dev.claroshop-services.io/config/")

println "\n--- t1pagos src/ directory ---"
println sshExec("ls -la /var/www/sites/t1pagos-api.dev.claroshop-services.io/src/")

println "\n--- t1pagos config/autoload/ ---"
println sshExec("ls -la /var/www/sites/t1pagos-api.dev.claroshop-services.io/config/autoload/ 2>&1")

println "\n--- cat ALL config files from t1pagos ---"
println sshExec("cat /var/www/sites/t1pagos-api.dev.claroshop-services.io/config/autoload/global.php 2>&1")
println sshExec("cat /var/www/sites/t1pagos-api.dev.claroshop-services.io/config/autoload/local.php 2>&1")
println sshExec("cat /var/www/sites/t1pagos-api.dev.claroshop-services.io/config/autoload/database.php 2>&1")
println sshExec("cat /var/www/sites/t1pagos-api.dev.claroshop-services.io/config/autoload/database.local.php 2>&1")

println "\n--- result.txt (root dir of /home/jenkins) ---"
println sshExec("cat /home/jenkins/result.txt 2>&1")

// apicredito config
println "\n=== LECTURA CONFIG apicredito.dev.sears.com.mx ==="
println sshExec("ls -la /var/www/sites/apicredito.dev.sears.com.mx/config/")
println sshExec("ls -la /var/www/sites/apicredito.dev.sears.com.mx/config/autoload/ 2>&1")
println sshExec("cat /var/www/sites/apicredito.dev.sears.com.mx/config/autoload/global.php 2>&1")
println sshExec("cat /var/www/sites/apicredito.dev.sears.com.mx/config/autoload/local.php 2>&1")
println sshExec("cat /var/www/sites/apicredito.dev.sears.com.mx/config/autoload/database.php 2>&1")
println sshExec("cat /var/www/sites/apicredito.dev.sears.com.mx/config/autoload/database.local.php 2>&1")

// pse-admin (Sears)
println "\n=== LECTURA CONFIG pse-admin-api.dev.mrc-services.io ==="
println sshExec("ls -la /var/www/sites/pse-admin-api.dev.mrc-services.io/config/ 2>&1")
println sshExec("cat /var/www/sites/pse-admin-api.dev.mrc-services.io/config/autoload/local.php 2>&1")

// credito-api  
println "\n=== LECTURA CONFIG credito-api.dev.mrc-services.io ==="
println sshExec("ls -la /var/www/sites/credito-api.dev.mrc-services.io/config/ 2>&1")
println sshExec("ls -la /var/www/sites/credito-api.dev.mrc-services.io/config/autoload/ 2>&1")
println sshExec("cat /var/www/sites/credito-api.dev.mrc-services.io/config/autoload/local.php 2>&1")
println sshExec("cat /var/www/sites/credito-api.dev.mrc-services.io/config/autoload/global.php 2>&1")

// t1pagos mrc-services
println "\n=== LECTURA CONFIG t1pagos-api.dev.mrc-services.io ==="
println sshExec("ls -la /var/www/sites/t1pagos-api.dev.mrc-services.io/config/autoload/ 2>&1")
println sshExec("cat /var/www/sites/t1pagos-api.dev.mrc-services.io/config/autoload/local.php 2>&1")

// axii.dev.claroshop (recently modified - Aug 2026)
println "\n=== LECTURA CONFIG axii.dev.claroshop.com (reciente) ==="
println sshExec("ls -la /var/www/sites/axii.dev.claroshop.com/config/ 2>&1")
println sshExec("ls -la /var/www/sites/axii.dev.claroshop.com/config/autoload/ 2>&1")
println sshExec("cat /var/www/sites/axii.dev.claroshop.com/config/autoload/local.php 2>&1")

// default (recently modified)
println "\n=== /var/www/sites/default ==="
println sshExec("ls -la /var/www/sites/default/ 2>&1")

// ats.dev.claroshop.com (recently modified Aug 22)
println "\n=== ats.dev.claroshop.com config ==="
println sshExec("ls -la /var/www/sites/ats.dev.claroshop.com/config/autoload/ 2>&1")
println sshExec("cat /var/www/sites/ats.dev.claroshop.com/config/autoload/local.php 2>&1")

println "\n=== FIN ==="
