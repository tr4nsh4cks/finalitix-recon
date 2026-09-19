#!/usr/bin/env python3
"""
HEXAGON GLM 5.2 - FINDEP SIF (sif.findep.mx) Analysis
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

SIF_URL = "https://sif.findep.mx"

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

    # 1. GET SIF home
    print("\n[*] === SIF home ===")
    cmd = (
        f"curl -sk -m 20 -A 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        f"AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36' "
        f"-c /tmp/sif_cookies.txt '{SIF_URL}/' -o /tmp/sif_home.html 2>&1; "
        f"wc -c /tmp/sif_home.html"
    )
    out, _ = ssh_exec(client, cmd, timeout=25)
    print(f"  Home: {out.strip()}")

    cmd = "cat /tmp/sif_home.html"
    out, _ = ssh_exec(client, cmd, timeout=15)
    home_html = out
    log["home_html"] = home_html
    safe_print(home_html[:3000])

    # 2. Buscar JS bundles
    print("\n[*] === Find JS bundles ===")
    cmd = "grep -oP 'src=\"[^\"]+\\.js[^\"]*\"' /tmp/sif_home.html"
    out, _ = ssh_exec(client, cmd, timeout=10)
    js_refs = [l.strip() for l in out.strip().split("\n") if l.strip()]
    print(f"  JS refs: {js_refs}")

    # 3. Descargar cada JS
    print("\n[*] === Download JS bundles ===")
    js_files = {}
    for ref in js_refs:
        m = re.search(r'src="([^"]+)"', ref)
        if not m:
            continue
        path = m.group(1)
        if path.startswith("/"):
            url = f"{SIF_URL}{path}"
        elif path.startswith("http"):
            url = path
        else:
            url = f"{SIF_URL}/{path}"
        fname = path.split("/")[-1].split("?")[0]
        cmd = (
            f"curl -sk -m 30 -A 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            f"AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36' "
            f"'{url}' -o /tmp/sif_{fname} 2>&1; wc -c /tmp/sif_{fname}"
        )
        out, _ = ssh_exec(client, cmd, timeout=35)
        print(f"  {url}: {out.strip()}")
        cmd = f"cat /tmp/sif_{fname}"
        out, _ = ssh_exec(client, cmd, timeout=20)
        js_files[fname] = out

    # 4. Buscar endpoints API en JS
    print("\n[*] === API endpoints in JS ===")
    api_endpoints = set()
    for fname, content in js_files.items():
        endpoints = re.findall(r"""['"`](/(?:api|v1|v2|auth|login|users|sif|teacher|courses|students|payments|spei|graphql)[^'"`]*?)['"`]""", content)
        api_endpoints.update(endpoints)
        urls = re.findall(r"""['"`](https?://[^'"`]+)['"`]""", content)
        for u in urls:
            if "findep" in u or "sif" in u:
                api_endpoints.add(u)
        routes = re.findall(r"""(?:fetch|axios|get|post|put|delete)\s*\(\s*['"`]([^'"`]+)['"`]""", content)
        for r in routes:
            if r.startswith("/") or r.startswith("http"):
                api_endpoints.add(r)

    print(f"  Endpoints encontrados: {len(api_endpoints)}")
    for ep in sorted(api_endpoints):
        print(f"    {ep}")
    log["api_endpoints"] = sorted(api_endpoints)
    log["js_files"] = list(js_files.keys())
    log["js_sizes"] = {k: len(v) for k, v in js_files.items()}
    log["js_contents"] = js_files

    # 5. Probar endpoints comunes
    print("\n[*] === Probar endpoints comunes ===")
    common_paths = [
        "/api", "/api/", "/api/v1", "/api/v1/", "/api/auth", "/api/auth/login",
        "/api/login", "/api/users", "/api/users/me", "/api/me",
        "/api/teachers", "/api/students", "/api/courses", "/api/classes",
        "/api/payments", "/api/spei", "/api/transactions",
        "/auth/login", "/login", "/users", "/me",
        "/api/health", "/health", "/api/status", "/status",
        "/api/config", "/config",
        "/api-docs", "/docs", "/swagger", "/swagger-ui", "/v1/api-docs",
        "/.env", "/package.json", "/robots.txt", "/sitemap.xml",
        "/api/sif", "/sif", "/teacher", "/teachers",
        "/api/dashboard", "/dashboard",
    ]
    probe_results = {}
    for path in common_paths:
        cmd = (
            f"curl -sk -m 10 -A 'Mozilla/5.0' "
            f"-o /dev/null -w 'HTTP:%{{http_code}} SIZE:%{{size_download}} TYPE:%{{content_type}}' "
            f"'{SIF_URL}{path}'"
        )
        out, _ = ssh_exec(client, cmd, timeout=15)
        probe_results[path] = out.strip()
        if "HTTP:404" not in out and "HTTP:000" not in out:
            print(f"  {path}: {out.strip()}")
    log["probe_results"] = probe_results

    # 6. Para endpoints con respuesta, descargar body
    print("\n[*] === Download bodies for interesting endpoints ===")
    interesting_bodies = {}
    for path, res in probe_results.items():
        if "HTTP:200" in res and "SIZE:0" not in res:
            cmd = f"curl -sk -m 10 '{SIF_URL}{path}' | head -c 3000"
            out, _ = ssh_exec(client, cmd, timeout=15)
            interesting_bodies[path] = out
            print(f"\n--- {path} ---")
            safe_print(out[:1500])
    log["interesting_bodies"] = interesting_bodies

    # 7. Guardar
    log["timestamp"] = datetime.now(timezone.utc).isoformat()
    out_file = r"c:\xampp\htdocs\pentagi\independencia_attack\hexagon_glm_sif.json"
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(log, f, indent=2, ensure_ascii=False)
    print(f"\n[+] SIF guardado en {out_file}")

    client.close()

if __name__ == "__main__":
    main()
