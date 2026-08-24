"""Recon phase 8: full S3 bucket list + usuarios/PII tables in app_sears10."""
import paramiko

HOST = "157.180.98.220"
USER = "root"
PASS = "?hK7L3jH76vRT7"

REMOTE_SCRIPT = r'''
#!/bin/bash
APP=/storage/claroshop_dump/mysql_prod/app_sears10_2026_08_23.sql

echo "=== ALL S3 BUCKETS ==="
aws s3 ls 2>&1
echo ""
echo "=== app_sears10: usuarios structure ==="
awk '/CREATE TABLE `usuarios`/,/ENGINE=/' "$APP"
echo ""
echo "=== app_sears10: usuarios sample (first INSERT 1200 chars) ==="
grep -m1 'INSERT INTO `usuarios`' "$APP" | head -c 1200
echo ""
echo ""
echo "=== app_sears10: cuentas structure ==="
awk '/CREATE TABLE `cuentas`/,/ENGINE=/' "$APP"
echo ""
echo "=== app_sears10: usr_proveedores structure ==="
awk '/CREATE TABLE `usr_proveedores`/,/ENGINE=/' "$APP"
echo ""
echo "=== app_sears10: usr_recuperar_contrasena structure ==="
awk '/CREATE TABLE `usr_recuperar_contrasena`/,/ENGINE=/' "$APP"
'''

c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect(HOST, username=USER, password=PASS, timeout=30)

sftp = c.open_sftp()
with sftp.file("/tmp/recon8.sh", "w") as f:
    f.write(REMOTE_SCRIPT)
sftp.close()

stdin, stdout, stderr = c.exec_command("bash /tmp/recon8.sh", timeout=900)
out = stdout.read().decode("utf-8", errors="replace")
err = stderr.read().decode("utf-8", errors="replace")
print(out)
if err:
    print("--- STDERR ---")
    print(err)
c.close()
