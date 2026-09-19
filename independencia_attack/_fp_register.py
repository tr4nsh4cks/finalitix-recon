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

PAO = "https://pao.findep.com.mx"


# ========================================
# 1. ANALYZE SIGNUP FORM
# ========================================
sys.stdout.write("=" * 60 + "\n=== SIGNUP FORM ANALYSIS ===\n" + "=" * 60 + "\n\n")

r = s.get(f"{PAO}/MRcgi/MRsignUp.pl", timeout=10)
sys.stdout.write(f"SignUp: [{r.status_code}] ({len(r.text)}b)\n\n")

# Extract ALL form elements
all_inputs = re.findall(r'<input[^>]+>', r.text, re.I)
all_selects = re.findall(r'<select[^>]+name=["\']([^"\']+)["\'][^>]*>(.*?)</select>', r.text, re.I | re.S)
all_textareas = re.findall(r'<textarea[^>]+name=["\']([^"\']+)["\']', r.text, re.I)

sys.stdout.write("Input elements:\n")
for inp in all_inputs:
    name = re.search(r'name=["\']([^"\']+)["\']', inp, re.I)
    type_ = re.search(r'type=["\']([^"\']+)["\']', inp, re.I)
    value = re.search(r'value=["\']([^"\']*)["\']', inp, re.I)
    if name:
        sys.stdout.write(f"  {name.group(1)}: type={type_.group(1) if type_ else 'text'} value={value.group(1)[:50] if value else ''}\n")

sys.stdout.write(f"\nSelect elements: {len(all_selects)}\n")
for name, options_html in all_selects:
    options = re.findall(r'<option[^>]*value=["\']([^"\']*)["\'][^>]*>([^<]*)', options_html, re.I)
    sys.stdout.write(f"  {name}: {options[:10]}\n")

sys.stdout.write(f"\nTextareas: {all_textareas}\n")

# Extract form action more precisely
forms = re.findall(r'<form[^>]*action=["\']([^"\']+)["\'][^>]*>(.*?)</form>', r.text, re.I | re.S)
sys.stdout.write(f"\nForms with actions:\n")
for action, body in forms:
    sys.stdout.write(f"  Action: {action}\n")
    inputs = re.findall(r'name=["\']([^"\']+)["\']', body, re.I)
    sys.stdout.write(f"  Fields: {inputs}\n\n")

# Also look for JavaScript that reveals required fields
js_blocks = re.findall(r'<script[^>]*>(.*?)</script>', r.text, re.I | re.S)
for js in js_blocks:
    if "signup" in js.lower() or "register" in js.lower() or "submit" in js.lower():
        sys.stdout.write(f"\nRelevant JS:\n{js[:2000]}\n\n")

# Dump the form section more carefully
form_section = re.search(r'(?:Registr|Sign\s*Up|Crear|Nueva\s+cuenta).*?</form>', r.text, re.I | re.S)
if form_section:
    sys.stdout.write(f"\nForm section:\n{form_section.group()[:3000]}\n")


# ========================================
# 2. ATTEMPT REGISTRATION
# ========================================
sys.stdout.write("\n\n" + "=" * 60 + "\n=== REGISTRATION ATTEMPT ===\n" + "=" * 60 + "\n\n")

# Standard FootPrints signup fields
reg_data = {
    "PROJECTID": "1",
    "FIRST_NAME": "Carlos",
    "LAST_NAME": "Martinez Lopez",
    "EMAIL": "cmartinezl@findep.com.mx",
    "USERID": "cmartinezl",
    "PASSWORD": "Findep2026!",
    "CONFIRM_PASSWORD": "Findep2026!",
    "PHONE": "5551234567",
    "DEPARTMENT": "Sistemas",
    "TITLE": "Analista",
    "MRSubmit": "Submit",
}

