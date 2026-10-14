"""R2 Capital - Find all STP accounts and CLABE details"""
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
        return {"_err": r["error"].get("data", {}).get("message", str(r["error"]))[:500]}
    return r.get("result")

print("=" * 60)
print("R2 CAPITAL — STP ACCOUNTS & CLABEs")
print("=" * 60)

# 1. All bank accounts where bank name contains STP
print("\n[1] Bank accounts with STP...")
try:
    r = obj_exec("res.partner.bank", "search_read",
                  [["|", "|", "|",
                    ["bank_id.name", "ilike", "stp"],
                    ["bank_id.name", "ilike", "sistema de transferencias"],
                    ["acc_number", "like", "6461"],
                    ["acc_number", "like", "6468"]]],
                  {"fields": ["acc_number", "acc_holder_name", "bank_id", "partner_id",
                              "company_id", "acc_type", "l10n_mx_edi_clabe"],
                   "limit": 100})
    if isinstance(r, list):
        print(f"  Found: {len(r)}")
        for b in r:
            print(f"  [{b['id']}] acc={b.get('acc_number')} | clabe={b.get('l10n_mx_edi_clabe')} | holder={b.get('acc_holder_name')} | bank={b.get('bank_id')} | partner={b.get('partner_id')} | company={b.get('company_id')}")
    else:
        print(f"  {r}")
except Exception as e:
    print(f"  Error: {e}")

# 2. All bank accounts with CLABE pattern (646xxx = STP)
print("\n[2] All accounts with CLABE field populated...")
try:
    r = obj_exec("res.partner.bank", "search_read",
                  [[["l10n_mx_edi_clabe", "!=", False]]],
                  {"fields": ["acc_number", "l10n_mx_edi_clabe", "bank_id", "partner_id", "company_id"],
                   "limit": 200})
    if isinstance(r, list):
        print(f"  Found: {len(r)}")
        for b in r:
            clabe = b.get("l10n_mx_edi_clabe", "")
            stp = " <<< STP" if str(clabe).startswith("646") else ""
            print(f"  [{b['id']}] clabe={clabe}{stp} | acc={b.get('acc_number')} | bank={b.get('bank_id')} | partner={b.get('partner_id')}")
    else:
        print(f"  {r}")
except Exception as e:
    print(f"  Error: {e}")

# 3. ALL bank accounts (complete dump) — look for 646 patterns
print("\n[3] Full bank account dump (looking for STP/646 CLABEs)...")
try:
    r = obj_exec("res.partner.bank", "search_read", [[]],
                  {"fields": ["acc_number", "acc_holder_name", "bank_id", "partner_id",
                              "company_id", "l10n_mx_edi_clabe", "acc_type"],
                   "limit": 500})
    if isinstance(r, list):
        print(f"  Total bank accounts: {len(r)}")
        stp_accounts = []
        clabe_accounts = []
        for b in r:
            acc = str(b.get("acc_number", ""))
            clabe = str(b.get("l10n_mx_edi_clabe", "") or "")
            bank_name = str(b.get("bank_id", ""))
            
            is_stp = ("STP" in bank_name.upper() or 
                      acc.startswith("646") or 
                      clabe.startswith("646"))
            
            if is_stp:
                stp_accounts.append(b)
            if clabe and clabe != "False":
                clabe_accounts.append(b)
        
        print(f"\n  STP accounts: {len(stp_accounts)}")
        for b in stp_accounts:
            print(f"  [{b['id']}] acc={b.get('acc_number')} | clabe={b.get('l10n_mx_edi_clabe')} | bank={b.get('bank_id')} | partner={b.get('partner_id')} | company={b.get('company_id')} | holder={b.get('acc_holder_name')}")
        
        print(f"\n  Accounts with CLABE: {len(clabe_accounts)}")
        for b in clabe_accounts:
            stp_flag = " <<< STP" if str(b.get('l10n_mx_edi_clabe','')).startswith('646') else ""
            print(f"  [{b['id']}] clabe={b.get('l10n_mx_edi_clabe')}{stp_flag} | acc={b.get('acc_number')} | bank={b.get('bank_id')} | partner={b.get('partner_id')}")
    else:
        print(f"  {r}")
except Exception as e:
    print(f"  Error: {e}")

