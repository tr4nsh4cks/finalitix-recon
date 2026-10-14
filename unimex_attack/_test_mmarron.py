"""Test mmarron@madecconsultoria.com + API key on Odoo instances"""
import paramiko, json, sys

VPS_IP = "82.27.100.115"
VPS_PW = "37W92I_Wd9581g5j1g1LzI"

SCRIPT = r'''python3 -c "
import json, sys, ssl
from urllib.request import Request, urlopen

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

USER = 'mmarron@madecconsultoria.com'
APIKEY = '9242f55eec6e9ffcb167ca16751f797a204eb604'

def rpc(base, service, method, args):
    payload = json.dumps({
        'jsonrpc': '2.0', 'id': 1, 'method': 'call',
        'params': {'service': service, 'method': method, 'args': args}
    }).encode()
    req = Request(base + '/jsonrpc', data=payload,
                  headers={'Content-Type': 'application/json'})
    resp = urlopen(req, timeout=20, context=ctx)
    return json.loads(resp.read().decode())

def try_web_login(base, db, user, pw):
    import re
    from urllib.request import build_opener, HTTPCookieProcessor
    from http.cookiejar import CookieJar
    from urllib.parse import urlencode
    jar = CookieJar()
    opener = build_opener(HTTPCookieProcessor(jar))
    # Get CSRF
    req = Request(base + '/web/login')
    resp = opener.open(req, timeout=20)
    html = resp.read().decode(errors='replace')
    m = re.search(r'name=\"csrf_token\"\s+value=\"([^\"]+)\"', html)
    csrf = m.group(1) if m else ''
    # POST login
    data = urlencode({'login': user, 'password': pw, 'csrf_token': csrf, 'db': db, 'redirect': '/'}).encode()
    req = Request(base + '/web/login', data=data,
                  headers={'Content-Type': 'application/x-www-form-urlencoded'})
    try:
        resp = opener.open(req, timeout=20)
        url = resp.geturl()
        body = resp.read().decode(errors='replace')[:500]
        if '/web' in url and 'login' not in url:
            return 'LOGIN OK -> ' + url
        elif 'Wrong login' in body or 'incorrecto' in body.lower():
            return 'Wrong login/password'
        else:
            return 'status=' + str(resp.status) + ' url=' + url[:100]
    except Exception as e:
        return str(e)

# ===== 1. Test on unii.com.mx =====
print('='*60)
print('TEST 1: unii.com.mx (DB=unii)')
print('='*60)

try:
    r = rpc('https://unii.com.mx', 'common', 'login', ['unii', USER, APIKEY])
    uid = r.get('result')
    if uid and uid is not False and uid != 0:
        print('  JSON-RPC HIT!!! UID =', uid)
    else:
        print('  JSON-RPC -> False')
except Exception as e:
    print('  JSON-RPC error:', e)

try:
    wl = try_web_login('https://unii.com.mx', 'unii', USER, APIKEY)
    print('  Web login ->', wl)
except Exception as e:
    print('  Web login error:', e)

# ===== 2. Probe madecconsultoria.com =====
print()
print('='*60)
print('TEST 2: Probing madecconsultoria.com')
print('='*60)

import socket
for host in ['madecconsultoria.com', 'www.madecconsultoria.com', 'odoo.madecconsultoria.com',
             'erp.madecconsultoria.com', 'app.madecconsultoria.com', 'sistema.madecconsultoria.com']:
    try:
        ip = socket.gethostbyname(host)
        print(f'  {host} -> {ip}')
    except:
        print(f'  {host} -> NXDOMAIN')

# Probe main domain
for url in ['https://madecconsultoria.com', 'http://madecconsultoria.com',
            'https://www.madecconsultoria.com']:
    try:
        req = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        resp = urlopen(req, timeout=15, context=ctx)
        body = resp.read().decode(errors='replace')
        print(f'  [{resp.status}] {url}')
        # Check if it's Odoo
        if 'odoo' in body.lower() or 'o_' in body or 'web/login' in body:
            print('    >>> ODOO DETECTED <<<')
        title_start = body.find('<title>')
        title_end = body.find('</title>')
        if title_start > -1 and title_end > -1:
            print(f'    title: {body[title_start+7:title_end][:100]}')
        print(f'    body[:200]: {body[:200]}')
    except Exception as e:
        print(f'  [ERR] {url} -> {e}')

# ===== 3. If madecconsultoria.com is Odoo, try auth =====
print()
print('='*60)
print('TEST 3: Try auth on madecconsultoria.com (if Odoo)')  
print('='*60)

for base in ['https://madecconsultoria.com', 'http://madecconsultoria.com',
             'https://www.madecconsultoria.com']:
    try:
        r = rpc(base, 'common', 'version', [])
        ver = r.get('result', {}).get('server_version', '?')
        print(f'  {base} Odoo version: {ver}')
        
        # Try DB list or known names
        for db in ['madec', 'madecconsultoria', 'main', 'production', 'prod', 'odoo']:
            try:
                r = rpc(base, 'common', 'login', [db, USER, APIKEY])
                uid = r.get('result')
                if uid and uid is not False and uid != 0:
                    print(f'  !!! HIT db={db} UID={uid} !!!')
                else:
                    print(f'  db={db} -> False')
            except Exception as e:
                print(f'  db={db} error: {e}')
        
        # Try db.list
        try:
            r = rpc(base, 'db', 'list', [])
            dbs = r.get('result', [])
            print(f'  DB list: {dbs}')
            for db in dbs:
                r2 = rpc(base, 'common', 'login', [db, USER, APIKEY])
                uid2 = r2.get('result')
                if uid2 and uid2 is not False and uid2 != 0:
                    print(f'  !!! HIT db={db} UID={uid2} !!!')
                else:
                    print(f'  db={db} -> {uid2}')
        except Exception as e:
            print(f'  DB list error: {e}')
            
        break
    except Exception as e:
        print(f'  {base} -> {e}')

print()
print('Done')
"
'''

print(f"[*] Connecting to VPS {VPS_IP}...")
client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(VPS_IP, username="root", password=VPS_PW, timeout=10,
               look_for_keys=False, allow_agent=False)
print(f"[+] Connected!")

stdin, stdout, stderr = client.exec_command(SCRIPT, timeout=120)
out = stdout.read().decode(errors="replace")
err = stderr.read().decode(errors="replace")

print(out)
if err:
    print(f"STDERR: {err[:1000]}")

client.close()