r_reg = s.post(f"{PAO}/MRcgi/MRsignUp2.pl", data=reg_data, timeout=15, allow_redirects=False)
sys.stdout.write(f"Register POST: [{r_reg.status_code}] ({len(r_reg.text)}b)\n")
sys.stdout.write(f"Location: {r_reg.headers.get('Location', 'NONE')}\n")
sys.stdout.write(f"Set-Cookie: {r_reg.headers.get('Set-Cookie', 'NONE')}\n")

if r_reg.status_code == 200:
    title = re.search(r'<title>(.*?)</title>', r_reg.text[:2000], re.I)
    sys.stdout.write(f"Title: {title.group(1) if title else 'N/A'}\n")
    
    # Check for success/error
    if "error" in r_reg.text[:2000].lower():
        error_text = re.search(r'(?:error|Error|ERROR)[^<]*', r_reg.text[:5000])
        sys.stdout.write(f"Error: {error_text.group()[:300] if error_text else 'unknown'}\n")
    
    if "success" in r_reg.text.lower() or "created" in r_reg.text.lower() or "registr" in r_reg.text.lower():
        sys.stdout.write("*** REGISTRATION MAY HAVE SUCCEEDED ***\n")
    
    sys.stdout.write(f"\nResponse preview:\n{r_reg.text[:3000]}\n")

# Follow redirect
if r_reg.status_code in [302, 301]:
    loc = r_reg.headers.get("Location", "")
    r_follow = s.get(loc if loc.startswith("http") else f"{PAO}{loc}", timeout=10)
    sys.stdout.write(f"\nFollowed redirect: [{r_follow.status_code}] ({len(r_follow.text)}b)\n")
    sys.stdout.write(f"Content: {r_follow.text[:2000]}\n")


# ========================================
# 3. TRY LOGIN WITH REGISTERED USER
# ========================================
sys.stdout.write("\n\n" + "=" * 60 + "\n=== LOGIN WITH REGISTERED USER ===\n" + "=" * 60 + "\n\n")

# The entrance page form has USER, PASSWORD, REMEMBER_PASSWORD, PROJECTID, SCREEN
# Let's use the entrance page form which is different from MRlogin.pl
r_ent = s.get(f"{PAO}/MRcgi/MRentrancePage.pl", timeout=10)

# Try to find the actual login submit URL from JavaScript
js_login = re.findall(r'(?:function|var)\s+\w*(?:login|Login|submit|Submit)[^}]*\}', r_ent.text, re.S)
for jf in js_login[:3]:
    sys.stdout.write(f"Login JS: {jf[:500]}\n\n")

# Find ALL form actions
all_forms = re.findall(r'<form[^>]*>(.*?)</form>', r_ent.text, re.I | re.S)
sys.stdout.write(f"Entrance page forms: {len(all_forms)}\n")
for i, f in enumerate(all_forms):
    action = re.search(r'action=["\']([^"\']+)["\']', f, re.I)
    inputs = re.findall(r'name=["\']([^"\']+)["\']', f, re.I)
    sys.stdout.write(f"  Form {i}: action={action.group(1) if action else 'N/A'} inputs={inputs}\n")

# Try the entrance page login with various field combos
login_attempts = [
    # Standard FootPrints login
    {"USER": "cmartinezl", "PASSWORD": "Findep2026!", "PROJECTID": "1", "SCREEN": ""},
    {"USER": "cmartinezl", "PASSWORD": "Findep2026!", "PROJECTID": "1", "SCREEN": "", "button": "Iniciar sesi\xf3n"},
    # Try with bmendezar using correct form fields
    {"USER": "bmendezar", "PASSWORD": "Pao1234+", "PROJECTID": "1", "SCREEN": ""},
]

