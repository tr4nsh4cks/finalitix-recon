"""Upload and run R2 Capital Odoo test on VPS via paramiko SFTP"""
import paramiko, sys, os, tempfile

VPS_IP = "82.27.100.115"
VPS_PW = "37W92I_Wd9581g5j1g1LzI"

REMOTE_SCRIPT = """
import json, sys, ssl, re, socket
try:
    from urllib.request import Request, urlopen, build_opener, HTTPCookieProcessor
    from urllib.error import URLError, HTTPError
    from urllib.parse import urlencode
    from http.cookiejar import CookieJar
except ImportError:
    print("Python 3 required")
    sys.exit(1)

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

BASE   = "https://r2-r2capital.odoo.com"
USER   = "mmarron@madecconsultoria.com"
APIKEY = "9242f55eec6e9ffcb167ca16751f797a204eb604"

def rpc(service, method, args):
    payload = json.dumps({
        "jsonrpc": "2.0", "id": 1, "method": "call",
        "params": {"service": service, "method": method, "args": args}
    }).encode()
    req = Request(BASE + "/jsonrpc", data=payload,
                  headers={"Content-Type": "application/json"})
    resp = urlopen(req, timeout=25, context=ctx)
    return json.loads(resp.read().decode())

def obj_exec(db, uid, model, method, args=None, kwargs=None):
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

print("=" * 60)
print("R2 CAPITAL TECHNOLOGIES MX - Odoo SaaS")
print("Target: " + BASE)
print("=" * 60)

# 1. DNS + Version
print()
print("[1] DNS + Version...")
try:
    ip = socket.gethostbyname("r2-r2capital.odoo.com")
    print("    IP: " + ip)
except:
    print("    DNS failed")

try:
    v = rpc("common", "version", [])
    ver = v.get("result", {})
    print("    Server version: " + str(ver.get("server_version", "?")))
    print("    Protocol: " + str(ver.get("protocol_version", "?")))
except Exception as e:
    print("    Version error: " + str(e))

# 2. DB discovery
print()
print("[2] Database discovery...")
dbs = []
try:
    r = rpc("db", "list", [])
    dbs = r.get("result", [])
    print("    DB list: " + str(dbs))
except Exception as e:
    print("    db.list: " + str(e))

if not dbs:
    for db in ["r2-r2capital", "r2capital", "r2-r2capital-main", "r2_capital",
               "r2", "main", "production", "prod", "odoo"]:
        try:
            r = rpc("db", "db_exist", [db])
            if r.get("result"):
                print("    DB EXISTS: " + db)
                dbs.append(db)
        except:
            pass

# 3. Web login page analysis
print()
print("[3] Login page analysis...")
jar = CookieJar()
opener = build_opener(HTTPCookieProcessor(jar))
page_db = None
csrf = ""

try:
    req = Request(BASE + "/web/login", headers={"User-Agent": "Mozilla/5.0"})
    resp = opener.open(req, timeout=20)
    html = resp.read().decode(errors="replace")
    
    m = re.search(r'name="csrf_token"\\s+value="([^"]+)"', html)
    csrf = m.group(1) if m else ""
    
    m2 = re.search(r'name="db"\\s+value="([^"]+)"', html)
    if not m2:
        m2 = re.search(r'value="([^"]+)"[^>]*name="db"', html)
    page_db = m2.group(1) if m2 else ""
    
    if page_db:
        print("    DB from page: " + page_db)
        if page_db not in dbs:
            dbs.insert(0, page_db)
    
    # Check for DB selector
    db_options = re.findall(r'<option[^>]*value="([^"]+)"', html)
    if db_options:
        print("    DB options: " + str(db_options))
        for d in db_options:
            if d not in dbs:
                dbs.append(d)
    
    # Hidden inputs
    hiddens = re.findall(r'<input[^>]*type="hidden"[^>]*name="([^"]+)"[^>]*value="([^"]*)"', html)
    for name, val in hiddens:
        if name != "csrf_token":
            print("    Hidden: " + name + " = " + val[:60])
    
    print("    CSRF: " + csrf[:30] + "...")
    
except Exception as e:
    print("    Error: " + str(e))

# 4. JSON-RPC Auth
print()
print("[4] JSON-RPC authenticate...")
uid = None
working_db = None

for db in dbs:
    try:
        r = rpc("common", "login", [db, USER, APIKEY])
        result = r.get("result")
        err = r.get("error")
        if result and result is not False and result != 0:
            print("    >>> HIT! db=" + db + " UID=" + str(result) + " <<<")
            uid = result
            working_db = db
            break
        elif err:
            emsg = str(err.get("data", {}).get("message", err))[:150]
            print("    db=" + db + " error: " + emsg)
        else:
            print("    db=" + db + " -> False")
    except Exception as e:
        print("    db=" + db + " -> " + str(e))

# 5. Web Login
if not uid:
    print()
    print("[5] Web login attempt...")
    login_db = page_db or (dbs[0] if dbs else "r2-r2capital")
    try:
        data = urlencode({
            "login": USER, "password": APIKEY,
            "csrf_token": csrf, "db": login_db, "redirect": "/"
        }).encode()
        req = Request(BASE + "/web/login", data=data,
                      headers={"Content-Type": "application/x-www-form-urlencoded",
                               "User-Agent": "Mozilla/5.0"})
        resp = opener.open(req, timeout=25)
        final_url = resp.geturl()
        body = resp.read().decode(errors="replace")
        
        if "/web" in final_url and "login" not in final_url:
            print("    >>> WEB LOGIN OK! -> " + final_url + " <<<")
            for cookie in jar:
                if cookie.name == "session_id":
                    print("    session_id: " + cookie.value[:30] + "...")
            
            # Get session info
            payload = json.dumps({"jsonrpc": "2.0", "id": 2, "params": {}}).encode()
            req = Request(BASE + "/web/session/get_session_info", data=payload,
                          headers={"Content-Type": "application/json"})
            resp = opener.open(req, timeout=20)
            info = json.loads(resp.read().decode()).get("result", {})
            uid = info.get("uid")
            working_db = info.get("db")
            print("    UID: " + str(uid))
            print("    DB: " + str(working_db))
            print("    Username: " + str(info.get("username")))
            print("    Is admin: " + str(info.get("is_admin")))
            print("    Is system: " + str(info.get("is_system")))
            print("    Company: " + str(info.get("company_id")))
            print("    Version: " + str(info.get("server_version")))
        else:
            if "Wrong" in body or "incorrecto" in body.lower() or "Invalid" in body:
                print("    Wrong login/password")
            else:
                print("    final_url: " + final_url)
                print("    body[:400]: " + body[:400])
    except Exception as e:
        print("    Error: " + str(e))

# 6. If auth OK, enumerate
if uid and working_db:
    print()
    print("=" * 60)
    print("[6] AUTHENTICATED UID=" + str(uid) + " DB=" + working_db)
    print("=" * 60)
    
    # 6a. Current user
    print()
    print("[6a] Current user...")
    try:
        r = obj_exec(working_db, uid, "res.users", "read", [[uid]],
                      {"fields": ["name","login","email","groups_id","company_id","company_ids"]})
        for u in r.get("result", []):
            print("    Name: " + str(u.get("name")))
            print("    Login: " + str(u.get("login")))
            print("    Email: " + str(u.get("email")))
            print("    Company: " + str(u.get("company_id")))
            print("    Companies: " + str(u.get("company_ids")))
            print("    Groups count: " + str(len(u.get("groups_id", []))))
    except Exception as e:
        print("    " + str(e))
    
    # 6b. All users
    print()
    print("[6b] All users...")
    try:
        r = obj_exec(working_db, uid, "res.users", "search_read", [[]],
                      {"fields": ["name","login","email","active"], "limit": 50})
        users = r.get("result", [])
        print("    Total: " + str(len(users)))
        for u in users:
            line = "    [%s] %s | %s | %s | active=%s" % (
                u.get("id"), u.get("name"), u.get("login"), u.get("email"), u.get("active"))
            print(line)
    except Exception as e:
        print("    " + str(e))
    
    # 6c. Companies
    print()
    print("[6c] Companies...")
    try:
        r = obj_exec(working_db, uid, "res.company", "search_read", [[]],
                      {"fields": ["name","email","phone","vat","currency_id","country_id"], "limit": 20})
        for c in r.get("result", []):
            print("    [%s] %s | %s | %s | VAT=%s" % (
                c.get("id"), c.get("name"), c.get("email"), c.get("phone"), c.get("vat")))
    except Exception as e:
        print("    " + str(e))
    
    # 6d. Bank accounts
    print()
    print("[6d] Bank accounts...")
    try:
        r = obj_exec(working_db, uid, "res.partner.bank", "search_read", [[]],
                      {"fields": ["acc_number","bank_id","partner_id","company_id"], "limit": 50})
        banks = r.get("result", [])
        print("    Total: " + str(len(banks)))
        for b in banks:
            print("    [%s] %s | bank=%s | partner=%s" % (
                b.get("id"), b.get("acc_number"), b.get("bank_id"), b.get("partner_id")))
    except Exception as e:
        print("    " + str(e))
    
    # 6e. Installed modules
    print()
    print("[6e] Installed modules...")
    try:
        r = obj_exec(working_db, uid, "ir.module.module", "search_read",
                      [[["state","=","installed"]]],
                      {"fields": ["name","shortdesc"], "limit": 100})
        mods = r.get("result", [])
        print("    Total installed: " + str(len(mods)))
        for m in mods:
            print("    - " + str(m.get("name")) + ": " + str(m.get("shortdesc")))
    except Exception as e:
        print("    " + str(e))
    
    # 6f. Partners
    print()
    print("[6f] Partners/Contacts (top 20)...")
    try:
        r = obj_exec(working_db, uid, "res.partner", "search_read", [[]],
                      {"fields": ["name","email","phone","vat","is_company"], "limit": 20})
        for p in r.get("result", []):
            print("    [%s] %s | %s | %s | VAT=%s" % (
                p.get("id"), p.get("name"), p.get("email"), p.get("phone"), p.get("vat")))
    except Exception as e:
        print("    " + str(e))
    
    # 6g. Invoices
    print()
    print("[6g] Recent invoices (top 10)...")
    try:
        r = obj_exec(working_db, uid, "account.move", "search_read",
                      [[["move_type","in",["out_invoice","in_invoice"]]]],
                      {"fields": ["name","partner_id","amount_total","state","invoice_date"],
                       "limit": 10, "order": "id desc"})
        for inv in r.get("result", []):
            print("    [%s] %s | %s | $%s | %s | %s" % (
                inv.get("id"), inv.get("name"), inv.get("partner_id"),
                inv.get("amount_total"), inv.get("state"), inv.get("invoice_date")))
    except Exception as e:
        print("    " + str(e))

print()
print("Done")
"""

print(f"[*] Connecting to VPS {VPS_IP}...")
client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(VPS_IP, username="root", password=VPS_PW, timeout=10,
               look_for_keys=False, allow_agent=False)
print(f"[+] Connected! Uploading script...")

# Upload via SFTP
sftp = client.open_sftp()
remote_path = "/tmp/r2cap_test.py"

with sftp.open(remote_path, "w") as f:
    f.write(REMOTE_SCRIPT)
sftp.close()

print(f"[+] Script uploaded. Executing...")
stdin, stdout, stderr = client.exec_command(f"python3 {remote_path}", timeout=180)
out = stdout.read().decode(errors="replace")
err = stderr.read().decode(errors="replace")

print(out)
if err:
    print(f"STDERR: {err[:2000]}")

# Cleanup
client.exec_command(f"rm -f {remote_path}")
client.close()
