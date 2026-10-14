"""R2 Capital - OSINT cred hunt for admin users"""
import requests, json, time, sys, urllib3
urllib3.disable_warnings()

# === API KEYS ===
INTELX_KEY = "6f65b43b-19df-4e12-aea3-115d793e9763"
LEAKCHECK_KEY = "0dea38425ea8e9ededceaa6b94ba08a1b3e74d42"
DEHASHED_KEY = "9zeY/ey9lw1BprbSzCdPKHr7/Ity2SlkAMWDyCnPp/akeTKOBile9IE="

ADMIN_EMAILS = [
    "diego.pereyra@r2.co",
    "cesar.sepulveda@r2capital.co",
    "fabrizio.albanese@r2capital.co",
    "ivan.garcia@r2capital.co",
    "ignacio.cabaud@r2capital.co",
    "jjmtechsolutions@gmail.com",
    "e@mawii.com.co",
]

DOMAINS = ["r2capital.co", "r2.co", "mawii.com.co"]

results = {"leakcheck": [], "dehashed": [], "intelx": []}

# ===== 1. LEAKCHECK =====
print("=" * 60)
print("[1] LeakCheck — Email search")
print("=" * 60)

for email in ADMIN_EMAILS:
    try:
        r = requests.get(f"https://leakcheck.io/api/v2/query/{email}",
                         headers={"X-API-Key": LEAKCHECK_KEY},
                         timeout=15)
        data = r.json()
        if data.get("found"):
            entries = data.get("result", [])
            print(f"\n  [HIT] {email} — {data.get('found')} results")
            for e in entries[:10]:
                pwd = e.get("password", "")
                hsh = e.get("hash", "")
                src = e.get("source", {}).get("name", "?")
                print(f"    pwd={pwd} | hash={hsh} | source={src}")
                results["leakcheck"].append({
                    "email": email, "password": pwd, "hash": hsh, "source": src
                })
        else:
            print(f"  [---] {email} — no results")
    except Exception as e:
        print(f"  [ERR] {email} — {e}")
    time.sleep(0.5)

# Domain search
print("\n  Domain search:")
for domain in DOMAINS:
    try:
        r = requests.get(f"https://leakcheck.io/api/v2/query/{domain}",
                         headers={"X-API-Key": LEAKCHECK_KEY},
                         params={"type": "domain"},
                         timeout=15)
        data = r.json()
        if data.get("found"):
            entries = data.get("result", [])
            print(f"\n  [HIT] {domain} — {data.get('found')} results")
            for e in entries[:20]:
                em = e.get("email", e.get("login", ""))
                pwd = e.get("password", "")
                hsh = e.get("hash", "")
                src = e.get("source", {}).get("name", "?")
                print(f"    {em} | pwd={pwd} | hash={hsh} | source={src}")
                results["leakcheck"].append({
                    "email": em, "password": pwd, "hash": hsh, "source": src
                })
        else:
            print(f"  [---] {domain} — no results")
    except Exception as e:
        print(f"  [ERR] {domain} — {e}")
    time.sleep(0.5)

# ===== 2. DEHASHED =====
print("\n" + "=" * 60)
print("[2] Dehashed — Domain search")
print("=" * 60)

for domain in DOMAINS:
    try:
        r = requests.post("https://api.dehashed.com/v2/search",
                          headers={"Content-Type": "application/json",
                                   "Dehashed-Api-Key": DEHASHED_KEY},
                          json={"query": f"domain:{domain}", "size": 100, "page": 1, "de_dupe": True},
                          timeout=20)
        data = r.json()
        entries = data.get("entries", [])
        total = data.get("total", 0)
        print(f"\n  {domain} — {total} total results, {len(entries)} returned")
        for e in entries[:30]:
            em = e.get("email", "")
            pwd = e.get("password", "")
            hpwd = e.get("hashed_password", "")
            uname = e.get("username", "")
            src = e.get("database_name", "?")
            if pwd or hpwd:
                print(f"    [CRED] {em} | user={uname} | pwd={pwd} | hash={hpwd[:40]} | db={src}")
                results["dehashed"].append({
                    "email": em, "username": uname, "password": pwd,
                    "hash": hpwd, "source": src
                })
            else:
                print(f"    [info] {em} | user={uname} | db={src}")
    except Exception as e:
        print(f"  [ERR] {domain} — {e}")
    time.sleep(1)

