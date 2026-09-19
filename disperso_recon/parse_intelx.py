import json

with open(r"c:\xampp\htdocs\pentagi\disperso_recon\intelx_results.json") as f:
    d = json.load(f)

print("=== DISPERSO.COM PHONEBOOK ===")
disp = d.get("disperso_phonebook", [])
for v in disp:
    print(f"  {v}")
print(f"Total disperso: {len(disp)}")

print("\n=== TUXPAN.CL REAL EMAILS (sin hashes) ===")
tux = d.get("tuxpan_phonebook", [])
real_emails = []
for v in tux:
    sv = str(v)
    # Solo emails reales (sin hex hashes y no subdominios)
    if "@tuxpan.cl" in sv:
        local = sv.split("@")[0]
        # skip hex hashes (long hex strings with dots)
        if len(local) > 20 and all(c in "0123456789abcdef." for c in local):
            continue
        real_emails.append(sv)
        print(f"  {sv}")

print(f"\nTotal real tuxpan emails: {len(real_emails)}")

# Pattern inference
print("\n=== PATRÓN DE EMAIL (derivado) ===")
print("Patrón confirmado: [inicial_nombre][apellido]@tuxpan.cl")
print("Empleados mapeados:")
people = [
    ("Patricia", "Erazo", "CEO"),
    ("Sandra", "Ulloa", "Comercial"),
    ("Daniela", "Canales", "Lead Qualifier"),
    ("Monica", "Rojas", "Team"),
    ("Christian", "Ramirez", "SOPORTE/DEV"),
    ("Jonathan", "Hernandez", "SW Engineer"),
    ("Willians", "Briones", "DevOps"),
    ("Esteban", "Conejeros", "Architect"),
]
for fname, lname, role in people:
    pattern_tux = f"{fname[0].lower()}{lname.lower()}@tuxpan.cl"
    pattern_dis = f"{fname[0].lower()}{lname.lower()}@disperso.com"
    fname_dis = f"{fname.lower()}@disperso.com"
    print(f"  {role}: {pattern_tux} | {pattern_dis} | {fname_dis}")
