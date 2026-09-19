import re

with open(r'c:\xampp\htdocs\pentagi\disperso_recon\app_bundle.js', 'r', encoding='utf-8', errors='replace') as f:
    js = f.read()

# 1. Find variable definitions for R8, Si, pi, Gu, GP, nMe, rMe, aMe, iMe
print("=== VARIABLE DEFINITIONS ===")
for var in ['R8', 'Si', 'pi', 'Gu', 'GP', 'nMe', 'rMe', 'aMe', 'iMe', 'eMe', 'Y6']:
    # Look for: VAR="..." or VAR=`...` or const VAR=... or ,VAR=...
    for m in re.finditer(rf'(?:const |let |var |,){var}\s*=\s*', js):
        ctx = js[m.start():m.end()+150]
        print(f'  {var}: ...{ctx}...\n')
    # Also look for assignment without declaration
    for m in re.finditer(rf'[,;](?:\s*){var}\s*=\s*["\'`]', js):
        ctx = js[m.start():m.end()+100]
        print(f'  {var} (assign): ...{ctx}...\n')

# 2. Find the Bn function definition (path builder)
print("\n=== Bn FUNCTION DEFINITION ===")
for m in re.finditer(r'function\s+Bn\s*\(', js):
    ctx = js[max(0,m.start()-30):m.end()+200]
    print(f'  ...{ctx}...\n')
# Also lambda: const Bn = ...
for m in re.finditer(r'Bn\s*=\s*(?:function|\()', js):
    ctx = js[max(0,m.start()-20):m.end()+200]
    print(f'  ...{ctx}...\n')

# 3. Find the complete path object (the big object with all PATH_ keys)
print("\n=== PATH OBJECT (all PATH_ keys) ===")
for m in re.finditer(r'PATH_\w+\s*:\s*Bn\s*\(', js):
    ctx = js[max(0,m.start()-10):m.end()+100]
    print(f'  ...{ctx}...')

# 4. Roles and permissions
print("\n\n=== ROLES/PERMISSIONS ===")
roles = re.findall(r'["\'](ROLE_[A-Z_]+|ADMIN|OPERATOR|VIEWER|OWNER|MANAGER)["\']', js)
for r in sorted(set(roles)):
    print(f'  {r}')

# Also look for allowedRoles
for m in re.finditer(r'allowedRoles', js):
    ctx = js[max(0,m.start()-30):m.end()+150]
    print(f'  allowedRoles: ...{ctx}...')

# 5. reCAPTCHA integration context
print("\n\n=== RECAPTCHA ===")
for m in re.finditer(r'captcha|recaptcha|reCAPTCHA|6Ld', js, re.I):
    ctx = js[max(0,m.start()-50):m.end()+100]
    if 'captcha' in ctx.lower() and 'notification' not in ctx.lower()[:30]:
        print(f'  ...{ctx}...\n')

# 6. File upload details (format, S3 integration)
print("\n=== FILE UPLOAD ===")
for m in re.finditer(r'presigned|upload|csv|xlsx|process-from-s3', js, re.I):
    ctx = js[max(0,m.start()-80):m.end()+100]
    if 'upload' in ctx.lower() or 'presigned' in ctx.lower() or 's3' in ctx.lower():
        if 'Upload' in ctx or 'upload' in ctx or 'presigned' in ctx.lower() or 's3' in ctx.lower():
            print(f'  ...{ctx}...\n')

# 7. S3 bucket references
print("\n=== S3 BUCKETS ===")
s3 = re.findall(r'["\']([\w.-]+\.s3[.\w-]*amazonaws\.com[^"\']*)["\']', js)
for b in set(s3):
    print(f'  {b}')
s3_2 = re.findall(r'["\'](s3://[^"\']+)["\']', js)
for b in set(s3_2):
    print(f'  {b}')
# Also look for bucket names
buckets = re.findall(r'["\']([\w-]+-(?:dev|prod|staging|test|uploads?|files?|documents?)[^"\']*)["\']', js)
for b in set(buckets):
    if len(b) > 5 and len(b) < 100:
        print(f'  Possible bucket: {b}')

# 8. Country codes and multi-tenant
print("\n=== COUNTRY/MULTI-TENANT ===")
countries = re.findall(r'countryCode["\']?\s*[=:]\s*["\']([\w]+)["\']', js)
for c in set(countries):
    print(f'  countryCode: {c}')
# Country references
for m in re.finditer(r'custom:country', js):
    ctx = js[max(0,m.start()-60):m.end()+120]
    print(f'  ...{ctx}...')

# 9. Environment variables / config
print("\n\n=== ENV CONFIG ===")
env = re.findall(r'(?:REACT_APP_|VITE_|process\.env\.)([\w]+)', js)
for e in sorted(set(env)):
    print(f'  {e}')
