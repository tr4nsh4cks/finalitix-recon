// Extract all docker image references from Jenkins job configs = de facto Nexus catalog
def images = new TreeSet()
def pat = ~/(?:[a-z0-9-]+\.)*nexus\.dev\.claroshop\.com\/[A-Za-z0-9._\/-]+(?::[A-Za-z0-9._-]+)?/
def pat2 = ~/(?:docker-source-registry\.amxdigital\.net|dockeregistry\.amovildigitalops\.com|cs-docker-registry[a-z0-9.-]*)\/[A-Za-z0-9._\/-]+(?::[A-Za-z0-9._-]+)?/

Jenkins.getInstance().getAllItems(Job.class).each { job ->
    try {
        def cfg = job.getConfigFile()?.asString()
        if (cfg) {
            pat.matcher(cfg).each { m -> images.add(m) }
            pat2.matcher(cfg).each { m -> images.add(m) }
        }
    } catch (Exception e) { /* skip */ }
}

// Also scan pipeline scripts in job definitions (inline pipeline scripts)
Jenkins.getInstance().getAllItems(Job.class).each { job ->
    try {
        def props = job.getProperty(org.jenkinsci.plugins.workflow.job.properties.PipelineTriggersJobProperty)
    } catch (Exception e) {}
    try {
        if (job instanceof org.jenkinsci.plugins.workflow.job.WorkflowJob) {
            def script = job.getDefinition()
            if (script instanceof org.jenkinsci.plugins.workflow.cps.CpsFlowDefinition) {
                def s = script.getScript()
                pat.matcher(s).each { m -> images.add(m) }
                pat2.matcher(s).each { m -> images.add(m) }
            }
        }
    } catch (Exception e) {}
}

println "TOTAL_JOBS=" + Jenkins.getInstance().getAllItems(Job.class).size()
println "TOTAL_IMAGES=" + images.size()
images.each { println "IMG: " + it }
