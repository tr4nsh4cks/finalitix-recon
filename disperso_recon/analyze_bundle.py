import re, sys

bundle_path = sys.argv[1] if len(sys.argv) > 1 else r'c:\xampp\htdocs\pentagi\disperso_recon\app_bundle.js'

with open(bundle_path, 'rb') as f:
    js = f.read().decode('utf-8', errors='replace')

print(f'Bundle size: {len(js)} chars')
print()

# Find disperso URLs
print('=== API URLs / Base URLs (disperso) ===')
urls = re.findall(r'https?://[a-zA-Z0-9._/-]+\.disperso\.com[a-zA-Z0-9._/:-]*', js)
for u in sorted(set(urls)):
    print(u)

print()
print('=== AWS / Cognito / S3 / Lambda URLs ===')
aws_urls = re.findall(r'"(https?://[^"]*(?:amazonaws|cognito|execute-api|cloudfront|s3\.)[^"]*)"', js)
for u in sorted(set(aws_urls))[:30]:
    print(u)

print()
print('=== Other interesting URLs ===')
other_urls = re.findall(r'"(https?://[^"]{10,200})"', js)
skip_domains = ['google', 'w3.org', 'mozilla', 'github', 'unpkg', 'cdnjs', 'gstatic', 'disperso',
                'facebook', 'twitter', 'react', 'webpack', 'babel', 'npmjs', 'sentry', 'jquery']
interesting = []
for u in set(other_urls):
    if not any(d in u.lower() for d in skip_domains):
        interesting.append(u)
for u in sorted(interesting)[:50]:
    print(u)

print()
print('=== API route patterns ===')
routes = re.findall(r'["\'](/(?:api|v[12]|auth|user|payment|transfer|company|account|wallet|transaction|webhook|config|admin|batch|report|upload|download|file|notification|setting|role|permission|org|dispers|customer|merchant|kyc|onboard|register|signup|login|logout|recover|reset|verify|otp|token|session|billing|invoice|receipt|bank|clabe|spei|stp)[a-zA-Z0-9/_{}:.-]*)["\']', js)
for p in sorted(set(routes))[:80]:
    print(p)

print()
print('=== Environment / Config variables ===')
env_vars = re.findall(r'(?:VITE_|REACT_APP_|NEXT_PUBLIC_|process\.env\.)[A-Z_]+', js)
for v in sorted(set(env_vars))[:30]:
    print(v)

print()
print('=== Auth strings (Bearer, token, cognito, etc.) ===')
auth_strs = re.findall(r'"((?:Bearer |x-api-key|Authorization|cognito|auth0|firebase|okta|X-Amz|aws-cognito|amplify)[^"]*)"', js, re.I)
for s in sorted(set(auth_strs))[:30]:
    print(s)

print()
print('=== Cognito / Auth Pool IDs ===')
cognito_ids = re.findall(r'["\']([a-z]+-[a-z]+-\d_[A-Za-z0-9]+)["\']', js)
for c in sorted(set(cognito_ids))[:10]:
    print(c)

pool_ids = re.findall(r'["\']([a-z]+-[a-z]+-\d+:[0-9a-f-]+)["\']', js)
for p in sorted(set(pool_ids))[:10]:
    print(p)

client_ids = re.findall(r'["\']([\da-z]{20,30})["\']', js)
print(f'\nPotential client IDs (20-30 alnum): {len(set(client_ids))} found')
for c in sorted(set(client_ids))[:20]:
    if not c.startswith('000'):
        print(f'  {c}')

print()
print('=== Hardcoded keys / secrets ===')
secrets = re.findall(r'"([A-Za-z0-9+/=_-]{32,128})"', js)
print(f'Potential secrets (32-128 b64): {len(set(secrets))} found')
for s in sorted(set(secrets), key=len, reverse=True)[:20]:
    if not all(c in '0123456789abcdef' for c in s.lower()):
        print(f'  [{len(s)}] {s[:80]}...' if len(s) > 80 else f'  [{len(s)}] {s}')

print()
print('=== reCAPTCHA site key ===')
recaptcha = re.findall(r'["\'](6L[a-zA-Z0-9_-]{38})["\']', js)
for r_key in sorted(set(recaptcha)):
    print(r_key)
