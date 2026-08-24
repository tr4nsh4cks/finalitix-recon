// Enumerar jobs que despliegan a PROD (AWS SERVERS, t1envios PROD, sears PROD)
// y extraer credentialIds de SSH steps

def out = new StringBuilder()

Jenkins.getInstance().getAllItems(hudson.model.Job.class).each { job ->
  def name = job.getFullName()
  
  // Solo buscar jobs con "PROD" o "AWS SERVERS" o "sears" prod en el nombre o config
  def xml = ""
  try {
    def configFile = new File("/var/jenkins_home/jobs/${name.replace('/', '/jobs/')}/config.xml")
    if (configFile.exists()) {
      xml = configFile.text
    }
  } catch(Exception e) {}
  
  if (!xml) return
  
  def isProd = (xml.contains("AWS SERVERS") || 
                xml.contains("dbasears") || 
                xml.contains("sears.com.mx") && xml.contains("PROD") ||
                xml.contains("t1envios.com") && !xml.contains("dev.t1envios") ||
                xml.contains("172.27.141.24") ||
                xml.contains("admin.t1envios.com") && !xml.contains("sierra-admin.dev"))
  
  if (!isProd) return
  
  out.append("\n=== JOB: $name ===\n")
  
  // Extract sshUserPrivateKey steps
  def credMatcher = (xml =~ /credentialsId='([^']+)'|credentialsId="([^"]+)"/)
  def creds = [] as Set
  credMatcher.each { m -> creds.add(m[1] ?: m[2]) }
  if (creds) out.append("  CREDS: ${creds.join(', ')}\n")
  
  // Extract SSH publish targets
  def sshMatcher = (xml =~ /<server>([^<]+)<\/server>|sshPublisher.*?server[^>]*>([^<]+)/)
  sshMatcher.each { m -> out.append("  SSH_TARGET: ${m[1] ?: m[2]}\n") }
  
  // Extract environment host vars
  def envMatcher = (xml =~ /DEPLOY_HOST[^=]*=\s*"?([^"\n&]+)"?|SERVER[^=]*=\s*"?([^"\n&]+)"?|HOST[^=]*=\s*"?([^"\n&]+)"?/)
  envMatcher.each { m ->
    def val = m[1] ?: m[2] ?: m[3]
    if (val && !val.startsWith("{") && val.length() < 80) {
      out.append("  ENV_HOST: ${m[0].trim().take(120)}\n")
    }
  }
  
  // Extract relevant context lines (anything with prod/release/admin.t1envios/sears.com.mx)
  xml.readLines().each { line ->
    def lt = line.trim()
    if (lt.length() > 5 && lt.length() < 250 &&
       (lt.contains("admin.t1envios") || lt.contains("release.t1envios") ||
        lt.contains("sears.com.mx") || lt.contains("AWS SERVERS") ||
        lt.contains("172.27.141.24") || lt.contains("dbasears"))) {
      def clean = lt.replaceAll('&apos;',"'").replaceAll('&amp;',"&").replaceAll('&lt;',"<").replaceAll('&gt;',"=")
      if (!clean.startsWith("//") && clean.length() < 200) {
        out.append("  L: ${clean.take(180)}\n")
      }
    }
  }
}

println out.toString() ?: "NO PROD JOBS FOUND"
println "=== FIN ==="
