#!/usr/bin/env python3
# admon_run_multidump.py — corre PHP multi-tabla (ROW:<tabla>|<json>) y guarda JSON por tabla
# Uso: python admon_run_multidump.py <script.php> <out_prefix>
import sys, json, re, os
from admonplaza_query import run_php_in_container

sys.stdout.reconfigure(errors='replace')

php_file = sys.argv[1]
prefix = sys.argv[2]

php_code = open(php_file, encoding='utf-8').read()
out = run_php_in_container(php_code, timeout=900)

tables = {}
for line in out.splitlines():
    m = re.search(r'ROW:([A-Za-z0-9_]+)\|(\{.*\})', line)
    if m:
        t = m.group(1)
        try:
            row = json.loads(m.group(2))
            tables.setdefault(t, []).append(row)
        except Exception:
            pass

status = [re.sub(r'[^\x20-\x7e]', '', l).strip() for l in out.splitlines()
          if 'ROW:' not in l and l.strip()]
status = [s for s in status if s and not s.startswith('EXEC_ID')]
print('STATUS:')
for s in status:
    print('  ' + s)

result = {'tables': {t: len(r) for t, r in tables.items()}}
out_file = prefix + '.json'
with open(out_file, 'w', encoding='utf-8') as f:
    json.dump(tables, f, indent=2, ensure_ascii=False)

print('SAVED: %s' % out_file)
for t, rows in sorted(tables.items()):
    print('  %-40s %6d rows' % (t, len(rows)))
