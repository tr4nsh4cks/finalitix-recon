// MICRO-T: Read full Jenkinsfile of caja-api + find USERVAR injection mechanism
def run = { cmd ->
    def p = ["bash", "-c", cmd].execute()
    def out = new StringBuffer(); def err = new StringBuffer()
    p.consumeProcessOutput(out, err)
    p.waitForOrKill(15000)
    out.toString().take(6000)
}

// Extract full Jenkinsfile script from config.xml via python3
println "=== FULL CAJA-API JENKINSFILE ==="
println run('''python3 -c "
import sys
txt = open('/var/jenkins_home/jobs/cs_legacy_front/jobs/cs_legacy_pipe_build_caja-api/config.xml').read()
import html
# Decode HTML entities
txt = html.unescape(txt)
# Find script section
start = txt.find('<script>')
end = txt.rfind('</script>')
if start != -1 and end != -1:
    print(txt[start+8:end])
else:
    print('NO SCRIPT FOUND')
    print(txt[-2000:])
" 2>&1''')

println "\n=== DONE MICRO-T ==="
