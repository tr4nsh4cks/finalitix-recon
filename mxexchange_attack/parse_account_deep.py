import json

# Parse Account API spec for login/token endpoints
with open(r"C:\Users\Usuario\.cursor\projects\c-xampp-htdocs-pentagi\agent-tools\2543b2b4-04ac-48ee-b1aa-bd05edbc0eff.txt") as f:
    spec = json.loads(f.read())

print("=== ALL PATHS (grouped) ===\n")
paths = sorted(spec["paths"].keys())
for p in paths:
    methods = list(spec["paths"][p].keys())
    ms = ", ".join(m.upper() for m in methods)
    tags = set()
    for m in methods:
        tags.update(spec["paths"][p][m].get("tags", []))
    print(f"  {ms:20s} {p:55s} [{', '.join(tags)}]")

# Find ALL models that mention token, balance, wallet, login
print("\n\n=== KEY MODELS ===\n")
for name, model in spec.get("definitions", {}).items():
    props = list(model.get("properties", {}).keys())
    if any(k in name.lower() for k in ["balance", "wallet", "login", "token", "openapi", "key", "broker"]):
        print(f"\n  MODEL: {name}")
        for prop, det in model.get("properties", {}).items():
            t = det.get("type", det.get("$ref", "?").split("/")[-1])
            fmt = det.get("format", "")
            req = "REQ" if prop in model.get("required", []) else ""
            print(f"    {prop}: {t} {fmt} {req}".strip())
