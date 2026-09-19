import json, re
d = json.load(open(r'c:\xampp\htdocs\pentagi\independencia_attack\hexagon_glm_ppp.json','r',encoding='utf-8'))
js = d['js_contents']
content = js.get('./khorComun.js.asp', '')

# Find full sendval function with nested braces
def find_function(content, name):
    idx = content.find(f'function {name}(')
    if idx < 0:
        return None
    # Find matching closing brace
    depth = 0
    start = content.find('{', idx)
    if start < 0:
        return None
    i = start
    while i < len(content):
        if content[i] == '{':
            depth += 1
        elif content[i] == '}':
            depth -= 1
            if depth == 0:
                return content[idx:i+1]
        i += 1
    return None

for fname in ['sendval', 'parseAndNavToURL', 'navLogin', 'submitForm', 'doLogin', 'login']:
    f = find_function(content, fname)
    if f:
        print(f"\n=== {fname} ===")
        print(f[:3000])

# Also look for any function that calls .submit()
print("\n=== .submit() calls ===")
for m in re.finditer(r'\w+\.submit\(\)', content):
    start = max(0, m.start() - 200)
    end = min(len(content), m.end() + 100)
    print(content[start:end])
    print("---")

# Look for 'usr' and 'pwd' references
print("\n=== 'usr' / 'pwd' refs in khorComun ===")
for m in re.finditer(r"['\"](?:usr|pwd|usuario|password|user|pass)['\"]", content, re.IGNORECASE):
    start = max(0, m.start() - 100)
    end = min(len(content), m.end() + 100)
    print(content[start:end])
    print("---")
