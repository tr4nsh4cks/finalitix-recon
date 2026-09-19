import requests, json, time

HEADERS = {"x-key": "6f65b43b-19df-4e12-aea3-115d793e9763", "Content-Type": "application/json"}
BASE = "https://2.intelx.io"

def do_phonebook(term, target=1, label=""):
    print(f"\n--- Phonebook: {term} target={target} ({label}) ---")
    r = requests.post(f"{BASE}/phonebook/search", headers=HEADERS,
        json={"term": term, "maxresults": 100, "media": 0, "target": target}, timeout=45)
    print(f"  Search: {r.status_code}")
    if r.status_code != 200:
        print(f"  {r.text[:200]}")
        return []
    sid = r.json().get("id")
    time.sleep(5)
    r2 = requests.get(f"{BASE}/phonebook/search/result",
        params={"id": sid, "limit": 100, "offset": 0}, headers=HEADERS, timeout=45)
    if r2.status_code != 200:
        print(f"  Results err: {r2.status_code}")
        return []
    data = r2.json()
    selectors = data.get("selectors", [])
    print(f"  Found: {len(selectors)}")
    for s in selectors:
        sv = s.get("selectorvalue", "")
        st = s.get("selectortype", "")
        print(f"    [{st}] {sv}")
    return selectors

def do_intelligent(term, label=""):
    print(f"\n--- Intelligent: {term} ({label}) ---")
    r = requests.post(f"{BASE}/intelligent/search", headers=HEADERS,
        json={"term": term, "maxresults": 30, "media": 0,
              "buckets": ["leaks.logs","leaks.public","leaks.restricted","pastes","dumpster"]},
        timeout=45)
    print(f"  Search: {r.status_code}")
    if r.status_code != 200:
        print(f"  {r.text[:200]}")
        return []
    sid = r.json().get("id")
    time.sleep(8)
    r2 = requests.get(f"{BASE}/intelligent/search/result",
        params={"id": sid, "limit": 30, "offset": 0}, headers=HEADERS, timeout=45)
    if r2.status_code != 200:
        print(f"  Results err: {r2.status_code}")
        return []
    data = r2.json()
    records = data.get("records", [])
    print(f"  Found: {len(records)} records")
    for rec in records:
        name = rec.get("name", "")
        bucket = rec.get("bucket", "")
        added = rec.get("added", "")
        size = rec.get("size", 0)
        media = rec.get("media", 0)
        print(f"    [{bucket}] {name} ({size}b) media={media} added={added}")
        
        storageid = rec.get("systemid", "")
        if storageid and bucket in ("leaks.logs", "leaks.public", "pastes", "dumpster"):
            try:
                r3 = requests.get(f"{BASE}/file/read",
                    params={"type": 0, "storageid": storageid, "bucket": bucket},
                    headers=HEADERS, timeout=20)
                if r3.status_code == 200 and r3.text:
                    print(f"      CONTENT: {r3.text[:800]}")
            except Exception as e:
                print(f"      Read err: {e}")
            time.sleep(1)
    return records

all_data = {}

# 1. Disperso emails
sel = do_phonebook("disperso.com", target=1, label="disperso emails")
all_data["disperso_emails"] = [s.get("selectorvalue","") for s in sel]

# 2. Disperso domains/subdomains
sel2 = do_phonebook("disperso.com", target=2, label="disperso domains")
all_data["disperso_domains"] = [s.get("selectorvalue","") for s in sel2]

# 3. Intelligent leaks
recs = do_intelligent("disperso.com", label="disperso leaks")
all_data["disperso_leaks_count"] = len(recs)

# 4. Tuxpan emails (parent company)
sel3 = do_phonebook("tuxpan.cl", target=1, label="tuxpan.cl emails")
all_data["tuxpan_emails"] = [s.get("selectorvalue","") for s in sel3]

# 5. Tuxpan intelligent
recs2 = do_intelligent("tuxpan.cl", label="tuxpan leaks")
all_data["tuxpan_leaks_count"] = len(recs2)

print("\n\n========== FINAL SUMMARY ==========")
for k, v in all_data.items():
    if isinstance(v, list):
        print(f"\n{k}: {len(v)}")
        for item in v:
            print(f"  {item}")
    else:
        print(f"\n{k}: {v}")

with open("disperso_recon/intelx_results_final.json", "w") as f:
    json.dump(all_data, f, indent=2, default=str)
print("\nSaved to intelx_results_final.json")