for attempt in login_attempts:
    try:
        # POST to MRentrancePage.pl (the actual login endpoint)
        r_login = s.post(f"{PAO}/MRcgi/MRentrancePage.pl", data=attempt,
            timeout=10, allow_redirects=False)
        sys.stdout.write(f"\nLogin {attempt['USER']}:{attempt['PASSWORD'][:10]}... -> [{r_login.status_code}] ({len(r_login.text)}b)\n")
        sys.stdout.write(f"  Location: {r_login.headers.get('Location', 'NONE')}\n")
        sys.stdout.write(f"  Set-Cookie: {r_login.headers.get('Set-Cookie', 'NONE')[:200]}\n")
        sys.stdout.write(f"  Cookies: {dict(s.cookies)}\n")
        
        if r_login.status_code in [302, 301]:
            loc = r_login.headers.get("Location", "")
            if "homepage" in loc.lower() or "ticket" in loc.lower():
                sys.stdout.write(f"  *** LOGIN SUCCESS ***\n")
                # Follow redirect
                r_dash = s.get(loc if loc.startswith("http") else f"{PAO}{loc}", timeout=10)
                sys.stdout.write(f"  Dashboard: [{r_dash.status_code}] ({len(r_dash.text)}b)\n")
                sys.stdout.write(f"  Preview: {r_dash.text[:1000]}\n")
        elif r_login.status_code == 200:
            if "error" in r_login.text[:1000].lower() or "incorrect" in r_login.text[:1000].lower():
                sys.stdout.write(f"  Login failed (error in body)\n")
            elif len(r_login.text) > 30000:
                sys.stdout.write(f"  Large response - might be dashboard!\n")
                sys.stdout.write(f"  Title: {re.search(r'<title>(.*?)</title>', r_login.text[:2000], re.I)}\n")
    except Exception as e:
        sys.stdout.write(f"  ERR: {e}\n")
    sys.stdout.flush()


# ========================================
# 4. SERVICE CATALOG ANALYSIS (43KB!)
# ========================================
sys.stdout.write("\n\n" + "=" * 60 + "\n=== SERVICE CATALOG (43KB — NO AUTH) ===\n" + "=" * 60 + "\n\n")

r_cat = s.get(f"{PAO}/MRcgi/MRServiceCatalog.pl?PROJECTID=1", timeout=10)
sys.stdout.write(f"Catalog: [{r_cat.status_code}] ({len(r_cat.text)}b)\n\n")

# Extract service categories and items
categories = re.findall(r'(?:category|servicio|service|catalog)[^<>]*>([^<]+)', r_cat.text, re.I)
sys.stdout.write(f"Categories/items found: {len(categories)}\n")
for c in categories[:30]:
    c = c.strip()
    if len(c) > 2:
        sys.stdout.write(f"  {c}\n")

# Extract all links
cat_links = re.findall(r'href=["\']([^"\']+)["\']', r_cat.text, re.I)
interesting = [l for l in cat_links if 'MR' in l and '.pl' in l]
sys.stdout.write(f"\nCatalog links: {interesting[:20]}\n")

# Extract any internal hostnames/IPs
internal = re.findall(r'(?:https?://)?(?:10\.\d+\.\d+\.\d+|172\.(?:1[6-9]|2\d|3[01])\.\d+\.\d+|192\.168\.\d+\.\d+)[^\s<"\']*', r_cat.text)
if internal:
    sys.stdout.write(f"\nInternal IPs: {internal}\n")

hostnames = re.findall(r'(?:https?://)?[\w.-]+\.findep\.(?:mx|com\.mx|global|dev)[^\s<"\']*', r_cat.text)
if hostnames:
    sys.stdout.write(f"\nFINDEP hostnames: {set(hostnames)}\n")

# Dump key content
sys.stdout.write(f"\nFirst 3000 chars:\n{r_cat.text[:3000]}\n")
sys.stdout.write(f"\nLast 1000 chars:\n{r_cat.text[-1000:]}\n")


sys.stdout.write("\n\n=== ALL DONE ===\n")
sys.stdout.flush()
'''

sftp = ssh.open_sftp()
with sftp.open('/root/fp_register.py', 'w') as f:
    f.write(SCRIPT)
sftp.close()
print('Uploaded', flush=True)

stdin, stdout, stderr = ssh.exec_command('python3 -u /root/fp_register.py 2>&1', timeout=120)
out = stdout.read().decode(errors='replace')
print(out, flush=True)
ssh.close()
print('Fin.', flush=True)
