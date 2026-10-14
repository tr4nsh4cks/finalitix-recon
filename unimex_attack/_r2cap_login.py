"""R2 Capital - Web login WITHOUT db field (Odoo SaaS auto-detects)"""
import paramiko

VPS_IP = "82.27.100.115"
VPS_PW = "37W92I_Wd9581g5j1g1LzI"

REMOTE_SCRIPT = r"""
import json, sys, ssl, re
from urllib.request import Request, urlopen, build_opener, HTTPCookieProcessor, HTTPRedirectHandler
from urllib.parse import urlencode
from http.cookiejar import CookieJar

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

BASE   = "https://r2-r2capital.odoo.com"
USER   = "mmarron@madecconsultoria.com"
APIKEY = "9242f55eec6e9ffcb167ca16751f797a204eb604"

class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None

print("=" * 60)
print("R2 Capital - Odoo SaaS Web Login (no db field)")
print("=" * 60)

# 1. Get login page + CSRF
jar = CookieJar()
opener = build_opener(HTTPCookieProcessor(jar))

req = Request(BASE + "/web/login", headers={"User-Agent": "Mozilla/5.0"})
resp = opener.open(req, timeout=20)
html = resp.read().decode(errors="replace")

m = re.search(r'name="csrf_token"\s+value="([^"]+)"', html)
csrf = m.group(1) if m else ""
print(f"CSRF: {csrf[:30]}...")

# 2. Login WITHOUT db field
print("\n[1] POST /web/login (no db)...")
data = urlencode({
    "login": USER,
    "password": APIKEY,
    "csrf_token": csrf,
    "redirect": "",
}).encode()

req = Request(BASE + "/web/login", data=data,
              headers={"Content-Type": "application/x-www-form-urlencoded",
                       "User-Agent": "Mozilla/5.0"})
resp = opener.open(req, timeout=25)
final_url = resp.geturl()
body = resp.read().decode(errors="replace")

print(f"  Final URL: {final_url}")
print(f"  Status: 200 (followed redirect)")

# Check cookies
for cookie in jar:
    print(f"  Cookie: {cookie.name} = {cookie.value[:40]}...")

if "/web" in final_url and "login" not in final_url:
    print("\n  >>> LOGIN OK! <<<")
    
    # Session info
    payload = json.dumps({"jsonrpc": "2.0", "id": 2, "params": {}}).encode()
    req = Request(BASE + "/web/session/get_session_info", data=payload,
                  headers={"Content-Type": "application/json"})
    resp = opener.open(req, timeout=20)
    info = json.loads(resp.read().decode()).get("result", {})
    
    print(f"\n  UID: {info.get('uid')}")
    print(f"  DB: {info.get('db')}")
    print(f"  Username: {info.get('username')}")
    print(f"  Is admin: {info.get('is_admin')}")
    print(f"  Is system: {info.get('is_system')}")
    print(f"  Company: {info.get('company_id')}")
    print(f"  Server version: {info.get('server_version')}")
    print(f"  User companies: {info.get('user_companies')}")
    
    db = info.get("db")
    uid = info.get("uid")
    
    if uid and db:
        print(f"\n{'='*60}")
        print(f"AUTHENTICATED! UID={uid} DB={db}")
        print(f"{'='*60}")
        
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
            return json.loads(resp.read().decode())
        
        # Current user
        print("\n[A] Current user...")
        try:
            r = obj_exec("res.users", "read", [[uid]],
                          {"fields": ["name","login","email","groups_id","company_id","company_ids"]})
            for u in r.get("result", []):
                print(f"  Name: {u.get('name')}")
                print(f"  Login: {u.get('login')}")
                print(f"  Email: {u.get('email')}")
                print(f"  Company: {u.get('company_id')}")
                print(f"  Companies: {u.get('company_ids')}")
                print(f"  Groups: {len(u.get('groups_id', []))} groups")
        except Exception as e:
            print(f"  Error: {e}")
        
        # All users
        print("\n[B] All users...")
        try:
            r = obj_exec("res.users", "search_read", [[]],
                          {"fields": ["name","login","email","active"], "limit": 50})
            users = r.get("result", [])
            print(f"  Count: {len(users)}")
            for u in users:
                print(f"  [{u['id']}] {u.get('name')} | {u.get('login')} | active={u.get('active')}")
        except Exception as e:
            print(f"  Error: {e}")
        
        # Companies
        print("\n[C] Companies...")
        try:
            r = obj_exec("res.company", "search_read", [[]],
                          {"fields": ["name","email","phone","vat","currency_id"], "limit": 20})
            for c in r.get("result", []):
                print(f"  [{c['id']}] {c.get('name')} | {c.get('vat')} | {c.get('email')} | {c.get('phone')}")
        except Exception as e:
            print(f"  Error: {e}")
        
        # Bank accounts
        print("\n[D] Bank accounts...")
        try:
            r = obj_exec("res.partner.bank", "search_read", [[]],
                          {"fields": ["acc_number","bank_id","partner_id","company_id"], "limit": 50})
            banks = r.get("result", [])
            print(f"  Count: {len(banks)}")
            for b in banks:
                print(f"  [{b['id']}] {b.get('acc_number')} | bank={b.get('bank_id')} | partner={b.get('partner_id')}")
        except Exception as e:
            print(f"  Error: {e}")
        
        # Installed modules
        print("\n[E] Installed modules...")
        try:
            r = obj_exec("ir.module.module", "search_read",
                          [[["state","=","installed"]]],
                          {"fields": ["name","shortdesc"], "limit": 100})
            mods = r.get("result", [])
            print(f"  Installed: {len(mods)}")
            for m in mods:
                print(f"  - {m.get('name')}: {m.get('shortdesc')}")
        except Exception as e:
            print(f"  Error: {e}")
        
        # Partners (top 20)
        print("\n[F] Partners/Contacts (top 20)...")
        try:
            r = obj_exec("res.partner", "search_read", [[]],
                          {"fields": ["name","email","phone","vat","is_company","company_type"], "limit": 20})
            for p in r.get("result", []):
                print(f"  [{p['id']}] {p.get('name')} | {p.get('email')} | VAT={p.get('vat')} | company={p.get('is_company')}")
        except Exception as e:
            print(f"  Error: {e}")
        
        # Invoices
        print("\n[G] Recent invoices (top 10)...")
        try:
            r = obj_exec("account.move", "search_read",
                          [[["move_type","in",["out_invoice","in_invoice"]]]],
                          {"fields": ["name","partner_id","amount_total","state","invoice_date","currency_id"],
                           "limit": 10, "order": "id desc"})
            invs = r.get("result", [])
            print(f"  Count: {len(invs)}")
            for i in invs:
                print(f"  [{i['id']}] {i.get('name')} | {i.get('partner_id')} | ${i.get('amount_total')} | {i.get('state')}")
        except Exception as e:
            print(f"  Error: {e}")
        
        # Accounting / journal entries count
        print("\n[H] Journal entries count...")
        try:
            r = obj_exec("account.move", "search_count", [[]])
            print(f"  Total account.move: {r.get('result')}")
        except Exception as e:
            print(f"  Error: {e}")
        
        # HR employees
        print("\n[I] Employees...")
        try:
            r = obj_exec("hr.employee", "search_read", [[]],
                          {"fields": ["name","work_email","department_id","job_title"], "limit": 30})
            emps = r.get("result", [])
            print(f"  Count: {len(emps)}")
            for e in emps:
                print(f"  [{e['id']}] {e.get('name')} | {e.get('work_email')} | {e.get('department_id')} | {e.get('job_title')}")
        except Exception as e:
            print(f"  Error: {e}")

else:
    # Login failed - check why
    print("\n  Login page returned (not redirected to /web)")
    
    alerts = re.findall(r'class="alert[^"]*"[^>]*>(.*?)</div>', body, re.DOTALL)
    for a in alerts:
        clean = re.sub(r'<[^>]+>', '', a).strip()
        if clean:
            print(f"  Alert: {clean[:300]}")
    
    if "Wrong" in body:
        print("  >> Wrong login/password")
    elif "incorrect" in body.lower() or "incorrecto" in body.lower():
        print("  >> Invalid credentials")
    else:
        print(f"  body[:600]:")
        print(body[:600])

print("\nDone")
"""

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(VPS_IP, username="root", password=VPS_PW, timeout=10,
               look_for_keys=False, allow_agent=False)

sftp = client.open_sftp()
with sftp.open("/tmp/r2cap_login.py", "w") as f:
    f.write(REMOTE_SCRIPT)
sftp.close()

print("[+] Executing on VPS...")
stdin, stdout, stderr = client.exec_command("python3 /tmp/r2cap_login.py", timeout=180)
print(stdout.read().decode(errors="replace"))
err = stderr.read().decode(errors="replace")
if err:
    print(f"STDERR: {err[:2000]}")

client.exec_command("rm -f /tmp/r2cap_login.py")
client.close()
