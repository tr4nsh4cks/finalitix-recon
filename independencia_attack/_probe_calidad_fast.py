import paramiko, sys

VPS = '64.177.88.10'
PASS = '5F.jyTK$D6%.F{a='

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(VPS, username='root', password=PASS, timeout=10)
print('Connected', flush=True)

SCRIPT = r'''
import requests, urllib3, sys, socket
urllib3.disable_warnings()

IP = "35.238.21.37"

sys.stdout.write("=== CONNECTIVITY TEST ===\n")
sys.stdout.flush()

# 1. Raw socket test
for port in [443, 80, 8080]:
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(5)
        result = s.connect_ex((IP, port))
        s.close()
        state = "OPEN" if result == 0 else f"CLOSED({result})"
        sys.stdout.write(f"  TCP {IP}:{port} = {state}\n")
    except Exception as e:
        sys.stdout.write(f"  TCP {IP}:{port} = ERR({e})\n")
    sys.stdout.flush()

# 2. Quick HTTPS test with host header
sys.stdout.write("\n=== HTTPS TESTS (3s timeout) ===\n")
sys.stdout.flush()

hosts = [
    "bff-origination-service.orquesta.calidad-architect.com",
    "calidad-architect.com",
    "orquesta.calidad-architect.com",
    "eureka.calidad-architect.com",
    "mpago.calidad-architect.com",
]

for h in hosts:
    try:
        r = requests.get(
            f"https://{IP}/",
            headers={"Host": h, "User-Agent": "Mozilla/5.0"},
            timeout=3, verify=False, allow_redirects=False
        )
        sys.stdout.write(f"  {h}: [{r.status_code}] {len(r.text)}b CT={r.headers.get('Content-Type','?')}\n")
        if r.status_code == 200 and len(r.text) > 20:
            sys.stdout.write(f"    BODY: {repr(r.text[:300])}\n")
    except requests.exceptions.ConnectTimeout:
        sys.stdout.write(f"  {h}: CONNECT_TIMEOUT\n")
    except requests.exceptions.ReadTimeout:
        sys.stdout.write(f"  {h}: READ_TIMEOUT\n")
    except Exception as e:
        sys.stdout.write(f"  {h}: ERR {e}\n")
    sys.stdout.flush()

# 3. Try actuator on bff
sys.stdout.write("\n=== ACTUATOR QUICK TEST ===\n")
sys.stdout.flush()

bff = "bff-origination-service.orquesta.calidad-architect.com"
for path in ["/actuator/env", "/actuator/health", "/actuator", "/swagger-ui/", "/"]:
    try:
        r = requests.get(
            f"https://{IP}{path}",
            headers={"Host": bff, "User-Agent": "Mozilla/5.0", "Accept": "application/json"},
            timeout=3, verify=False, allow_redirects=False
        )
        tag = " *** HIT ***" if r.status_code == 200 and len(r.text) > 50 else ""
        sys.stdout.write(f"  [{r.status_code}] {path} ({len(r.text)}b){tag}\n")
        if tag:
            sys.stdout.write(f"    {repr(r.text[:400])}\n")
    except requests.exceptions.ConnectTimeout:
        sys.stdout.write(f"  TIMEOUT {path}\n")
    except Exception as e:
        sys.stdout.write(f"  ERR {path}: {e}\n")
    sys.stdout.flush()

sys.stdout.write("\nDONE\n")
sys.stdout.flush()
'''

sftp = ssh.open_sftp()
with sftp.open('/root/probe_fast.py', 'w') as f:
    f.write(SCRIPT)
sftp.close()
print('Uploaded', flush=True)

stdin, stdout, stderr = ssh.exec_command('python3 -u /root/probe_fast.py 2>&1', timeout=120)
out = stdout.read().decode(errors='replace')
print(out, flush=True)
ssh.close()
print('Done.', flush=True)
