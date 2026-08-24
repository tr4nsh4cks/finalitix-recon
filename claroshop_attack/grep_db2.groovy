def run = { List c ->
  try {
    def p = c.execute()
    def out = p.inputStream.text
    def err = p.errorStream.text
    p.waitFor()
    return (out + err).trim()
  } catch (Exception e) { return "ERR: " + e.message }
}

println("=== top-level xml ===")
println(run(['sh','-c','timeout 15 grep -l -i -E "mysql|jdbc|172\\.27\\." /var/jenkins_home/*.xml 2>/dev/null | head; echo END']))
println("=== jobs config.xml (solo nombres de jobs con DB) ===")
println(run(['sh','-c','timeout 20 grep -l -i -E "jdbc:mysql|dbasears|172\\.27\\.141|t1pagos" /var/jenkins_home/jobs/*/config.xml 2>/dev/null | head -20; echo END']))
println("=== env proceso ===")
println(run(['sh','-c','cat /proc/1/environ 2>/dev/null | tr "\\0" "\\n" | grep -i -E "mysql|_db|pass|database|jdbc" | head -20; echo END']))
println("DONE")
