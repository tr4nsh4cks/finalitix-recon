import requests, json, time

INTELX_KEY = '6f65b43b-19df-4e12-aea3-115d793e9763'
INTELX_URL = 'https://2.intelx.io'
headers = {'x-key': INTELX_KEY, 'Content-Type': 'application/json'}

domains = ['mx.exchange', 'mxglobal.com.my']
all_results = {}

for domain in domains:
    print(f'\n{"="*60}')
    print(f'IntelX Phonebook EMAILS: {domain}')
    print(f'{"="*60}')
    body = {'term': domain, 'maxresults': 100, 'media': 0, 'target': 2}
    r = requests.post(f'{INTELX_URL}/phonebook/search', json=body, headers=headers, timeout=15)
    if r.status_code != 200:
        print(f'  Search failed: {r.status_code}')
        continue
    sid = r.json().get('id')
    time.sleep(4)
    
    r2 = requests.get(f'{INTELX_URL}/phonebook/search/result?id={sid}&limit=100&offset=0', headers=headers, timeout=15)
    if r2.status_code == 200:
        data = r2.json()
        selectors = data.get('selectors', [])
        print(f'  Results: {len(selectors)}')
        emails = []
        for s in selectors:
            val = s.get("selectorvalue", "?")
            typ = s.get("selectortype", "?")
            print(f'    {val} (type={typ})')
            emails.append(val)
        all_results[f'{domain}_emails'] = emails
    else:
        print(f'  Results failed: {r2.status_code}')

    print(f'\n{"="*60}')
    print(f'IntelX Phonebook DOMAINS: {domain}')
    print(f'{"="*60}')
    body2 = {'term': domain, 'maxresults': 100, 'media': 0, 'target': 1}
    r3 = requests.post(f'{INTELX_URL}/phonebook/search', json=body2, headers=headers, timeout=15)
    if r3.status_code == 200:
        sid2 = r3.json().get('id')
        time.sleep(4)
        r4 = requests.get(f'{INTELX_URL}/phonebook/search/result?id={sid2}&limit=100&offset=0', headers=headers, timeout=15)
        if r4.status_code == 200:
            data2 = r4.json()
            sels2 = data2.get('selectors', [])
            print(f'  Subdomains: {len(sels2)}')
            subs = []
            for s in sels2:
                val = s.get("selectorvalue", "?")
                print(f'    {val}')
                subs.append(val)
            all_results[f'{domain}_subdomains'] = subs

    print(f'\n{"="*60}')
    print(f'IntelX Intelligent LEAKS: {domain}')
    print(f'{"="*60}')
    body3 = {'term': domain, 'maxresults': 20, 'media': 0, 'sort': 2, 'terminate': []}
    r5 = requests.post(f'{INTELX_URL}/intelligent/search', json=body3, headers=headers, timeout=15)
    if r5.status_code == 200:
        sid3 = r5.json().get('id')
        time.sleep(6)
        r6 = requests.get(f'{INTELX_URL}/intelligent/search/result?id={sid3}&limit=20&offset=0', headers=headers, timeout=15)
        if r6.status_code == 200:
            data3 = r6.json()
            records = data3.get('records', [])
            print(f'  Leak records: {len(records)}')
            leaks = []
            for rec in records[:20]:
                name = rec.get('name', '?')
                bucket = rec.get('bucket', '?')
                size = rec.get('size', 0)
                added = rec.get('added', '?')
                systemid = rec.get('systemid', '?')
                storageid = rec.get('storageid', '?')
                print(f'    [{bucket}] {name} ({size} bytes) added={added}')
                leaks.append({
                    'name': name, 'bucket': bucket, 'size': size,
                    'added': added, 'systemid': systemid, 'storageid': storageid
                })
            all_results[f'{domain}_leaks'] = leaks

# Save
with open('c:\\xampp\\htdocs\\pentagi\\mxexchange_attack\\intelx_results.json', 'w') as f:
    json.dump(all_results, f, indent=2)
print(f'\n[+] Results saved to intelx_results.json')
print('DONE')
