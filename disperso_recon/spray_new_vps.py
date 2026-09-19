"""
Deploy y monitorea spray desde VPS 64.177.88.10 (limpia, no usada en disperso)
"""
import paramiko, time

VPS2_IP = "64.177.88.10"
VPS2_USER = "root"
VPS2_PASS = "5F.jyTK$D6%.F{a="

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(VPS2_IP, username=VPS2_USER, password=VPS2_PASS, timeout=25)
print(f"[+] Connected to {VPS2_IP}")

def run(c, cmd, timeout=20):
    _, s, _ = c.exec_command(cmd, timeout=timeout)
    return s.read().decode().strip()

# Test target from fresh IP
print("[*] Testing target from fresh VPS IP...")
out = run(client, 'curl -sk -X POST https://soporte.disperso.com/api/auth/login -H "Content-Type: application/json" -d \'{"email":"admin@disperso.com","password":"test123"}\' -w "\\nHTTP_CODE:%{http_code}" --max-time 10 2>&1')
print(f"  Test 1: {out[:300]}")

time.sleep(2)
out = run(client, 'curl -sk -X POST https://soporte.disperso.com/api/auth/login -H "Content-Type: application/json" -d \'{"email":"soporte@disperso.com","password":"test123"}\' -w "\\nHTTP_CODE:%{http_code}" --max-time 10 2>&1')
print(f"  Test 2: {out[:300]}")

time.sleep(2)
out = run(client, 'curl -sk -X POST https://soporte.disperso.com/api/auth/login -H "Content-Type: application/json" -d \'{"email":"christian.ramirez@disperso.com","password":"Disperso2024!"}\' -w "\\nHTTP_CODE:%{http_code}" --max-time 10 2>&1')
print(f"  Test OSINT (christian.ramirez:Disperso2024!): {out[:300]}")

# Check Python
py_ver = run(client, 'python3 --version 2>&1')
print(f"\n[*] Python: {py_ver}")

req_ver = run(client, "python3 -c 'import requests; print(requests.__version__)' 2>&1")
print(f"[*] Requests: {req_ver}")
if not req_ver or 'Error' in req_ver:
    print("[*] Installing requests...")
    out = run(client, "pip3 install requests -q 2>&1", timeout=60)
    print(f"  {out[:200]}")

# Upload spray script
sftp = client.open_sftp()
sftp.put(r'c:\xampp\htdocs\pentagi\disperso_recon\spray_v2.py', '/tmp/spray_v2.py')
sftp.close()
print("[+] Spray script uploaded to VPS2")

# Kill any old processes and launch
run(client, 'pkill -f spray_v2 2>/dev/null; sleep 1')
out = run(client, 'rm -f /tmp/hexagon_spray_results.json /tmp/spray_v2_out.log; nohup python3 -u /tmp/spray_v2.py > /tmp/spray_v2_out.log 2>&1 & echo PID:$!')
print(f"[*] Launched: {out}")

# Monitor first 40 seconds
time.sleep(40)
log = run(client, 'cat /tmp/spray_v2_out.log')
print(f"\n[*] Log after 40s:\n{log[:2000]}")

client.close()
