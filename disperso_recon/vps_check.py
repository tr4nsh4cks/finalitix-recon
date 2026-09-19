"""Check VPS spray status and connectivity."""
import paramiko, time

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('64.177.83.195', username='root', password='Nm9.#p)WzifT.fo2', timeout=20)
print("[+] Connected")

def run(client, cmd, timeout=20):
    _, stdout, stderr = client.exec_command(cmd, timeout=timeout)
    out = stdout.read().decode().strip()
    err = stderr.read().decode().strip()
    return out, err

# Test target reachability
print("[*] Testing target connectivity...")
out, _ = run(client, 'curl -sk -X POST https://soporte.disperso.com/api/auth/login -H "Content-Type: application/json" -d \'{"email":"test@test.com","password":"test"}\' -w "\\nHTTP_CODE:%{http_code}" --max-time 10 2>&1')
print(f"    Target response: {out[:300]}")

# Kill old and relaunch with -u
out, _ = run(client, 'kill $(pgrep -f spray_soporte) 2>/dev/null; sleep 1; echo killed')
print(f"[*] Kill old: {out}")

out, _ = run(client, 'nohup python3 -u /tmp/spray_soporte.py > /tmp/spray_out.log 2>&1 & echo PID:$!')
print(f"[*] New launch: {out}")

time.sleep(10)

# Read log
out, _ = run(client, 'cat /tmp/spray_out.log')
print(f"[*] Log (10s):\n{out[:2000]}")

client.close()
