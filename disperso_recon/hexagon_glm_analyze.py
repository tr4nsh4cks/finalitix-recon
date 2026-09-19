#!/usr/bin/env python3
"""Analyze HEXAGON GLM results - extract findings"""
import json, sys

with open(r'c:\xampp\htdocs\pentagi\disperso_recon\hexagon_glm_results.json', 'r', encoding='utf-8') as f:
    d = json.load(f)

print('=' * 70)
print('HEXAGON GLM - DISPERSO ASSESSMENT - FINDINGS SUMMARY')
print('=' * 70)
print(f'Target: {d.get("target")}')
print(f'Run at: {d.get("run_at")}')
print(f'VPS: {d.get("vps")}')

for vname, vdata in d.get('vectors', {}).items():
    print(f'\n{"=" * 70}')
    print(f'VECTOR: {vname}')
    print('=' * 70)
    if 'error' in vdata:
        print(f'  ERROR: {vdata["error"]}')
        continue
    data = vdata.get('data', {})

    if vname == 'vector_1_intelx':
        print('\n--- Phonebook results ---')
        for key, sels in data.get('phonebook', {}).items():
            print(f'\n  [{key}]: {len(sels)} selectors')
            for s in sels[:10]:
                sv = s.get('selectorvalue', '') if isinstance(s, dict) else str(s)
                st = s.get('selectortypeh', '') if isinstance(s, dict) else ''
                print(f'    [{st}] {sv}')
        print('\n--- Intelligent results ---')
        for key, recs in data.get('intelligent', {}).items():
            print(f'\n  [{key}]: {len(recs)} records')
            for r in recs[:5]:
                if isinstance(r, dict):
                    name = r.get('name', '')[:80]
                    bucket = r.get('bucket', '')
                    added = r.get('added', '')[:10]
                    print(f'    [{bucket}] {name} ({added})')
        print(f'\n--- File reads: {len(data.get("file_reads", []))} ---')
        for fr in data.get('file_reads', []):
            print(f'  [{fr.get("bucket")}] {fr.get("label","")[:50]}: status={fr.get("status")} preview={fr.get("preview","")[:200]}')

    elif vname == 'vector_2_github':
        print('\n--- Code searches (401 = unauth) ---')
        for entry in data.get('code', []):
            if 'error' in entry:
                print(f'  {entry.get("query")}: {entry.get("error")}')
            else:
                print(f'  {entry.get("query")}: total={entry.get("total_count")} items={len(entry.get("items",[]))}')
        print('\n--- Commits ---')
        for entry in data.get('commits', []):
            print(f'  Query: {entry.get("query")} | total={entry.get("total_count")}')
            for it in entry.get('items', [])[:20]:
                print(f'    {it.get("repo")} | {it.get("author")} | {it.get("email")} | {it.get("message","")[:80]}')
        print('\n--- Repos ---')
        for entry in data.get('repos', []):
            print(f'  Query: {entry.get("query")} | total={entry.get("total_count")}')
            for it in entry.get('items', [])[:15]:
                print(f'    {it.get("full_name")} | stars={it.get("stars")} | {(it.get("description") or "")[:80]}')
        print('\n--- Secret hits ---')
        if not data.get('secrets'):
            print('  (none)')
        for s in data.get('secrets', []):
            print(f'  REPO: {s.get("repo")} | PATH: {s.get("path")}')
            print(f'    HITS: {s.get("hits")}')
            print(f'    PREVIEW: {s.get("preview","")[:500]}')

    elif vname == 'vector_3_notification':
        print(f'\nWebhook ID for XSS verification: {data.get("webhook_id")}')
        print('\n--- CDN (api.disperso.com) results ---')
        for entry in data.get('cdn', []):
            print(f'  {entry.get("label")}: status={entry.get("status")} len={entry.get("length")} body={entry.get("body_preview","")[:100]}')
        print('\n--- Gateway (direct API GW) results ---')
        for entry in data.get('gateway', []):
            print(f'  {entry.get("label")}: status={entry.get("status")} len={entry.get("length")} body={entry.get("body_preview","")[:100]}')

    elif vname == 'vector_4_jwt':
        print(f'\nForged tokens: {len(data.get("forged_tokens",[]))}')
        for t in data.get('forged_tokens', []):
            print(f'  {t.get("name")}: {t.get("token","")[:100]}...')
        print(f'\nEndpoint tests: {len(data.get("endpoints",[]))}')
        # Show non-401/403 results
        non_auth = [e for e in data.get('endpoints', []) if e.get('status') not in (401, 403)]
        if non_auth:
            print(f'\n*** NON-401/403 RESULTS ({len(non_auth)}): ***')
            for e in non_auth:
                print(f'  {e.get("endpoint")} [{e.get("token_name")}] {e.get("base")}: {e.get("status")} ({e.get("length")}b)')
                print(f'    Body: {e.get("body_preview","")[:200]}')
        else:
            print('\n  All 168 endpoint tests returned 401/403 (JWT null alg does NOT bypass)')

    elif vname == 'vector_5_actuator':
        print(f'\nEndpoint tests: {len(data.get("endpoints",[]))}')
        non_403 = [e for e in data.get('endpoints', []) if e.get('status') not in (403, 404)]
        if non_403:
            print(f'\n*** NON-403/404 RESULTS ({len(non_403)}): ***')
            for e in non_403:
                print(f'  [{e.get("base")}] {e.get("method")} {e.get("path")}: {e.get("status")} ({e.get("length")}b) CT={e.get("content_type","")}')
                print(f'    Body: {e.get("body_preview","")[:300]}')
        else:
            print('\n  All 92 actuator/api-docs tests returned 403/404 (no exposure)')

print('\n' + '=' * 70)
print('END OF REPORT')
print('=' * 70)
