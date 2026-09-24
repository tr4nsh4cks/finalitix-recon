import requests, json, sys, re, urllib3
urllib3.disable_warnings()
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
T = 30

BASE = "https://app.mx.exchange"
H = {"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36","Accept":"*/*"}

js_files = [
    "main.a9f9f1eacd481f95.js",
    "runtime.ac3e18b8368daa4f.js",
    "scripts.9613bb131e37a8ce.js",
]

patterns = [
    (r'client_id[\s":=\']+([a-zA-Z0-9._\-]+)', "client_id"),
    (r'clientId[\s":=\']+([a-zA-Z0-9._\-]+)', "clientId"),
    (r'client_secret[\s":=\']+([a-zA-Z0-9._\-]+)', "client_secret"),
    (r'clientSecret[\s":=\']+([a-zA-Z0-9._\-]+)', "clientSecret"),
    (r'authority[\s":=\']+([a-zA-Z0-9._\-:/]+)', "authority"),
    (r'identityUrl[\s":=\']+([a-zA-Z0-9._\-:/]+)', "identityUrl"),
    (r'IdentityUrl[\s":=\']+([a-zA-Z0-9._\-:/]+)', "IdentityUrl"),
    (r'identity\.mx\.exchange', "identity_ref"),
    (r'connect/token', "connect_token_ref"),
    (r'connect/authorize', "connect_authorize_ref"),
    (r'accountApi|walletApi|orderBookApi|brokerApi', "scope_ref"),
    (r'grant_type[\s":=\']+([a-zA-Z0-9._\-]+)', "grant_type"),
    (r'scope[\s":=\']+([a-zA-Z0-9._\- ]+)', "scope"),
    (r'stsServer[\s":=\']+([a-zA-Z0-9._\-:/]+)', "stsServer"),
    (r'issuer[\s":=\']+([a-zA-Z0-9._\-:/]+)', "issuer"),
    (r'redirectUrl[\s":=\']+([a-zA-Z0-9._\-:/]+)', "redirectUrl"),
    (r'redirect_uri[\s":=\']+([a-zA-Z0-9._\-:/]+)', "redirect_uri"),
    (r'postLogoutRedirectUri[\s":=\']+([a-zA-Z0-9._\-:/]+)', "postLogoutRedirectUri"),
    (r'silentRenew[\s":=\']+([a-zA-Z0-9._\-:/]+)', "silentRenew"),
    (r'openapi[\s":=\']+([a-zA-Z0-9._\-:/]+)', "openapi_ref"),
    (r'apiUrl[\s":=\']+([a-zA-Z0-9._\-:/]+)', "apiUrl"),
    (r'baseUrl[\s":=\']+([a-zA-Z0-9._\-:/]+)', "baseUrl"),
    (r'turnstile[\s":=\']+([a-zA-Z0-9._\-]+)', "turnstile_key"),
    (r'siteKey[\s":=\']+([a-zA-Z0-9._\-]+)', "siteKey"),
]

all_findings = {}

for js_name in js_files:
    url = f"{BASE}/{js_name}"
    print(f"\n{'='*60}")
    print(f"Fetching: {url}")
    try:
        r = requests.get(url, headers=H, timeout=T, verify=False)
        print(f"  Status: {r.status_code} ({len(r.text)} bytes)")
        
        if r.status_code != 200:
            continue
        
        text = r.text
        findings = {}
        
        for pat, label in patterns:
            matches = re.findall(pat, text)
            if matches:
                unique = list(set(matches))[:10]
                findings[label] = unique
                print(f"  [{label}] => {unique}")
        
        all_findings[js_name] = findings
        
        # Also look for environment config blocks
        env_patterns = [
            r'environment\s*[:=]\s*\{[^}]{0,2000}\}',
            r'config\s*[:=]\s*\{[^}]{0,2000}\}',
            r'oidc\s*[:=]\s*\{[^}]{0,2000}\}',
            r'auth\s*[:=]\s*\{[^}]{0,2000}\}',
        ]
        for ep in env_patterns:
            m = re.findall(ep, text)
            if m:
                for block in m[:3]:
                    if len(block) > 50:
                        clean = block.encode('ascii','replace').decode('ascii')
                        print(f"\n  [CONFIG BLOCK] ({len(block)}b):")
                        print(f"    {clean[:500]}")
        
        # Search around "client" keyword with context
        for m in re.finditer(r'client', text, re.IGNORECASE):
            start = max(0, m.start() - 40)
            end = min(len(text), m.end() + 100)
            ctx = text[start:end].encode('ascii','replace').decode('ascii')
            if any(k in ctx.lower() for k in ['id', 'secret', '_id', 'Id']):
                print(f"  [CLIENT CTX] ...{ctx}...")
        
    except Exception as e:
        print(f"  ERROR: {e}")

with open(r"c:\xampp\htdocs\pentagi\mxexchange_attack\js_findings.json", "w") as f:
    json.dump(all_findings, f, indent=2, ensure_ascii=True)

print(f"\n{'='*60}")
print("DONE")
