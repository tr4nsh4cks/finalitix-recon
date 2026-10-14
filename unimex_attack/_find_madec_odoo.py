"""Find the Odoo instance for Madec / mmarron"""
import paramiko, sys

VPS_IP = "82.27.100.115"
VPS_PW = "37W92I_Wd9581g5j1g1LzI"

SCRIPT = r'''python3 -c "
import json, sys, ssl, socket, re
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

USER = 'mmarron@madecconsultoria.com'
APIKEY = '9242f55eec6e9ffcb167ca16751f797a204eb604'

def rpc(base, service, method, args, timeout=15):
    payload = json.dumps({
        'jsonrpc': '2.0', 'id': 1, 'method': 'call',
        'params': {'service': service, 'method': method, 'args': args}
    }).encode()
    req = Request(base + '/jsonrpc', data=payload,
                  headers={'Content-Type': 'application/json'})
    resp = urlopen(req, timeout=timeout, context=ctx)
    return json.loads(resp.read().decode())

def check_url(url, timeout=12):
    try:
        req = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        resp = urlopen(req, timeout=timeout, context=ctx)
        body = resp.read().decode(errors='replace')
        return resp.status, body
    except HTTPError as e:
        return e.code, ''
    except Exception as e:
        return -1, str(e)

def try_odoo_auth(base, user, pw, dbs=None):
    # First check if /jsonrpc exists
    try:
        r = rpc(base, 'common', 'version', [])
        ver = r.get('result', {}).get('server_version', '?')
        print(f'  [ODOO] {base} -> v{ver}')
    except Exception as e:
        print(f'  [---] {base} -> no jsonrpc ({e})')
        return False
    
    # Get DB list
    if not dbs:
        try:
            r = rpc(base, 'db', 'list', [])
            dbs = r.get('result', [])
            print(f'  [DBs] {dbs}')
        except:
            dbs = ['madec', 'madecconsultoria', 'main', 'production', 'prod', 'odoo',
                   'madec_prod', 'madec_contable', 'unio', 'unimex']
            print(f'  [DBs] list blocked, trying common names')
    
    for db in dbs:
        try:
            r = rpc(base, 'common', 'login', [db, user, pw])
            uid = r.get('result')
            if uid and uid is not False and uid != 0:
                print(f'  >>> HIT! db={db} user={user} UID={uid} <<<')
                return True
            else:
                r2 = rpc(base, 'db', 'db_exist', [db])
                exists = r2.get('result')
                if exists:
                    print(f'  db={db} EXISTS but auth failed')
                # else: db doesn't exist, skip
        except Exception as e:
            pass
    return False

print('='*60)
print('PHASE 1: Odoo SaaS (*.odoo.com)')
print('='*60)

saas_names = ['madec', 'madecconsultoria', 'madec-consultoria', 'madec-mx',
              'madeccontable', 'madec-contable', 'mmarron']

for name in saas_names:
    url = f'https://{name}.odoo.com'
    try:
        ip = socket.gethostbyname(f'{name}.odoo.com')
        print(f'  {name}.odoo.com -> {ip}')
        status, body = check_url(url + '/web/login')
        if status == 200 and ('odoo' in body.lower() or 'csrf_token' in body):
            print(f'    ODOO LOGIN PAGE FOUND!')
            try_odoo_auth(url, USER, APIKEY, [name])
        else:
            print(f'    status={status}')
    except socket.gaierror:
        print(f'  {name}.odoo.com -> NXDOMAIN')
    except Exception as e:
        print(f'  {name}.odoo.com -> {e}')

print()
print('='*60)
print('PHASE 2: Other possible Odoo locations')
print('='*60)

# Check more subdomains of madecconsultoria.com
subs = ['admin', 'erp', 'odoo', 'sistema', 'app', 'portal', 'contabilidad',
        'cloud', 'mail', 'webmail', 'cpanel', 'ftp', 'test', 'dev', 'staging',
        'api', 'server', 'servidor', 'panel', 'mx', 'factura', 'facturacion']

print('Subdomains of madecconsultoria.com:')
for sub in subs:
    host = f'{sub}.madecconsultoria.com'
    try:
        ip = socket.gethostbyname(host)
        print(f'  {host} -> {ip}')
    except:
        pass

# Check main site more carefully
print()
print('Checking madecconsultoria.com for Odoo paths:')
paths = ['/web/login', '/web', '/web/database/selector', '/web/database/manager',
         '/jsonrpc', '/xmlrpc/2/common', '/odoo', '/admin']

for path in paths:
    for base in ['https://madecconsultoria.com', 'http://madecconsultoria.com']:
        try:
            status, body = check_url(base + path, timeout=10)
            if status == 200:
                snip = body[:150].replace(chr(10),' ').replace(chr(13),'')
                print(f'  [{status}] {base}{path} -> {snip}')
            elif status in (301, 302):
                print(f'  [{status}] {base}{path} -> redirect')
        except:
            pass

# Check IP 132.148.176.202 directly
print()
print('Checking IP 132.148.176.202 for Odoo:')
for proto in ['https', 'http']:
    try:
        status, body = check_url(f'{proto}://132.148.176.202/web/login', timeout=10)
        if status == 200:
            print(f'  [{status}] {proto}://132.148.176.202/web/login -> Odoo found!')
        elif status > 0:
            print(f'  [{status}] {proto}://132.148.176.202/web/login')
    except Exception as e:
        print(f'  {proto}://132.148.176.202 -> {e}')

# Also try on Unimex/UNIO related domains
print()
print('='*60)
print('PHASE 3: Other UNIO/Unimex Odoo instances')
print('='*60)

other_bases = [
    'https://unii.com.mx',
]

# Maybe the key works with a different DB name on unii.com.mx
print('Testing more DB names on unii.com.mx:')
extra_dbs = ['madec', 'madecconsultoria', 'madec_prod', 'unimex', 'unimex_digital',
             'unio', 'production', 'main', 'default']
for db in extra_dbs:
    try:
        # First check if DB exists
        r = rpc('https://unii.com.mx', 'db', 'db_exist', [db])
        exists = r.get('result')
        if exists:
            print(f'  DB {db} EXISTS on unii.com.mx!')
            r2 = rpc('https://unii.com.mx', 'common', 'login', [db, USER, APIKEY])
            uid = r2.get('result')
            if uid and uid is not False and uid != 0:
                print(f'  >>> HIT! db={db} UID={uid} <<<')
            else:
                print(f'  auth failed for db={db}')
    except:
        pass

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

stdin, stdout, stderr = client.exec_command(SCRIPT, timeout=180)
out = stdout.read().decode(errors="replace")
err = stderr.read().decode(errors="replace")

print(out)
if err and "InsecureRequestWarning" not in err:
    print(f"STDERR: {err[:1000]}")

client.close()
