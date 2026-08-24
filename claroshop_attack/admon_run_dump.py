#!/usr/bin/env python3
# admon_run_dump.py — corre un PHP dump via admonplaza_query y parsea ROW:{json}
# Uso: python admon_run_dump.py <script.php> <out_json> [out_csv]
import sys, json, re, csv
from admonplaza_query import run_php_in_container

sys.stdout.reconfigure(errors='replace')

php_file = sys.argv[1]
out_json = sys.argv[2]
out_csv = sys.argv[3] if len(sys.argv) > 3 else None

php_code = open(php_file, encoding='utf-8').read()
out = run_php_in_container(php_code, timeout=600)

rows = []
for line in out.splitlines():
    m = re.search(r'ROW:(\{.*\})', line)
    if m:
        try:
            rows.append(json.loads(m.group(1)))
        except Exception:
            pass

# Lineas de status (sin framing bytes de docker)
status = [re.sub(r'[^\x20-\x7eáéíóúñÁÉÍÓÚÑ]', '', l).strip() for l in out.splitlines()
          if 'ROW:' not in l and l.strip()]
status = [s for s in status if s and not s.startswith('EXEC_ID')]

with open(out_json, 'w', encoding='utf-8') as f:
    json.dump(rows, f, indent=2, ensure_ascii=False)

print('STATUS:')
for s in status:
    print('  ' + s)
print('ROWS_PARSED: %d -> %s' % (len(rows), out_json))

if out_csv and rows:
    keys = list(rows[0].keys())
    with open(out_csv, 'w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=keys)
        w.writeheader()
        w.writerows(rows)
    print('CSV: %s (%d rows, %d cols)' % (out_csv, len(rows), len(keys)))
