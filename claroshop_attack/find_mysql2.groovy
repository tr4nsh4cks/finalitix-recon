def run = { List c ->
  try {
    def p = c.execute()
    def out = p.inputStream.text
    def err = p.errorStream.text
    p.waitFor()
    return (out + err).trim()
  } catch (Exception e) { return "ERR: " + e.message }
}

println("=== mysql cli ===")
println(run(['sh','-c','which mysql mariadb 2>/dev/null; ls /usr/bin/ | grep -i -E "mysql|maria" 2>/dev/null; echo END']))
println("=== JDBC jars jenkins_home ===")
println(run(['sh','-c','find /var/jenkins_home -iname "*mysql*.jar" -o -iname "*mariadb*.jar" 2>/dev/null | head; echo END']))
println("=== JDBC jars sistema ===")
println(run(['sh','-c','find / -iname "mysql-connector*.jar" -o -iname "mariadb-java*.jar" 2>/dev/null | head; echo END']))
println("=== cualquier jar jdbc ===")
println(run(['sh','-c','find /var/jenkins_home -iname "*jdbc*.jar" 2>/dev/null | head; echo END']))
println("DONE")
