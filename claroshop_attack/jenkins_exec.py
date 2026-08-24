import urllib.request, base64, json, urllib.parse, ssl, sys, http.cookiejar

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

AUTH = base64.b64encode(b'eduardo.cruz:xwMyIxfkZZaDNkFg').decode()
BASE = 'https://jenkins-ng.dev.claroshop.com'

def jenkins_exec(script):
    cj = http.cookiejar.CookieJar()
    opener = urllib.request.build_opener(
        urllib.request.HTTPCookieProcessor(cj),
        urllib.request.HTTPSHandler(context=ctx)
    )
    
    # Get crumb (with session cookie)
    req = urllib.request.Request(
        BASE + '/crumbIssuer/api/json',
        headers={'Authorization': 'Basic ' + AUTH}
    )
    r = opener.open(req, timeout=15)
    crumb = json.loads(r.read().decode())
    
    # Execute script (same session)
    data = urllib.parse.urlencode({'script': script}).encode()
    headers = {
        'Authorization': 'Basic ' + AUTH,
        crumb['crumbRequestField']: crumb['crumb']
    }
    req2 = urllib.request.Request(BASE + '/scriptText', data=data, headers=headers)
    r2 = opener.open(req2, timeout=300)
    return r2.read().decode()

if __name__ == '__main__':
    if len(sys.argv) > 1:
        script = open(sys.argv[1], encoding='utf-8').read()
    else:
        script = 'println("CONNECTED_OK_" + Jenkins.getInstance().getVersion())'
    
    result = jenkins_exec(script)
    import sys
    sys.stdout.buffer.write(result.encode('utf-8', errors='replace'))
    sys.stdout.buffer.write(b'\n')
