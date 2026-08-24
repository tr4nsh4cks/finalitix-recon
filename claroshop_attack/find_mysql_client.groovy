def run = { String c ->
  try {
    def p = c.execute()
    def out = p.inputStream.text
    def err = p.errorStream.text
    p.waitFor()
    return (out + err).trim()
  } catch (Exception e) { return "ERR: " + e.message }
}

println("=== which mysql/mariadb ===")
println(run('sh -c "which mysql; which mariadb; ls /usr/bin/mysql* /usr/local/bin/mysql* 2>/dev/null"'))
println("=== JDBC jars en jenkins_home ===")
println(run('sh -c "find /var/jenkins_home -iname \'*mysql*.jar\' -o -iname \'*mariadb*.jar\' 2>/dev/null | head -20"'))
println("=== JDBC jars en sistema ===")
println(run('sh -c "find / -iname \'mysql-connector*.jar\' -o -iname \'mariadb-java*.jar\' 2>/dev/null | head -10"'))
println("=== java version ===")
println(run('sh -c "java -version 2>&1"'))
println("=== internet egress test ===")
try {
  def u = new URL('https://repo1.maven.org/maven2/')
  def c = u.openConnection()
  c.setConnectTimeout(6000); c.setReadTimeout(6000)
  c.connect()
  println("EGRESS_OK code=" + c.getResponseCode())
} catch (Exception e) {
  println("EGRESS_FAIL: " + e.message)
}
println("=== groovy sql disponible ===")
try {
  Class.forName('groovy.sql.Sql')
  println("groovy.sql.Sql OK")
} catch (Exception e) { println("no groovy.sql: " + e.message) }
println("DONE")
