"""Find the correct DB name on R2 Capital Odoo SaaS and authenticate"""
import paramiko, sys

VPS_IP = "82.27.100.115"
VPS_PW = "37W92I_Wd9581g5j1g1LzI"

REMOTE_SCRIPT = r"""
import json, sys, ssl, re
from urllib.request import Request, urlopen, build_opener, HTTPCookieProcessor
from urllib.error import URLError, HTTPError
from urllib.parse import urlencode
from http.cookiejar import CookieJar

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

BASE   = "https://r2-r2capital.odoo.com"
USER   = "mmarron@madecconsultoria.com"
APIKEY = "9242f55eec6e9ffcb167ca16751f797a204eb604"

def fetch(url, data=None, headers=None, jar=None):
    if jar:
        opener = build_opener(HTTPCookieProcessor(jar))
    else:
        opener = build_opener()
    hdrs = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    if headers:
        hdrs.update(headers)
    req = Request(url, data=data, headers=hdrs)
    resp = opener.open(req, timeout=25)
    return resp

def rpc(service, method, args):
    payload = json.dumps({
        "jsonrpc": "2.0", "id": 1, "method": "call",
        "params": {"service": service, "method": method, "args": args}
    }).encode()
    resp = fetch(BASE + "/jsonrpc", data=payload,
                 headers={"Content-Type": "application/json"})
    return json.loads(resp.read().decode())

print("=" * 60)
print("[1] Fetching login page HTML to find DB...")
print("=" * 60)

jar = CookieJar()
resp = fetch(BASE + "/web/login", jar=jar)
html = resp.read().decode(errors="replace")

# Dump all input fields
inputs = re.findall(r'<input[^>]+>', html)
print("\nAll <input> fields:")
for inp in inputs:
    print("  " + inp[:200])

# Find DB specifically
db_patterns = [
    r'name="db"\s+value="([^"]*)"',
    r'value="([^"]*)"\s+name="db"',
    r'name="db"[^>]*value="([^"]*)"',
    r"name='db'[^>]*value='([^']*)'",
    r'data-db="([^"]*)"',
    r'"db":\s*"([^"]*)"',
    r"'db':\s*'([^']*)'",
]

found_db = None
for pat in db_patterns:
    m = re.search(pat, html, re.IGNORECASE)
    if m:
        found_db = m.group(1)
        print(f"\nDB found with pattern '{pat}': '{found_db}'")
        break

# Also check for DB in JavaScript
js_dbs = re.findall(r'["\']database["\']:\s*["\']([^"\']+)["\']', html)
js_dbs2 = re.findall(r'["\']db_name["\']:\s*["\']([^"\']+)["\']', html)
js_dbs3 = re.findall(r'["\']db["\']:\s*["\']([^"\']+)["\']', html)
if js_dbs: print(f"\nJS database: {js_dbs}")
if js_dbs2: print(f"JS db_name: {js_dbs2}")
if js_dbs3: print(f"JS db: {js_dbs3}")

# Check select elements for DB
selects = re.findall(r'<select[^>]*name="db"[^>]*>(.*?)</select>', html, re.DOTALL)
if selects:
    opts = re.findall(r'<option[^>]*value="([^"]*)"', selects[0])
    print(f"\nDB select options: {opts}")
    if opts:
        found_db = opts[0]

# Check cookies
print("\nCookies set:")
for cookie in jar:
    print(f"  {cookie.name} = {cookie.value[:60]}...")

# Check response headers
print(f"\nLogin page title:")
title = re.search(r'<title>([^<]+)</title>', html)
if title:
    print(f"  {title.group(1)}")

# Check for Odoo session info in page
session_info = re.search(r'session_info\s*=\s*(\{[^}]+\})', html)
if session_info:
    print(f"\nSession info in page: {session_info.group(1)[:500]}")

# On Odoo SaaS, the DB name is usually in the URL or auto-detected
# Let's try common patterns
print("\n" + "=" * 60)
print("[2] Trying DB names with JSON-RPC auth...")
print("=" * 60)

db_candidates = []
if found_db:
    db_candidates.append(found_db)

# Odoo SaaS DB naming patterns
db_candidates.extend([
    "r2-r2capital",
    "r2-r2capital-main",
    "r2-r2capital-r2-r2capital-main",
    "r2capital",
    "r2-r2capital-production",
    "r2-r2capital-prod",
])

# Also try db_exist
for db in db_candidates[:]:
    try:
        r = rpc("db", "db_exist", [db])
        if r.get("result"):
            print(f"  DB '{db}' EXISTS!")
        else:
            print(f"  DB '{db}' does not exist")
    except Exception as e:
        print(f"  DB '{db}' check error: {e}")

# Try authenticate on each
for db in db_candidates:
    try:
        r = rpc("common", "login", [db, USER, APIKEY])
        uid = r.get("result")
        err = r.get("error")
        if uid and uid is not False and uid != 0:
            print(f"  >>> HIT! db={db} UID={uid} <<<")
            break
        elif err:
            emsg = str(err.get("data", {}).get("message", ""))[:200]
            print(f"  db={db} -> error: {emsg}")
        else:
            print(f"  db={db} -> False")
    except Exception as e:
        print(f"  db={db} -> {e}")

# Also try XML-RPC  
print("\n" + "=" * 60)
print("[3] XML-RPC authenticate...")
print("=" * 60)

for db in db_candidates[:3]:
    try:
        xml = '<?xml version="1.0"?><methodCall><methodName>authenticate</methodName><params>'
        xml += '<param><value><string>%s</string></value></param>' % db
        xml += '<param><value><string>%s</string></value></param>' % USER
        xml += '<param><value><string>%s</string></value></param>' % APIKEY
        xml += '<param><value><struct></struct></value></param>'
        xml += '</params></methodCall>'
        resp = fetch(BASE + "/xmlrpc/2/common", data=xml.encode(),
                     headers={"Content-Type": "text/xml"})
        body = resp.read().decode()
        print(f"  db={db}: {body[:300]}")
    except Exception as e:
        print(f"  db={db}: {e}")

# Try web login with the found DB
print("\n" + "=" * 60)
print("[4] Web login with best DB candidate...")
print("=" * 60)

login_db = found_db or "r2-r2capital"
jar2 = CookieJar()
resp = fetch(BASE + "/web/login", jar=jar2)
html2 = resp.read().decode(errors="replace")
m = re.search(r'name="csrf_token"\s+value="([^"]+)"', html2)
csrf = m.group(1) if m else ""

data = urlencode({
    "login": USER, "password": APIKEY,
    "csrf_token": csrf, "db": login_db, "redirect": "/"
}).encode()

try:
    opener = build_opener(HTTPCookieProcessor(jar2))
    req = Request(BASE + "/web/login", data=data,
                  headers={"Content-Type": "application/x-www-form-urlencoded",
                           "User-Agent": "Mozilla/5.0"})
    resp = opener.open(req, timeout=25)
    final_url = resp.geturl()
    body = resp.read().decode(errors="replace")
    
    print(f"  db={login_db}")
    print(f"  final_url: {final_url}")
    
    if "/web" in final_url and "login" not in final_url:
        print("  >>> LOGIN OK! <<<")
        # Get session info
        payload = json.dumps({"jsonrpc": "2.0", "id": 2, "params": {}}).encode()
        req = Request(BASE + "/web/session/get_session_info", data=payload,
                      headers={"Content-Type": "application/json"})
        resp = opener.open(req, timeout=20)
        info = json.loads(resp.read().decode()).get("result", {})
        for k in ["uid", "db", "username", "is_admin", "is_system", "company_id",
                   "server_version", "user_context"]:
            print(f"  {k}: {info.get(k)}")
    else:
        # Check error  
        alerts = re.findall(r'class="alert[^"]*"[^>]*>(.*?)</div>', body, re.DOTALL)
        for a in alerts:
            clean = re.sub(r'<[^>]+>', '', a).strip()
            if clean:
                print(f"  Alert: {clean[:200]}")
        
        if "Wrong" not in body and "incorrecto" not in body.lower():
            print(f"  body[:500]: {body[:500]}")

except Exception as e:
    print(f"  Error: {e}")

print("\nDone")
"""

print(f"[*] Connecting to VPS {VPS_IP}...")
client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(VPS_IP, username="root", password=VPS_PW, timeout=10,
               look_for_keys=False, allow_agent=False)

sftp = client.open_sftp()
with sftp.open("/tmp/r2cap_db.py", "w") as f:
    f.write(REMOTE_SCRIPT)
sftp.close()

print(f"[+] Executing...")
stdin, stdout, stderr = client.exec_command("python3 /tmp/r2cap_db.py", timeout=120)
print(stdout.read().decode(errors="replace"))
err = stderr.read().decode(errors="replace")
if err:
    print(f"STDERR: {err[:1500]}")

client.exec_command("rm -f /tmp/r2cap_db.py")
client.close()
