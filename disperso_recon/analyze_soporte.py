"""Analyze soporte.disperso.com JS bundle"""
import re

with open(r'c:\xampp\htdocs\pentagi\disperso_recon\soporte_bundle.js', 'rb') as f:
    js = f.read().decode('utf-8', errors='replace')

print(f'Soporte bundle: {len(js)} chars')

# 1. API URLs
print('\n=== URLs ===')
urls = re.findall(r'"(https?://[^"]{10,200})"', js)
interesting = [u for u in set(urls) if 'disperso' in u or 'amazonaws' in u or 'cognito' in u or 'cloudflare' in u]
for u in sorted(interesting):
    print(f'  {u}')

# 2. API paths
print('\n=== API paths ===')
api_paths = re.findall(r'"(/api/[^"]{3,100})"', js)
for p in sorted(set(api_paths)):
    print(f'  {p}')

# 3. Auth patterns
print('\n=== Auth patterns ===')
auth = re.findall(r'"([^"]*(?:Bearer|Authorization|token|jwt|session|cookie|auth|login|turnstile|captcha)[^"]*)"', js, re.I)
for a in sorted(set(auth)):
    if len(a) > 3 and len(a) < 100:
        print(f'  {a}')

# 4. Cloudflare Turnstile (from CSP)
print('\n=== Turnstile/Captcha ===')
turnstile = re.findall(r'"([^"]*turnstile[^"]*)"', js, re.I)
for t in sorted(set(turnstile)):
    print(f'  {t}')

# Also Cloudflare challenge keys
cf_keys = re.findall(r'"(0x[A-Za-z0-9_-]{20,50})"', js)
for k in sorted(set(cf_keys)):
    print(f'  CF key: {k}')

# 5. Mesa/desk/ticket configuration
print('\n=== Mesa/desk config ===')
mesa = re.findall(r'"([^"]*(?:mesa|desk|ticket|agent|support|soporte|helpdesk|zendesk|intercom|freshdesk|crisp|tawk)[^"]*)"', js, re.I)
for m in sorted(set(mesa)):
    if len(m) > 3 and len(m) < 100:
        print(f'  {m}')

# 6. WebSocket patterns
print('\n=== WebSocket ===')
ws = re.findall(r'"(wss?://[^"]+)"', js)
for w in sorted(set(ws)):
    print(f'  {w}')

# Also SockJS/STOMP patterns
stomp = re.findall(r'"([^"]*(?:stomp|sockjs|websocket|ws/)[^"]*)"', js, re.I)
for s in sorted(set(stomp)):
    if len(s) > 3 and len(s) < 100:
        print(f'  {s}')

# 7. Route definitions
print('\n=== Routes ===')
routes = re.findall(r'path:\s*"([^"]+)"', js)
for r2 in sorted(set(routes)):
    print(f'  {r2}')

# 8. Fetch/axios base URLs
print('\n=== Base URLs ===')
base = re.findall(r'(?:baseURL|baseUrl|BASE_URL|apiUrl|API_URL)\s*[:=]\s*"([^"]+)"', js, re.I)
for b in sorted(set(base)):
    print(f'  {b}')

# 9. Context around "api" in template literals
print('\n=== Template API literals ===')
templates = re.findall(r'`(/api[^`]{3,120})`', js)
for t in sorted(set(templates)):
    print(f'  {t}')

# 10. Unique meaningful strings
print('\n=== Unique meaningful strings (mesa/soporte) ===')
meaningful = re.findall(r'"([^"]{5,80})"', js)
mesa_strings = set()
for m in meaningful:
    if any(kw in m.lower() for kw in ['mesa', 'ticket', 'agent', 'desk', 'chat', 'message', 'support', 'contact', 'email', 'phone']):
        if not any(skip in m.lower() for skip in ['css', 'svg', 'transform', 'animation', 'react', 'webpack']):
            mesa_strings.add(m)
for m in sorted(mesa_strings)[:50]:
    print(f'  {m}')
