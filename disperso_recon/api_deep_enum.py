import requests, json, time

BASE = "https://rdrrxexkm4.execute-api.us-east-2.amazonaws.com/prod"
HEADERS = {
    "Content-Type": "application/json",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}

results = []

def probe(method, path, label=""):
    url = f"{BASE}{path}"
    try:
        if method == "GET":
            r = requests.get(url, headers=HEADERS, timeout=15)
        elif method == "POST":
            r = requests.post(url, headers=HEADERS, json={}, timeout=15)
        elif method == "PUT":
            r = requests.put(url, headers=HEADERS, json={}, timeout=15)
        elif method == "PATCH":
            r = requests.patch(url, headers=HEADERS, json={}, timeout=15)
        elif method == "DELETE":
            r = requests.delete(url, headers=HEADERS, timeout=15)
        elif method == "OPTIONS":
            r = requests.options(url, headers=HEADERS, timeout=15)
        else:
            return None
        
        entry = {
            "method": method, "path": path, "status": r.status_code,
            "length": len(r.text), "label": label
        }
        if r.status_code not in (403,):
            entry["body"] = r.text[:300]
        results.append(entry)
        
        marker = "!!!" if r.status_code in (200, 201, 500) else "**" if r.status_code == 401 else ""
        if r.status_code != 403:
            print(f"  {marker} {method:6} {path:55} -> {r.status_code} ({len(r.text)}b) {label}")
            if r.status_code in (200, 201, 500) and r.text:
                print(f"         Body: {r.text[:200]}")
        return r.status_code
    except Exception as e:
        print(f"  ERR  {method:6} {path:55} -> {e}")
        return None
    finally:
        time.sleep(0.3)

print("=== PHASE 1: SPEI/TRANSFER/PAYMENT PATHS (GET+POST) ===")
paths_p1 = [
    "/api/v1/spei", "/api/v1/stp", "/api/v1/transfer", "/api/v1/transfers",
    "/api/v1/transaction", "/api/v1/transactions", "/api/v1/payment", "/api/v1/payments",
    "/api/v1/payout", "/api/v1/payouts", "/api/v1/disbursement", "/api/v1/disbursements",
    "/api/v1/batch", "/api/v1/batch-payment", "/api/v1/mass-payment", "/api/v1/bulk-payment",
    "/api/v1/webhook", "/api/v1/webhooks", "/api/v1/callback", "/api/v1/clabe",
    "/api/v1/beneficiary", "/api/v1/beneficiaries", "/api/v1/recipient", "/api/v1/recipients",
    "/api/v1/account", "/api/v1/accounts", "/api/v1/balance", "/api/v1/movements",
    "/api/v1/report", "/api/v1/reports", "/api/v1/dashboard",
    "/api/v1/configuration", "/api/v1/settings", "/api/v1/access-token", "/api/v1/api-key",
    "/api/v1/representative", "/api/v1/users", "/api/v1/admin",
    "/api/v1/role", "/api/v1/roles", "/api/v1/company", "/api/v1/currency",
    "/api/v1/exchange-rate", "/api/v1/quotation", "/api/v1/quote",
    "/api/v1/sandbox", "/api/v1/test", "/api/v1/health", "/api/v1/status",
    "/api/v1/version", "/api/v1/info", "/api/v1/frontend-cognito",
    "/api/v1/min-balance", "/api/v1/max-transfer", "/api/v1/change-enabled",
    "/api/v1/dashboard-report", "/api/v1/report-payment", "/api/v1/pay-in-report",
    "/api/v1/transaction-summary", "/api/v1/movement-report",
]
for p in paths_p1:
    probe("GET", p, "p1")
    probe("POST", p, "p1")

print("\n=== PHASE 2: V2 API ===")
v2_paths = [
    "/api/v2/bank", "/api/v2/notification", "/api/v2/client-account",
    "/api/v2/payment-order", "/api/v2/settlement", "/api/v2/transfer",
    "/api/v2/spei", "/api/v2/document", "/api/v2/ip-valid",
]
for p in v2_paths:
    probe("GET", p, "v2")
    probe("POST", p, "v2")

