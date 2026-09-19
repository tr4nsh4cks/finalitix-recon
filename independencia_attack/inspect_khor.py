import json
import io
import sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
d = json.load(open(r'c:\xampp\htdocs\pentagi\independencia_attack\hexagon_glm_ppp.json','r',encoding='utf-8'))
js = d['js_contents']
# Save khorComun.js.asp to a file
for k in js:
    if 'khorComun' in k or 'ajaxFunctions' in k:
        out_path = r'c:\xampp\htdocs\pentagi\independencia_attack\khorComun.js.asp'
        with open(out_path, 'w', encoding='utf-8') as f:
            f.write(js[k])
        print(f"Saved {k} -> {out_path} (size={len(js[k])})")

# Also save the HTML
with open(r'c:\xampp\htdocs\pentagi\independencia_attack\ppp_login.html','w',encoding='utf-8') as f:
    f.write(d['html'])
print("Saved ppp_login.html")

# Search for sendval function in khorComun
content = js.get('./khorComun.js.asp', '')
import re
# Find sendval definition
m = re.search(r'function\s+sendval\s*\([^)]*\)\s*\{[^}]*\}', content, re.DOTALL)
if m:
    print("\n=== sendval function ===")
    print(m.group(0))
# Find parseAndNavToURL
m = re.search(r'function\s+parseAndNavToURL\s*\([^)]*\)\s*\{[^}]*\}', content, re.DOTALL)
if m:
    print("\n=== parseAndNavToURL ===")
    print(m.group(0))
# Find MM_findObj
m = re.search(r'function\s+MM_findObj\s*\([^)]*\)\s*\{.*?\n\}', content, re.DOTALL)
if m:
    print("\n=== MM_findObj ===")
    print(m.group(0)[:2000])
# Find stripCharsInBag
m = re.search(r'function\s+stripCharsInBag\s*\([^)]*\)\s*\{[^}]*\}', content, re.DOTALL)
if m:
    print("\n=== stripCharsInBag ===")
    print(m.group(0))
