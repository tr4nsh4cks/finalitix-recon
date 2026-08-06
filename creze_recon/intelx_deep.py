import re, collections, json, sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

path = r"c:\Users\Usuario\OneDrive\Escritorio\OSTIN}\CREZE.txt"
with open(path, "r", encoding="utf-8", errors="replace") as f:
    lines = f.readlines()

# Extract lines with FRESH 2026 / recent + application signin
fresh = []
stealer = []
dns_bits = []
whois_bits = []
tech = []

for line in lines:
    low = line.lower()
    if "2026-" in line or "fresh ulp" in low:
        m = re.search(r"((?:https?://)?[^\s:]*creze\.com[^\s:]*)\s*:\s*([^:]+)\s*:\s*(.+)$", line, re.I)
        if m:
            fresh.append((m.group(1).strip(), m.group(2).strip(), m.group(3).strip()[:60]))
    if "stealer" in low or "passwords.txt" in low or "login data" in low or "cookies" in low:
        stealer.append(line[:250])
    if "google-site-verification" in low or "logmein" in low or "spf1" in low or "dmarc" in low:
        dns_bits.append(line[:400])
    if "whois" in low[:80] or "ciclomart" in low or "david lask" in low:
        whois_bits.append(line[:350])
    if "apollo" in low and ("hubspot" in low or "react" in low or "cloudflare" in low):
        tech.append(line[80:400])

print(f"FRESH_2026_ULPS {len(fresh)}")
seen=set()
for u,user,pw in fresh:
    k=(u.lower(),user.lower(),pw)
    if k in seen: continue
    seen.add(k)
    print(f"  {u}:{user}:{pw}")

print(f"\nSTEALER_HITS {len(stealer)}")
for s in stealer[:15]:
    print(" ", s[:200])

print(f"\nDNS_BITS {len(dns_bits)}")
for s in dns_bits[:10]:
    print(" ", s[:300])

print(f"\nWHOIS {len(whois_bits)}")
for s in whois_bits[:5]:
    print(" ", s[:300])

# Unique users for application.creze.com with frequency
app_users = collections.Counter()
app_pairs = {}
ulp = re.compile(r"((?:https?://)?(?:[\w.-]*\.)?creze\.com(?:\.mx)?(?:/[^\s:]*)?)\s*:\s*([^:\s][^:]{0,100}?)\s*:\s*([^\s].{0,80})", re.I)
for line in lines:
    m = ulp.search(line)
    if not m: continue
    url, user, pw = m.group(1), m.group(2).strip(), m.group(3).strip().split("  ")[0][:60]
    if "application.creze" not in url.lower(): continue
    if '"' in url or "@creze.com" in user: continue
    if ".key" in user.lower() or "fiel" in user.lower(): continue
    uk = user.lower()
    app_users[uk] += 1
    app_pairs.setdefault(uk, set()).add(pw)

print(f"\nTOP_APP_USERS {len(app_users)}")
for u, n in app_users.most_common(40):
    pws = list(app_pairs[u])[:4]
    print(f"  {n:3d}  {u}  passwords={pws}")

# Hosts mentioned beyond merklemap
extra_hosts = set()
for line in lines:
    for h in re.findall(r"(?:https?://)?([a-z0-9.-]+\.creze\.com(?:\.mx)?)", line, re.I):
        extra_hosts.add(h.lower())
print(f"\nALL_HOSTS_IN_DUMP {len(extra_hosts)}")
for h in sorted(extra_hosts):
    print(" ", h)
