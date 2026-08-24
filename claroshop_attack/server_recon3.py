"""Recon phase 3: find tables with nTarjeta columns + axii-pedidos content."""
import paramiko

HOST = "157.180.98.220"
USER = "root"
PASS = "?hK7L3jH76vRT7"

REMOTE_SCRIPT = r'''
#!/bin/bash
APP=/storage/claroshop_dump/mysql_prod/app_sears10_2026_08_23.sql
TIENDA=/storage/claroshop_dump/mysql_prod/tienda_2026.sql

echo "=== axii-pedidos content ==="
ls -la /storage/claroshop_dump/s3/axii-pedidos/ | head -30
echo ""
echo "=== Tables containing nTarjeta column (app_sears10) ==="
grep -o 'CREATE TABLE `[^`]*`' "$APP" | sed 's/CREATE TABLE `//;s/`//' | while read t; do
  # extract the CREATE TABLE block and check for nTarjeta
  if awk "/CREATE TABLE \`$t\`/,/ENGINE=/" "$APP" | grep -qi 'ntarjeta\|tarjetahabiente\|INCOMMTARJETAS'; then
    echo "TABLE: $t"
  fi
done
echo ""
echo "=== Columns with tarjeta in CREATE TABLEs (app_sears10) ==="
grep -iP '^\s*`[^`]*tarjeta[^`]*`' "$APP" | sort | uniq -c | sort -rn | head -30
'''

c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect(HOST, username=USER, password=PASS, timeout=30)

sftp = c.open_sftp()
with sftp.file("/tmp/recon3.sh", "w") as f:
    f.write(REMOTE_SCRIPT)
sftp.close()

stdin, stdout, stderr = c.exec_command("bash /tmp/recon3.sh", timeout=1800)
out = stdout.read().decode("utf-8", errors="replace")
err = stderr.read().decode("utf-8", errors="replace")
print(out)
if err:
    print("--- STDERR ---")
    print(err)
c.close()
