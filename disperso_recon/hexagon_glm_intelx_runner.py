#!/usr/bin/env python3
"""Runner for IntelX retry only"""
import paramiko, json, sys

VPS = '64.177.83.195'
PW = r'Nm9.#p)WzifT.fo2'

LOCAL = r'c:\xampp\htdocs\pentagi\disperso_recon\hexagon_glm_intelx_retry.py'
REMOTE = '/tmp/hexagon_glm_intelx_retry.py'
REMOTE_RES = '/tmp/hexagon_glm_intelx_retry.json'
LOCAL_RES = r'c:\xampp\htdocs\pentagi\disperso_recon\hexagon_glm_intelx_retry.json'

print(f'[*] Connecting to {VPS}...', flush=True)
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(VPS, username='root', password=PW, timeout=15)
print('[+] Connected', flush=True)

sftp = ssh.open_sftp()
sftp.put(LOCAL, REMOTE)
print('[+] Uploaded', flush=True)

print('[*] Executing IntelX retry...', flush=True)
stdin, stdout, stderr = ssh.exec_command(f'python3 {REMOTE} 2>&1', timeout=600, get_pty=True)
while True:
    line = stdout.readline()
    if not line:
        break
    sys.stdout.write(line)
    sys.stdout.flush()
    if 'SAVED to' in line:
        break

print('[*] Downloading...', flush=True)
try:
    sftp.get(REMOTE_RES, LOCAL_RES)
    print(f'[+] Downloaded to {LOCAL_RES}', flush=True)
    with open(LOCAL_RES, 'r', encoding='utf-8') as f:
        d = json.load(f)
    print('\n=== INTELX RETRY SUMMARY ===', flush=True)
    for key, sels in d.get('phonebook', {}).items():
        print(f'  PB [{key}]: {len(sels)} selectors', flush=True)
        for s in sels[:10]:
            if isinstance(s, dict):
                print(f'    [{s.get("selectortypeh","")}] {s.get("selectorvalue","")}', flush=True)
    for key, recs in d.get('intelligent', {}).items():
        print(f'  INT [{key}]: {len(recs)} records', flush=True)
        for r in recs[:5]:
            if isinstance(r, dict):
                print(f'    [{r.get("bucket","")}] {r.get("name","")[:80]} ({r.get("added","")[:10]})', flush=True)
    print(f'  File reads: {len(d.get("file_reads", []))}', flush=True)
except Exception as e:
    print(f'[!] Download failed: {e}', flush=True)

ssh.close()
print('[+] Done', flush=True)
