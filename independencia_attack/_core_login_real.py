import paramiko, sys, time

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('64.177.88.10', username='root', password='5F.jyTK$D6%.F{a=', timeout=10)
print('Connected', flush=True)

SCRIPT = """
import requests, urllib3, json, sys, time, re
urllib3.disable_warnings()
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.6834.111 Safari/537.36"

BASE = "https://core.findep.mx"
s = requests.Session()
s.verify = False
s.headers.update({"User-Agent": UA, "Referer": BASE + "/core/index.jsp"})

# Step 1: GET login page + extract JSESSIONID
r = s.get(BASE + "/core/index.jsp", timeout=15)
sys.stdout.write("Login page: [" + str(r.status_code) + "] " + str(len(r.text)) + "b\\n")

# Extract jsessionid from form action
act_m = re.search(r'action="([^"]+)"', r.text)
action = act_m.group(1) if act_m else "/core/valida.do"
sys.stdout.write("Action: " + action + "\\n")

# Extract hidden fields
cve_idToken = ""
m = re.search(r'name="cve_idToken"\\s+value="([^"]*)"', r.text)
if m: cve_idToken = m.group(1)

msjPass = ""
m = re.search(r'name="msjPass"\\s+value="([^"]*)"', r.text)
if m: msjPass = m.group(1)

cveUsr = ""
m = re.search(r'name="cveUsr"\\s+value="([^"]*)"', r.text)
if m: cveUsr = m.group(1)

sys.stdout.write("cve_idToken=" + cve_idToken + " msjPass=" + msjPass + " cveUsr=" + cveUsr + "\\n")
sys.stdout.write("Cookies: " + str(dict(s.cookies)) + "\\n\\n")

# Step 2: POST with CORRECT field names
payload = {
    "cve_idToken": cve_idToken,
    "msjPass": msjPass,
    "cveUsr": cveUsr,
    "cve_usr": "afigueroac",
    "cve_psd": "afigueroac",
    "ok_btn": "Aceptar",
}

post_url = BASE + action
sys.stdout.write("POST " + post_url + "\\n")
sys.stdout.write("Payload: " + json.dumps(payload) + "\\n\\n")

r2 = s.post(post_url, data=payload, timeout=15, allow_redirects=True)
sys.stdout.write("Response: [" + str(r2.status_code) + "] " + str(len(r2.text)) + "b\\n")
sys.stdout.write("URL: " + str(r2.url) + "\\n")
sys.stdout.write("Cookies: " + str(dict(s.cookies)) + "\\n")

title = ""
tm = re.search(r'<title>(.*?)</title>', r2.text, re.I | re.S)
if tm: title = tm.group(1).strip()
sys.stdout.write("Title: " + title[:100] + "\\n\\n")

# Check if logged in
is_login = "cve_usr" in r2.text and "cve_psd" in r2.text
has_error = False
err_m = re.findall(r'(?:error|incorrecto|inv.lido|bloqueado|expirado|sesion)[^<]{0,100}', r2.text, re.I)
if err_m:
    has_error = True
    for em in err_m[:5]:
        sys.stdout.write("  ERROR: " + em.strip()[:100] + "\\n")

has_menu = "menu" in r2.text.lower() or "bienvenido" in r2.text.lower() or "inicio" in r2.text.lower()

if is_login and has_error:
    sys.stdout.write("\\n>>> STILL ON LOGIN PAGE (error message)\\n")
    # Extract the specific error
    alert_m = re.findall(r'<div[^>]*class="[^"]*(?:error|alert|mensaje)[^"]*"[^>]*>(.*?)</div>', r2.text, re.S | re.I)
    for am in alert_m:
        clean = re.sub(r'<[^>]+>', '', am).strip()
        if clean:
            sys.stdout.write("  Alert: " + clean[:200] + "\\n")
    
    # Also check msjPass hidden field for error
    m = re.search(r'name="msjPass"\\s+value="([^"]*)"', r2.text)
    if m and m.group(1):
        sys.stdout.write("  msjPass: " + m.group(1)[:200] + "\\n")
    
    # Check cveUsr hidden field
    m = re.search(r'name="cveUsr"\\s+value="([^"]*)"', r2.text)
    if m and m.group(1):
        sys.stdout.write("  cveUsr: " + m.group(1)[:200] + "\\n")
    
    # Extract ALL text content around error/message
    scripts = re.findall(r'<script[^>]*>(.*?)</script>', r2.text, re.S | re.I)
    for sc in scripts:
        if "alert" in sc or "error" in sc.lower() or "mensaje" in sc.lower():
            sys.stdout.write("  JS: " + sc.strip()[:300] + "\\n")

elif not is_login:
    sys.stdout.write("\\n>>> DIFFERENT PAGE — POSSIBLE LOGIN SUCCESS! <<<\\n")
    sys.stdout.write("First 1000 chars:\\n" + r2.text[:1000] + "\\n")
    
    # Save full response
    with open("/root/core_loggedin.html", "w") as f:
        f.write(r2.text)
    sys.stdout.write("\\nSaved to /root/core_loggedin.html\\n")
    
    # Try to navigate
    links = re.findall(r'href="([^"]+)"', r2.text)
    sys.stdout.write("\\nLinks found: " + str(len(links)) + "\\n")
    for l in links[:20]:
        sys.stdout.write("  " + l[:100] + "\\n")
    
    # Follow main/menu link
    for l in links:
        if "menu" in l.lower() or "main" in l.lower() or "home" in l.lower() or "inicio" in l.lower():
            try:
                full = l if l.startswith("http") else BASE + l
                r3 = s.get(full, timeout=10)
                sys.stdout.write("\\n  Follow " + full + ": [" + str(r3.status_code) + "] " + str(len(r3.text)) + "b\\n")
                sys.stdout.write("  " + r3.text[:500] + "\\n")
            except:
                pass
            break

sys.stdout.write("\\n\\n--- Response diff analysis ---\\n")
sys.stdout.write("Login page size: " + str(len(r.text)) + "b\\n")
sys.stdout.write("Post response size: " + str(len(r2.text)) + "b\\n")
sys.stdout.write("Size diff: " + str(len(r2.text) - len(r.text)) + "b\\n")

# Save for analysis
with open("/root/core_response.html", "w") as f:
    f.write(r2.text)
sys.stdout.write("Saved response to /root/core_response.html\\n")

sys.stdout.write("\\n=== DONE ===\\n")
"""

sftp = ssh.open_sftp()
with sftp.open('/root/core_login_real.py', 'w') as f:
    f.write(SCRIPT)
sftp.close()
print('Uploaded', flush=True)

transport = ssh.get_transport()
channel = transport.open_session()
channel.exec_command('python3 -u /root/core_login_real.py 2>&1')
channel.settimeout(5)

start = time.time()
while time.time() - start < 60:
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
