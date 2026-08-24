// Buscar URLs del panel admin en configs de Jenkins jobs
def jenkins = Jenkins.getInstance()
def patterns = ~/(?i)(admonplaza|axii|admin\.sears|panel\.sears|backoffice\.sears|admon\.|\.sears\.com\.mx|pot\.admin|administracion|backoffice)/
def seen = [:]

jenkins.getAllItems(hudson.model.Job.class).each { job ->
    try {
        def cfg = job.getConfigFile()?.asString()
        if (!cfg) return
        def hits = []
        cfg.eachLine { line ->
            def m = patterns.matcher(line)
            if (m.find()) {
                def clean = line.trim().take(300)
                if (!seen[clean]) { hits << clean; seen[clean] = 1 }
            }
        }
        if (hits) {
            println "=== JOB: ${job.fullName} ==="
            hits.take(15).each { println "  " + it }
        }
    } catch (e) { }
}
println "GREP_DONE"
