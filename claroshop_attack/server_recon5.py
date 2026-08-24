"""Recon phase 5: download logs + sears tables structure + sample data."""
import paramiko

HOST = "157.180.98.220"
USER = "root"
PASS = "?hK7L3jH76vRT7"

REMOTE_SCRIPT = r'''
#!/bin/bash
TIENDA=/storage/claroshop_dump/mysql_prod/tienda_2026.sql

echo "=== s3_sync.log ==="
cat /storage/claroshop_dump/s3_sync.log
echo ""
echo "=== download.log (first 60 lines) ==="
head -60 /storage/claroshop_dump/mysql_prod/download.log
echo ""
echo "=== download.log (last 30 lines) ==="
tail -30 /storage/claroshop_dump/mysql_prod/download.log
echo ""
echo "=== axii folder ==="
find /storage/claroshop_dump/s3/axii-pedidos/axii -type f 2>/dev/null | head -40
echo ""
echo "=== crons folder ==="
find /storage/claroshop_dump/s3/axii-pedidos/crons -type f 2>/dev/null | head -40
echo ""
echo "=== decompras folder ==="
find /storage/claroshop_dump/s3/axii-pedidos/decompras -type f 2>/dev/null | head -40
echo ""
echo "=== concilia / conciliacionSears ==="
find /storage/claroshop_dump/s3/axii-pedidos/concilia /storage/claroshop_dump/s3/axii-pedidos/conciliacionSears -type f 2>/dev/null | head -40
'''

c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect(HOST, username=USER, password=PASS, timeout=30)

sftp = c.open_sftp()
with sftp.file("/tmp/recon5.sh", "w") as f:
    f.write(REMOTE_SCRIPT)
sftp.close()

stdin, stdout, stderr = c.exec_command("bash /tmp/recon5.sh", timeout=600)
out = stdout.read().decode("utf-8", errors="replace")
err = stderr.read().decode("utf-8", errors="replace")
print(out)
if err:
    print("--- STDERR ---")
    print(err)
c.close()
