"""Deploy y ejecuta el spray en el VPS via SSH/paramiko."""
import paramiko, time, sys, os

VPS_IP = "64.177.83.195"
VPS_USER = "root"
VPS_PASS = "Nm9.#p)WzifT.fo2"

SPRAY_SCRIPT = r"c:\xampp\htdocs\pentagi\disperso_recon\spray_soporte.py"
REMOTE_SCRIPT = "/tmp/spray_soporte.py"
REMOTE_RESULTS = "/tmp/hexagon_spray_results.json"
LOCAL_RESULTS = r"c:\xampp\htdocs\pentagi\disperso_recon\hexagon_sonnet_results.json"

def run_cmd(client, cmd, timeout=30):
    stdin, stdout, stderr = client.exec_command(cmd, timeout=timeout)
    out = stdout.read().decode().strip()
    err = stderr.read().decode().strip()
    return out, err

print(f"[*] Conectando a {VPS_IP}...")
client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(VPS_IP, username=VPS_USER, password=VPS_PASS, timeout=20)
print("[+] Conectado OK")

# Verificar Python
out, err = run_cmd(client, "python3 --version 2>&1")
print(f"[*] Python: {out}")

# Verificar requests
out, err = run_cmd(client, "python3 -c 'import requests; print(requests.__version__)' 2>&1")
print(f"[*] requests: {out}")
if not out or "Error" in out or "ModuleNotFoundError" in out:
    print("[*] Instalando requests...")
    out, err = run_cmd(client, "pip3 install requests -q 2>&1", timeout=60)
    print(f"    {out[:200]}")

# Subir el script via SFTP
print(f"[*] Subiendo {SPRAY_SCRIPT} -> {REMOTE_SCRIPT}")
sftp = client.open_sftp()
sftp.put(SPRAY_SCRIPT, REMOTE_SCRIPT)
sftp.close()
print("[+] Script subido")

# Ejecutar en background con nohup
cmd = f"nohup python3 {REMOTE_SCRIPT} > /tmp/spray_out.log 2>&1 &"
out, err = run_cmd(client, cmd)
print(f"[*] Lanzado: {cmd}")

# Esperar 5s y verificar que está corriendo
time.sleep(5)
out, err = run_cmd(client, "pgrep -af spray_soporte")
print(f"[*] Proceso activo: {out}")

# Mostrar primeras líneas del log
time.sleep(3)
out, err = run_cmd(client, "head -30 /tmp/spray_out.log")
print(f"[*] Log inicial:\n{out}")

client.close()
print("[*] Setup completo. Script corriendo en background.")
