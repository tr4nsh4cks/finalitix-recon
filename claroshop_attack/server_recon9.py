"""Recon phase 9: search backup buckets for SQL dumps (datostarjeta source)."""
import paramiko

HOST = "157.180.98.220"
USER = "root"
PASS = "?hK7L3jH76vRT7"

REMOTE_SCRIPT = r'''
#!/bin/bash
echo "=== sears-backups bucket ==="
aws s3 ls s3://sears-backups --recursive 2>&1 | head -40
echo ""
echo "=== respaldo-servers ==="
aws s3 ls s3://respaldo-servers 2>&1 | head -20
echo ""
echo "=== respaldos_otros ==="
aws s3 ls s3://respaldos_otros 2>&1 | head -20
echo ""
echo "=== respaldos_plazavip ==="
aws s3 ls s3://respaldos_plazavip 2>&1 | head -20
echo ""
echo "=== prodigy-bk ==="
aws s3 ls s3://prodigy-bk 2>&1 | head -20
echo ""
echo "=== portales-cs ==="
aws s3 ls s3://portales-cs 2>&1 | head -20
echo ""
echo "=== comunicados ==="
aws s3 ls s3://comunicados 2>&1 | head -15
echo ""
echo "=== decompras bucket ==="
aws s3 ls s3://decompras 2>&1 | head -15
'''

c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect(HOST, username=USER, password=PASS, timeout=30)

sftp = c.open_sftp()
with sftp.file("/tmp/recon9.sh", "w") as f:
    f.write(REMOTE_SCRIPT)
sftp.close()

stdin, stdout, stderr = c.exec_command("bash /tmp/recon9.sh", timeout=600)
out = stdout.read().decode("utf-8", errors="replace")
err = stderr.read().decode("utf-8", errors="replace")
print(out)
if err:
    print("--- STDERR ---")
    print(err)
c.close()
