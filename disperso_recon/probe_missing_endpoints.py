import requests, json, time

BASE = "https://rdrrxexkm4.execute-api.us-east-2.amazonaws.com/prod"
API = "/api/v1"
HEADERS = {
    "Content-Type": "application/json",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}

results = []

def probe(method, path, label=""):
    url = f"{BASE}{path}"
    try:
        r = getattr(requests, method.lower())(url, headers=HEADERS, json={} if method in ("POST","PUT","PATCH") else None, timeout=15)
        status = r.status_code
        marker = "!!!" if status in (200,201,500) else "**" if status == 401 else "   "
        if status != 403:
            print(f"  {marker} {method:6} {path:70} -> {status} ({len(r.text)}b)")
            if status in (200, 201, 500):
                print(f"         {r.text[:200]}")
        else:
            print(f"       {method:6} {path:70} -> 403 (no existe)")
        results.append({"method": method, "path": path, "status": status, "length": len(r.text), "label": label})
        return status
    except Exception as e:
        print(f"  ERR  {method:6} {path:70} -> {e}")
        return None
    finally:
        time.sleep(0.35)

print("=== MISSING ENDPOINTS FROM VARIABLE MAPPING ===\n")

# Si = /reporter
print("--- Si=/reporter (movement & payment-order under reporter) ---")
reporter_paths = [
    f"{API}/reporter",
    f"{API}/reporter/movement",
    f"{API}/reporter/movement/pay-in",
    f"{API}/reporter/movement/pay-in-detail",
    f"{API}/reporter/payment-order",
    f"{API}/reporter/payment-order/consolidation",
    f"{API}/reporter/payment-order/consolidation-detail",
    f"{API}/reporter/payment-order/get-transaction-summary",
    f"{API}/reporter/payment-order/get-transaction-summary-status",
    f"{API}/reporter/payment-order/get-transaction-summary-status-detail",
    f"{API}/reporter/payment-order/users",
    f"{API}/reporter/payment-order/users-report",
]
for p in reporter_paths:
    probe("GET", p, "reporter")

# GP = /movement (direct, not under reporter)
print("\n--- GP=/movement (direct get-all) ---")
gp_paths = [
    f"{API}/movement",
    f"{API}/movement/get-all",
    f"{API}/movement/get-all?clientAccountId=test",
]
for p in gp_paths:
    probe("GET", p, "movement")

# R8 = /payment-report
print("\n--- R8=/payment-report ---")
r8_paths = [
    f"{API}/payment-report",
    f"{API}/payment-report/client-account",
    f"{API}/payment-report/dashboard",
]
for p in r8_paths:
    probe("GET", p, "payment-report")

# rMe = /quote
print("\n--- rMe=/quote ---")
quote_paths = [
    f"{API}/quote",
    f"{API}/quote/get-all",
]
for p in quote_paths:
    probe("GET", p, "quote")
    probe("POST", p, "quote")

# aMe = /catalog
print("\n--- aMe=/catalog ---")
catalog_paths = [
    f"{API}/catalog",
    f"{API}/catalog/get-all",
    f"{API}/catalog/countries",
    f"{API}/catalog/currencies",
    f"{API}/catalog/banks",
]
for p in catalog_paths:
    probe("GET", p, "catalog")

# nMe = /user (already got /user/me = 401)
print("\n--- nMe=/user ---")
user_paths = [
    f"{API}/user",
    f"{API}/user/me",
    f"{API}/user/get-all",
    f"{API}/user/profile",
    f"{API}/user/register",
]
for p in user_paths:
    probe("GET", p, "user")
    probe("POST", p, "user")

# /document (standalone, not under client-account)
print("\n--- /document (standalone) ---")
doc_paths = [
    f"{API}/document",
    f"{API}/document/presigned-upload",
    f"{API}/document/get-all",
]
for p in doc_paths:
    probe("GET", p, "document")
    probe("POST", p, "document")

# Notification (was accepting POST before)
print("\n--- /notification ---")
probe("GET", f"{API}/notification", "notification")
probe("POST", f"{API}/notification", "notification-post")
probe("POST", f"{API}/notification/new-potential-client", "notification-npc")

# Others from tMe
print("\n--- Others ---")
other_paths = [
    f"{API}/monthly-billing",
    f"{API}/settlement",
    f"{API}/ip-valid",
]
for p in other_paths:
    probe("GET", p, "other")

# Xt routes - try frontend routes as API paths 
print("\n--- Frontend routes as API paths ---")
fe_paths = [
    f"{API}/dashboard",
    f"{API}/config",
    f"{API}/questions",
    f"{API}/massive-payments",
    f"{API}/online-payments",
]
for p in fe_paths:
    probe("GET", p, "fe-route")

print(f"\n=== FINAL SUMMARY ===")
real_endpoints = [r for r in results if r["status"] == 401]
open_endpoints = [r for r in results if r["status"] in (200, 201)]
errors = [r for r in results if r["status"] == 500]
nonexist = [r for r in results if r["status"] == 403]

print(f"\n  REAL (401 auth required): {len(real_endpoints)}")
for r in sorted(real_endpoints, key=lambda x: x["path"]):
    print(f"    {r['method']:6} {r['path']}")

print(f"\n  OPEN (200/201): {len(open_endpoints)}")
for r in open_endpoints:
    print(f"    {r['method']:6} {r['path']}")

print(f"\n  ERROR (500): {len(errors)}")
for r in errors:
    print(f"    {r['method']:6} {r['path']}")

print(f"\n  NON-EXISTENT (403): {len(nonexist)}")

with open("disperso_recon/missing_endpoints_results.json", "w") as f:
    json.dump(results, f, indent=2)
print(f"\nSaved {len(results)} results")
