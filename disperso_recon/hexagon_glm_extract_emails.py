#!/usr/bin/env python3
"""Extract real (non-anonymized) emails from IntelX tuxpan.cl results"""
import json, re

with open(r'c:\xampp\htdocs\pentagi\disperso_recon\hexagon_glm_intelx_retry.json', 'r', encoding='utf-8') as f:
    d = json.load(f)

# Anonymized emails look like: 3a1b18df.d6797c5c@tuxpan.cl (hex.hex@ with 7-8 hex each segment)
anon_pattern = re.compile(r'^[0-9a-f]{7,8}\.[0-9a-f]{6,8}@')

all_emails = []
print('=== ALL TUXPAN.CL EMAILS (100 selectors) ===')
for key, sels in d.get('phonebook', {}).items():
    if 'tuxpan' not in key:
        continue
    for s in sels:
        if isinstance(s, dict):
            sv = s.get('selectorvalue', '')
            st = s.get('selectortypeh', '')
            if st == 'Email Address' and '@tuxpan.cl' in sv:
                all_emails.append(sv)

# Dedupe
all_emails = list(set(all_emails))
real_emails = [e for e in all_emails if not anon_pattern.match(e)]
anon_emails = [e for e in all_emails if anon_pattern.match(e)]

print(f'\nTotal emails: {len(all_emails)}')
print(f'Real (named) emails: {len(real_emails)}')
print(f'Anonymized emails: {len(anon_emails)}')

print('\n=== REAL EMAILS (usable for spray) ===')
for e in sorted(real_emails):
    print(f'  {e}')

print('\n=== ANONYMIZED EMAILS (hashed - not directly usable) ===')
for e in sorted(anon_emails)[:20]:
    print(f'  {e}')
if len(anon_emails) > 20:
    print(f'  ... and {len(anon_emails)-20} more')

# Also show disperso.com emails
print('\n=== DISPERSO.COM EMAILS ===')
for key, sels in d.get('phonebook', {}).items():
    if 'disperso' not in key:
        continue
    for s in sels:
        if isinstance(s, dict):
            sv = s.get('selectorvalue', '')
            st = s.get('selectortypeh', '')
            if st == 'Email Address':
                print(f'  {sv}')

# Generate possible Disperso emails from Tuxpan naming patterns
print('\n=== POSSIBLE DISPERSO EMAILS (inferred from Tuxpan naming) ===')
# Extract first names / patterns from tuxpan emails
first_names = set()
for e in real_emails:
    local = e.split('@')[0]
    # Strip numbers, dots
    base = re.sub(r'[0-9.]+', '', local)
    if base and len(base) > 2:
        first_names.add(base.lower())

# Common patterns: first@, first.last@, flast@, firstl@
inferred = []
for fn in sorted(first_names):
    inferred.append(f'{fn}@disperso.com')
    if len(fn) > 3:
        inferred.append(f'{fn[0]}{fn}@disperso.com')  # flast
print(f'  Generated {len(inferred)} inferred emails from {len(first_names)} base names')
for e in inferred[:30]:
    print(f'  {e}')

# Save consolidated
out = {
    'tuxpan_real_emails': sorted(real_emails),
    'tuxpan_anon_emails': sorted(anon_emails),
    'disperso_emails': ['sales@disperso.com'],
    'inferred_disperso_emails': inferred,
    'first_names_extracted': sorted(first_names)
}
with open(r'c:\xampp\htdocs\pentagi\disperso_recon\hexagon_glm_emails_consolidated.json', 'w', encoding='utf-8') as f:
    json.dump(out, f, indent=2)
print(f'\nSaved to hexagon_glm_emails_consolidated.json')
