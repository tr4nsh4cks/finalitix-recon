#!/usr/bin/env python3
"""HEXAGON GLM runner - upload script to VPS, execute, download results"""
import paramiko, json, time, sys, os

VPS = '64.177.83.195'
PW = r'Nm9.#p)WzifT.fo2'
USER = 'root'

LOCAL_SCRIPT = r'c:\xampp\htdocs\pentagi\disperso_recon\hexagon_glm_vectors.py'
REMOTE_SCRIPT = '/tmp/hexagon_glm_vectors.py'
REMOTE_RESULTS = '/tmp/hexagon_glm_results.json'
LOCAL_RESULTS = r'c:\xampp\htdocs\pentagi\disperso_recon\hexagon_glm_results.json'
LOCAL_LOG = r'c:\xampp\htdocs\pentagi\disperso_recon\hexagon_glm_run.log'

print(f'[*] Connecting to {VPS}...', flush=True)
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(VPS, username=USER, password=PW, timeout=15)
print(f'[+] Connected', flush=True)

# Upload script
print(f'[*] Uploading script...', flush=True)
sftp = ssh.open_sftp()
sftp.put(LOCAL_SCRIPT, REMOTE_SCRIPT)
print(f'[+] Uploaded', flush=True)

# Ensure requests installed
print(f'[*] Ensuring requests...', flush=True)
stdin, stdout, stderr = ssh.exec_command('pip3 install requests urllib3 -q 2>&1', timeout=60)
stdout.channel.recv_exit_status()
print(f'[+] requests ready', flush=True)

# Execute the script
print(f'[*] Executing vectors (this may take 5-10 min)...', flush=True)
stdin, stdout, stderr = ssh.exec_command(f'python3 {REMOTE_SCRIPT} 2>&1', timeout=900, get_pty=True)

log_lines = []
try:
    while True:
        line = stdout.readline()
        if not line:
            break
        sys.stdout.write(line)
        sys.stdout.flush()
        log_lines.append(line)
        if 'RESULTS SAVED' in line:
            break
except Exception as e:
    print(f'[!] Stream interrupted: {e}', flush=True)

# Save log
with open(LOCAL_LOG, 'w', encoding='utf-8') as f:
    f.writelines(log_lines)
print(f'[+] Log saved to {LOCAL_LOG}', flush=True)

# Download results
print(f'[*] Downloading results...', flush=True)
try:
    sftp.get(REMOTE_RESULTS, LOCAL_RESULTS)
    print(f'[+] Results downloaded to {LOCAL_RESULTS}', flush=True)
    # Show summary
    with open(LOCAL_RESULTS, 'r') as f:
        data = json.load(f)
    print(f'\n=== SUMMARY ===', flush=True)
    print(f'Target: {data.get("target")}', flush=True)
    print(f'Run at: {data.get("run_at")}', flush=True)
    print(f'Vectors: {list(data.get("vectors", {}).keys())}', flush=True)
    for vname, vdata in data.get('vectors', {}).items():
        if 'error' in vdata:
            print(f'  {vname}: ERROR - {vdata["error"][:100]}', flush=True)
        elif 'data' in vdata:
            d = vdata['data']
            if vname.startswith('vector_1'):
                pb_count = sum(len(v) for v in d.get('phonebook', {}).values())
                int_count = sum(len(v) for v in d.get('intelligent', {}).values())
                print(f'  {vname}: PB selectors={pb_count}, INT records={int_count}, file_reads={len(d.get("file_reads", []))}', flush=True)
            elif vname.startswith('vector_2'):
                print(f'  {vname}: code={len(d.get("code",[]))}, commits={len(d.get("commits",[]))}, repos={len(d.get("repos",[]))}, secrets={len(d.get("secrets",[]))}', flush=True)
            elif vname.startswith('vector_3'):
                print(f'  {vname}: cdn={len(d.get("cdn",[]))}, gateway={len(d.get("gateway",[]))}', flush=True)
            elif vname.startswith('vector_4'):
                print(f'  {vname}: tokens={len(d.get("forged_tokens",[]))}, endpoint_tests={len(d.get("endpoints",[]))}', flush=True)
            elif vname.startswith('vector_5'):
                non_403 = [e for e in d.get('endpoints', []) if e.get('status') not in (403, 404)]
                print(f'  {vname}: endpoint_tests={len(d.get("endpoints",[]))}, non-403/404={len(non_403)}', flush=True)
except Exception as e:
    print(f'[!] Download failed: {e}', flush=True)

# Cleanup
try:
    sftp.close()
except:
    pass
ssh.close()
print(f'[+] Done', flush=True)
