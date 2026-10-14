"""Quick probe - is unii.com.mx Odoo alive?"""
import requests, urllib3
urllib3.disable_warnings()

PROXY = "http://brd-customer-hl_25b43d3c-zone-residential_mx1-country-mx:erjvs0sv8cvs@brd.superproxy.io:22225"
PX = {"http": PROXY, "https": PROXY}
TO = 20

targets = [
    ("https://unii.com.mx", "GET"),
    ("https://unii.com.mx/web/login", "GET"),
    ("https://unii.com.mx/web/database/selector", "GET"),
    ("https://unii.com.mx/jsonrpc", "POST"),
]

for url, method in targets:
    try:
        if method == "GET":
            r = requests.get(url, timeout=TO, verify=False, proxies=PX, allow_redirects=False)
        else:
            r = requests.post(url, json={"jsonrpc":"2.0","id":1,"method":"call",
                "params":{"service":"common","method":"version","args":[]}},
                timeout=TO, verify=False, proxies=PX)
        print(f"[{r.status_code}] {url}")
        print(f"    headers: server={r.headers.get('server','?')}, ct={r.headers.get('content-type','?')}")
        print(f"    body[:300]: {r.text[:300]}")
        if r.status_code in (301,302,303):
            print(f"    Location: {r.headers.get('Location','?')}")
        print()
    except Exception as e:
        print(f"[ERR] {url} → {e}\n")
