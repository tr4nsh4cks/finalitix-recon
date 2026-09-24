import requests, json, sys, urllib3, time
urllib3.disable_warnings()

S = requests.Session()
S.headers.update({
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Content-Type": "application/json",
    "Accept": "application/json",
})
TIMEOUT = 20

BASE_HKDEV = "https://accounthkdev.mx.exchange"
BASE_UAT = "https://openapiuat.azurewebsites.net"

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

print("=" * 70)
print("MX EXCHANGE — REGISTER + LOGIN + BALANCE")
print("=" * 70)

# ========== STEP 1: REGISTER ON HK DEV ==========
print("\n[1] REGISTERING ON HK DEV...")

# Try different accountType values (0=individual, 1=corporate, 2=broker?)
for acct_type in [0, 1, 2]:
    for country in [1, 158]:  # 1=Malaysia?, 158=?
        payload = {
            "name": NAME,
            "email": EMAIL,
            "password": PASSWORD,
            "confirmPassword": PASSWORD,
            "country": country,
            "accountType": acct_type,
        }
        r = req("POST", f"{BASE_HKDEV}/api/Account/Register", payload)
        if r:
            print(f"  accountType={acct_type} country={country} => {r.status_code} ({len(r.text)}b)")
            if r.text:
                print(f"    BODY: {r.text[:500]}")
            if r.status_code in (200, 201):
                print(f"    [!!!] REGISTERED SUCCESSFULLY")
                break
    else:
        continue
    break

# ========== STEP 1b: ALSO TRY UAT REGISTER ==========
print("\n[1b] TRYING REGISTER ON UAT...")
for acct_type in [0, 1]:
    payload = {
        "name": NAME,
        "email": EMAIL,
        "password": PASSWORD,
        "confirmPassword": PASSWORD,
        "country": 1,
        "accountType": acct_type,
    }
    r = req("POST", f"{BASE_UAT}/api/Account/Register", payload)
    if r:
        print(f"  UAT accountType={acct_type} => {r.status_code} ({len(r.text)}b)")
        if r.text:
            print(f"    BODY: {r.text[:500]}")

# ========== STEP 2: CHECK TEST INTEGRATION EVENTS (no auth?) ==========
print("\n[2] TEST INTEGRATION EVENTS (no auth test)...")
test_events = [
    ("ApproveKyc", {"userId": 1}),
    ("ConfirmEmail", {"userId": 1}),
    ("ApproveBeneficiary", {"beneficiaryId": 1}),
    ("KycLevelPendingCount", {}),
    ("BeneficiaryPendingCount", {}),
    ("RejectKyc", {"userId": 1}),
    ("RejectBeneficiary", {"beneficiaryId": 1}),
]
for event_name, payload in test_events:
    r = req("POST", f"{BASE_HKDEV}/api/TestIntegrationEvent/{event_name}", payload)
    if r:
        tag = "[!!!]" if r.status_code in (200, 201, 204) else "[x]" if r.status_code == 401 else "[?]"
        print(f"  {tag} {event_name} => {r.status_code} ({len(r.text)}b) {r.text[:200]}")

# ========== STEP 3: TRY PUBLIC ENDPOINTS ==========
print("\n[3] PUBLIC ENDPOINTS (no auth)...")
public_tests = [
    ("GET", f"{BASE_HKDEV}/api/MasterData"),
    ("GET", f"{BASE_HKDEV}/api/Roles"),
    ("GET", f"{BASE_HKDEV}/api/Banks/AllBank"),
    ("GET", f"{BASE_HKDEV}/api/Beneficiaries/CountryOfResidence"),
    ("GET", f"{BASE_HKDEV}/api/Beneficiaries/NationalityList"),
    ("GET", f"{BASE_HKDEV}/api/Kyc/KycFieldTypes"),
    ("GET", f"{BASE_HKDEV}/api/Kyc/KycApprovalStatuses"),
    ("GET", f"{BASE_HKDEV}/api/Kyc/KycLimitationTypes"),
    ("GET", f"{BASE_HKDEV}/api/Kyc/KycLimitationPeriodTypes"),
    ("POST", f"{BASE_HKDEV}/api/Account/CheckAccountEmail"),
    ("GET", f"{BASE_HKDEV}/api/Account/VerifyReferralCode"),
    ("GET", f"{BASE_HKDEV}/api/Account/ShortUserReport"),
    ("GET", f"{BASE_HKDEV}/api/Users/Report"),
    ("GET", f"{BASE_HKDEV}/api/Users/TempList"),
    ("GET", f"{BASE_HKDEV}/api/Users/GetCustomerData"),
    ("GET", f"{BASE_HKDEV}/api/Users/GetCustomerAccountData"),
    ("GET", f"{BASE_HKDEV}/api/Users/Balance/1"),
    ("GET", f"{BASE_HKDEV}/api/Users/Balance/2"),
    ("GET", f"{BASE_HKDEV}/api/Users/Balance/3"),
    ("GET", f"{BASE_HKDEV}/api/Users"),
    ("GET", f"{BASE_HKDEV}/api/Users/1"),
    ("GET", f"{BASE_HKDEV}/api/Users/2"),
    ("GET", f"{BASE_HKDEV}/api/AuditTrail"),
    ("GET", f"{BASE_HKDEV}/api/Groups"),
    ("GET", f"{BASE_HKDEV}/api/CountryAccessible"),
]

for method, url in public_tests:
    r = req(method, url)
    if r:
        tag = "[!!!]" if r.status_code in (200, 201, 204) else "[x]" if r.status_code == 401 else "[?]"
        body = r.text[:300] if r.text else ""
        print(f"  {tag} {method} {url.split('.exchange')[1]} => {r.status_code} ({len(r.text)}b)")
        if r.status_code in (200, 201, 204) and r.text:
            print(f"      BODY: {body}")

# ========== STEP 4: ALSO TRY COMMON API MARKET (it gave 500) ==========
print("\n[4] COMMON API DEEP PROBE...")
COMMON = "https://commonhkdev.mx.exchange"
common_tests = [
    ("GET", f"{COMMON}/api/Currency/list"),
    ("GET", f"{COMMON}/api/Market/list"),
    ("GET", f"{COMMON}/api/Market/active"),
    ("GET", f"{COMMON}/api/Country/list"),
    ("GET", f"{COMMON}/api/Fee/list"),
    ("GET", f"{COMMON}/api/Email"),
]
for method, url in common_tests:
    r = req(method, url)
    if r:
        tag = "[!!!]" if r.status_code in (200, 201, 204) else "[x]" if r.status_code == 401 else "[?]"
        print(f"  {tag} {method} {url.split('.exchange')[1]} => {r.status_code} ({len(r.text)}b) {r.text[:200] if r.text else ''}")

print("\n" + "=" * 70)
print("DONE")
