import csv, socket, ssl, urllib.request, concurrent.futures, json, re, os, sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

csv_path = r"c:\Users\Usuario\Downloads\merklemap_export (78).csv"
hosts = set()
with open(csv_path, newline="", encoding="utf-8") as f:
    for row in csv.DictReader(f):
        h = row["hostname"].strip().lstrip("*.")
        if h:
            hosts.add(h)

extras = [
    "creze.com", "application.creze.com", "ci.creze.com", "app.creze.com",
    "portal.creze.com", "admin.creze.com", "mail.creze.com", "staging.creze.com",
    "qa.creze.com", "partners.creze.com", "officedepot.creze.com",
    "register.creze.com", "myaccount.creze.com", "api.creze.com",
]
for e in extras:
    hosts.add(e)

def probe(host):
    info = {"host": host, "dns": None, "scheme": None, "status": None,
            "title": None, "server": None, "redir": None, "cf": None}
    try:
        ips = socket.getaddrinfo(host, 443, type=socket.SOCK_STREAM)
        info["dns"] = sorted({x[4][0] for x in ips})
    except Exception:
        try:
            ips = socket.getaddrinfo(host, 80, type=socket.SOCK_STREAM)
            info["dns"] = sorted({x[4][0] for x in ips})
        except Exception:
            return info

    ctx = ssl.create_default_context()
    for scheme in ("https", "http"):
        try:
            req = urllib.request.Request(
                f"{scheme}://{host}/",
                headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/124.0"},
            )
            with urllib.request.urlopen(req, timeout=10, context=ctx) as r:
                body = r.read(12000).decode("utf-8", "replace")
                info["status"] = r.status
                info["server"] = r.headers.get("Server")
                info["cf"] = r.headers.get("CF-Ray") or r.headers.get("cf-ray")
                info["redir"] = r.geturl()
                info["scheme"] = scheme
                m = re.search(r"<title[^>]*>([^<]+)", body, re.I)
                info["title"] = m.group(1).strip()[:140] if m else None
                break
        except urllib.error.HTTPError as e:
            info["status"] = e.code
            info["scheme"] = scheme
            info["server"] = e.headers.get("Server") if e.headers else None
            break
        except Exception as e:
            info["status"] = type(e).__name__ + ":" + str(e)[:60]
    return info

results = []
with concurrent.futures.ThreadPoolExecutor(16) as ex:
    for r in ex.map(probe, sorted(hosts)):
        results.append(r)
        print(f"{r['host']:42s} dns={r['dns']} status={r['status']} title={r['title']} srv={r['server']}")

os.makedirs(r"c:\xampp\htdocs\pentagi\creze_recon", exist_ok=True)
out = r"c:\xampp\htdocs\pentagi\creze_recon\subdomain_probe.json"
with open(out, "w", encoding="utf-8") as f:
    json.dump(results, f, indent=2, ensure_ascii=False)
alive = [r for r in results if r["dns"]]
print(f"\nALIVE_DNS {len(alive)}/{len(results)} -> {out}")
