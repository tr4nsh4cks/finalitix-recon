"""Extract all API calls and axios/fetch patterns from Disperso bundle"""
import re

with open(r'c:\xampp\htdocs\pentagi\disperso_recon\app_bundle.js', 'rb') as f:
    js = f.read().decode('utf-8', errors='replace')

# 1. Axios calls: Nt.get/post/put/delete/patch("path")
print('=== Axios calls (Nt.method) ===')
axios_calls = re.findall(r'Nt\.(get|post|put|delete|patch)\s*\(\s*["`]([^"`]+)["`]', js)
for method, path in sorted(set(axios_calls)):
    print(f'  {method.upper():6} {path}')

# Also try other axios variable names
print('\n=== Other HTTP calls ===')
other_calls = re.findall(r'(?:axios|http|api|client)\.(get|post|put|delete|patch)\s*\(\s*["`]([^"`]+)["`]', js, re.I)
for method, path in sorted(set(other_calls)):
    print(f'  {method.upper():6} {path}')

# 2. Template literal paths with variables
print('\n=== Template literal API paths ===')
template_paths = re.findall(r'`(/api/v1/[^`]{3,120})`', js)
for p in sorted(set(template_paths)):
    print(f'  {p}')

# Broader template search
template_paths2 = re.findall(r'`(/[a-z][^`]{3,100})`', js)
for p in sorted(set(template_paths2)):
    if '/api/' in p or '/v1/' in p:
        print(f'  {p}')

# 3. String concatenation patterns for URLs
print('\n=== Concatenated URL patterns ===')
concat = re.findall(r'"(/api/v1/[^"]+)"\s*\+', js)
for c in sorted(set(concat)):
    print(f'  {c}')
concat2 = re.findall(r'\+\s*"(/[^"]+)"', js)
for c in sorted(set(concat2)):
    if '/api/' in c or '/v1/' in c:
        print(f'  {c}')

# 4. Look for sandBox/sandbox references
print('\n=== Sandbox references ===')
sandbox_refs = []
for m in re.finditer(r'sand[Bb]ox', js):
    start = max(0, m.start() - 150)
    end = min(len(js), m.end() + 150)
    ctx = js[start:end].replace('\n', ' ')
    sandbox_refs.append(ctx)
for i, ctx in enumerate(sandbox_refs[:10]):
    print(f'  [{i}] ...{ctx}...')

# 5. Look for "bank" references (confirmed 401 endpoint)
print('\n=== "bank" API references ===')
for m in re.finditer(r'["\'/]bank(?:["\'/s]|$)', js):
    start = max(0, m.start() - 200)
    end = min(len(js), m.end() + 200)
    ctx = js[start:end].replace('\n', ' ')
    print(f'  ...{ctx[:350]}...')

# 6. Look for all endpoint string patterns
print('\n=== All quoted paths starting with / ===')
all_paths = re.findall(r'"(/[a-z][a-z0-9/_-]{4,60})"', js)
path_counts = {}
for p in all_paths:
    path_counts[p] = path_counts.get(p, 0) + 1
# Filter likely API paths (not CSS/React)
api_likely = {p: c for p, c in path_counts.items() 
              if not any(x in p for x in ['node_modules', 'react', 'src/', 'assets/', 'webpack', 'svg', 'icon', 'font', 'image'])}
for p in sorted(api_likely.keys()):
    print(f'  {p} (x{api_likely[p]})')

# 7. Look for TOKEN_EXPEI and session storage keys
print('\n=== Session storage keys ===')
storage_keys = re.findall(r'(?:sessionStorage|localStorage)\.\w+Item\s*\(\s*"?([^")\s]+)"?\s*\)', js)
for k in sorted(set(storage_keys)):
    print(f'  {k}')

# Also find jr.* constants
jr_consts = re.findall(r'jr\.([A-Z_]+)', js)
for k in sorted(set(jr_consts)):
    print(f'  jr.{k}')

# 8. Redux action types / store keys
print('\n=== Redux/Store keys ===')
store_keys = re.findall(r'(?:dispatch|useSelector|getState)\([^)]*(?:\.([a-zA-Z]+))', js)
for k in sorted(set(store_keys))[:30]:
    print(f'  {k}')

# 9. Look for "payment" related functions/endpoints
print('\n=== Payment-related strings ===')
payment_strs = re.findall(r'"([^"]*(?:payment|pago|transfer|transf|liquidaci|factura|cobro|abono|deposito|retiro|spei|stp|clabe)[^"]*)"', js, re.I)
for s in sorted(set(payment_strs)):
    if len(s) > 3 and len(s) < 100:
        print(f'  {s}')

# 10. Navigation/menu items (reveal features)
print('\n=== Menu/Navigation labels ===')
menu_items = re.findall(r'(?:label|title|name|text)\s*:\s*"([^"]{3,60})"', js)
unique_labels = set()
for m in menu_items:
    if any(kw in m.lower() for kw in ['pago', 'transfer', 'report', 'config', 'admin', 'usuario', 'banco', 'cuenta', 'factura', 'liquidac', 'comisi', 'masiv', 'online', 'cobro']):
        unique_labels.add(m)
for l in sorted(unique_labels):
    print(f'  {l}')
