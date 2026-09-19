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
sesskey = re.search(r'"sesskey":"([^"]+)"', r_auth.text)
sk = sesskey.group(1) if sesskey else ""
sys.stdout.write(f"Logged in, sesskey={sk}\n\n")


# ========================================
# 1. ACCESS DISPERSIÓN COURSES (17, 929)
# ========================================
sys.stdout.write("=" * 60 + "\n=== DISPERSIÓN COURSES ===\n" + "=" * 60 + "\n\n")

target_courses = [17, 929]

for cid in target_courses:
    sys.stdout.write(f"\n{'='*50}\n--- Course {cid} ---\n{'='*50}\n")
    
    # Try regular access
    r = ms.get(f"{MOODLE}/course/view.php?id={cid}", timeout=10)
    title = re.search(r'<title>(.*?)</title>', r.text[:3000], re.I)
    sys.stdout.write(f"[{r.status_code}] Title: {title.group(1)[:80] if title else 'N/A'}\n")
    
    if "No est" in r.text[:5000] or "cannot" in r.text[:5000].lower() or "not enrolled" in r.text[:5000].lower():
        sys.stdout.write("  NOT ENROLLED - trying self-enrol...\n")
        
        # Try self-enrollment
        enrol_url = re.search(r'href="([^"]*enrol[^"]*)"', r.text)
        if enrol_url:
            sys.stdout.write(f"  Enrol URL: {enrol_url.group(1)}\n")
            r_enrol = ms.get(enrol_url.group(1), timeout=10)
            sys.stdout.write(f"  Enrol page: [{r_enrol.status_code}] ({len(r_enrol.text)}b)\n")
            
            # Try to self-enrol
            enrol_form = re.search(r'<form[^>]*action="([^"]*enrol[^"]*)"[^>]*>(.*?)</form>', r_enrol.text, re.S)
            if enrol_form:
                action = enrol_form.group(1)
                inputs = {}
                for name, val in re.findall(r'name="([^"]+)"\s+value="([^"]*)"', enrol_form.group(2)):
                    inputs[name] = val
                sys.stdout.write(f"  Enrol form: action={action} fields={list(inputs.keys())}\n")
                
                # Submit enrollment
                if action:
                    r_submit = ms.post(action if action.startswith("http") else f"{MOODLE}{action}",
                        data=inputs, timeout=10, allow_redirects=True)
                    sys.stdout.write(f"  Enrol submit: [{r_submit.status_code}] ({len(r_submit.text)}b)\n")
                    
                    # Re-check course
                    r = ms.get(f"{MOODLE}/course/view.php?id={cid}", timeout=10)
                    sys.stdout.write(f"  Re-check: [{r.status_code}] ({len(r.text)}b)\n")
        
        # Try guest access
        r_guest = ms.get(f"{MOODLE}/course/view.php?id={cid}&guest=1", timeout=10)
        if r_guest.status_code == 200 and len(r_guest.text) > 5000:
            sys.stdout.write(f"  Guest access: [{r_guest.status_code}] ({len(r_guest.text)}b)\n")
            r = r_guest
    
    # If we have access, extract content
    if r.status_code == 200 and len(r.text) > 5000:
        # Activities
        activities = re.findall(r'class="instancename"[^>]*>(.*?)<', r.text)
        sys.stdout.write(f"\nActivities ({len(activities)}):\n")
        for a in activities:
            clean = re.sub(r'<[^>]+>', '', a).strip()
            if clean:
                sys.stdout.write(f"  - {clean}\n")
        
        # Section names
        sections = re.findall(r'class="sectionname"[^>]*>(.*?)<', r.text)
        sys.stdout.write(f"\nSections ({len(sections)}):\n")
        for s in sections:
            clean = re.sub(r'<[^>]+>', '', s).strip()
            if clean:
                sys.stdout.write(f"  - {clean}\n")
        
        # Resources and files
        resources = re.findall(r'href="([^"]*(?:pluginfile|mod/resource|mod/page|mod/url|mod/scorm|mod/folder)[^"]*)"', r.text)
        if resources:
            sys.stdout.write(f"\nResources ({len(resources)}):\n")
            for res in resources:
                sys.stdout.write(f"  {res[:120]}\n")
        
        # Downloadable files
        files = re.findall(r'href="([^"]*(?:\.pdf|\.docx?|\.xlsx?|\.pptx?|\.csv|\.zip)[^"]*)"', r.text, re.I)
        if files:
            sys.stdout.write(f"\n*** DOWNLOADABLE FILES ***:\n")
            for f in files:
                sys.stdout.write(f"  {f[:120]}\n")
        
        # Content summary
        summary = re.search(r'class="summary"[^>]*>(.*?)</div>', r.text, re.S)
        if summary:
            clean = re.sub(r'<[^>]+>', ' ', summary.group(1)).strip()
            sys.stdout.write(f"\nSummary: {clean[:500]}\n")
        
        # All SCORM packages
        scorms = re.findall(r'mod/scorm/view\.php\?id=(\d+)', r.text)
        sys.stdout.write(f"\nSCORM IDs: {scorms}\n")
        
        for sid in scorms[:5]:
            r_scorm = ms.get(f"{MOODLE}/mod/scorm/view.php?id={sid}", timeout=10)
            scorm_title = re.search(r'<title>(.*?)</title>', r_scorm.text[:2000], re.I)
            sys.stdout.write(f"  SCORM {sid}: {scorm_title.group(1)[:60] if scorm_title else 'N/A'}\n")
            
            # Look for SCORM package URL
            pkg = re.findall(r'href="([^"]*pluginfile[^"]*\.zip[^"]*)"', r_scorm.text)
            if pkg:
                sys.stdout.write(f"    Package: {pkg[0][:100]}\n")
            
            # Look for launch URL
            launch = re.search(r'var\s+launch(?:_url|Url|URL)\s*=\s*["\']([^"\']+)', r_scorm.text)
            if launch:
                sys.stdout.write(f"    Launch: {launch.group(1)[:100]}\n")
    
    sys.stdout.flush()


