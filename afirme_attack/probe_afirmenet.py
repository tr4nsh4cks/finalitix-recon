import urllib.request, ssl, re, socket
ctx = ssl.create_default_context(); ctx.check_hostname=False; ctx.verify_mode=ssl.CERT_NONE

host = 'www.afirmeeninternet.com'
print('IP:', socket.gethostbyname(host))

def get(url):
    req = urllib.request.Request(url, headers={'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
    try:
        r = urllib.request.urlopen(req, context=ctx, timeout=12)
        return r.status, dict(r.headers), r.read().decode('utf-8','replace')
    except urllib.error.HTTPError as e:
        return e.code, dict(e.headers), e.read().decode('utf-8','replace')
    except Exception as e:
        return None, {}, str(e)

for path in ['/AfirmeNetP/login/contrato.htm', '/AfirmeNetP/', '/AfirmeNetE/', '/AfirmeNetE/login/contrato.htm']:
    st, h, body = get('https://'+host+path)
    print('===', path, '=>', st, '| server:', h.get('Server'), '| len:', len(body))
    if st == 200:
        setc = h.get('Set-Cookie','')
        if setc: print('  Set-Cookie:', setc[:150])
        for m in re.findall(r'(?:src|href|action)="([^"]{5,120})"', body)[:15]:
            print('  ', m)
