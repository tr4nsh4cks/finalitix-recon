"""Server-side recon: table inventory for both dumps."""
import paramiko

HOST = "157.180.98.220"
USER = "root"
PASS = "?hK7L3jH76vRT7"

REMOTE_SCRIPT = r'''
#!/bin/bash
APP=/storage/claroshop_dump/mysql_prod/app_sears10_2026_08_23.sql
TIENDA=/storage/claroshop_dump/mysql_prod/tienda_2026.sql

echo "=== APP_SEARS10 TABLES ==="
grep -o 'CREATE TABLE `[^`]*`' "$APP" | sed 's/CREATE TABLE `//;s/`//' | sort -u > /tmp/tables_app.txt
wc -l < /tmp/tables_app.txt
cat /tmp/tables_app.txt

echo ""
echo "=== TIENDA TABLES ==="
grep -o 'CREATE TABLE `[^`]*`' "$TIENDA" | sed 's/CREATE TABLE `//;s/`//' | sort -u > /tmp/tables_tienda.txt
wc -l < /tmp/tables_tienda.txt
cat /tmp/tables_tienda.txt
'''

c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect(HOST, username=USER, password=PASS, timeout=30)

# Write script to server
sftp = c.open_sftp()
with sftp.file("/tmp/recon.sh", "w") as f:
    f.write(REMOTE_SCRIPT)
sftp.close()

stdin, stdout, stderr = c.exec_command("bash /tmp/recon.sh", timeout=900)
out = stdout.read().decode("utf-8", errors="replace")
err = stderr.read().decode("utf-8", errors="replace")
print(out)
if err:
    print("--- STDERR ---")
    print(err)
c.close()
