import json, re, ssl, urllib.request, sys, socket
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
ctx = ssl.create_default_context()

hosts = [
    "https://creze.com/",
    "https://www.creze.com/",
    "https://application.creze.com/",
    "https://application.creze.com/signin",
    "https://c.creze.com/",
    "https://ci.creze.com/",
    "https://partners.creze.com/",
    "https://partners.creze.com/signin",
    "https://officedepot.creze.com/",
    "https://register.creze.com/",
    "https://myaccount.creze.com/",
    "https://account.creze.com/",
    "https://api-account.creze.com/",
    "https://api.creze.com/",
    "https://api-v4.creze.com/",
    "https://dev.creze.com/",
    "https://staging.creze.com/",
    "https://score.creze.com/",
    "https://new.creze.com/",
    "https://blog.creze.com/",
    "https://creze.com.mx/",
]

def get(url):
    req = urllib.request.Request(url, headers={
        "User-Agent": UA,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "es-MX,es;q=0.9,en;q=0.8",
        "Cache-Control": "no-cache",
    })
    try:
        with urllib.request.urlopen(req, timeout=15, context=ctx) as r:
            body = r.read(20000).decode("utf-8", "replace")
            title = re.search(r"<title[^>]*>([^<]+)", body, re.I)
            return {
                "url": url, "status": r.status, "final": r.geturl(),
                "server": r.headers.get("Server"),
                "cf": bool(r.headers.get("CF-Ray")),
                "title": title.group(1).strip()[:100] if title else None,
                "len": len(body),
                "snippet": re.sub(r"\s+", " ", body)[:180],
            }
    except urllib.error.HTTPError as e:
        body = e.read(8000).decode("utf-8", "replace") if e.fp else ""
        title = re.search(r"<title[^>]*>([^<]+)", body, re.I)
        return {
            "url": url, "status": e.code, "final": url,
            "server": e.headers.get("Server") if e.headers else None,
            "cf": bool(e.headers.get("CF-Ray") if e.headers else False),
            "title": title.group(1).strip()[:100] if title else None,
            "len": len(body),
            "snippet": re.sub(r"\s+", " ", body)[:180],
        }
    except Exception as e:
        return {"url": url, "status": str(e)[:100], "title": None, "len": 0, "snippet": ""}

results = []
for u in hosts:
    r = get(u)
    results.append(r)
    print(f"{r['status']!s:>6}  {u:55s}  title={r.get('title')}  len={r.get('len')}")

# DNS TXT
print("\n--- DNS TXT ---")
try:
    import subprocess
    out = subprocess.check_output(["nslookup", "-type=TXT", "creze.com"], text=True, errors="replace")
    print(out)
except Exception as e:
    print(e)

with open(r"c:\xampp\htdocs\pentagi\creze_recon\http_probe.json", "w", encoding="utf-8") as f:
    json.dump(results, f, indent=2, ensure_ascii=False)
