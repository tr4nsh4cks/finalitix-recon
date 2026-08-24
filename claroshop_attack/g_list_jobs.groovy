// Lista todos los jobs de Jenkins con sus rutas en el filesystem
import jenkins.model.Jenkins

def jenkins = Jenkins.getInstance()

println "=== JENKINS JOBS LIST ==="
println "Total jobs: " + jenkins.getAllItems().size()
println "=" * 60

jenkins.getAllItems().each { job ->
    println "JOB: ${job.fullName}"
    println "  Class: ${job.class.simpleName}"
    println "  URL: ${job.absoluteUrl}"
    def configFile = new File("/var/jenkins_home/jobs/${job.fullName.replace('/', '/jobs/')}/config.xml")
    println "  Config exists: ${configFile.exists()}"
    println "---"
}

println "\n=== FILESYSTEM JOB DIRS ==="
def jobsDir = new File("/var/jenkins_home/jobs")
if (jobsDir.exists()) {
    jobsDir.eachDir { dir ->
        println "DIR: ${dir.name}"
        def subJobs = new File(dir, "jobs")
        if (subJobs.exists()) {
            subJobs.eachDir { sub ->
                println "  SUBJOB: ${sub.name}"
            }
        }
    }
}
