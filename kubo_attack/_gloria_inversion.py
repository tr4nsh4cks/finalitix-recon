import requests, urllib3, sys, json, re
urllib3.disable_warnings()
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

BASE = 'https://www.api.kubofinanciero.cloud'
BASIC = 'aW50ZXJuYWwtdXNlci5hcHBzLmt1Ym9maW5hbmNpZXJvLmNvbTo4MDM2ZDliYTBlZTAwODkwNGIzODJjNDQ2N2YzNDVkNTExZTE4YjE3YTk4ZGRlYjExMDc3MGQ0MWUyMGYxYjFk'
GEO = '-99.17885920237521;19.363957498510498'
CB_AUTH = ('cuentas.apps.kubofinanciero.com', 'sGaNwsqu9rXFqauBHnDGg7uwjjU5FvKdcBEgesy2JZVA6dajWTQzdHYFpQC7d7fm')
VAULT = 'https://vault.kubofinanciero.cloud'
VH = {'X-Vault-Token': 's.ZqoLy9Wr91nCQEbverlhfKub'}

s = requests.Session()
s.trust_env = False
s.verify = False

r = s.post(BASE + '/security/login', headers={
    'Authorization': 'Basic ' + BASIC, 'Content-Type': 'application/x-www-form-urlencoded',
    'Geo-Position': GEO, 'X-Caller-Ip': '201.141.0.1'
}, data='grant_type=password&username=mifelnet@gmail.com&password=Aloverg4$11', timeout=15)
TOKEN = r.json()['access_token']
H = {'Authorization': 'Bearer ' + TOKEN, 'Access-Token': TOKEN, 'Content-Type': 'application/json', 'Geo-Position': GEO, 'X-Caller-Ip': '201.141.0.1'}

CLIENT_ID = 51622

# 1. Vault — check for inversion service creds
print('=== VAULT: INVERSION SERVICE ===')
vault_paths = [
    'services-prod/corebank-inversion-api',
    'services-prod/inversion-api',
    'services-prod/inversiones',
    'services-prod/corebank-inversiones',
]
for vp in vault_paths:
    try:
        rv = s.get(f'{VAULT}/v1/{vp}', headers=VH, timeout=8)
        if rv.status_code == 200:
            data = rv.json().get('data', {})
            print(f'\n[+] {vp}:')
            for k, v in sorted(data.items()):
                if isinstance(v, str) and len(v) < 200:
                    print(f'    {k} = {v}')
    except Exception as e:
        print(f'  [{vp}]: {str(e)[:60]}')

# 2. customer-gateway env — search for inversion URLs
print('\n\n=== CG ENV: INVERSION CONFIG ===')
try:
    r_env = s.get(BASE + '/customer-gateway/actuator/env', headers=H, timeout=10)
    if r_env.status_code == 200:
        env = r_env.json()
        for ps in env.get('propertySources', []):
            for k, v in ps.get('properties', {}).items():
                kl = k.lower()
                if any(x in kl for x in ['inversion', 'invest', 'fixed', 'plazo']):
                    print(f'  {k} = {v.get("value", "")}')
except Exception as e:
    print(f'  Error: {str(e)[:80]}')

# 3. Try direct SAFI /microfin paths for inversiones
print('\n\n=== MICROFIN DIRECT PATHS ===')
mf_paths = [
    f'/customer-gateway/microfin/inversionesPorCliente.htm?clienteID={CLIENT_ID}',
    f'/customer-gateway/microfin/listaInversiones.htm?clienteID={CLIENT_ID}',
    f'/customer-gateway/microfin/consultaInversion.htm?clienteID={CLIENT_ID}',
    f'/customer-gateway/microfin/inversionPlazoFijo.htm?clienteID={CLIENT_ID}',
]
for path in mf_paths:
    try:
        r2 = s.get(BASE + path, headers=H, timeout=8)
        if r2.status_code not in [404]:
            print(f'  GET {path.split("?")[0]}: [{r2.status_code}] {r2.text[:200]}')
    except:
        pass

# 4. Try investmentProducts or similar general endpoints
print('\n\n=== CG INVESTMENT PRODUCTS ===')
prod_paths = [
    '/customer-gateway/investment/products',
    '/customer-gateway/investment/rates',
    '/customer-gateway/fixedTerm/rates',
    '/customer-gateway/fixedTerm/products',
]
for path in prod_paths:
    try:
        r3 = s.get(BASE + path, headers=H, timeout=8)
        if r3.status_code == 200:
            print(f'  [+] {path}: {r3.text[:300]}')
    except:
        pass
