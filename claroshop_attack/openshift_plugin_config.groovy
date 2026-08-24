// Extraer configuración del plugin OpenShift Sync
// El plugin almacena URL del servidor y token en la config global de Jenkins

println "=== OPENSHIFT SYNC PLUGIN CONFIG ==="
println ""

// 1. Leer configuración del plugin openshift-sync desde el XML
def configFiles = [
    "/var/jenkins_home/io.fabric8.jenkins.openshiftsync.GlobalPluginConfiguration.xml",
    "/var/jenkins_home/com.openshift.jenkins.plugins.OpenShiftCloud.xml",
    "/var/jenkins_home/com.openshift.jenkins.plugins.pipeline.OpenShiftCloudPlugin.xml",
    "/var/jenkins_home/config.xml"
]

configFiles.each { path ->
    def f = new File(path)
    if (f.exists() && f.canRead()) {
        println "\n=== FILE: ${path} ==="
        def content = f.text
        // Buscar tokens/credenciales en el XML
        content.split("\n").each { line ->
            def ll = line.toLowerCase()
            if (ll.contains("server") || ll.contains("token") || ll.contains("credential") || 
                ll.contains("openshift") || ll.contains("amxnova") || ll.contains("namespace") ||
                ll.contains("apiserver") || ll.contains("clusterurl") || ll.contains("password") ||
                ll.contains("secret") || ll.contains("bearer")) {
                println line
            }
        }
    }
}

// 2. Buscar configuración del plugin via API de Jenkins
println ""
println "--- OPENSHIFT SYNC VIA API ---"
try {
    def cls = Class.forName("io.fabric8.jenkins.openshiftsync.GlobalPluginConfiguration")
    def instance = cls.getDeclaredMethod("get").invoke(null)
    println "Server: ${instance.getServer()}"
    println "Credential: ${instance.getCredentialsId()}"
    println "Namespaces: ${instance.getNamespaces()}"
    println "Auto: ${instance.isEnabled()}"
} catch(e) {
    println "openshift-sync GlobalPluginConfiguration: ${e.message}"
}

// 3. Listar TODOS los XML de configuración de plugins en jenkins_home
println ""
println "--- XML FILES EN JENKINS HOME ---"
def jenkinsHome = new File("/var/jenkins_home")
if (jenkinsHome.exists()) {
    jenkinsHome.listFiles().findAll { it.name.endsWith(".xml") && !it.name.equals("config.xml") }.each { f ->
        println f.name
    }
} else {
    println "No encontrado /var/jenkins_home"
    // Probar con el home del sistema
    def jHome = System.getProperty("user.home")
    println "user.home = ${jHome}"
    new File(jHome).listFiles()?.findAll { it.name.endsWith(".xml") }?.each { f ->
        println f.name
    }
}

// 4. Leer config.xml de Jenkins para encontrar cloud/openshift config
println ""
println "--- JENKINS CLOUDS CONFIG (config.xml excerpt) ---"
def mainConfig = new File("/var/jenkins_home/config.xml")
if (!mainConfig.exists()) {
    // Buscar por propiedad del sistema
    def home = System.getProperty("JENKINS_HOME") ?: "/var/jenkins_home"
    mainConfig = new File("${home}/config.xml")
}
if (mainConfig.exists()) {
    def content = mainConfig.text
    // Extraer sección clouds
    def inCloud = false
    def depth = 0
    content.split("\n").each { line ->
        if (line.contains("<clouds>") || line.contains("<cloud>") || line.contains("OpenShift") || 
            line.contains("kubernetes") || line.contains("amxnova") || line.contains("sophia")) {
            inCloud = true
        }
        if (inCloud) {
            println line
            if (line.contains("</clouds>")) inCloud = false
        }
    }
}

// 5. Intentar via Jenkins.getInstance() las cloud configs (para k8s/openshift cloud)
println ""
println "--- CLOUDS VIA JENKINS API ---"
try {
    jenkins.model.Jenkins.getInstance().clouds.each { cloud ->
        println "Cloud: ${cloud.name} | Type: ${cloud.class.simpleName}"
        cloud.properties.each { k, v ->
            println "  ${k} = ${v}"
        }
    }
} catch(e) {
    println "Clouds API error: ${e.message}"
}

// 6. Buscar en credentials.xml el token de OpenShift
println ""
println "--- credentials.xml FULL (filtrado) ---"
def credXml = new File("/var/jenkins_home/credentials.xml")
if (credXml.exists()) {
    credXml.text.split("\n").each { line ->
        println line
    }
} else {
    println "credentials.xml no encontrado en /var/jenkins_home"
}

println ""
println "=== FIN CONFIG HUNT ==="
