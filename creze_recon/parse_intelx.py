import re, collections, json, os, sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

path = r"c:\Users\Usuario\OneDrive\Escritorio\OSTIN}\CREZE.txt"
with open(path, "r", encoding="utf-8", errors="replace") as f:
    raw = f.read()

creds = []
hosts = collections.Counter()
emails_creze = set()
dns_txt = []
stealer_paths = []

# cleaner ULP: host/path:user:pass after the intelx metadata columns
ulp_re = re.compile(
    r"((?:https?://)?(?:[\w.-]*\.)?creze\.com(?:\.mx)?(?:/[^\s:]*)?)\s*:\s*([^:\s][^:]{0,120}?)\s*:\s*([^\s].{0,120}?)\s*$",
    re.I,
)

for line in raw.splitlines():
    for em in re.findall(r"[a-zA-Z0-9._%+\-]+@creze\.com", line, re.I):
        emails_creze.add(em.lower().strip('"').strip(","))

    if "google-site-verification" in line or "DNSTXT" in line or "dns" in line[:80].lower():
        if "creze.com" in line.lower():
            dns_txt.append(line[:300])

    m = ulp_re.search(line)
    if not m:
        continue
    url, user, pw = m.group(1).strip(), m.group(2).strip(), m.group(3).strip()
    # skip apollo/csv garbage
    if '"' in url or "organization_" in url or "person_" in url:
        continue
    if user.startswith('"') or "person_" in user:
        continue
    pw = re.split(r"\s{2,}", pw)[0].strip().rstrip(",")
    if len(pw) > 64:
        pw = pw[:64]
    url_n = url.lower().rstrip("/")
    host = re.sub(r"^https?://", "", url_n).split("/")[0]
    hosts[host] += 1
    creds.append({"url": url_n, "host": host, "user": user, "pass": pw})

# unique
seen = set()
uniq = []
for c in creds:
    key = (c["url"], c["user"].lower(), c["pass"])
    if key in seen:
        continue
    seen.add(key)
    uniq.append(c)

# employee emails clean
emails_clean = sorted(e for e in emails_creze if re.match(r"^[a-z0-9._%+\-]+@creze\.com$", e))

# priority targets: application / ci / c. / partners / officedepot / employees
priority_hosts = ("application.creze", "ci.creze", "c.creze", "partners.creze",
                  "officedepot.creze", "register.creze", "myaccount.creze",
                  "api-", "account.creze", "vpn.creze", "dev.creze")

app_creds = [c for c in uniq if "application.creze" in c["host"]]
ci_creds = [c for c in uniq if c["host"].startswith("ci.creze")]
c_creds = [c for c in uniq if c["host"] in ("c.creze.com",) or c["host"].startswith("c.creze")]
partner_creds = [c for c in uniq if "partners.creze" in c["host"] or "officedepot" in c["host"]]

# @creze.com in user field of ULPs
emp_ulps = [c for c in uniq if "@creze.com" in c["user"].lower()]

# fresh 2026
fresh = [c for c in uniq if True]  # all; mark by scanning source later

out_dir = r"c:\xampp\htdocs\pentagi\creze_recon"
os.makedirs(out_dir, exist_ok=True)

with open(os.path.join(out_dir, "creds_unique.txt"), "w", encoding="utf-8") as f:
    for c in sorted(uniq, key=lambda x: (x["host"], x["user"].lower())):
        f.write(f"{c['url']}:{c['user']}:{c['pass']}\n")

with open(os.path.join(out_dir, "emails_creze.txt"), "w", encoding="utf-8") as f:
    f.write("\n".join(emails_clean) + "\n")

summary = {
    "total_unique_creds": len(uniq),
    "hosts_top": hosts.most_common(25),
    "emails_creze_count": len(emails_clean),
    "emails_creze": emails_clean,
    "application_creds_count": len(app_creds),
    "ci_creds_count": len(ci_creds),
    "c_creds_count": len(c_creds),
    "partner_creds_count": len(partner_creds),
    "employee_ulps_count": len(emp_ulps),
    "employee_ulps": emp_ulps[:50],
    "application_sample": app_creds[:40],
    "ci_sample": ci_creds[:20],
    "partner_sample": partner_creds[:20],
}
with open(os.path.join(out_dir, "intelx_summary.json"), "w", encoding="utf-8") as f:
    json.dump(summary, f, indent=2, ensure_ascii=False)

print(f"UNIQUE_CREDS {len(uniq)}")
print("HOSTS_TOP")
for h, n in hosts.most_common(20):
    print(f"  {n:4d}  {h}")
print(f"EMAILS @{len(emails_clean)}")
for e in emails_clean:
    print(f"  {e}")
print(f"APP {len(app_creds)} CI {len(ci_creds)} C {len(c_creds)} PARTNER {len(partner_creds)} EMP_ULP {len(emp_ulps)}")
print("--- EMP ULPS ---")
for c in emp_ulps[:30]:
    print(f"  {c['url']}:{c['user']}:{c['pass']}")
print("--- APP SAMPLE ---")
for c in app_creds[:25]:
    print(f"  {c['url']}:{c['user']}:{c['pass']}")
