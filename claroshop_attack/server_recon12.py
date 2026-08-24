"""Recon phase 12: row counts, PII samples, API keys, sync progress."""
import paramiko

HOST = "157.180.98.220"
USER = "root"
PASS = "?hK7L3jH76vRT7"

REMOTE_SCRIPT = r'''
#!/bin/bash
APP=/storage/claroshop_dump/mysql_prod/app_sears10_2026_08_23.sql
TIENDA=/storage/claroshop_dump/mysql_prod/tienda_2026.sql

echo "=== SYNC PROGRESS ==="
tail -5 /storage/claroshop_dump/s3_sync.log
du -sh /storage/claroshop_dump/s3/ 2>/dev/null
echo ""

echo "=== ROW COUNTS app_sears10 (INSERT statements) ==="
for t in usuarios usr_proveedores cuentas tiendas notificaciones logs logs_additionals usr_recuperar_contrasena productos usr_perfiles; do
  n=$(grep -c "INSERT INTO \`$t\`" "$APP")
  echo "$t: $n INSERTs"
done
echo ""

echo "=== usuarios: total rows estimate (count value-tuples is expensive; use AUTO_INCREMENT alt: count lines) ==="
grep -m1 -o 'AUTO_INCREMENT=[0-9]*' "$APP" | head -1
echo ""

echo "=== tiendas structure + sample ==="
awk '/CREATE TABLE `tiendas`/,/ENGINE=/' "$APP" | head -40
grep -m1 'INSERT INTO `tiendas`' "$APP" | head -c 800
echo ""
echo ""

echo "=== usr_perfiles sample ==="
grep -m1 'INSERT INTO `usr_perfiles`' "$APP" | head -c 600
echo ""
echo ""

echo "=== app_cron_api_claroshop_requests structure (API keys?) ==="
awk '/CREATE TABLE `app_cron_api_claroshop_requests`/,/ENGINE=/' "$APP" | head -25
grep -m1 'INSERT INTO `app_cron_api_claroshop_requests`' "$APP" | head -c 600
echo ""
echo ""

echo "=== sears_pago_audit_referencias sample ==="
grep -m1 'INSERT INTO `sears_pago_audit_referencias`' "$TIENDA" | head -c 500
echo ""
echo ""

echo "=== notificaciones structure ==="
awk '/CREATE TABLE `notificaciones`/,/ENGINE=/' "$APP" | head -25
echo ""

echo "=== usuarios: count distinct emails sample (first 3 INSERTs emails only) ==="
grep -m3 'INSERT INTO `usuarios`' "$APP" | grep -oP "'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+'" | sort -u | head -30
'''

c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect(HOST, username=USER, password=PASS, timeout=30)

sftp = c.open_sftp()
with sftp.file("/tmp/recon12.sh", "w") as f:
    f.write(REMOTE_SCRIPT)
sftp.close()

stdin, stdout, stderr = c.exec_command("bash /tmp/recon12.sh", timeout=1800)
out = stdout.read().decode("utf-8", errors="replace")
err = stderr.read().decode("utf-8", errors="replace")
import sys
sys.stdout.buffer.write(out.encode("utf-8", errors="replace"))
if err:
    sys.stdout.buffer.write(("\n--- STDERR ---\n" + err).encode("utf-8", errors="replace"))
sys.stdout.buffer.write(b"\n")
c.close()
