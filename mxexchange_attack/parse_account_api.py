import json

with open(r"C:\Users\Usuario\.cursor\projects\c-xampp-htdocs-pentagi\agent-tools\2543b2b4-04ac-48ee-b1aa-bd05edbc0eff.txt", "r") as f:
    spec = json.loads(f.read())

# Find Register endpoint
for path, methods in spec["paths"].items():
    if "register" in path.lower() or "login" in path.lower() or "auth" in path.lower():
        print(f"\n{'='*60}")
        print(f"ENDPOINT: {path}")
        for method, detail in methods.items():
            print(f"  METHOD: {method.upper()}")
            print(f"  OPERATION: {detail.get('operationId','?')}")
            print(f"  TAGS: {detail.get('tags',[])}")
            if 'parameters' in detail:
                for p in detail['parameters']:
                    if p.get('in') == 'body' and '$ref' in p.get('schema', {}):
                        ref = p['schema']['$ref'].split('/')[-1]
                        print(f"  BODY MODEL: {ref}")
                        if ref in spec.get('definitions', {}):
                            model = spec['definitions'][ref]
                            print(f"    PROPERTIES:")
                            for prop, pdetail in model.get('properties', {}).items():
                                req = "REQUIRED" if prop in model.get('required', []) else "optional"
                                ptype = pdetail.get('type', pdetail.get('$ref', '?'))
                                print(f"      - {prop}: {ptype} ({req})")
                    elif p.get('in') == 'body' and 'properties' in p.get('schema', {}):
                        print(f"  BODY INLINE:")
                        for prop, pdetail in p['schema']['properties'].items():
                            print(f"      - {prop}: {pdetail.get('type','?')}")
                    elif p.get('in') != 'body':
                        print(f"  PARAM: {p['name']} (in={p['in']}, type={p.get('type','?')}, required={p.get('required',False)})")

# Also check for RegisterBindingModel / RegisterViewModel in definitions
print(f"\n{'='*60}")
print("REGISTRATION-RELATED MODELS:")
for name, model in spec.get('definitions', {}).items():
    if 'register' in name.lower() or 'login' in name.lower() or 'auth' in name.lower() or 'token' in name.lower():
        print(f"\n  MODEL: {name}")
        for prop, pdetail in model.get('properties', {}).items():
            req = "REQUIRED" if prop in model.get('required', []) else "optional"
            ptype = pdetail.get('type', pdetail.get('$ref', '?'))
            fmt = pdetail.get('format', '')
            print(f"    - {prop}: {ptype} {fmt} ({req})")

# Also dump all endpoint paths for overview
print(f"\n{'='*60}")
print("ALL ENDPOINT PATHS:")
for path in sorted(spec["paths"].keys()):
    methods = list(spec["paths"][path].keys())
    print(f"  {', '.join(m.upper() for m in methods):10s} {path}")
