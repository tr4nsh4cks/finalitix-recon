"""Recon phase 6: tienda table structures, samples, sync status, bucket list."""
import paramiko

HOST = "157.180.98.220"
USER = "root"
PASS = "?hK7L3jH76vRT7"

REMOTE_SCRIPT = r'''
#!/bin/bash
TIENDA=/storage/claroshop_dump/mysql_prod/tienda_2026.sql

echo "=== SYNC RUNNING? ==="
ps aux | grep -i 'aws\|s3\|sync' | grep -v grep | head -10
echo ""
echo "=== Sync script / bucket list ==="
ls -la /storage/claroshop_dump/*.sh /root/*.sh /storage/*.sh 2>/dev/null
find /storage -maxdepth 2 -name '*.sh' 2>/dev/null | head
cat /storage/claroshop_dump/s3_sync.sh 2>/dev/null | head -50
crontab -l 2>/dev/null | head -20
echo ""
echo "=== TIENDA: CREATE TABLE structures ==="
awk '/CREATE TABLE/,/ENGINE=/' "$TIENDA" | head -200
'''

c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect(HOST, username=USER, password=PASS, timeout=30)

sftp = c.open_sftp()
with sftp.file("/tmp/recon6.sh", "w") as f:
    f.write(REMOTE_SCRIPT)
sftp.close()

stdin, stdout, stderr = c.exec_command("bash /tmp/recon6.sh", timeout=600)
out = stdout.read().decode("utf-8", errors="replace")
err = stderr.read().decode("utf-8", errors="replace")
print(out)
if err:
    print("--- STDERR ---")
    print(err)
c.close()
