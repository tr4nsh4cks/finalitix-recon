"""IntelX phonebook search for @disperso.com and @tuxpan.cl"""
import requests, json, time
from datetime import datetime

INTELX_KEY = "6f65b43b-19df-4e12-aea3-115d793e9763"
INTELX_URL = "https://2.intelx.io"
HEADERS = {"x-key": INTELX_KEY, "Content-Type": "application/json"}

def phonebook_search(term, max_results=100):
    """Phonebook (domain email) search."""
    body = {
        "term": term,
        "buckets": [],
        "lookuplevel": 0,
        "maxresults": max_results,
        "timeout": 0,
        "datefrom": "",
        "dateto": "",
        "sort": 4,
        "media": 0,
        "terminate": []
    }
    r = requests.post(f"{INTELX_URL}/phonebook/search", headers=HEADERS, json=body, timeout=30)
    if r.status_code != 200:
        print(f"  Error {r.status_code}: {r.text[:200]}")
        return None
    return r.json().get("id")

def get_results(search_id, wait=5):
    time.sleep(wait)
    r = requests.get(
        f"{INTELX_URL}/phonebook/search/result?id={search_id}&limit=1000&offset=0",
        headers=HEADERS, timeout=30
    )
    if r.status_code != 200:
        return []
    data = r.json()
    return data.get("selectors", [])

def intelligent_search(term, max_results=100):
    """Full text search in leaks."""
    body = {
        "term": term,
        "buckets": ["leaks.logs", "leaks.public", "dumpster", "pastes"],
        "lookuplevel": 0,
        "maxresults": max_results,
        "timeout": 0,
        "datefrom": "",
        "dateto": "",
        "sort": 4,
        "media": 0,
        "terminate": []
    }
    r = requests.post(f"{INTELX_URL}/intelligent/search", headers=HEADERS, json=body, timeout=30)
    if r.status_code != 200:
        return None
    return r.json().get("id")

def get_intel_results(search_id, wait=8):
    time.sleep(wait)
    r = requests.get(
        f"{INTELX_URL}/intelligent/search/result?id={search_id}&limit=50&offset=0",
        headers=HEADERS, timeout=30
    )
    if r.status_code != 200:
        return []
    return r.json().get("records", [])

all_results = {}

# --- Phonebook search for disperso.com ---
print("[*] IntelX phonebook: disperso.com")
sid = phonebook_search("disperso.com")
if sid:
    results = get_results(sid)
    print(f"  Found {len(results)} selectors")
    for r in results:
        v = r.get("selectorvalue", "")
        print(f"    {v}")
    all_results["disperso_phonebook"] = [r.get("selectorvalue","") for r in results]
else:
    print("  No search ID returned")

time.sleep(3)

# --- Phonebook search for tuxpan.cl ---
print("\n[*] IntelX phonebook: tuxpan.cl")
sid2 = phonebook_search("tuxpan.cl")
if sid2:
    results2 = get_results(sid2)
    print(f"  Found {len(results2)} selectors")
    for r in results2:
        v = r.get("selectorvalue", "")
        print(f"    {v}")
    all_results["tuxpan_phonebook"] = [r.get("selectorvalue","") for r in results2]

time.sleep(3)

# --- Intelligent search for "disperso.com" password ---
print("\n[*] IntelX intelligent: 'disperso.com password'")
sid3 = intelligent_search("disperso.com")
if sid3:
    records = get_intel_results(sid3, wait=10)
    print(f"  Found {len(records)} records")
    for rec in records[:10]:
        print(f"    [{rec.get('type','?')}] {rec.get('name','?')} | date={rec.get('date','?')[:10]}")
    all_results["disperso_intel"] = records[:10]

time.sleep(3)

# --- Save ---
out_file = r"c:\xampp\htdocs\pentagi\disperso_recon\intelx_results.json"
with open(out_file, "w") as f:
    json.dump(all_results, f, indent=2, default=str)
print(f"\n[*] Saved: {out_file}")
