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
        if status != 403:
            body = r.text[:300]
            print(f"  {'!!!' if status in (200,201,500) else '**'} {method:6} {path:65} -> {status} ({len(r.text)}b)")
            if status in (200, 201, 500) and r.text:
                print(f"         {r.text[:200]}")
            results.append({"method": method, "path": path, "status": status, "length": len(r.text), "body": body, "label": label})
        return status
    except Exception as e:
        print(f"  ERR  {method:6} {path:65} -> {e}")
        return None
    finally:
        time.sleep(0.4)

print("=== NEW ENDPOINTS FROM JS BUNDLE ===\n")

# From Si variable (payment-order / movement paths)
print("--- Si paths (payment-order/movement) ---")
si_paths = [
    f"{API}/movement",
    f"{API}/movement/pay-in",
    f"{API}/movement/pay-in-detail",
    f"{API}/payment-order/consolidation",
    f"{API}/payment-order/consolidation-detail",
    f"{API}/payment-order/get-transaction-summary",
    f"{API}/payment-order/get-transaction-summary-status",
    f"{API}/payment-order/get-transaction-summary-status-detail",
    f"{API}/payment-order/users",
    f"{API}/payment-order/users-report",
]
for p in si_paths:
    probe("GET", p, "Si")
    probe("POST", p, "Si")

# From Gu variable (file paths)
print("\n--- Gu paths (file) ---")
gu_paths = [
    f"{API}/file",
    f"{API}/file/process-from-s3",
    f"{API}/file/process-status",
    f"{API}/get-all",
    f"{API}/get-all?client-account-id=test",
    f"{API}/get-all?clientAccountId=test",
]
for p in gu_paths:
    probe("GET", p, "Gu")
    probe("POST", p, "Gu")

# From pi variable (client-account sub-paths)
print("\n--- pi paths (client-account config) ---")
pi_paths = [
    f"{API}/client-account/access-token",
    f"{API}/client-account/access-token/list-actions",
    f"{API}/client-account/frontend-cognito",
    f"{API}/client-account/frontend-cognito/change-enable",
    f"{API}/client-account/max-transfer",
    f"{API}/client-account/min-amount",
    f"{API}/client-account/transfer-account",
]
for p in pi_paths:
    for m in ["GET", "POST", "PATCH"]:
        probe(m, p, "pi")

# From GP variable
print("\n--- GP paths ---")
gp_paths = [
    f"{API}/client-account/get-all",
    f"{API}/client-account/get-all?clientAccountId=test",
]
for p in gp_paths:
    probe("GET", p, "GP")

# Recovery / Auth paths
print("\n--- Auth/Recovery paths ---")
auth_paths = [
    f"{API}/auth",
    f"{API}/auth/login",
    f"{API}/auth/register",
    f"{API}/auth/recover-password",
    f"{API}/auth/forgot-password",
    f"{API}/auth/reset-password",
    f"{API}/auth/verify",
    f"{API}/recover-password",
    f"{API}/forgot-password",
    f"{API}/reset-password",
    f"{API}/register",
    f"{API}/signup",
    f"{API}/user",
    f"{API}/user/me",
    f"{API}/profile",
]
for p in auth_paths:
    probe("GET", p, "auth")
    probe("POST", p, "auth")

# Notification sub-paths (with new-potential-client being real)
print("\n--- Notification deep ---")
notif_paths = [
    f"{API}/notification/new-potential-client",
    f"{API}/notification/contact",
    f"{API}/notification/lead",
    f"{API}/notification/demo",
    f"{API}/notification/request",
]
for p in notif_paths:
    probe("POST", p, "notif")

# IP validation with various params
print("\n--- IP validation ---")
probe("GET", f"{API}/ip-valid", "ip")
probe("GET", f"{API}/ip-valid?ip=127.0.0.1", "ip")
probe("POST", f"{API}/ip-valid", "ip")

# Bank with country codes
print("\n--- Bank catalog ---")
for cc in ["CL", "PE", "MX", "CO", "AR"]:
    probe("GET", f"{API}/bank?countryCode={cc}", "bank")

print(f"\n=== SUMMARY ===")
non_403 = [r for r in results if r["status"] != 403]
print(f"Total probed: {len(results)+results.count(None)}")
print(f"Non-403 (real endpoints): {len(non_403)}")
for r in sorted(non_403, key=lambda x: (x["status"], x["path"])):
    print(f"  {r['method']:6} {r['path']:65} -> {r['status']} ({r['length']}b) [{r['label']}]")

with open("disperso_recon/new_endpoints_results.json", "w") as f:
    json.dump(results, f, indent=2)
print(f"\nSaved {len(results)} results")
