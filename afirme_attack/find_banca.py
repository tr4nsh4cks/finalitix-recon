import urllib.request, ssl, re
ctx = ssl.create_default_context(); ctx.check_hostname=False; ctx.verify_mode=ssl.CERT_NONE
html = urllib.request.urlopen('https://www.afirme.com/afirme', context=ctx, timeout=15).read().decode('utf-8','replace')
links = sorted(set(re.findall(r'(?:href|src|action)="([^"]+)"', html)))
for l in links:
    if any(k in l.lower() for k in ['banca','net','login','acces','movil','linea','segur','afirmenet','empresa']):
        print(l)
