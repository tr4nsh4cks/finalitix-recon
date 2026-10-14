"""R2 Capital - Try /web/session/authenticate (Odoo SaaS auto-DB)"""
import paramiko

VPS_IP = "82.27.100.115"
VPS_PW = "37W92I_Wd9581g5j1g1LzI"

REMOTE_SCRIPT = r"""
import json, sys, ssl, re
from urllib.request import Request, urlopen, build_opener, HTTPCookieProcessor
from http.cookiejar import CookieJar

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

BASE   = "https://r2-r2capital.odoo.com"
USER   = "mmarron@madecconsultoria.com"
APIKEY = "9242f55eec6e9ffcb167ca16751f797a204eb604"

def post_json(url, data, jar=None):
    opener = build_opener(HTTPCookieProcessor(jar)) if jar else build_opener()
    payload = json.dumps(data).encode()
    req = Request(url, data=payload,
                  headers={"Content-Type": "application/json",
                           "User-Agent": "Mozilla/5.0"})
    resp = opener.open(req, timeout=25)
    return json.loads(resp.read().decode())

print("=" * 60)
print("R2 Capital - Session Authenticate Tests")
print("=" * 60)

# Test 1: /web/session/authenticate (no db - SaaS should auto-detect)
print("\n[1] /web/session/authenticate (db empty)...")
jar1 = CookieJar()
try:
    r = post_json(BASE + "/web/session/authenticate", {
        "jsonrpc": "2.0", "id": 1,
        "params": {"db": "", "login": USER, "password": APIKEY}
    }, jar=jar1)
    result = r.get("result", {})
    error = r.get("error")
    if result and result.get("uid"):
        print(f"  >>> AUTH OK! UID={result.get('uid')} DB={result.get('db')} <<<")
        print(f"  Username: {result.get('username')}")
        print(f"  Is admin: {result.get('is_admin')}")
        print(f"  Company: {result.get('company_id')}")
    elif error:
        print(f"  Error: {json.dumps(error.get('data', error))[:500]}")
    else:
        print(f"  Result: {json.dumps(result)[:500]}")
except Exception as e:
    print(f"  Exception: {e}")

# Test 2: /web/session/authenticate with db=False
print("\n[2] /web/session/authenticate (db=False)...")
jar2 = CookieJar()
try:
    r = post_json(BASE + "/web/session/authenticate", {
        "jsonrpc": "2.0", "id": 1,
        "params": {"db": False, "login": USER, "password": APIKEY}
    }, jar=jar2)
    result = r.get("result", {})
    error = r.get("error")
    if result and result.get("uid"):
        print(f"  >>> AUTH OK! UID={result.get('uid')} DB={result.get('db')} <<<")
    elif error:
        emsg = error.get("data", {}).get("message", str(error))[:500]
        print(f"  Error: {emsg}")
    else:
        print(f"  Result: {json.dumps(result)[:300]}")
except Exception as e:
    print(f"  Exception: {e}")

# Test 3: Try with SaaS DB naming patterns (numeric suffix)
print("\n[3] Brute DB name with common Odoo SaaS patterns...")
# Odoo SaaS typically uses: subdomain-main-XXXXXXXX (8 digit timestamp-like)
# Or just the subscription ID
import hashlib

# Generate candidate names
candidates = [
    "r2-r2capital",
    "r2-r2capital-main",
    "r2r2capital",
    "r2_r2capital",
]

# Try getting DB name from /web/session/get_session_info without auth
print("\n[4] /web/session/get_session_info (no auth)...")
jar4 = CookieJar()
try:
    # First get a session cookie
    opener = build_opener(HTTPCookieProcessor(jar4))
    req = Request(BASE + "/web/login", headers={"User-Agent": "Mozilla/5.0"})
    resp = opener.open(req, timeout=15)
    html = resp.read().decode(errors="replace")
    
    # Try session info  
    r = post_json(BASE + "/web/session/get_session_info", {
        "jsonrpc": "2.0", "id": 1, "params": {}
    }, jar=jar4)
    result = r.get("result", {})
    print(f"  DB: {result.get('db')}")
    print(f"  UID: {result.get('uid')}")
    print(f"  Server version: {result.get('server_version')}")
    if result.get("db"):
        db_found = result.get("db")
        print(f"\n  >>> Found DB name: {db_found} <<<")
        
        # Now try auth with this DB
        print(f"\n[5] JSON-RPC auth with discovered DB '{db_found}'...")
        payload = json.dumps({
            "jsonrpc": "2.0", "id": 1, "method": "call",
            "params": {"service": "common", "method": "login",
                       "args": [db_found, USER, APIKEY]}
        }).encode()
        req = Request(BASE + "/jsonrpc", data=payload,
                      headers={"Content-Type": "application/json"})
        resp = urlopen(req, timeout=25, context=ctx)
        r = json.loads(resp.read().decode())
        uid = r.get("result")
        if uid and uid is not False and uid != 0:
            print(f"  >>> HIT! UID={uid} <<<")
        else:
            print(f"  -> {uid}")
            err = r.get("error")
            if err:
                print(f"  Error: {err.get('data', {}).get('message', str(err))[:300]}")
except Exception as e:
    print(f"  Exception: {e}")

# Test 5: Check /website/info
print("\n[6] /website/info...")
try:
    req = Request(BASE + "/website/info", headers={"User-Agent": "Mozilla/5.0"})
    resp = urlopen(req, timeout=15, context=ctx)
    body = resp.read().decode(errors="replace")
    print(f"  Status: {resp.status}")
    print(f"  Body[:500]: {body[:500]}")
except Exception as e:
    print(f"  Error: {e}")

# Test 6: Check /web/webclient/version_info
print("\n[7] /web/webclient/version_info...")
try:
    r = post_json(BASE + "/web/webclient/version_info", {
        "jsonrpc": "2.0", "id": 1, "params": {}
    })
    print(f"  Result: {json.dumps(r.get('result', {}))[:500]}")
except Exception as e:
    print(f"  Error: {e}")

print("\nDone")
"""

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(VPS_IP, username="root", password=VPS_PW, timeout=10,
               look_for_keys=False, allow_agent=False)

sftp = client.open_sftp()
with sftp.open("/tmp/r2cap_sa.py", "w") as f:
    f.write(REMOTE_SCRIPT)
sftp.close()

print("[+] Executing on VPS...")
stdin, stdout, stderr = client.exec_command("python3 /tmp/r2cap_sa.py", timeout=120)
print(stdout.read().decode(errors="replace"))
err = stderr.read().decode(errors="replace")
if err:
    print(f"STDERR: {err[:1500]}")

client.exec_command("rm -f /tmp/r2cap_sa.py")
client.close()
