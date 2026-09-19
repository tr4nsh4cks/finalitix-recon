import re

with open(r'c:\xampp\htdocs\pentagi\disperso_recon\app_bundle.js', 'r', encoding='utf-8', errors='replace') as f:
    js = f.read()

print('=== REGISTER BUTTON / ROUTES ===')
for pat in ['register:"Registrate', 'Xt.REGISTER', 'REGISTER:', 'signUp(', '.signUp', 'PreSignUp', 'Rut indicado', 'taxId']:
    print(f'\n--- {pat} ---')
    count = 0
    for m in re.finditer(re.escape(pat), js):
        ctx = js[max(0,m.start()-160):m.end()+220].replace('\n',' ')
        print(f'  ...{ctx}...\n')
        count += 1
        if count >= 6:
            break

print('\n=== Xt FULL ===')
idx = js.find('Xt={')
print(js[idx:idx+1200] if idx>=0 else 'not found')

print('\n=== COUNTRY ENUM rn ===')
for m in re.finditer(r'rn=\{', js):
    print(js[m.start():m.start()+300])
    break
for m in re.finditer(r'PER:|MEX:|CHL:', js):
    ctx = js[max(0,m.start()-40):m.end()+80]
    if 'rn' in ctx or 'country' in ctx.lower() or 'CHL' in ctx:
        print(ctx)
        if m.start() > 2000000:
            break
