"""Recon phase 2: table structures + search for datostarjeta + other dumps."""
import paramiko

HOST = "157.180.98.220"
USER = "root"
PASS = "?hK7L3jH76vRT7"

REMOTE_SCRIPT = r'''
#!/bin/bash
APP=/storage/claroshop_dump/mysql_prod/app_sears10_2026_08_23.sql
TIENDA=/storage/claroshop_dump/mysql_prod/tienda_2026.sql

echo "=== OTHER FILES ON SERVER ==="
ls -laR /storage/claroshop_dump/ 2>/dev/null | head -40
echo ""
echo "=== SEARCH datostarjeta in tienda ==="
grep -c -i 'datostarjeta' "$TIENDA" || echo "0 matches"
echo "=== SEARCH tarjeta in tienda (case-insens, table/col names) ==="
grep -o -i '[a-z_]*tarjeta[a-z_]*' "$TIENDA" | sort | uniq -c | sort -rn | head -20
echo ""
echo "=== SEARCH tarjeta in app_sears10 ==="
grep -o -i '[a-z_]*tarjeta[a-z_]*' "$APP" | sort | uniq -c | sort -rn | head -20
echo ""
echo "=== TIENDA: all CREATE TABLE statements (full) ==="
grep -A40 'CREATE TABLE' "$TIENDA" | head -250
'''

c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect(HOST, username=USER, password=PASS, timeout=30)

sftp = c.open_sftp()
with sftp.file("/tmp/recon2.sh", "w") as f:
    f.write(REMOTE_SCRIPT)
sftp.close()

stdin, stdout, stderr = c.exec_command("bash /tmp/recon2.sh", timeout=900)
out = stdout.read().decode("utf-8", errors="replace")
err = stderr.read().decode("utf-8", errors="replace")
print(out)
if err:
    print("--- STDERR ---")
    print(err)
c.close()
