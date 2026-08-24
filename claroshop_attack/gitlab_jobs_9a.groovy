// PHASE 9a: Fast - List jobs + git URLs + find USERVAR values
// No git clones here - just read configs

def jobsDir = new File("/var/jenkins_home/jobs")

// ===== List all jobs with GitLab URLs =====
println "=== JENKINS JOBS WITH GITLAB REPOS ==="
def allJobs = []
jobsDir.eachFileRecurse { f ->
    if (f.name != "config.xml") return
    def text = f.text
    def urls = [] as Set
    (text =~ /<url>(https?:\/\/[^<]*gitlab[^<]+)<\/url>/).each { m -> urls << m[1].trim() }
    if (urls) {
        def jobPath = f.absolutePath.replace('/var/jenkins_home/jobs/', '')
        allJobs << [path: jobPath, urls: urls]
    }
}
println "Total jobs: ${allJobs.size()}"
allJobs.sort { it.path }.each { j ->
    println "  ${j.path.take(80)}"
    j.urls.each { u -> println "    URL: ${u}" }
}

// ===== Find ALL USERVAR_* with actual values =====
println "\n=== USERVAR_* WITH VALUES ==="
jobsDir.eachFileRecurse { f ->
    if (f.name != "config.xml") return
    def text = f.text
    // Look for <string>USERVAR_X=value</string> or in parameter defaults
    def found = false
    (text =~ /<string>(USERVAR_[A-Z_]+=([^<]+))<\/string>/).each { m ->
        if (!found) { println "\n  JOB: ${f.absolutePath.replace('/var/jenkins_home/jobs/','')}"; found = true }
        println "  ${m[1].take(200)}"
    }
    // Also look for USERVAR in parameter descriptions
    if (text.contains("USERVAR_DB_PASSWORD") || text.contains("USERVAR_DB_HOST")) {
        println "\n  [HAS DB VARS] ${f.absolutePath.replace('/var/jenkins_home/jobs/','')})"
        }
}

// ===== Find jobs with PROD Sears references =====
println "\n=== JOBS WITH PROD SEARS DB REFS ==="
def prodKws = ["dbasears.mrc-services", "172.27.141.4", "172.27.141.6", "payment_t1", "apifincadob"]
jobsDir.eachFileRecurse { f ->
    if (f.name != "config.xml") return
    def text = f.text
    def found = prodKws.findAll { text.contains(it) }
    if (!found) return
    println "\n  JOB: ${f.absolutePath.replace('/var/jenkins_home/jobs/','')}"
    println "  KEYWORDS: ${found}"
    // Print env vars that contain these keywords
    (text =~ /<string>([^<]{10,300})<\/string>/).each { m ->
        if (found.any { k -> m[1].contains(k) }) println "  STRING: ${m[1].take(200)}"
    }
}

// ===== Unique GitLab repo paths from ALL jobs =====
println "\n=== ALL GITLAB REPO PATHS ==="
def allPaths = [] as Set
jobsDir.eachFileRecurse { f ->
    if (f.name != "config.xml") return
    def text = f.text
    (text =~ /<url>https?:\/\/[^@]*?gitlab\.dev\.claroshop\.com\/([a-zA-Z0-9_.\/\-]+?)(?:\.git)?<\/url>/).each { m ->
        allPaths << m[1]
    }
    (text =~ /gitlab\.dev\.claroshop\.com\/([a-zA-Z0-9_.\/\-]{5,80}?)(?:\.git|['"<\s])/).each { m ->
        allPaths << m[1]
    }
}
println "Total unique repos: ${allPaths.size()}"
allPaths.sort().each { println "  ${it}" }

println "\n=== DONE 9a ==="
