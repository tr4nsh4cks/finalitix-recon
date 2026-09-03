import requests, urllib3, time
urllib3.disable_warnings()

s = requests.Session()
s.verify = False
s.proxies = {"http": "socks5h://127.0.0.1:1081", "https": "socks5h://127.0.0.1:1081"}
s.headers["User-Agent"] = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"

tests = [
    "https://159.60.138.202/.magnolia/admincentral",
    "https://159.60.138.202/",
    "https://159.60.138.202/.rest/nodes/v1/website/?depth=0",
    "http://159.60.138.202/.magnolia/admincentral",
]
for u in tests:
    try:
        r = s.get(u, timeout=30, allow_redirects=False)
        rej = "rejected" in r.text.lower()
        print(f"{u:52s} {r.status_code} len={len(r.text):6d} rejected={rej} srv={r.headers.get('Server','')[:30]}", flush=True)
    except Exception as e:
        print(f"{u:52s} ERR {str(e)[:70]}", flush=True)
    time.sleep(0.5)
