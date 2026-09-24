import requests, json, sys, urllib3
urllib3.disable_warnings()
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
T = 20

def r(url, **kw):
    try:
        resp = requests.get(url, timeout=T, verify=False, 
                           headers={"User-Agent":"Mozilla/5.0","Accept":"application/json"}, **kw)
        return resp
    except Exception as e:
        return None

def safe(t, n=500):
    return t[:n].encode('ascii','replace').decode('ascii') if t else ""

UAT = "https://openapiuat.azurewebsites.net"
PROD = "https://openapi.mx.exchange"
ACCT = "https://accounthkdev.mx.exchange"

hits = {}

print("=" * 70)
print("BALANCE + MARKET DATA + REGISTER FIX")
print("=" * 70)

# 1. PUBLIC MARKET DATA (no auth needed)
print("\n[1] PUBLIC DATA — UAT + PROD")
for env, base in [("UAT", UAT), ("PROD", PROD)]:
    pairs = ["BTCMYR", "ETHMYR", "XRPMYR", "SOLMYR", "WLDMYR"]
    
    # Ticker
    for pair in pairs:
        resp = r(f"{base}/api/1/ticker?pair={pair}")
        if resp and resp.status_code == 200:
            print(f"  [{env}] ticker {pair}: {safe(resp.text, 300)}")
            hits[f"{env}_ticker_{pair}"] = resp.text
        elif resp:
            print(f"  [{env}] ticker {pair}: {resp.status_code}")
    
    # Orderbook
    for pair in ["BTCMYR", "ETHMYR"]:
        resp = r(f"{base}/api/1/orderbook?pair={pair}")
        if resp and resp.status_code == 200:
            data = resp.json()
            bids = len(data.get("bids", []))
            asks = len(data.get("asks", []))
            print(f"  [{env}] orderbook {pair}: {bids} bids, {asks} asks ({len(resp.text)}b)")
            hits[f"{env}_orderbook_{pair}"] = resp.text[:5000]
    
    # Trades
    for pair in ["BTCMYR"]:
        resp = r(f"{base}/api/1/trade?pair={pair}")
        if resp and resp.status_code == 200:
            data = resp.json()
            trades = data.get("trades", [])
            print(f"  [{env}] trades {pair}: {len(trades)} trades")
            if trades:
                print(f"    Last: {safe(json.dumps(trades[0]), 200)}")
            hits[f"{env}_trades_{pair}"] = resp.text[:10000]
    
    # Currency
    resp = r(f"{base}/api/1/currency")
    if resp and resp.status_code == 200:
        print(f"  [{env}] currencies: {safe(resp.text, 400)}")
        hits[f"{env}_currency"] = resp.text
    
    resp = r(f"{base}/api/1/currency/active")
    if resp and resp.status_code == 200:
        print(f"  [{env}] active currencies: {safe(resp.text, 400)}")
        hits[f"{env}_currency_active"] = resp.text
    
    # Ticker all
    resp = r(f"{base}/api/1/ticker/all")
    if resp and resp.status_code == 200:
        print(f"  [{env}] ticker/all: {safe(resp.text, 500)}")
        hits[f"{env}_ticker_all"] = resp.text

# 2. REGISTER WITH DIFFERENT EMAILS
print("\n[2] REGISTER ATTEMPTS...")
emails_to_try = [
    "testuser@gmail.com",
    "mxtest@yahoo.com",
    "user123@outlook.com",
    "test@mx.exchange",
    "admin@mx.exchange",
    "test@mailinator.com",
    "john@example.com",
    "a@b.com",
]

for email in emails_to_try:
    payload = {
        "name": "Test User",
        "email": email,
        "password": "TestPass123!@#",
        "confirmPassword": "TestPass123!@#",
        "country": 1,
        "accountType": 0,
    }
    try:
        resp = requests.post(f"{ACCT}/api/Account/Register", json=payload, timeout=T, verify=False,
                            headers={"Content-Type":"application/json","Accept":"application/json",
                                     "User-Agent":"Mozilla/5.0"})
        print(f"  {email:35s} => {resp.status_code} {safe(resp.text, 200)}")
        if resp.status_code in (200, 201):
            print(f"    [!!!] REGISTERED!")
            hits[f"register_{email}"] = resp.text
            break
    except Exception as e:
        print(f"  {email:35s} => ERROR: {e}")

# 3. CHECK UAT REGISTER
print("\n[3] UAT REGISTER...")
for email in ["testuser@gmail.com", "a@b.com"]:
    payload = {
        "name": "Test User",
        "email": email,
        "password": "TestPass123!@#",
        "confirmPassword": "TestPass123!@#",
        "country": 1,
        "accountType": 0,
    }
    try:
        resp = requests.post(f"{UAT}/api/Account/Register", json=payload, timeout=T, verify=False,
                            headers={"Content-Type":"application/json","Accept":"application/json",
                                     "User-Agent":"Mozilla/5.0"})
        print(f"  UAT {email:35s} => {resp.status_code} {safe(resp.text, 300)}")
        if resp.status_code in (200, 201):
            print(f"    [!!!] REGISTERED ON UAT!")
            hits[f"uat_register_{email}"] = resp.text
    except Exception as e:
        print(f"  UAT {email:35s} => ERROR: {e}")

# 4. Check what the PROD app registration looks like
print("\n[4] PROD APP REGISTER...")
APP = "https://account.mx.exchange"
for email in ["testuser@gmail.com"]:
    payload = {
        "name": "Test User",
        "email": email,
        "password": "TestPass123!@#",
        "confirmPassword": "TestPass123!@#",
        "country": 1,
        "accountType": 0,
    }
    try:
        resp = requests.post(f"{APP}/api/Account/Register", json=payload, timeout=T, verify=False,
                            headers={"Content-Type":"application/json","Accept":"application/json",
                                     "User-Agent":"Mozilla/5.0"})
        print(f"  PROD {email:35s} => {resp.status_code} {safe(resp.text, 300)}")
        if resp.status_code in (200, 201):
            hits[f"prod_register_{email}"] = resp.text
    except Exception as e:
        print(f"  PROD {email:35s} => ERROR: {e}")

# Save
with open(r"c:\xampp\htdocs\pentagi\mxexchange_attack\market_data_results.json", "w", encoding="utf-8") as f:
    json.dump(hits, f, indent=2, ensure_ascii=True)

print(f"\n{'='*70}")
print(f"TOTAL HITS: {len(hits)}")
print("=" * 70)
