"""Test target from AlexHost RO VPS (diferente proveedor y geo)."""
import paramiko, time

# AlexHost RO batch 2026-08-25
VPS_ALEX = [
    {"ip": "85.121.5.9", "pass": "Z0Y611fRygsXVlxbRo"},
    {"ip": "85.122.114.169", "pass": "puu4EHMixZ1JeUtL0y"},
    {"ip": "80.96.58.99", "pass": "xviwKHoa3B9E4VJL7K"},
]

for vps in VPS_ALEX:
    print(f"\n[*] Testing {vps['ip']}...")
    try:
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(vps['ip'], username='root', password=vps['pass'], timeout=15)
        
        _, stdout, _ = client.exec_command('curl -sk -X POST https://soporte.disperso.com/api/auth/login -H "Content-Type: application/json" -d \'{"email":"test@test.com","password":"test"}\' -w "\\nHTTP_CODE:%{http_code}" --max-time 10 2>&1')
        out = stdout.read().decode().strip()
        print(f"  Response: {out[:300]}")
        
        client.close()
    except Exception as e:
        print(f"  Error: {e}")
    
    time.sleep(2)

print("\n[*] Done")