# 4. Check for STP-specific models
print("\n[4] STP-specific models...")
stp_models = ["stp.transferencia", "vor.stp.transferencia", "l10n_mx_edi.payment",
               "stp.account", "stp.config", "stp.payment", "account.stp"]
for model in stp_models:
    try:
        r = obj_exec("ir.model", "search_read",
                      [[["model", "=", model]]],
                      {"fields": ["name", "model", "state"]})
        if r and isinstance(r, list) and len(r) > 0:
            print(f"  FOUND: {model} -> {r[0].get('name')}")
        else:
            pass
    except:
        pass

# 5. Search models containing "stp" 
print("\n[5] All models containing 'stp'...")
try:
    r = obj_exec("ir.model", "search_read",
                  [[["model", "ilike", "stp"]]],
                  {"fields": ["name", "model", "state"], "limit": 50})
    if isinstance(r, list) and r:
        for m in r:
            print(f"  {m.get('model')} -> {m.get('name')} (state={m.get('state')})")
    else:
        print("  No STP models found")
except Exception as e:
    print(f"  Error: {e}")

# 6. Company STP config fields
print("\n[6] Company details (STP fields)...")
try:
    # Get all fields of res.company
    r = obj_exec("ir.model.fields", "search_read",
                  [[["model", "=", "res.company"], 
                    "|", "|", "|",
                    ["name", "ilike", "stp"],
                    ["name", "ilike", "clabe"],
                    ["name", "ilike", "spei"],
                    ["name", "ilike", "transfer"]]],
                  {"fields": ["name", "field_description", "ttype"], "limit": 50})
    if isinstance(r, list) and r:
        print(f"  STP/SPEI fields in res.company:")
        for f in r:
            print(f"    {f.get('name')} ({f.get('ttype')}): {f.get('field_description')}")
        
        # Read those fields from company
        field_names = [f["name"] for f in r]
        companies = obj_exec("res.company", "read", [[2, 12]], {"fields": field_names})
        if isinstance(companies, list):
            for c in companies:
                print(f"\n  Company ID {c.get('id')}:")
                for k, v in c.items():
                    if k != "id" and v:
                        print(f"    {k} = {v}")
    else:
        print("  No STP fields in res.company")
except Exception as e:
    print(f"  Error: {e}")

# 7. Journals with STP bank
print("\n[7] Journals linked to STP banks...")
try:
    r = obj_exec("account.journal", "search_read", [[]],
                  {"fields": ["name", "type", "code", "bank_account_id", "bank_id",
                              "company_id", "l10n_mx_edi_payment_method_id"],
                   "limit": 50})
    if isinstance(r, list):
        for j in r:
            bank_name = str(j.get("bank_id", ""))
            bank_acc = str(j.get("bank_account_id", ""))
            if "STP" in bank_name.upper() or "646" in bank_acc:
                print(f"  [{j['id']}] {j.get('name')} | {j.get('type')} | bank={j.get('bank_id')} | acc={j.get('bank_account_id')} | company={j.get('company_id')}")
    else:
        print(f"  {r}")
except Exception as e:
    print(f"  Error: {e}")

# 8. All bank accounts with acc starting with 6461 (STP CLABE prefix)
print("\n[8] Accounts with 6461/6468 in acc_number...")
try:
    r = obj_exec("res.partner.bank", "search_read",
                  [["|", ["acc_number", "like", "6461"], ["acc_number", "like", "6468"]]],
                  {"fields": ["acc_number", "acc_holder_name", "bank_id", "partner_id", "company_id"],
                   "limit": 100})
    if isinstance(r, list):
        print(f"  Found: {len(r)}")
        for b in r:
            print(f"  [{b['id']}] {b.get('acc_number')} | holder={b.get('acc_holder_name')} | bank={b.get('bank_id')} | partner={b.get('partner_id')} | company={b.get('company_id')}")
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
with sftp.open("/tmp/r2cap_stp.py", "w") as f:
    f.write(REMOTE_SCRIPT)
sftp.close()

print("[+] Executing on VPS...")
stdin, stdout, stderr = client.exec_command("python3 /tmp/r2cap_stp.py", timeout=120)
print(stdout.read().decode(errors="replace"))
err = stderr.read().decode(errors="replace")
if err:
    print(f"STDERR: {err[:1500]}")

client.exec_command("rm -f /tmp/r2cap_stp.py")
client.close()