# ========================================
# 2. ENUMERATE MORE COURSES (look for financial ones)
# ========================================
sys.stdout.write("\n\n" + "=" * 60 + "\n=== ENUMERATE ALL COURSES ===\n" + "=" * 60 + "\n\n")

# Use AJAX to get course list
for cat_id in range(1, 20):
    try:
        call = [{"index": 0, "methodname": "core_course_get_courses_by_field",
                 "args": {"field": "category", "value": str(cat_id)}}]
        r = ms.post(f"{MOODLE}/lib/ajax/service.php?sesskey={sk}&info=core_course_get_courses_by_field",
            json=call, timeout=10)
        data = r.json()
        if isinstance(data, list) and data and not data[0].get("error"):
            courses = data[0].get("data", {}).get("courses", [])
            if courses:
                sys.stdout.write(f"\nCategory {cat_id}: {len(courses)} courses\n")
                for c in courses:
                    cname = c.get("fullname", "")
                    cid = c.get("id", "?")
                    # Flag financial courses
                    flag = ""
                    for keyword in ["dispers", "spei", "stp", "pago", "transfer", "tesor", "contab", 
                                    "financ", "credito", "cobran", "cartera", "operaci", "clabe",
                                    "banco", "gedyd", "domicilia"]:
                        if keyword in cname.lower():
                            flag = " *** FINANCIAL ***"
                            break
                    sys.stdout.write(f"  [{cid}] {cname[:80]}{flag}\n")
    except:
        pass
    sys.stdout.flush()

# Also try sequential course IDs around the discovered ones
sys.stdout.write("\n--- Sequential course probe (1-50) ---\n")
for cid in range(1, 51):
    try:
        r = ms.get(f"{MOODLE}/course/view.php?id={cid}", timeout=5, allow_redirects=False)
        if r.status_code == 200:
            title = re.search(r'<title>(.*?)</title>', r.text[:2000], re.I)
            if title:
                tname = title.group(1).replace(" | Universidad FINDEP", "").strip()
                flag = ""
                for kw in ["dispers", "spei", "stp", "pago", "transfer", "tesor", "contab",
                            "financ", "credito", "cobran", "cartera", "operaci", "domicilia", "gedyd"]:
                    if kw in tname.lower():
                        flag = " *** FINANCIAL ***"
                        break
                sys.stdout.write(f"  [{cid}] {tname[:80]}{flag}\n")
        elif r.status_code in [302, 303]:
            loc = r.headers.get("Location", "")
            if "enrol" in loc.lower():
                sys.stdout.write(f"  [{cid}] -> enrol (not enrolled)\n")
    except:
        pass
    sys.stdout.flush()


