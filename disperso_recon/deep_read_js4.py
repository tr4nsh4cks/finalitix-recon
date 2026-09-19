import re

with open(r'c:\xampp\htdocs\pentagi\disperso_recon\app_bundle.js', 'r', encoding='utf-8', errors='replace') as f:
    js = f.read()

# 1. Find tMe object definition (the path segments object)
print("=== tMe OBJECT (path segments) ===")
idx = js.find('tMe={')
if idx >= 0:
    # Extract up to the next }
    end = js.find('}', idx)
    print(f'  {js[idx:end+1]}')

# 2. Find assignments like: pi = tMe.something or const {pi} = tMe
print("\n=== DESTRUCTURED/ASSIGNED VARIABLES ===")
# Look for: {VAR1:pi, VAR2:Si, ...} = tMe
destructure = re.findall(r'\{([^}]{20,300})\}\s*=\s*tMe', js)
for d in destructure:
    print(f'  Destructure: {d}')

# Look for: pi = tMe.something
for var in ['pi', 'Si', 'Gu', 'R8', 'GP', 'nMe', 'rMe', 'aMe', 'iMe']:
    assigns = re.findall(rf'{var}\s*=\s*tMe\.(\w+)', js)
    for a in assigns:
        print(f'  {var} = tMe.{a}')

# 3. Context around tMe - 500 chars to see full object + destructuring
print("\n=== tMe FULL CONTEXT (500 chars) ===")
idx = js.find('tMe=')
if idx >= 0:
    ctx = js[idx:idx+500]
    print(f'  {ctx}')

# 4. What comes after the tMe object? (the variable assignments)
print("\n=== AFTER tMe (1000 chars) ===")
if idx >= 0:
    end_brace = js.find('}', idx)
    ctx_after = js[end_brace:end_brace+1000]
    print(f'  {ctx_after}')

# 5. Explicit search for: variable = "/client-account" or "/payment-order" etc
print("\n=== DIRECT PATH ASSIGNMENTS ===")
for path_seg in ['/client-account', '/payment-order', '/movement', '/user', '/notification', '/settlement', '/bank', '/document']:
    # Find: VARNAME="/path" or VARNAME='/path'
    assigns = re.findall(rf'(\w{{1,5}})\s*=\s*["\']{path_seg}["\']', js)
    for var in assigns:
        print(f'  {var} = "{path_seg}"')

# 6. React Router paths (Xt object)
print("\n=== Xt ROUTE DEFINITIONS ===")
idx_xt = js.find('Xt={')
if idx_xt == -1:
    # Try: Xt.LOGIN = "..." pattern
    xt_defs = re.findall(r'Xt\.(\w+)\s*[:=]\s*["\'](/[^"\']+)["\']', js)
    for name, path in sorted(set(xt_defs)):
        print(f'  Xt.{name} = "{path}"')
else:
    ctx = js[idx_xt:idx_xt+500]
    print(f'  {ctx}')

# Try destructured: {LOGIN:...,DASHBOARD:...} = Xt or similar
print("\n=== Xt OBJECT ===")
for m in re.finditer(r'(?:const |let |var )?Xt\s*=\s*\{', js):
    ctx = js[m.start():m.start()+800]
    print(f'  {ctx}')

# 7. All named route definitions (alternative patterns)
print("\n=== NAMED ROUTES ===")
# Pattern: {name:"DASHBOARD", path:"/dashboard", ...}
routes = re.findall(r'name\s*:\s*["\']([\w_]+)["\'].*?path\s*:\s*["\'](/[^"\']+)["\']', js[:500000])
for name, path in routes:
    print(f'  {name} → {path}')

# Also: path:"..." from route config
routes2 = re.findall(r'name\s*:\s*["\']([\w_]+)["\'].*?path\s*:\s*(?:Xt\.[\w]+|["\'][^"\']+["\'])', js[:500000])
for r in routes2:
    print(f'  Route: {r}')
