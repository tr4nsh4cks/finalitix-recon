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

# Sears T1Pagos config
print("=" * 60)
print("SEARS T1PAGOS local.php")
print("=" * 60)
q1 = 'def r = ["bash","-c","find /var/jenkins_home/jobs/se_new_front/jobs/se_new_pipe_build_t1pagos-api-config/builds -name local.php -type f 2>/dev/null | tail -1 | xargs cat 2>/dev/null"].execute().text\nprintln r'
print(run_groovy(q1))

# Sanborns T1Pagos config
print("=" * 60)
print("SANBORNS T1PAGOS local.php")
print("=" * 60)
q2 = 'def r = ["bash","-c","find /var/jenkins_home/jobs/sn_new_front/jobs/sn_new_pipe_build_t1pagos-api-config/builds -name local.php -type f 2>/dev/null | tail -1 | xargs cat 2>/dev/null"].execute().text\nprintln r'
print(run_groovy(q2))

# Search for dispersión/payout configs across all jobs
print("=" * 60)
print("DISPERSION/PAYOUT job configs")
print("=" * 60)
q3 = 'def r = ["bash","-c","find /var/jenkins_home/jobs -maxdepth 3 -name config.xml -type f 2>/dev/null | xargs grep -il dispersi 2>/dev/null | head -10"].execute().text\nprintln r'
print(run_groovy(q3))

# Search for conekta/openpay/stripe
print("=" * 60)
print("CONEKTA/OPENPAY/STRIPE job configs")
print("=" * 60)
q4 = 'def r = ["bash","-c","find /var/jenkins_home/jobs -maxdepth 3 -name config.xml -type f 2>/dev/null | xargs grep -il conekta 2>/dev/null; find /var/jenkins_home/jobs -maxdepth 3 -name config.xml -type f 2>/dev/null | xargs grep -il openpay 2>/dev/null; find /var/jenkins_home/jobs -maxdepth 3 -name config.xml -type f 2>/dev/null | xargs grep -il stripe 2>/dev/null"].execute().text\nprintln r'
print(run_groovy(q4))

# List all payment-related jobs
print("=" * 60)
print("ALL PAYMENT-RELATED JOBS (directory names)")
print("=" * 60)
q5 = 'def r = ["bash","-c","find /var/jenkins_home/jobs -maxdepth 3 -type d -name *pago* 2>/dev/null; find /var/jenkins_home/jobs -maxdepth 3 -type d -name *payment* 2>/dev/null; find /var/jenkins_home/jobs -maxdepth 3 -type d -name *dispers* 2>/dev/null; find /var/jenkins_home/jobs -maxdepth 3 -type d -name *spei* 2>/dev/null"].execute().text\nprintln r'
print(run_groovy(q5))
