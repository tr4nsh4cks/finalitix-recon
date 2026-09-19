#!/usr/bin/env python3
"""
HEXAGON GLM 5.2 - FINDEP Recon
Reconocimiento inicial desde VPS contra superficie FINDEP.
"""
import paramiko
import json
import time
import sys
from datetime import datetime

VPS_HOST = "64.177.88.10"
VPS_USER = "root"
VPS_PASS = "5F.jyTK$D6%.F{a="

TARGETS = [
    # PPP KHOR
    "https://ppp.findep.mx/khorLogin.asp",
    "https://pppindependencia.independencia.com.mx/khorLogin.asp",
    # Dynamics BC
    "https://findep.global",
    "https://bc.findep.global",
    "https://businesscentral.dynamics.com",
    # WebLogic
    "http://core.findep.mx:7001",
    "https://core.findep.mx:7001",
    # Moodle
    "https://universidad.findep.mx",
    # SIF
    "https://sif.findep.mx",
    # Otros
    "https://www.findep.mx",
    "https://findep.mx",
    "https://www.independencia.com.mx",
    "https://independencia.com.mx",
]

def ssh_exec(client, cmd, timeout=30):
    stdin, stdout, stderr = client.exec_command(cmd, timeout=timeout)
    out = stdout.read().decode("utf-8", errors="replace")
    err = stderr.read().decode("utf-8", errors="replace")
    return out, err

def main():
    print(f"[*] Conectando a VPS {VPS_HOST}...")
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(VPS_HOST, username=VPS_USER, password=VPS_PASS, timeout=30)
    print("[+] Conectado al VPS")

    # Verificar herramientas en VPS
    out, err = ssh_exec(client, "which curl python3 dig nslookup host 2>&1; curl --version | head -1")
    print(f"[*] Tools VPS:\n{out}")

    # DNS resolution
    print("\n[*] === DNS Resolution ===")
    hosts_to_resolve = [
        "ppp.findep.mx",
        "pppindependencia.independencia.com.mx",
        "findep.global",
        "bc.findep.global",
        "core.findep.mx",
        "universidad.findep.mx",
        "sif.findep.mx",
        "www.findep.mx",
        "findep.mx",
        "www.independencia.com.mx",
        "independencia.com.mx",
        "businesscentral.dynamics.com",
    ]
    dns_results = {}
    for h in hosts_to_resolve:
        out, _ = ssh_exec(client, f"host {h} 2>&1 | head -5; echo '---'; dig +short {h} 2>&1 | head -5")
        dns_results[h] = out.strip()
        print(f"  {h}: {out.strip()[:200]}")

    # HTTP probe
    print("\n[*] === HTTP Probe ===")
    http_results = {}
    for url in TARGETS:
        cmd = (
            f"curl -sk -m 15 -A 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            f"AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36' "
            f"-o /dev/null -w 'HTTP:%{{http_code}} SIZE:%{{size_download}} "
            f"TIME:%{{time_total}} REDIR:%{{redirect_url}} SERVER:%{{content_type}}' '{url}' 2>&1"
        )
        out, err = ssh_exec(client, cmd, timeout=20)
        http_results[url] = out.strip()
        print(f"  {url}: {out.strip()}")

    # Headers detallados para los targets principales
    print("\n[*] === Headers detallados ===")
    headers_results = {}
    for url in TARGETS[:9]:
        cmd = (
            f"curl -sk -m 15 -A 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            f"AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36' "
            f"-I '{url}' 2>&1 | head -30"
        )
        out, _ = ssh_exec(client, cmd, timeout=20)
        headers_results[url] = out.strip()
        print(f"\n--- {url} ---\n{out.strip()[:600]}")

    # Guardar resultados
    results = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "vps": VPS_HOST,
        "dns": dns_results,
        "http_probe": http_results,
        "headers": headers_results,
    }

    out_file = r"c:\xampp\htdocs\pentagi\independencia_attack\hexagon_glm_recon.json"
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    print(f"\n[+] Recon guardado en {out_file}")

    client.close()
    print("[*] VPS desconectado")

if __name__ == "__main__":
    main()
