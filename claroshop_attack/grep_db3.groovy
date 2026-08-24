def run = { List c ->
  try {
    def p = c.execute()
    def out = p.inputStream.text
    def err = p.errorStream.text
    p.waitFor()
    return (out + err).trim()
  } catch (Exception e) { return "ERR: " + e.message }
}

println("=== config.xml DB lines ===")
println(run(['sh','-c','timeout 10 grep -i -E "mysql|jdbc|172\\.27\\.|dbasears|t1pagos|database" /var/jenkins_home/config.xml 2>/dev/null | head -30; echo END']))
println("=== jobs depth2 ===")
println(run(['sh','-c','timeout 20 grep -l -i -E "jdbc:mysql|dbasears|172\\.27\\.141" /var/jenkins_home/jobs/*/jobs/*/config.xml 2>/dev/null | head -10; echo END']))
println("=== workflow-libs / shared libs ===")
println(run(['sh','-c','ls /var/jenkins_home/ | head -40; echo END']))
println("DONE")
