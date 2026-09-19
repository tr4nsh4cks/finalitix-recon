#!/usr/bin/env python3
"""HEXAGON GLM - Vector 1 IntelX retry - more robust NoneType handling"""
import requests, json, time, sys, urllib3
from datetime import datetime
urllib3.disable_warnings()

INTELX_KEY = '6f65b43b-19df-4e12-aea3-115d793e9763'
INTELX_URL = 'https://2.intelx.io'
INTELX_HEADERS = {'x-key': INTELX_KEY, 'Content-Type': 'application/json'}

results = {
    'target': 'disperso.com',
    'vector': 'vector_1_intelx_retry',
    'run_at': datetime.utcnow().isoformat(),
    'phonebook': {},
    'intelligent': {},
    'file_reads': []
}

def log(m): print(f'[*] {m}', flush=True)

def safe_json(r):
    try:
        return r.json() or {}
    except Exception:
        return {}

def phonebook(term, target=1, label=''):
    log(f'  PB: {term} t={target} ({label})')
    try:
        r = requests.post(f'{INTELX_URL}/phonebook/search', headers=INTELX_HEADERS,
            json={'term': term, 'maxresults': 100, 'media': 0, 'target': target}, timeout=45)
        if r.status_code != 200:
            log(f'    status={r.status_code} body={r.text[:120]}')
            return []
        data = safe_json(r)
        sid = data.get('id')
        if not sid:
            log(f'    no search id returned')
            return []
        time.sleep(5)
        r2 = requests.get(f'{INTELX_URL}/phonebook/search/result',
            params={'id': sid, 'limit': 100, 'offset': 0}, headers=INTELX_HEADERS, timeout=45)
        if r2.status_code != 200:
            log(f'    results err: {r2.status_code}')
            return []
        data2 = safe_json(r2) or {}
        selectors = data2.get('selectors') or []
        if selectors is None:
            selectors = []
        log(f'    Found {len(selectors)} selectors')
        return selectors
    except Exception as e:
        log(f'    ERR: {e}')
        return []

def intelligent(term, label='', buckets=None):
    if buckets is None:
        buckets = ['leaks.logs', 'leaks.public', 'pastes', 'dumpster', 'web.public']
    log(f'  INT: {term} ({label})')
    try:
        r = requests.post(f'{INTELX_URL}/intelligent/search', headers=INTELX_HEADERS,
            json={'term': term, 'maxresults': 30, 'media': 0, 'buckets': buckets}, timeout=45)
        if r.status_code != 200:
            log(f'    status={r.status_code} body={r.text[:120]}')
            return []
        data = safe_json(r) or {}
        sid = data.get('id')
        if not sid:
            log(f'    no search id returned')
            return []
        time.sleep(8)
        r2 = requests.get(f'{INTELX_URL}/intelligent/search/result',
            params={'id': sid, 'limit': 30, 'offset': 0}, headers=INTELX_HEADERS, timeout=45)
        if r2.status_code != 200:
            log(f'    results err: {r2.status_code}')
            return []
        data2 = safe_json(r2) or {}
        records = data2.get('records') or []
        if records is None:
            records = []
        log(f'    Found {len(records)} records')
        return records
    except Exception as e:
        log(f'    ERR: {e}')
        return []

def read_file(systemid, bucket, label=''):
    try:
        r = requests.get(f'{INTELX_URL}/file/read',
            params={'type': 0, 'storageid': systemid, 'bucket': bucket, 'id': systemid},
            headers=INTELX_HEADERS, timeout=20)
        content = r.text[:2000] if r.text else ''
        log(f'      READ [{bucket}] {label[:40]}: status={r.status_code} len={len(r.text)}')
        results['file_reads'].append({
            'bucket': bucket, 'systemid': systemid, 'label': label,
            'status': r.status_code, 'preview': content
        })
        return content
    except Exception as e:
        log(f'      Read err: {e}')
        return ''

# Phonebook searches
pb_terms = [
    ('disperso.com', 1, 'emails'),
    ('disperso.com', 2, 'domains'),
    ('tuxpan.cl', 1, 'emails'),
    ('tuxpan.cl', 2, 'domains'),
    ('disperso', 1, 'partial'),
    ('dispersohq', 1, 'linkedin'),
    ('@disperso.com', 1, 'explicit'),
    ('@tuxpan.cl', 1, 'tuxpan-explicit'),
]
for term, target, label in pb_terms:
    sels = phonebook(term, target=target, label=label)
    results['phonebook'][f'{term}|t{target}|{label}'] = sels
    time.sleep(1)

# Intelligent searches
int_terms = [
    ('disperso.com password', 'pw-leak'),
    ('disperso.com login', 'login-leak'),
    ('disperso.com cognito', 'cognito-leak'),
    ('disperso.com aws', 'aws-leak'),
    ('disperso.com secret', 'secret-leak'),
    ('tuxpan.cl password', 'tuxpan-pw'),
    ('tuxpan.cl login', 'tuxpan-login'),
    ('disperso.com api_key', 'api-key'),
    ('rdrrxexkm4', 'api-gw-id'),
    ('us-east-2_SOCtEIx2s', 'cognito-pool'),
    ('4fjbm9cornhgfqk4o8m33rjt2f', 'cognito-client'),
]
for term, label in int_terms:
    recs = intelligent(term, label=label)
    results['intelligent'][f'{term}|{label}'] = recs
    # Only read files if we have valid records
    if recs and isinstance(recs, list):
        for rec in recs[:3]:
            if not isinstance(rec, dict):
                continue
            bucket = rec.get('bucket', '')
            sysid = rec.get('systemid', '')
            name = rec.get('name', '')[:80] if rec.get('name') else ''
            if sysid and bucket in ('leaks.logs', 'leaks.public', 'pastes', 'dumpster', 'leaks.restricted'):
                read_file(sysid, bucket, label=f'{term}|{name}')
                time.sleep(1)
    time.sleep(1)

# Save
out = '/tmp/hexagon_glm_intelx_retry.json'
with open(out, 'w') as f:
    json.dump(results, f, indent=2, default=str)
log(f'\n=== SAVED to {out} ===')
log(f'PB groups: {len(results["phonebook"])}, INT groups: {len(results["intelligent"])}, Reads: {len(results["file_reads"])}')
