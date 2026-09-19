import re

with open(r'c:\xampp\htdocs\pentagi\disperso_recon\app_bundle.js', 'r', encoding='utf-8', errors='replace') as f:
    js = f.read()

# 1. Context around "register" (200 chars each side)
print("=== REGISTER CONTEXT ===")
for m in re.finditer(r'register', js, re.I):
    ctx = js[max(0,m.start()-150):m.end()+150].replace('\n',' ')
    if '/register' in ctx or 'Register' in ctx or 'register/' in ctx:
        print(f'\n  ...{ctx}...\n')

# 2. Find base path variables (the ones used in template literals)
print("\n=== BASE PATH VARIABLES ===")
# Pattern: VARNAME=concat("base","/api/v1/something") or VARNAME="/api/v1/something"
base_paths = re.findall(r'(\w{1,4})\s*=\s*["`]([^"`]*api[^"`]*)["`]', js)
for var, val in set(base_paths):
    print(f'  {var} = "{val}"')

# Also look for the Bn() function calls that define paths
print("\n=== Bn() PATH DEFINITIONS ===")
bn_paths = re.findall(r'Bn\s*\(\s*["`]([^"`]+)["`]\s*\)', js)
for p in sorted(set(bn_paths)):
    print(f'  Bn("{p}")')

# And look for Bn with template literals
bn_template = re.findall(r'Bn\s*\(\s*`([^`]+)`\s*\)', js)
for p in sorted(set(bn_template)):
    print(f'  Bn(`{p}`)')

# 3. TOKEN_EXPEI and TOKEN_ACCESS context
print("\n=== TOKEN KEYS ===")
for keyword in ['TOKEN_EXPEI', 'TOKEN_ACCESS', 'TOKEN_REFRESH', 'TOKEN']:
    for m in re.finditer(keyword, js):
        ctx = js[max(0,m.start()-100):m.end()+100].replace('\n',' ')
        print(f'  [{keyword}] ...{ctx}...\n')

# 4. Nt (axios instance) interceptors and config
print("\n=== AXIOS CONFIG ===")
for m in re.finditer(r'Nt\.', js):
    ctx = js[max(0,m.start()-50):m.end()+100].replace('\n',' ')
    if 'interceptor' in ctx or 'defaults' in ctx or 'create' in ctx or 'baseURL' in ctx:
        print(f'  ...{ctx}...\n')

# 5. R8 and Si variables (base path holders)
print("\n=== R8 VARIABLE ===")
for m in re.finditer(r'R8[=,\s]', js):
    ctx = js[max(0,m.start()-80):m.end()+120].replace('\n',' ')
    if 'api' in ctx.lower() or 'path' in ctx.lower() or '/' in ctx:
        print(f'  ...{ctx}...\n')

print("\n=== Si VARIABLE ===")
for m in re.finditer(r'Si[=,\s/]', js):
    ctx = js[max(0,m.start()-30):m.end()+120].replace('\n',' ')
    if ('api' in ctx.lower() or 'path' in ctx.lower() or '/' in ctx) and 'Si ' not in ctx[:5]:
        print(f'  ...{ctx}...\n')

# 6. Full template literal API calls: `${something}/path`
print("\n=== FULL TEMPLATE LITERAL CALLS ===")
tpl_calls = re.findall(r'`(\$\{[^}]+\}/[^`]{3,60})`', js)
for t in sorted(set(tpl_calls)):
    print(f'  `{t}`')

# 7. sessionStorage keys
print("\n=== SESSION STORAGE KEYS ===")
ss_keys = re.findall(r'sessionStorage\.(?:get|set|remove)Item\s*\(\s*(\w+\.?\w*)', js)
for k in sorted(set(ss_keys)):
    print(f'  {k}')

# 8. Sandbox mode context
print("\n=== SANDBOX CONTEXT ===")
for m in re.finditer(r'sandBox|sandbox|SANDBOX', js):
    ctx = js[max(0,m.start()-100):m.end()+150].replace('\n',' ')
    if 'active' in ctx or 'toggle' in ctx or 'mode' in ctx or 'dispatch' in ctx or 'state' in ctx:
        print(f'  ...{ctx}...\n')

# 9. Password policy from error messages
print("\n=== PASSWORD POLICY ===")
for m in re.finditer(r'Debe|password|contrase', js, re.I):
    ctx = js[max(0,m.start()-20):m.end()+100].replace('\n',' ')
    if 'Debe' in ctx or 'password' in ctx.lower() or 'contrase' in ctx.lower():
        # Only show unique contexts
        if any(k in ctx for k in ['caracteres', 'especial', 'mayúscula', 'número', 'contrase']):
            print(f'  ...{ctx}...')
