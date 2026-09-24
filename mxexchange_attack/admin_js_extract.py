import re, sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

f = open(r'c:\xampp\htdocs\pentagi\mxexchange_attack\admin_admin-hkdev_mx_exchange_main.js', 'r', encoding='utf-8', errors='replace')
text = f.read()
f.close()
print(f'Admin main.js size: {len(text)} bytes')

# Find SystemConstants - webpack bundled, so look for the key assignment patterns
patterns = [
    (r'SystemConstants\s*=\s*\{([^}]{10,500})\}', 'SystemConstants object'),
    (r'SystemConstants\.(\w+)\s*=\s*"([^"]+)"', 'SystemConstants.X = "..."'),
    (r'class\s+SystemConstants[^{]*\{([^}]{10,2000})\}', 'class SystemConstants'),
    (r'SystemConstants\.ClientId\s*=\s*"([^"]+)"', 'SystemConstants.ClientId'),
    (r'SystemConstants\.ClientSecret\s*=\s*"([^"]+)"', 'SystemConstants.ClientSecret'),
    (r'SystemConstants\.GrantType\s*=\s*"([^"]+)"', 'SystemConstants.GrantType'),
    (r'ClientId\s*=\s*"([^"]{3,80})"', 'ClientId = "..."'),
    (r'ClientSecret\s*=\s*"([^"]{3,80})"', 'ClientSecret = "..."'),
    (r'GrantType\s*=\s*"([^"]{3,80})"', 'GrantType = "..."'),
    (r'client_id\s*:\s*"([^"]+)"', 'client_id: "..."'),
    (r'client_secret\s*:\s*"([^"]+)"', 'client_secret: "..."'),
    (r'scope\s*:\s*"([a-zA-Z0-9._\- ]{5,100})"', 'scope: "..."'),
    (r'authority\s*:\s*"(https?://[^"]+)"', 'authority: "..."'),
    (r'stsServer\s*:\s*"(https?://[^"]+)"', 'stsServer: "..."'),
    (r'identityApi\s*:\s*"(https?://[^"]+)"', 'identityApi: "..."'),
    (r'accountApi\s*:\s*"(https?://[^"]+)"', 'accountApi: "..."'),
    (r'walletApi\s*:\s*"(https?://[^"]+)"', 'walletApi: "..."'),
    (r'orderBookApi\s*:\s*"(https?://[^"]+)"', 'orderBookApi: "..."'),
    (r'notificationApi\s*:\s*"(https?://[^"]+)"', 'notificationApi: "..."'),
    (r'commonApi\s*:\s*"(https?://[^"]+)"', 'commonApi: "..."'),
    (r'apiUrl\s*:\s*"(https?://[^"]+)"', 'apiUrl: "..."'),
    (r'"api[Kk]ey"\s*:\s*"([^"]+)"', 'apiKey: "..."'),
    (r'"[Aa]dmin[Kk]ey"\s*:\s*"([^"]+)"', 'AdminKey: "..."'),
    (r'"[Ss]ecret[Kk]ey"\s*:\s*"([^"]+)"', 'SecretKey: "..."'),
    (r'password\s*:\s*"([^"]{4,50})"', 'password: "..."'),
    (r'redirect_uri\s*:\s*"([^"]+)"', 'redirect_uri: "..."'),
    (r'postLogoutRedirectUri\s*:\s*"([^"]+)"', 'postLogoutRedirectUri: "..."'),
]

print("\n--- ADMIN JS Pattern Matches ---\n")
for pat, label in patterns:
    matches = re.findall(pat, text)
    if matches:
        unique_matches = []
        seen = set()
        for m in matches:
            key = str(m) if isinstance(m, str) else str(m)
            if key not in seen:
                seen.add(key)
                unique_matches.append(m)
        for m in unique_matches[:8]:
            if isinstance(m, tuple):
                print(f'  [{label}] {m}')
            else:
                clean = m[:200]
                print(f'  [{label}] {clean}')

# Also look for the specific WEBPACK constant class pattern
# In Angular admin apps, it's typically a module that exports constants
print("\n--- WEBPACK Constants Search ---\n")

# Find context around SystemConstants
idx = 0
count = 0
while idx < len(text) and count < 20:
    idx = text.find('SystemConstants', idx)
    if idx == -1:
        break
    start = max(0, idx - 50)
    end = min(len(text), idx + 200)
    snippet = text[start:end].encode('ascii', 'replace').decode('ascii')
    snippet = re.sub(r'\s+', ' ', snippet)
    print(f'  @{idx}: ...{snippet}...')
    idx += 15
    count += 1

# Look for the typical Angular environment config
print("\n--- Angular Environment Config ---\n")
env_patterns = [
    r'environment\s*=\s*\{([^}]{20,2000})\}',
    r'environment\.production\s*=\s*(true|false)',
    r'production\s*:\s*(true|false)',
]
for pat in env_patterns:
    matches = re.findall(pat, text)
    if matches:
        for m in matches[:3]:
            clean = m[:500].encode('ascii', 'replace').decode('ascii')
            print(f'  {clean}')

# Search for any URL that looks like an API endpoint
print("\n--- API URLs Found ---\n")
urls = re.findall(r'"(https?://[a-zA-Z0-9._\-:]+(?:mx\.exchange|azurewebsites\.net)[^"]*)"', text)
unique_urls = list(set(urls))
for u in sorted(unique_urls)[:30]:
    print(f'  {u}')
