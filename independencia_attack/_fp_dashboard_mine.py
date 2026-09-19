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

# Follow the JS redirect exactly as the browser would
params = {
    "CUSTM": "bmendezar",
    "USER": "bmendezar",
    "PROJECTID": "50",
    "WRITECACHE": "1",
    "CUSTUSER": "on",
    "MRP": MRP,
    "FIRST_TIME_IN_FP": "1",
    "FIRST_TIME_IN_PROJ": "1",
    "USERID": "bmendezar",
    "MRSubmit": "Submit",
    "LASTSTEP": "1",
}

r_home = s.get(f"{PAO}/MRcgi/MRhomepage.pl", params=params, timeout=60)
sys.stdout.write(f"Homepage: [{r_home.status_code}] ({len(r_home.text)}b)\n\n")

if len(r_home.text) > 50000:
    # SAVE FULL HTML for offline analysis
    with open('/root/fp_homepage.html', 'w') as f:
        f.write(r_home.text)
    sys.stdout.write("Saved to /root/fp_homepage.html\n\n")
    
    # ========================================
    # EXTRACT ALL TICKET DATA
    # ========================================
    sys.stdout.write("=" * 60 + "\n=== TICKET EXTRACTION ===\n" + "=" * 60 + "\n\n")
    
    html = r_home.text
    
    # 1. Extract ticket table rows
    rows = re.findall(r'<tr[^>]*class="[^"]*homepageRow[^"]*"[^>]*>(.*?)</tr>', html, re.S)
    sys.stdout.write(f"Homepage rows: {len(rows)}\n\n")
    
    for i, row in enumerate(rows[:50]):
        cells = re.findall(r'<td[^>]*>(.*?)</td>', row, re.S)
        clean_cells = []
        for c in cells:
            clean = re.sub(r'<[^>]+>', '', c).strip()
            clean = re.sub(r'\s+', ' ', clean)
            if clean:
                clean_cells.append(clean[:60])
        if clean_cells:
            sys.stdout.write(f"  Row {i}: {' | '.join(clean_cells)}\n")
    
    # 2. Extract all links
    all_links = re.findall(r'href="([^"]*MR[^"]*)"', html)
    unique_links = list(set(all_links))
    sys.stdout.write(f"\nInternal links ({len(unique_links)}):\n")
    for link in sorted(unique_links)[:30]:
        sys.stdout.write(f"  {link[:100]}\n")
    
    # 3. Extract ticket IDs from any format
    ticket_patterns = [
        (r'MESSION=(\d+)', 'MESSION'),
        (r'SESSION=(\d+)', 'SESSION'),
        (r'ESSION=(\d+)', 'ESSION'),
        (r'ticketid=(\d+)', 'ticketid'),
        (r'id=(\d+)', 'id'),
    ]
    
    for pattern, name in ticket_patterns:
        matches = re.findall(pattern, html, re.I)
        if matches:
            unique = sorted(set(matches))[:20]
            sys.stdout.write(f"\n  {name}: {unique}\n")
    
    # 4. Extract JavaScript variables
    js_vars = re.findall(r'var\s+(\w+)\s*=\s*["\']([^"\']*)["\']', html[:50000])
    sys.stdout.write(f"\nJS variables ({len(js_vars)}):\n")
    for name, val in js_vars[:20]:
        sys.stdout.write(f"  {name} = {val[:60]}\n")
    
    # 5. Check for menu/navigation
    menus = re.findall(r'(?:menu|nav|sidebar)[^>]*>(.*?)</(?:div|ul|table)', html, re.S|re.I)
    sys.stdout.write(f"\nMenus: {len(menus)}\n")
    
    # 6. Extract form actions
    forms = re.findall(r'<form[^>]*action="([^"]+)"[^>]*>', html, re.I)
    sys.stdout.write(f"\nForm actions: {forms[:10]}\n")
    
    # 7. Look for interesting content
    for keyword in ["SPEI", "transfer", "dispersion", "STP", "clabe", "cuenta",
                     "servidor", "server", "produccion", "base dato", "clave",
                     "contrase", "password", "vpn", "red", "acceso",
                     "correo", "email", "admin", "root"]:
        count = html.lower().count(keyword.lower())
        if count > 0:
            sys.stdout.write(f"  Keyword '{keyword}': {count} hits\n")
            # Show context
            for m in re.finditer(keyword, html, re.I):
                start = max(0, m.start()-30)
                end = min(len(html), m.end()+100)
                chunk = re.sub(r'<[^>]+>', ' ', html[start:end]).strip()
                chunk = re.sub(r'\s+', ' ', chunk)
                sys.stdout.write(f"    ...{chunk[:120]}...\n")
                break  # Only first occurrence
    
    # ========================================
    # FOLLOW NEXT PAGE
    # ========================================
    sys.stdout.write("\n\n=== NEXT PAGE ===\n\n")
    
    next_form = re.search(r'<form[^>]*name="nextpage"[^>]*>(.*?)</form>', html, re.S|re.I)
    if next_form:
        # Extract hidden fields
        hidden_fields = re.findall(r'<input[^>]*name="([^"]+)"[^>]*value="([^"]*)"', next_form.group(1), re.I)
        sys.stdout.write(f"Next page fields: {hidden_fields[:10]}\n")
        
        # Submit next page
        next_data = {name: val for name, val in hidden_fields}
        r_next = s.post(f"{PAO}/MRcgi/MRhomepage.pl", data=next_data, timeout=30)
        sys.stdout.write(f"Next page: [{r_next.status_code}] ({len(r_next.text)}b)\n")
        
        # Count rows on next page
        next_rows = re.findall(r'<tr[^>]*class="[^"]*homepageRow[^"]*"[^>]*>(.*?)</tr>', r_next.text, re.S)
        sys.stdout.write(f"Next page rows: {len(next_rows)}\n")
else:
    sys.stdout.write(f"Homepage too small ({len(r_home.text)}b) — session issue\n")
    sys.stdout.write(f"Body: {r_home.text[:3000]}\n")
    
    # Try with POST
    r_post = s.post(f"{PAO}/MRcgi/MRhomepage.pl", data=params, timeout=60)
    sys.stdout.write(f"\nPOST: [{r_post.status_code}] ({len(r_post.text)}b)\n")
    
    if len(r_post.text) > 50000:
        sys.stdout.write("POST worked! Saving...\n")
        with open('/root/fp_homepage.html', 'w') as f:
            f.write(r_post.text)


sys.stdout.write("\n\n=== ALL DONE ===\n")
sys.stdout.flush()
'''

sftp = ssh.open_sftp()
with sftp.open('/root/fp_dashboard_mine.py', 'w') as f:
    f.write(SCRIPT)
sftp.close()
print('Uploaded', flush=True)

stdin, stdout, stderr = ssh.exec_command('python3 -u /root/fp_dashboard_mine.py 2>&1', timeout=120)
out = stdout.read().decode(errors='replace')
print(out, flush=True)
ssh.close()
print('Fin.', flush=True)
