"""R2 Capital - Login with real password + enumerate everything"""
import paramiko

VPS_IP = "82.27.100.115"
VPS_PW = "37W92I_Wd9581g5j1g1LzI"

REMOTE_SCRIPT = r"""
import json, sys, ssl, re
from urllib.request import Request, urlopen, build_opener, HTTPCookieProcessor
from urllib.parse import urlencode
from http.cookiejar import CookieJar

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

BASE   = "https://r2-r2capital.odoo.com"
USER   = "mmarron@madecconsultoria.com"
PASSW  = "OdooR2yPrh"
APIKEY = "9242f55eec6e9ffcb167ca16751f797a204eb604"

def post_json(url, data, jar=None):
    opener = build_opener(HTTPCookieProcessor(jar)) if jar else build_opener()
    payload = json.dumps(data).encode()
    req = Request(url, data=payload,
                  headers={"Content-Type": "application/json",
                           "User-Agent": "Mozilla/5.0"})
    resp = opener.open(req, timeout=30)
    return json.loads(resp.read().decode())

print("=" * 60)
print("R2 CAPITAL TECHNOLOGIES MX")
print(f"Target: {BASE}")
print("=" * 60)

# ===== WEB LOGIN =====
print("\n[1] Web login...")
jar = CookieJar()
opener = build_opener(HTTPCookieProcessor(jar))

req = Request(BASE + "/web/login", headers={"User-Agent": "Mozilla/5.0"})
resp = opener.open(req, timeout=20)
html = resp.read().decode(errors="replace")
m = re.search(r'name="csrf_token"\s+value="([^"]+)"', html)
csrf = m.group(1) if m else ""

data = urlencode({
    "login": USER, "password": PASSW,
    "csrf_token": csrf, "redirect": "",
}).encode()

req = Request(BASE + "/web/login", data=data,
              headers={"Content-Type": "application/x-www-form-urlencoded",
                       "User-Agent": "Mozilla/5.0"})
resp = opener.open(req, timeout=25)
final_url = resp.geturl()

if "/web" in final_url and "login" not in final_url:
    print(f"  >>> LOGIN OK! -> {final_url}")
else:
    body = resp.read().decode(errors="replace")
    if "Wrong" in body:
        print("  Wrong login/password with real password")
    print(f"  URL: {final_url}")
    # Try /web/session/authenticate
    print("\n  Trying /web/session/authenticate...")
    try:
        r = post_json(BASE + "/web/session/authenticate", {
            "jsonrpc": "2.0", "id": 1,
            "params": {"db": "", "login": USER, "password": PASSW}
        }, jar=jar)
        result = r.get("result", {})
        if result.get("uid"):
            print(f"  >>> AUTH OK via session/authenticate! <<<")
            final_url = BASE + "/web"
        else:
            print(f"  Result: {json.dumps(result)[:300]}")
    except Exception as e:
        print(f"  Error: {e}")

# Get session info
print("\n[2] Session info...")
try:
    r = post_json(BASE + "/web/session/get_session_info", {
        "jsonrpc": "2.0", "id": 1, "params": {}
    }, jar=jar)
    info = r.get("result", {})
    uid = info.get("uid")
    db = info.get("db")
    
    print(f"  UID: {uid}")
    print(f"  DB: {db}")
    print(f"  Username: {info.get('username')}")
    print(f"  Name: {info.get('name')}")
    print(f"  Is admin: {info.get('is_admin')}")
    print(f"  Is system: {info.get('is_system')}")
    print(f"  Company: {info.get('company_id')}")
    print(f"  User companies: {info.get('user_companies')}")
    print(f"  Server version: {info.get('server_version')}")
    print(f"  User context: {info.get('user_context')}")
except Exception as e:
    print(f"  Error: {e}")
    uid = None
    db = None

if not uid or not db:
    print("\n[!] Web login failed. Trying JSON-RPC with API key...")
    # Try /web/session/authenticate with apikey
    jar2 = CookieJar()
    try:
        r = post_json(BASE + "/web/session/authenticate", {
            "jsonrpc": "2.0", "id": 1,
            "params": {"db": "", "login": USER, "password": APIKEY}
        }, jar=jar2)
        result = r.get("result", {})
        if result.get("uid"):
            uid = result.get("uid")
            db = result.get("db")
            jar = jar2
            print(f"  >>> AUTH OK with API key! UID={uid} DB={db} <<<")
    except Exception as e:
        print(f"  Error: {e}")

if not uid or not db:
    print("\n[!] All auth methods failed.")
    sys.exit(1)

print(f"\n{'='*60}")
print(f"AUTHENTICATED! UID={uid} DB={db}")
print(f"{'='*60}")

# Helper for ORM calls via web session
def call_kw(model, method, args=None, kwargs=None):
    r = post_json(BASE + "/web/dataset/call_kw", {
        "jsonrpc": "2.0", "id": 1,
        "params": {
            "model": model, "method": method,
            "args": args if args is not None else [[]],
            "kwargs": kwargs or {}
        }
    }, jar=jar)
    if "error" in r:
        emsg = r["error"].get("data", {}).get("message", str(r["error"]))
        return {"_err": emsg[:500]}
    return r.get("result")

# Also test JSON-RPC with discovered DB
def obj_exec(model, method, args=None, kwargs=None):
    payload = json.dumps({
        "jsonrpc": "2.0", "id": 1, "method": "call",
        "params": {"service": "object", "method": "execute_kw",
                   "args": [db, uid, APIKEY, model, method,
                            args if args is not None else [[]],
                            kwargs or {}]}
    }).encode()
    req = Request(BASE + "/jsonrpc", data=payload,
                  headers={"Content-Type": "application/json"})
    resp = urlopen(req, timeout=25, context=ctx)
    r = json.loads(resp.read().decode())
    if "error" in r:
        return {"_err": r["error"].get("data", {}).get("message", str(r["error"]))[:500]}
    return r.get("result")

# ===== ENUMERATE =====

# A. Current user
print("\n[A] Current user...")
try:
    r = call_kw("res.users", "read", [[uid]],
                {"fields": ["name","login","email","groups_id","company_id","company_ids","partner_id"]})
    if isinstance(r, list):
        for u in r:
            print(f"  Name: {u.get('name')}")
            print(f"  Login: {u.get('login')}")
            print(f"  Email: {u.get('email')}")
            print(f"  Company: {u.get('company_id')}")
            print(f"  Companies: {u.get('company_ids')}")
            print(f"  Groups: {len(u.get('groups_id', []))} groups")
    else:
        print(f"  {r}")
except Exception as e:
    print(f"  Error: {e}")

# B. All users
print("\n[B] All users...")
try:
    r = call_kw("res.users", "search_read", [[]],
                {"fields": ["name","login","email","active"], "limit": 50})
    if isinstance(r, list):
        print(f"  Count: {len(r)}")
        for u in r:
            print(f"  [{u['id']}] {u.get('name')} | {u.get('login')} | active={u.get('active')}")
    else:
        print(f"  {r}")
except Exception as e:
    print(f"  Error: {e}")

# C. Companies
print("\n[C] Companies...")
try:
    r = call_kw("res.company", "search_read", [[]],
                {"fields": ["name","email","phone","vat","currency_id","street","city","country_id"], "limit": 20})
    if isinstance(r, list):
        for c in r:
            print(f"  [{c['id']}] {c.get('name')} | VAT={c.get('vat')} | {c.get('email')} | {c.get('phone')}")
            print(f"       {c.get('street')}, {c.get('city')}, {c.get('country_id')}")
    else:
        print(f"  {r}")
except Exception as e:
    print(f"  Error: {e}")

# D. Bank accounts
print("\n[D] Bank accounts...")
try:
    r = call_kw("res.partner.bank", "search_read", [[]],
                {"fields": ["acc_number","acc_holder_name","bank_id","partner_id","company_id"], "limit": 50})
    if isinstance(r, list):
        print(f"  Count: {len(r)}")
        for b in r:
            print(f"  [{b['id']}] {b.get('acc_number')} | holder={b.get('acc_holder_name')} | bank={b.get('bank_id')} | partner={b.get('partner_id')}")
    else:
        print(f"  {r}")
except Exception as e:
    print(f"  Error: {e}")

# E. Installed modules
print("\n[E] Installed modules...")
try:
    r = call_kw("ir.module.module", "search_read",
                [[["state","=","installed"]]],
                {"fields": ["name","shortdesc"], "limit": 100})
    if isinstance(r, list):
        print(f"  Installed: {len(r)}")
        for m in r:
            print(f"  - {m.get('name')}: {m.get('shortdesc')}")
    else:
        print(f"  {r}")
except Exception as e:
    print(f"  Error: {e}")

# F. Partners top 30
print("\n[F] Partners/Contacts (top 30)...")
try:
    r = call_kw("res.partner", "search_read", [[]],
                {"fields": ["name","email","phone","vat","is_company","company_type","street","city"], "limit": 30})
    if isinstance(r, list):
        total = call_kw("res.partner", "search_count", [[]])
        print(f"  Total partners: {total}")
        for p in r:
            print(f"  [{p['id']}] {p.get('name')} | {p.get('email')} | {p.get('phone')} | VAT={p.get('vat')} | company={p.get('is_company')}")
    else:
        print(f"  {r}")
except Exception as e:
    print(f"  Error: {e}")

# G. Invoices
print("\n[G] Recent invoices (top 15)...")
try:
    r = call_kw("account.move", "search_read",
                [[["move_type","in",["out_invoice","in_invoice"]]]],
                {"fields": ["name","partner_id","amount_total","state","invoice_date","currency_id","move_type"],
                 "limit": 15, "order": "id desc"})
    if isinstance(r, list):
        total = call_kw("account.move", "search_count", [[]])
        print(f"  Total journal entries: {total}")
        print(f"  Invoices shown: {len(r)}")
        for i in r:
            t = "OUT" if i.get("move_type") == "out_invoice" else "IN"
            print(f"  [{i['id']}] {i.get('name')} | {t} | {i.get('partner_id')} | ${i.get('amount_total')} | {i.get('state')} | {i.get('invoice_date')}")
    else:
        print(f"  {r}")
except Exception as e:
    print(f"  Error: {e}")

# H. HR Employees
print("\n[H] Employees...")
try:
    r = call_kw("hr.employee", "search_read", [[]],
                {"fields": ["name","work_email","department_id","job_title","work_phone"], "limit": 50})
    if isinstance(r, list):
        print(f"  Count: {len(r)}")
        for e in r:
            print(f"  [{e['id']}] {e.get('name')} | {e.get('work_email')} | {e.get('job_title')} | dept={e.get('department_id')}")
    elif isinstance(r, dict) and "_err" in r:
        print(f"  Module not installed: {r['_err'][:200]}")
    else:
        print(f"  {r}")
except Exception as e:
    print(f"  Error: {e}")

# I. Payment / accounting journals
print("\n[I] Account journals...")
try:
    r = call_kw("account.journal", "search_read", [[]],
                {"fields": ["name","type","code","bank_account_id","company_id"], "limit": 20})
    if isinstance(r, list):
        for j in r:
            print(f"  [{j['id']}] {j.get('name')} | type={j.get('type')} | code={j.get('code')} | bank={j.get('bank_account_id')}")
    else:
        print(f"  {r}")
except Exception as e:
    print(f"  Error: {e}")

# J. Payments
print("\n[J] Recent payments (top 10)...")
try:
    r = call_kw("account.payment", "search_read", [[]],
                {"fields": ["name","partner_id","amount","state","date","payment_type","journal_id"],
                 "limit": 10, "order": "id desc"})
    if isinstance(r, list):
        total = call_kw("account.payment", "search_count", [[]])
        print(f"  Total payments: {total}")
        for p in r:
            print(f"  [{p['id']}] {p.get('name')} | {p.get('payment_type')} | {p.get('partner_id')} | ${p.get('amount')} | {p.get('state')}")
    else:
        print(f"  {r}")
except Exception as e:
    print(f"  Error: {e}")

# K. Test JSON-RPC with API key + discovered DB
print(f"\n[K] JSON-RPC API key test (db={db})...")
try:
    r = obj_exec("res.users", "read", [[uid]], {"fields": ["name","login"]})
    if isinstance(r, list):
        print(f"  API key works! User: {r[0].get('name')}")
    elif isinstance(r, dict) and "_err" in r:
        print(f"  API key error: {r['_err'][:300]}")
    else:
        print(f"  {r}")
except Exception as e:
    print(f"  Error: {e}")

print("\nDone")
"""

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(VPS_IP, username="root", password=VPS_PW, timeout=10,
               look_for_keys=False, allow_agent=False)

sftp = client.open_sftp()
with sftp.open("/tmp/r2cap_go.py", "w") as f:
    f.write(REMOTE_SCRIPT)
sftp.close()

print("[+] Executing on VPS...")
stdin, stdout, stderr = client.exec_command("python3 /tmp/r2cap_go.py", timeout=300)
print(stdout.read().decode(errors="replace"))
err = stderr.read().decode(errors="replace")
if err:
    print(f"STDERR: {err[:2000]}")

client.exec_command("rm -f /tmp/r2cap_go.py")
client.close()
