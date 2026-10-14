"""IntelX + Dehashed + LeakCheck — hunt for Odoo .mx credentials"""
import requests, json, time, sys, urllib3
urllib3.disable_warnings()

INTELX_KEY = "6f65b43b-19df-4e12-aea3-115d793e9763"
INTELX_URL = "https://2.intelx.io"
LEAKCHECK_KEY = "0dea38425ea8e9ededceaa6b94ba08a1b3e74d42"
DEHASHED_KEY = "9zeY/ey9lw1BprbSzCdPKHr7/Ity2SlkAMWDyCnPp/akeTKOBile9IE="

results = {"intelx": [], "dehashed": [], "leakcheck": []}

# ===== 1. INTELX — Search for odoo.com with .mx in stealer logs =====
print("=" * 60)
print("[1] IntelX Phonebook — odoo.com passwords")
print("=" * 60)

def intelx_phonebook(term, target=2, maxresults=1000):
    """target: 0=all, 1=emails, 2=passwords, 3=domains, 4=urls"""
    r = requests.post(f"{INTELX_URL}/phonebook/search",
                      json={"term": term, "maxresults": maxresults, "media": 0,
                            "target": target, "timeout": 30},
                      headers={"x-key": INTELX_KEY}, timeout=30)
    data = r.json()
    sid = data.get("id")
    if not sid:
        return []
    
    time.sleep(5)
    
    all_selectors = []
    for _ in range(3):
        r2 = requests.get(f"{INTELX_URL}/phonebook/search/result",
                          params={"id": sid, "limit": maxresults},
                          headers={"x-key": INTELX_KEY}, timeout=30)
        data2 = r2.json()
        sels = data2.get("selectors", [])
        all_selectors.extend(sels)
        if data2.get("status") in [0, 2]:  # done
            break
        time.sleep(3)
    
    return all_selectors

# Search for odoo.com — get emails/passwords
print("\n  Searching 'odoo.com' phonebook (emails)...")
try:
    emails = intelx_phonebook("odoo.com", target=1, maxresults=500)
    mx_emails = [e for e in emails if ".mx" in str(e.get("selectorvalue", "")).lower()
                 or "@" in str(e.get("selectorvalue", "")) and ".mx" in str(e.get("selectorvalue", "")).lower()]
    print(f"  Total emails found: {len(emails)}")
    print(f"  .mx emails: {len(mx_emails)}")
    for e in mx_emails[:50]:
        sv = e.get("selectorvalue", "")
        print(f"    {sv}")
        results["intelx"].append({"type": "email", "value": sv, "source": "phonebook"})
except Exception as e:
    print(f"  Error: {e}")

# Search for *.odoo.com URLs
print("\n  Searching '*.odoo.com' phonebook (URLs)...")
try:
    urls = intelx_phonebook("odoo.com", target=4, maxresults=500)
    mx_urls = [u for u in urls if ".mx" in str(u.get("selectorvalue", "")).lower()
               or "mexico" in str(u.get("selectorvalue", "")).lower()]
    print(f"  Total URLs found: {len(urls)}")
    print(f"  .mx related URLs: {len(mx_urls)}")
    for u in mx_urls[:30]:
        sv = u.get("selectorvalue", "")
        print(f"    {sv}")
        results["intelx"].append({"type": "url", "value": sv, "source": "phonebook"})
    
    # Also show ALL odoo.com subdomain URLs (not just .mx)
    print(f"\n  All odoo.com URLs (first 50):")
    for u in urls[:50]:
        sv = u.get("selectorvalue", "")
        print(f"    {sv}")
except Exception as e:
    print(f"  Error: {e}")

# ===== 2. IntelX Intelligent search for odoo login credentials =====
print("\n" + "=" * 60)
print("[2] IntelX Intelligent — 'odoo.com' stealer logs")
print("=" * 60)

def intelx_intelligent(term, maxresults=100):
    r = requests.post(f"{INTELX_URL}/intelligent/search",
                      json={"term": term, "maxresults": maxresults, "timeout": 30,
                            "sort": 2, "media": 0},
                      headers={"x-key": INTELX_KEY}, timeout=30)
    data = r.json()
    sid = data.get("id")
    if not sid:
        return []
    
    time.sleep(5)
    
    r2 = requests.get(f"{INTELX_URL}/intelligent/search/result",
                      params={"id": sid, "limit": maxresults},
                      headers={"x-key": INTELX_KEY}, timeout=30)
    return r2.json().get("records", [])

for search_term in ["odoo.com .mx", "odoo.com mexico"]:
    print(f"\n  Searching: '{search_term}'")
    try:
        records = intelx_intelligent(search_term, maxresults=50)
        print(f"  Records found: {len(records)}")
        for rec in records[:20]:
            name = rec.get("name", "?")
            bucket = rec.get("bucket", "?")
            size = rec.get("size", 0)
            added = rec.get("added", "")[:10]
            systemid = rec.get("systemid", "")
            storageid = rec.get("storageid", "")
            print(f"    {name} | bucket={bucket} | size={size} | {added}")
            results["intelx"].append({
                "type": "record", "name": name, "bucket": bucket,
                "systemid": systemid, "storageid": storageid
            })
    except Exception as e:
        print(f"  Error: {e}")
    time.sleep(2)

# ===== 3. Try to read stealer log content for odoo =====
print("\n" + "=" * 60)
print("[3] IntelX File Preview — stealer content with odoo.com")
print("=" * 60)

