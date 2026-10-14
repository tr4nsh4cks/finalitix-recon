"""R2 Capital - Check if we can create STP bank journal + payment method"""
import paramiko, json

VPS_IP = "82.27.100.115"
VPS_PW = "37W92I_Wd9581g5j1g1LzI"

REMOTE_SCRIPT = r"""
import json, sys, ssl
from urllib.request import Request, urlopen, build_opener, HTTPCookieProcessor
from urllib.parse import urlencode
from http.cookiejar import CookieJar
import re

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

BASE   = "https://r2-r2capital.odoo.com"
DB     = "adrianr2capital-r2capital-production-9575492"
USER   = "mmarron@madecconsultoria.com"
PASSW  = "OdooR2yPrh"
APIKEY = "9242f55eec6e9ffcb167ca16751f797a204eb604"
UID    = 31

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
        return {"_err": r["error"].get("data", {}).get("message", str(r["error"]))[:500]}
    return r.get("result")

print("=" * 60)
print("R2 CAPITAL - STP METHOD REGISTRATION TEST")
print("=" * 60)

# 1. Check our groups (what permissions do we have?)
print("\n[1] Our permission groups...")
try:
    r = obj_exec("res.users", "read", [[UID]], {"fields": ["groups_id"]})
    if isinstance(r, list) and r:
        group_ids = r[0].get("groups_id", [])
        groups = obj_exec("res.groups", "read", [group_ids], {"fields": ["full_name", "name"]})
        if isinstance(groups, list):
            print(f"  Total groups: {len(groups)}")
            for g in sorted(groups, key=lambda x: x.get("full_name", "")):
                print(f"  - {g.get('full_name')}")
except Exception as e:
    print(f"  Error: {e}")

# 2. Check if we can write to res.partner.bank (create bank account)
print("\n[2] Test: Can we CREATE a bank account?")
try:
    # Try creating a test STP bank account on company's partner
    # First get the partner_id of company 12 (R2 Capital)
    company = obj_exec("res.company", "read", [[12]], {"fields": ["partner_id"]})
    if isinstance(company, list) and company:
        partner_id = company[0].get("partner_id", [None])[0]
        print(f"  Company 12 partner_id: {partner_id}")
    
    # Try a dry-run: check_access_rights
    access = obj_exec("res.partner.bank", "check_access_rights", ["create"], {"raise_exception": False})
    print(f"  CREATE access on res.partner.bank: {access}")
    
    access_w = obj_exec("res.partner.bank", "check_access_rights", ["write"], {"raise_exception": False})
    print(f"  WRITE access on res.partner.bank: {access_w}")
except Exception as e:
    print(f"  Error: {e}")

# 3. Check if we can create/write account.journal
print("\n[3] Test: Can we CREATE/WRITE account.journal?")
try:
    access_c = obj_exec("account.journal", "check_access_rights", ["create"], {"raise_exception": False})
    print(f"  CREATE access on account.journal: {access_c}")
    
    access_w = obj_exec("account.journal", "check_access_rights", ["write"], {"raise_exception": False})
    print(f"  WRITE access on account.journal: {access_w}")
except Exception as e:
    print(f"  Error: {e}")

# 4. Check payment permissions
print("\n[4] Test: Can we CREATE account.payment?")
try:
    access = obj_exec("account.payment", "check_access_rights", ["create"], {"raise_exception": False})
    print(f"  CREATE access on account.payment: {access}")
    
    access_w = obj_exec("account.payment", "check_access_rights", ["write"], {"raise_exception": False})
    print(f"  WRITE access on account.payment: {access_w}")
except Exception as e:
    print(f"  Error: {e}")

# 5. Check res.company write access
print("\n[5] Test: Can we WRITE res.company?")
try:
    access = obj_exec("res.company", "check_access_rights", ["write"], {"raise_exception": False})
    print(f"  WRITE access on res.company: {access}")
except Exception as e:
    print(f"  Error: {e}")

# 6. Check ir.module.module install permissions
print("\n[6] Test: Can we INSTALL modules?")
try:
    access = obj_exec("ir.module.module", "check_access_rights", ["write"], {"raise_exception": False})
    print(f"  WRITE access on ir.module.module: {access}")
except Exception as e:
    print(f"  Error: {e}")

# 7. Check existing payment methods
print("\n[7] Existing payment methods...")
try:
    r = obj_exec("account.payment.method", "search_read", [[]],
                  {"fields": ["name", "code", "payment_type"], "limit": 50})
    if isinstance(r, list):
        for m in r:
            print(f"  [{m['id']}] {m.get('name')} | code={m.get('code')} | type={m.get('payment_type')}")
    else:
        print(f"  {r}")
except Exception as e:
    print(f"  Error: {e}")

# 8. Check payment method lines (link between journal and payment method)
print("\n[8] Payment method lines on bank journals...")
try:
    r = obj_exec("account.payment.method.line", "search_read", [[]],
                  {"fields": ["name", "payment_method_id", "journal_id", "payment_type"],
                   "limit": 50})
    if isinstance(r, list):
        print(f"  Count: {len(r)}")
        for m in r[:20]:
            print(f"  [{m['id']}] {m.get('name')} | method={m.get('payment_method_id')} | journal={m.get('journal_id')} | type={m.get('payment_type')}")
    else:
        print(f"  {r}")
except Exception as e:
    print(f"  Error: {e}")

# 9. If we CAN create, try creating a bank account with STP CLABE
print("\n[9] Attempt: Create STP bank account (Multiplica)...")
try:
    # Find STP bank ID
    stp_bank = obj_exec("res.bank", "search_read", [[["name", "ilike", "STP"]]],
                         {"fields": ["name", "bic"], "limit": 5})
    print(f"  STP banks: {stp_bank}")
    
    stp_bank_id = None
    if isinstance(stp_bank, list) and stp_bank:
        stp_bank_id = stp_bank[0]["id"]
    
    if stp_bank_id:
        # Try to create
        result = obj_exec("res.partner.bank", "create", [{
            "acc_number": "646180234500000003",
            "bank_id": stp_bank_id,
            "partner_id": partner_id if 'partner_id' in dir() else 15449,
            "l10n_mx_edi_clabe": "646180234500000003",
            "acc_holder_name": "MULTIPLICA MEX",
        }])
        if isinstance(result, dict) and "_err" in result:
            print(f"  CREATE FAILED: {result['_err'][:300]}")
        else:
            print(f"  >>> CREATED! Bank account ID: {result} <<<")
    else:
        print("  No STP bank found in catalog")
except Exception as e:
    print(f"  Error: {e}")

# 10. Check if there are any payment provider / acquirer models
print("\n[10] Payment providers/acquirers...")
try:
    r = obj_exec("payment.provider", "search_read", [[]],
                  {"fields": ["name", "code", "state", "company_id"], "limit": 20})
    if isinstance(r, list):
        for p in r:
            print(f"  [{p['id']}] {p.get('name')} | code={p.get('code')} | state={p.get('state')}")
    elif isinstance(r, dict) and "_err" in r:
        print(f"  Model not found: {r['_err'][:200]}")
    else:
        print(f"  {r}")
except Exception as e:
    print(f"  Error: {e}")

# 11. List ALL models with "payment" in name
print("\n[11] All payment-related models...")
try:
    r = obj_exec("ir.model", "search_read",
                  [[["model", "ilike", "payment"]]],
                  {"fields": ["model", "name"], "limit": 30})
    if isinstance(r, list):
        for m in r:
            print(f"  {m.get('model')} -> {m.get('name')}")
except Exception as e:
    print(f"  Error: {e}")

print("\nDone")
"""

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(VPS_IP, username="root", password=VPS_PW, timeout=10,
               look_for_keys=False, allow_agent=False)

sftp = client.open_sftp()
with sftp.open("/tmp/r2cap_stpc.py", "w") as f:
    f.write(REMOTE_SCRIPT)
sftp.close()

print("[+] Executing on VPS...")
stdin, stdout, stderr = client.exec_command("python3 /tmp/r2cap_stpc.py", timeout=120)
print(stdout.read().decode(errors="replace"))
err = stderr.read().decode(errors="replace")
if err:
    print(f"STDERR: {err[:1500]}")

client.exec_command("rm -f /tmp/r2cap_stpc.py")
client.close()
