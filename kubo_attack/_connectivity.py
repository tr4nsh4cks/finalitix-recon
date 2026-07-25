import requests, urllib3, sys, socket, ssl
urllib3.disable_warnings()
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

HOST = 'www.api.kubofinanciero.cloud'

# DNS check
print(f'=== DNS: {HOST} ===')
try:
    ips = socket.getaddrinfo(HOST, 443)
    for ip in set([x[4][0] for x in ips]):
        print(f'  IP: {ip}')
except Exception as e:
    print(f'  DNS ERROR: {e}')

# Raw TCP connect
print(f'\n=== TCP connect :443 ===')
try:
    s = socket.create_connection((HOST, 443), timeout=10)
    print(f'  TCP OK')
    s.close()
except Exception as e:
    print(f'  TCP FAIL: {e}')

# TLS handshake
print(f'\n=== TLS handshake ===')
try:
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    s = socket.create_connection((HOST, 443), timeout=10)
    ss = ctx.wrap_socket(s, server_hostname=HOST)
    print(f'  TLS OK: {ss.version()}')
    ss.close()
except Exception as e:
    print(f'  TLS FAIL: {e}')

# HTTP GET
print(f'\n=== HTTP GET ===')
try:
    r = requests.get(f'https://{HOST}/', verify=False, timeout=15)
    print(f'  [{r.status_code}] {r.text[:100]}')
except Exception as e:
    print(f'  HTTP FAIL: {str(e)[:150]}')

# Check other Kubo domains
print(f'\n=== Other domains ===')
for d in ['micuenta.kubofinanciero.com', 'vault.kubofinanciero.cloud', 'backoffice.kubofinanciero.com']:
    try:
        r = requests.get(f'https://{d}/', verify=False, timeout=10)
        print(f'  {d}: [{r.status_code}]')
    except Exception as e:
        print(f'  {d}: {str(e)[:80]}')