# Search specifically for stealer logs
try:
    records = intelx_intelligent("odoo.com/web/login", maxresults=30)
    print(f"  Records with 'odoo.com/web/login': {len(records)}")
    
    for rec in records[:10]:
        name = rec.get("name", "?")
        systemid = rec.get("systemid", "")
        storageid = rec.get("storageid", "")
        bucket = rec.get("bucket", "?")
        print(f"\n  [{name}] bucket={bucket}")
        
        # Try to preview content
        if storageid and systemid:
            try:
                r = requests.get(f"{INTELX_URL}/file/preview",
                                 params={"type": 0, "storageid": storageid,
                                         "bucket": bucket, "f": 0, "l": 20,
                                         "c": 1, "k": INTELX_KEY},
                                 headers={"x-key": INTELX_KEY}, timeout=20)
                if r.status_code == 200:
                    lines = r.text.split("\n")
                    # Filter for odoo.com lines
                    odoo_lines = [l for l in lines if "odoo.com" in l.lower()]
                    mx_lines = [l for l in lines if ".mx" in l.lower() and "odoo" in l.lower()]
                    
                    if mx_lines:
                        print(f"    .mx + odoo lines:")
                        for l in mx_lines[:10]:
                            print(f"      {l[:200]}")
                    elif odoo_lines:
                        print(f"    odoo lines ({len(odoo_lines)}):")
                        for l in odoo_lines[:5]:
                            print(f"      {l[:200]}")
                    else:
                        print(f"    No odoo lines in preview ({len(lines)} total lines)")
                else:
                    print(f"    Preview: HTTP {r.status_code}")
            except Exception as e:
                print(f"    Preview error: {e}")
            time.sleep(1)
except Exception as e:
    print(f"  Error: {e}")

# ===== 4. DEHASHED — odoo.com domain =====
print("\n" + "=" * 60)
print("[4] Dehashed — odoo.com credentials")
print("=" * 60)

try:
    r = requests.post("https://api.dehashed.com/v2/search",
                      headers={"Content-Type": "application/json",
                               "Dehashed-Api-Key": DEHASHED_KEY},
                      json={"query": "domain:odoo.com", "size": 100, "page": 1, "de_dupe": True},
                      timeout=20)
    data = r.json()
    entries = data.get("entries", [])
    total = data.get("total", 0)
    print(f"  odoo.com total: {total}, returned: {len(entries)}")
    
    # Filter for .mx emails or Mexican-related
    mx_entries = [e for e in entries if any(
        ".mx" in str(v).lower() for v in [e.get("email",""), e.get("username",""), e.get("name","")]
    )]
    
    print(f"  .mx related: {len(mx_entries)}")
    for e in mx_entries[:30]:
        em = e.get("email", "")
        pwd = e.get("password", "")
        hpwd = e.get("hashed_password", "")
        uname = e.get("username", "")
        src = e.get("database_name", "?")
        name = e.get("name", "")
        if pwd:
            print(f"    [CRED] {em} | user={uname} | name={name} | pwd={pwd} | db={src}")
            results["dehashed"].append({"email": em, "password": pwd, "username": uname, "source": src})
    
    # Show all with passwords
    print(f"\n  All with passwords:")
    for e in entries:
        pwd = e.get("password", "")
        if pwd:
            em = e.get("email", "")
            src = e.get("database_name", "?")
            print(f"    {em} | pwd={pwd} | db={src}")
            results["dehashed"].append({"email": em, "password": pwd, "source": src})

except Exception as e:
    print(f"  Error: {e}")

# ===== 5. LEAKCHECK — odoo.com =====
print("\n" + "=" * 60)
print("[5] LeakCheck — odoo.com domain")
print("=" * 60)

try:
    r = requests.get(f"https://leakcheck.io/api/v2/query/odoo.com",
                     headers={"X-API-Key": LEAKCHECK_KEY},
                     params={"type": "domain"},
                     timeout=15)
    data = r.json()
    if data.get("found"):
        entries = data.get("result", [])
        print(f"  Found: {data.get('found')} results")
        mx_entries = [e for e in entries if ".mx" in str(e.get("email", "")).lower()]
        print(f"  .mx entries: {len(mx_entries)}")
        for e in mx_entries[:30]:
            em = e.get("email", "")
            pwd = e.get("password", "")
            src = e.get("source", {}).get("name", "?")
            print(f"    {em} | pwd={pwd} | src={src}")
            results["leakcheck"].append({"email": em, "password": pwd, "source": src})
    else:
        print(f"  No results")
except Exception as e:
    print(f"  Error: {e}")

# ===== SUMMARY =====
print("\n" + "=" * 60)
print("SUMMARY")
print("=" * 60)

all_creds = []
for src, entries in results.items():
    for e in entries:
        pwd = e.get("password", "")
        if pwd and e.get("email"):
            all_creds.append(e)

print(f"\nTotal credentials with passwords: {len(all_creds)}")
seen = set()
for c in all_creds:
    key = f"{c.get('email')}:{c.get('password')}"
    if key not in seen:
        seen.add(key)
        print(f"  {c.get('email')} | pwd={c.get('password')} | src={c.get('source')}")

with open("r2capital_odoo_mx_hunt.json", "w") as f:
    json.dump(results, f, indent=2, default=str)
print(f"\nSaved to r2capital_odoo_mx_hunt.json")

print("\nDone")