print("\n=== PHASE 3: CLIENT-ACCOUNT SUB-PATHS ===")
ca_subs = [
    "/api/v1/client-account/transfer/spei",
    "/api/v1/client-account/transfer/stp",
    "/api/v1/client-account/transfer/batch",
    "/api/v1/client-account/transfer/status",
    "/api/v1/client-account/balance",
    "/api/v1/client-account/movement",
    "/api/v1/client-account/clabe",
    "/api/v1/client-account/bank-account",
    "/api/v1/client-account/beneficiary",
    "/api/v1/client-account/config",
    "/api/v1/client-account/representative",
    "/api/v1/client-account/summary",
    "/api/v1/client-account/report",
    "/api/v1/client-account/sandbox",
]
for p in ca_subs:
    probe("GET", p, "ca-sub")
    probe("POST", p, "ca-sub")

print("\n=== PHASE 4: ACTUATOR / SWAGGER / OPENAPI ===")
infra_paths = [
    "/actuator", "/actuator/health", "/actuator/env", "/actuator/info",
    "/actuator/mappings", "/actuator/beans", "/actuator/heapdump",
    "/actuator/prometheus", "/actuator/metrics", "/actuator/loggers",
    "/health", "/info", "/env",
    "/swagger-ui.html", "/swagger-ui/", "/swagger-ui/index.html",
    "/v3/api-docs", "/v2/api-docs", "/openapi.json", "/openapi.yaml",
    "/api-docs", "/docs", "/api/docs",
]
for p in infra_paths:
    probe("GET", p, "infra")

print("\n=== PHASE 5: PAYMENT-ORDER SUB-PATHS ===")
po_subs = [
    "/api/v1/payment-order/batch",
    "/api/v1/payment-order/spei",
    "/api/v1/payment-order/transfer",
    "/api/v1/payment-order/status",
    "/api/v1/payment-order/process",
    "/api/v1/payment-order/confirm",
    "/api/v1/payment-order/cancel",
    "/api/v1/payment-order/draft",
    "/api/v1/payment-order/upload",
    "/api/v1/payment-order/download",
    "/api/v1/payment-order/summary",
    "/api/v1/payment-order/report",
]
for p in po_subs:
    probe("GET", p, "po-sub")
    probe("POST", p, "po-sub")

print("\n=== PHASE 6: METHOD FUZZING on interesting 401 endpoints ===")
fuzz_401 = []
for r in results:
    if r["status"] == 401 and r["path"] not in [x["path"] for x in fuzz_401]:
        fuzz_401.append(r)

new_401_paths = set()
for r in fuzz_401:
    if r["path"] not in ["/api/v1/bank", "/api/v1/client-account/transfer",
                          "/api/v1/settlement", "/api/v1/monthly-billing",
                          "/api/v1/ip-valid", "/api/v1/notification"]:
        new_401_paths.add(r["path"])

print(f"  Found {len(new_401_paths)} new 401 paths to method-fuzz")
for p in sorted(new_401_paths):
    for m in ["PUT", "PATCH", "DELETE", "OPTIONS"]:
        probe(m, p, "method-fuzz")

print(f"\n=== SUMMARY ===")
by_status = {}
for r in results:
    s = r["status"]
    by_status[s] = by_status.get(s, 0) + 1
for s in sorted(by_status.keys()):
    print(f"  {s}: {by_status[s]} responses")

non_403 = [r for r in results if r["status"] != 403]
print(f"\n  NON-403 responses: {len(non_403)}")
for r in sorted(non_403, key=lambda x: x["status"]):
    print(f"    {r['method']:7} {r['path']:55} -> {r['status']} ({r['length']}b)")

with open("disperso_recon/api_deep_enum_results.json", "w") as f:
    json.dump(results, f, indent=2)
print(f"\nSaved {len(results)} results")
