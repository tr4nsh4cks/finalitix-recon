"""IntelX phonebook + intelligent search for disperso.com"""
import requests, json, time

INTELX_KEY = '6f65b43b-19df-4e12-aea3-115d793e9763'
INTELX_URL = 'https://2.intelx.io'
headers = {'x-key': INTELX_KEY, 'Content-Type': 'application/json'}

# 1. Phonebook - emails
print('=== IntelX Phonebook: disperso.com (emails) ===')
r = requests.post(f'{INTELX_URL}/phonebook/search', headers=headers, json={
    'term': 'disperso.com',
    'maxresults': 100,
    'media': 0,
    'target': 1
}, timeout=15)
print(f'Search status: {r.status_code}')
search_data = r.json()
search_id = search_data.get('id', '')
print(f'Search ID: {search_id}')

time.sleep(5)

r2 = requests.get(f'{INTELX_URL}/phonebook/search/result?id={search_id}&limit=100&offset=0', headers=headers, timeout=15)
print(f'Results status: {r2.status_code}')
results = r2.json()
selectors = results.get('selectors', [])
print(f'Found {len(selectors)} selectors')
for s in selectors:
    stype = s.get('selectortypeh', '')
    sval = s.get('selectorvalue', '')
    print(f'  [{stype}] {sval}')

# 2. Phonebook - domains
print('\n=== IntelX Phonebook: disperso.com (domains) ===')
r = requests.post(f'{INTELX_URL}/phonebook/search', headers=headers, json={
    'term': 'disperso.com',
    'maxresults': 100,
    'media': 0,
    'target': 2
}, timeout=15)
search_id = r.json().get('id', '')
time.sleep(5)
r2 = requests.get(f'{INTELX_URL}/phonebook/search/result?id={search_id}&limit=100&offset=0', headers=headers, timeout=15)
selectors = r2.json().get('selectors', [])
print(f'Found {len(selectors)} selectors')
for s in selectors:
    print(f'  [{s.get("selectortypeh", "")}] {s.get("selectorvalue", "")}')

# 3. Intelligent search for leaks
print('\n=== IntelX Intelligent: disperso.com ===')
r3 = requests.post(f'{INTELX_URL}/intelligent/search', headers=headers, json={
    'term': 'disperso.com',
    'maxresults': 50,
    'media': 0,
    'sort': 2,
    'terminate': []
}, timeout=15)
search_data2 = r3.json()
search_id2 = search_data2.get('id', '')
print(f'Search ID: {search_id2}')

time.sleep(5)

r4 = requests.get(f'{INTELX_URL}/intelligent/search/result?id={search_id2}&limit=50&offset=0', headers=headers, timeout=15)
results2 = r4.json()
records = results2.get('records', [])
print(f'Found {len(records)} records')
for rec in records[:30]:
    name = rec.get('name', '')
    bucket = rec.get('bucketh', '')
    size = rec.get('size', 0)
    date = rec.get('date', '')[:10]
    media = rec.get('mediah', '')
    print(f'  [{bucket}] [{media}] {name[:80]} ({size} bytes, {date})')

# Save results
with open(r'c:\xampp\htdocs\pentagi\disperso_recon\intelx_results.json', 'w') as f:
    json.dump({'selectors': selectors, 'records': records}, f, indent=2)
print('\nSaved to intelx_results.json')