# Individual email search
print("\n  Individual email search:")
for email in ADMIN_EMAILS:
    try:
        r = requests.post("https://api.dehashed.com/v2/search",
                          headers={"Content-Type": "application/json",
                                   "Dehashed-Api-Key": DEHASHED_KEY},
                          json={"query": f"email:{email}", "size": 50, "page": 1, "de_dupe": True},
                          timeout=20)
        data = r.json()
        entries = data.get("entries", [])
        total = data.get("total", 0)
        if entries:
            print(f"\n  [HIT] {email} — {total} results")
            for e in entries[:10]:
                pwd = e.get("password", "")
                hpwd = e.get("hashed_password", "")
                src = e.get("database_name", "?")
                if pwd or hpwd:
                    print(f"    pwd={pwd} | hash={hpwd[:40]} | db={src}")
                    results["dehashed"].append({
                        "email": email, "password": pwd, "hash": hpwd, "source": src
                    })
        else:
            print(f"  [---] {email}")
    except Exception as e:
        print(f"  [ERR] {email} — {e}")
    time.sleep(0.5)

# ===== 3. INTELX =====
print("\n" + "=" * 60)
print("[3] IntelX — Phonebook + Intelligent")
print("=" * 60)

INTELX_URL = "https://2.intelx.io"

def intelx_search(term, search_type="phonebook"):
    endpoint = f"{INTELX_URL}/{search_type}/search"
    body = {"term": term, "maxresults": 100, "media": 0, "target": 2,  # 2=passwords
            "timeout": 10}
    if search_type == "intelligent":
        body = {"term": term, "maxresults": 100, "timeout": 10}
    
    r = requests.post(endpoint, json=body,
                      headers={"x-key": INTELX_KEY}, timeout=20)
    data = r.json()
    search_id = data.get("id")
    if not search_id:
        return []
    
    time.sleep(3)
    
    r2 = requests.get(f"{INTELX_URL}/{search_type}/search/result",
                      params={"id": search_id, "limit": 100},
                      headers={"x-key": INTELX_KEY}, timeout=20)
    return r2.json().get("selectors", r2.json().get("records", []))

# Phonebook for passwords
for domain in DOMAINS:
    print(f"\n  Phonebook passwords: {domain}")
    try:
        sels = intelx_search(domain, "phonebook")
        if sels:
            print(f"    Found: {len(sels)} selectors")
            for s in sels[:30]:
                sv = s.get("selectorvalue", "")
                print(f"    {sv}")
                results["intelx"].append({"domain": domain, "selector": sv})
        else:
            print(f"    No results")
    except Exception as e:
        print(f"    Error: {e}")

# Intelligent search for specific emails  
for email in ADMIN_EMAILS[:4]:
    print(f"\n  Intelligent: {email}")
    try:
        records = intelx_search(email, "intelligent")
        if records:
            print(f"    Found: {len(records)} records")
            for rec in records[:5]:
                name = rec.get("name", "?")
                bucket = rec.get("bucket", "?")
                size = rec.get("size", 0)
                print(f"    {name} | bucket={bucket} | size={size}")
                results["intelx"].append({
                    "email": email, "name": name, "bucket": bucket,
                    "systemid": rec.get("systemid"), "storageid": rec.get("storageid")
                })
        else:
            print(f"    No results")
    except Exception as e:
        print(f"    Error: {e}")
    time.sleep(1)

# ===== SUMMARY =====
print("\n" + "=" * 60)
print("SUMMARY — Credentials found")
print("=" * 60)

all_creds = []
for src, entries in results.items():
    for e in entries:
        pwd = e.get("password", "")
        if pwd:
            all_creds.append(e)

if all_creds:
    print(f"\n  Total credentials with passwords: {len(all_creds)}")
    for c in all_creds:
        print(f"  {c.get('email', c.get('selector', '?'))} | pwd={c.get('password')} | src={c.get('source', c.get('domain', '?'))}")
else:
    print("\n  No plaintext passwords found")

# Save results
with open("r2capital_osint_results.json", "w") as f:
    json.dump(results, f, indent=2, default=str)
print(f"\n  Saved to r2capital_osint_results.json")

print("\nDone")
