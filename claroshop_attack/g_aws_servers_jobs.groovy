// Buscar los jobs de "AWS SERVERS" que hacen deploy a PROD
// y extraer credenciales SSH / IPs de PROD servers

def out = new StringBuilder()

Jenkins.getInstance().getAllItems(hudson.model.Job.class).each { job ->
  def name = job.getFullName()
  
  // Buscar jobs con AWS en el nombre o en el path
  if (!name.toLowerCase().contains("aws") && !name.contains("pipe_sierra-t1envios")) return
  
  def configFile = null
  try {
    configFile = new File("/var/jenkins_home/jobs/${name.replace('/', '/jobs/')}/config.xml")
    if (!configFile.exists()) {
      // Intenta con subfolder jobs
      configFile = new File("/var/jenkins_home/jobs/" + name.replace('/', '/jobs/') + "/config.xml")
    }
  } catch(Exception e) {}
  
  if (!configFile || !configFile.exists()) return
  
  def xml = configFile.text
  out.append("\n=== JOB: $name ===\n")
  
  // Full content for AWS SERVER jobs (truncated)
  def lines = xml.readLines()
  lines.each { line ->
    def lt = line.trim()
    if (lt.length() > 5 && lt.length() < 300) {
      // Skip pure XML tags with no interesting content
      if (lt =~ /^<[a-z\/]/) return  // skip pure structural XML
      def clean = lt.replaceAll('&apos;',"'").replaceAll('&amp;',"&").replaceAll('&lt;',"<").replaceAll('&gt;',">").replaceAll('&#xd;',"")
      out.append("  ${clean.take(200)}\n")
    }
  }
}

// Also directly list all job names containing "aws" or "pipe_sierra" or "pipe_t1"  
out.append("\n\n=== ALL AWS/PROD JOB NAMES ===\n")
Jenkins.getInstance().getAllItems(hudson.model.Job.class).each { job ->
  def name = job.getFullName()
  if (name.toLowerCase().contains("aws") || name.contains("pipe_sierra-t1envios") || 
      name.contains("pipe_t1-admin")) {
    out.append("  $name\n")
  }
}

println out.toString() ?: "NO AWS JOBS FOUND"
println "=== FIN AWS ==="
