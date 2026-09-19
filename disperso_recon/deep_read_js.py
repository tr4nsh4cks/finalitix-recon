import re, json

with open(r'c:\xampp\htdocs\pentagi\disperso_recon\app_bundle.js', 'r', encoding='utf-8', errors='replace') as f:
    js = f.read()

print(f'Bundle size: {len(js):,} chars')

# 1. ALL string literals that look like API/URL paths
paths = re.findall(r'["\'](/(?:api|v[12]|auth)[a-zA-Z0-9/_{}:.?&=-]*)["\']', js)
print('\n=== API PATH STRINGS ===')
for p in sorted(set(paths)):
    print(f'  {p}')

# 2. All URLs with disperso or amazonaws
urls = re.findall(r'["\'](https?://[^"\']{10,})["\']', js)
print('\n=== FULL URLs ===')
for u in sorted(set(urls)):
    if any(k in u.lower() for k in ['disperso', 'amazon', 'cognito', 'execute-api', 'cloudfront', 's3']):
        print(f'  {u}')

# 3. Path constant assignments (var/const/let NAME = "path" or {KEY: "path"})  
path_assigns = re.findall(r'(PATH[A-Z_]*|URL[A-Z_]*|ENDPOINT[A-Z_]*|API_[A-Z_]*)\s*[=:]\s*["\'](/[^"\']+)["\']', js)
print('\n=== PATH CONSTANTS ===')
for name, val in sorted(set(path_assigns)):
    print(f'  {name} = "{val}"')

# 4. Object property paths like Nt.get("/api/v1/...") or .post("/api/...")
api_calls = re.findall(r'\.(get|post|put|patch|delete|request)\s*\(\s*["\'](/[^"\']+)["\']', js, re.I)
print('\n=== DIRECT API CALLS (.get/.post etc) ===')
for method, path in sorted(set(api_calls)):
    print(f'  {method.upper():7} {path}')

# 5. Template literals with paths: `${base}/something`
template_paths = re.findall(r'`\$\{[^}]+\}(/[a-zA-Z0-9/_{}:.?&=-]+)`', js)
print('\n=== TEMPLATE LITERAL PATHS ===')
for p in sorted(set(template_paths)):
    print(f'  ${...}{p}')

# 6. String concatenation patterns: something + "/path"
concat = re.findall(r'\+\s*["\'](/[a-zA-Z0-9/_{}:.?&=-]+)["\']', js)
print('\n=== CONCATENATED PATH FRAGMENTS ===')
for p in sorted(set(concat)):
    print(f'  + "{p}"')

# 7. Context around "spei", "clabe", "transfer", "payment" (50 chars each side)
print('\n=== CONTEXT: spei/clabe/transfer/settlement ===')
for keyword in ['spei', 'SPEI', 'clabe', 'CLABE', 'settlement', 'Settlement']:
    for m in re.finditer(re.escape(keyword), js):
        start = max(0, m.start() - 80)
        end = min(len(js), m.end() + 80)
        ctx = js[start:end].replace('\n', ' ')
        print(f'\n  [{keyword}] ...{ctx}...')

# 8. Cognito config
print('\n=== COGNITO CONFIG ===')
cognito = re.findall(r'["\'](us-[a-z]+-\d_[A-Za-z0-9]+)["\']', js)
for c in set(cognito):
    print(f'  Pool: {c}')
clients = re.findall(r'["\']([\da-z]{20,40})["\']', js)
# Filter for likely Cognito client IDs
for c in set(clients):
    if len(c) >= 20 and len(c) <= 40 and c.isalnum():
        idx = js.index(c)
        ctx = js[max(0,idx-50):idx+len(c)+50]
        if 'client' in ctx.lower() or 'cognito' in ctx.lower() or 'pool' in ctx.lower():
            print(f'  Client: {c} (context: ...{ctx[:80]}...)')

# 9. Redux action types and store keys related to finance
print('\n=== FINANCE REDUX ACTIONS/KEYS ===')
finance_keys = re.findall(r'["\']((?:SET_|GET_|FETCH_|CREATE_|UPDATE_|DELETE_|RESET_)?(?:PAYMENT|TRANSFER|BANK|SETTLEMENT|ORDER|BALANCE|CLABE|SPEI|MOVEMENT|TRANSACTION|BENEFICIARY|SANDBOX)[A-Z_]*)["\']', js)
for k in sorted(set(finance_keys)):
    print(f'  {k}')

# 10. Route paths (React Router)
print('\n=== REACT ROUTER PATHS ===')
routes = re.findall(r'path\s*:\s*["\'](/[^"\']+)["\']', js)
for r2 in sorted(set(routes)):
    print(f'  {r2}')

# 11. Notification endpoint context
print('\n=== NOTIFICATION CONTEXT ===')
for m in re.finditer(r'notification', js, re.I):
    start = max(0, m.start() - 120)
    end = min(len(js), m.end() + 120)
    ctx = js[start:end].replace('\n', ' ')
    print(f'  ...{ctx}...')

# 12. Error messages (Spanish - business logic)
print('\n=== ERROR MESSAGES (Spanish) ===')
errors = re.findall(r'["\'](Error al [^"\']+)["\']', js)
for e in sorted(set(errors)):
    print(f'  {e}')
messages = re.findall(r'["\']((?:No se pudo|No existe|Ya existe|Debe|El campo|La cuenta|El pago|La transferencia|El monto|El archivo)[^"\']{5,80})["\']', js)
for m2 in sorted(set(messages)):
    print(f'  {m2}')