# ========================================
# 3. SEARCH RESULT DEEP DIVE — "DISPERSIÓN"
# ========================================
sys.stdout.write("\n\n" + "=" * 60 + "\n=== DEEP SEARCH — dispersi, domicilia, gedyd ===\n" + "=" * 60 + "\n\n")

for term in ["GEDYD", "domiciliacion", "dispersiones", "domicilia", "EVALUACION DISPERSION"]:
    r = ms.get(f"{MOODLE}/search/index.php?q={term}&perpage=50", timeout=15)
    
    # Extract actual result content (not sidebar links)
    # Moodle 3.x search results format
    result_blocks = re.findall(r'<li\s+class="[^"]*result[^"]*"[^>]*>(.*?)</li>', r.text, re.S)
    if not result_blocks:
        result_blocks = re.findall(r'class="searchresult"[^>]*>(.*?)</(?:div|article|section)', r.text, re.S)
    
    sys.stdout.write(f"\n--- '{term}': {len(result_blocks)} result blocks ---\n")
    
    for rb in result_blocks[:10]:
        # Title
        rb_title = re.search(r'<a[^>]*>(.*?)</a>', rb)
        if rb_title:
            clean_title = re.sub(r'<[^>]+>', '', rb_title.group(1)).strip()
            sys.stdout.write(f"  TITLE: {clean_title[:100]}\n")
        
        # Description/content
        rb_desc = re.search(r'class="[^"]*description[^"]*"[^>]*>(.*?)</(?:div|p)', rb, re.S)
        if not rb_desc:
            rb_desc = re.search(r'class="[^"]*content[^"]*"[^>]*>(.*?)</(?:div|p)', rb, re.S)
        if rb_desc:
            clean_desc = re.sub(r'<[^>]+>', ' ', rb_desc.group(1)).strip()
            clean_desc = re.sub(r'\s+', ' ', clean_desc)
            sys.stdout.write(f"  DESC: {clean_desc[:300]}\n")
        
        # Context (which course)
        rb_context = re.search(r'en curso\s+(.*?)</', rb)
        if rb_context:
            sys.stdout.write(f"  IN COURSE: {re.sub(r'<[^>]+>', '', rb_context.group(1)).strip()}\n")
        
        # Links
        rb_links = re.findall(r'href="([^"]+)"', rb)
        for rl in rb_links:
            if 'mod/' in rl or 'course/' in rl:
                sys.stdout.write(f"  LINK: {rl[:120]}\n")
        
        sys.stdout.write("\n")
    
    # If no structured results, dump raw search area
    if not result_blocks:
        main = re.search(r'id="region-main"[^>]*>(.*?)id="page-footer"', r.text, re.S)
        if main:
            # Extract all titles/headers
            headers = re.findall(r'<h[234][^>]*>(.*?)</h[234]>', main.group(1), re.S)
            for h in headers[:10]:
                clean_h = re.sub(r'<[^>]+>', '', h).strip()
                if clean_h and len(clean_h) > 3:
                    sys.stdout.write(f"  HEADER: {clean_h[:120]}\n")
            
            # Extract all links with context
            links = re.findall(r'<a[^>]*href="([^"]*(?:mod/|course/)[^"]*)"[^>]*>(.*?)</a>', main.group(1), re.S)
            for href, text in links[:15]:
                clean_text = re.sub(r'<[^>]+>', '', text).strip()
                if clean_text and 'universidad.findep.mx' in href:
                    sys.stdout.write(f"  {clean_text[:60]} -> {href[:100]}\n")
    
    sys.stdout.flush()


sys.stdout.write("\n\n=== ALL DONE ===\n")
sys.stdout.flush()
'''

sftp = ssh.open_sftp()
with sftp.open('/root/fp_moodle_disp.py', 'w') as f:
    f.write(SCRIPT)
sftp.close()
print('Uploaded', flush=True)

stdin, stdout, stderr = ssh.exec_command('python3 -u /root/fp_moodle_disp.py 2>&1', timeout=300)
out = stdout.read().decode(errors='replace')
print(out, flush=True)
ssh.close()
print('Fin.', flush=True)
