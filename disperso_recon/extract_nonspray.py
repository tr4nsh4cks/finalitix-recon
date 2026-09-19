import re

with open(r'c:\xampp\htdocs\pentagi\disperso_recon\app_bundle.js', 'r', encoding='utf-8', errors='replace') as f:
    js = f.read()

keywords = [
    'invite', 'Invit', 'solicitar', 'demo', 'contacto', 'contact',
    'new-potential', 'potential', 'AdminCreate', 'hosted',
    'identityPool', 'IdentityPool', 'oauth', 'OAuth', 'Google',
    'microsoft', 'federat', 'sso', 'SSO', 'signUp', 'SignUp',
    'createUser', 'CreateUser', 'confirmSign', 'resend',
    'sourceMap', 'sourcemap', '.map', 'presigned',
    'bucket', 's3.amazonaws', 'extra_info', 'No tienes',
]
print('=== KEYWORD CONTEXTS ===')
seen = set()
for kw in keywords:
    for m in re.finditer(re.escape(kw), js):
        start = max(0, m.start() - 90)
        end = min(len(js), m.end() + 90)
        ctx = js[start:end].replace('\n', ' ')
        key = ctx[:80]
        if key in seen:
            continue
        seen.add(key)
        # skip ant design / recaptcha library noise
        if any(x in ctx for x in ['rc-upload', 'antNotification', 'grecaptcha', 'Upload:{', 'colorPrimary']):
            continue
        print(f'\n[{kw}] ...{ctx}...')
        if len(seen) > 80:
            break

print('\n\n=== extra_info / no tienes cuenta ===')
for m in re.finditer(r'No tienes|extra_info|solicita|contacto@|sales@', js, re.I):
    print(js[max(0,m.start()-80):m.end()+120].replace('\n',' '))
    print()
