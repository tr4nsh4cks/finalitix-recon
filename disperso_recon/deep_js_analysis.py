"""Deep JS bundle analysis for Disperso"""
import re, sys

bundle_path = sys.argv[1] if len(sys.argv) > 1 else r'c:\xampp\htdocs\pentagi\disperso_recon\app_bundle.js'

with open(bundle_path, 'rb') as f:
    js = f.read().decode('utf-8', errors='replace')

print(f'Bundle: {bundle_path}')
print(f'Size: {len(js)} chars')

# 1. All /api/* paths
print('\n=== ALL /api/* paths ===')
api_paths = re.findall(r'"(/?api/[^"]{3,80})"', js)
for p in sorted(set(api_paths)):
    print(f'  {p}')

# 2. Paths with /v1/
print('\n=== Paths with /v1/ ===')
v1_paths = re.findall(r'"(/?v1/[^"]{3,80})"', js)
for p in sorted(set(v1_paths)):
    print(f'  {p}')

# 3. React router paths
print('\n=== Route definitions (path:) ===')
routes = re.findall(r'path:\s*"(/?[a-zA-Z0-9/_:-]+)"', js)
for r2 in sorted(set(routes)):
    print(f'  {r2}')

# 4. User roles / permissions
print('\n=== User roles / permissions ===')
roles = re.findall(r'"((?:ROLE_|ADMIN|SUPER|VIEWER|EDITOR|MANAGER|OPERATOR|role_|admin|superadmin|viewer|owner|member)[A-Za-z_]*)"', js, re.I)
for r2 in sorted(set(roles)):
    if len(r2) > 3:
        print(f'  {r2}')

# 5. Cognito SDK patterns
print('\n=== Cognito SDK config ===')
cognito_strs = re.findall(r'"((?:CognitoIdentity|cognito-idp|UserPool|AppClient|IdentityPool|userPool|appClient)[^"]*)"', js, re.I)
for s in sorted(set(cognito_strs)):
    print(f'  {s}')

# 6. Amplify config
print('\n=== Amplify config values ===')
amplify = re.findall(r'(?:userPoolId|userPoolWebClientId|region|identityPoolId|authenticationFlowType)\s*:\s*"(.*?)"', js)
for a in sorted(set(amplify)):
    print(f'  {a}')

# 7. fetch/axios base URLs
print('\n=== Base URLs (fetch/axios) ===')
base_urls = re.findall(r'(?:baseURL|baseUrl|BASE_URL|apiUrl|API_URL|apiBase|API_BASE)\s*[:=]\s*"(https?://[^"]+)"', js, re.I)
for u in sorted(set(base_urls)):
    print(f'  {u}')

# Also look for concatenated URLs
concat_urls = re.findall(r'concat\("(https?://[^"]+)"', js)
for u in sorted(set(concat_urls)):
    print(f'  [concat] {u}')

# 8. Action names (CRUD operations)
print('\n=== Action/Mutation names ===')
actions = re.findall(r'"((?:create|update|delete|get|list|fetch|send|cancel|approve|reject|execute|validate|confirm|process|generate|export|import|download|upload)[A-Z][a-zA-Z]+)"', js)
for a in sorted(set(actions))[:60]:
    print(f'  {a}')

# 9. Status/Type enums
print('\n=== Status enums ===')
enums = re.findall(r'"((?:PENDING|APPROVED|REJECTED|COMPLETED|CANCELLED|PROCESSING|FAILED|ACTIVE|INACTIVE|DRAFT|SENT|RECEIVED|LIQUIDATED|IN_PROGRESS|PAID|UNPAID|EXPIRED|BLOCKED)[A-Z_]*)"', js)
for e in sorted(set(enums)):
    print(f'  {e}')

# 10. Error codes
print('\n=== Error messages/codes ===')
errors = re.findall(r'"((?:error|Error|ERROR|err_|ERR_)[^"]{5,80})"', js)
for e in sorted(set(errors))[:30]:
    print(f'  {e}')

# 11. S3 bucket names
print('\n=== S3 buckets ===')
s3 = re.findall(r'"([a-z0-9.-]+\.s3(?:\.[a-z0-9-]+)?\.amazonaws\.com[^"]*)"', js)
for s in sorted(set(s3)):
    print(f'  {s}')
s3_buckets = re.findall(r'"(s3://[^"]+)"', js)
for s in sorted(set(s3_buckets)):
    print(f'  {s}')

# 12. Lambda function names
print('\n=== Lambda/function names ===')
lambdas = re.findall(r'"((?:arn:aws:lambda|function:)[^"]+)"', js)
for l in sorted(set(lambdas)):
    print(f'  {l}')

# 13. ClientMetadata / validation data patterns
print('\n=== ClientMetadata / validation patterns ===')
metadata = re.findall(r'(?:ClientMetadata|clientMetadata|validationData|ValidationData)\s*[:=]\s*\{([^}]{1,300})\}', js)
for m in metadata:
    print(f'  {m[:200]}')

# 14. recaptchaResponse patterns
print('\n=== reCAPTCHA integration ===')
recaptcha = re.findall(r'["\']([^"\']*(?:recaptcha|captcha|g-recaptcha|grecaptcha)[^"\']*)["\']', js, re.I)
for r2 in sorted(set(recaptcha)):
    print(f'  {r2}')

# 15. Key context around "bank" endpoint (confirmed 401)
print('\n=== Context around "bank" endpoint ===')
idx = 0
while True:
    idx = js.find('/api/v1/bank', idx)
    if idx == -1:
        break
    start = max(0, idx - 200)
    end = min(len(js), idx + 200)
    context = js[start:end].replace('\n', ' ')
    print(f'  ...{context}...')
    idx += 1

# 16. Context around execute-api
print('\n=== Context around execute-api ===')
idx = 0
while True:
    idx = js.find('execute-api', idx)
    if idx == -1:
        break
    start = max(0, idx - 300)
    end = min(len(js), idx + 300)
    context = js[start:end].replace('\n', ' ')
    print(f'  ...{context[:500]}...')
    idx += 1

# 17. Look for REST method definitions paired with paths
print('\n=== REST method + path pairs ===')
methods = re.findall(r'(?:method|Method)\s*:\s*"(GET|POST|PUT|DELETE|PATCH)"[^}]{0,200}(?:url|path|endpoint)\s*:\s*"([^"]+)"', js)
for m, p in sorted(set(methods)):
    print(f'  {m} {p}')

methods2 = re.findall(r'\.(?:get|post|put|delete|patch)\s*\(\s*"([^"]+)"', js)
for p in sorted(set(methods2)):
    if '/' in p and len(p) > 3 and len(p) < 100:
        print(f'  .method("{p}")')
