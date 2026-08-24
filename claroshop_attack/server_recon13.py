"""Recon phase 13: exact usuarios count, reset tokens, logs, final inventory."""
import paramiko

HOST = "157.180.98.220"
USER = "root"
PASS = "?hK7L3jH76vRT7"

REMOTE_SCRIPT = r'''
#!/bin/bash
APP=/storage/claroshop_dump/mysql_prod/app_sears10_2026_08_23.sql
TIENDA=/storage/claroshop_dump/mysql_prod/tienda_2026.sql

echo "=== usuarios exact row count (tuples in the single INSERT) ==="
grep -m1 'INSERT INTO `usuarios`' "$APP" | grep -o '),(' | wc -l
echo "(+1 for first tuple)"
echo ""

echo "=== usuarios: MD5 hash count (32-hex passwords) ==="
grep -m1 'INSERT INTO `usuarios`' "$APP" | grep -oP "'[a-f0-9]{32}'" | wc -l
echo ""

echo "=== usr_recuperar_contrasena sample (reset tokens) ==="
grep -m1 'INSERT INTO `usr_recuperar_contrasena`' "$APP" | head -c 800
echo ""
echo ""

echo "=== logs structure + sample ==="
awk '/CREATE TABLE `logs` \(/,/ENGINE=/' "$APP" | head -20
grep -m1 'INSERT INTO `logs` VALUES' "$APP" | head -c 600
echo ""
echo ""

echo "=== app_consecutivo_xml_salesforce structure ==="
awk '/CREATE TABLE `app_consecutivo_xml_salesforce`/,/ENGINE=/' "$APP" | head -15
echo ""

echo "=== cuentas sample ==="
grep -m1 'INSERT INTO `cuentas`' "$APP" | head -c 400
echo ""
echo ""

echo "=== app_sears10: proveedores (usr_proveedores) sample ==="
grep -m1 'INSERT INTO `usr_proveedores`' "$APP" | head -c 400
echo ""
echo ""

echo "=== tienda: distinct id_forma_pago (banks) in sears_intentos_pago sample ==="
grep -m2 'INSERT INTO `sears_intentos_pago`' "$TIENDA" | grep -oP ',\d{4},' | sort | uniq -c | sort -rn | head -10
echo ""

echo "=== tienda: date range sears_intentos_pago ==="
grep -m1 'INSERT INTO `sears_intentos_pago`' "$TIENDA" | grep -oP "'20\d\d-\d\d-\d\d" | head -2
tail -c 100000000 "$TIENDA" | grep -oP "'20\d\d-\d\d-\d\d" | tail -2
echo ""

echo "=== app_sears10 size on disk vs tables with most INSERTs ==="
for t in $(cat /tmp/tables_app.txt); do
  n=$(grep -c "INSERT INTO \`$t\`" "$APP" 2>/dev/null)
  if [ "$n" -gt 50 ]; then echo "$n $t"; fi
done | sort -rn | head -15
'''

c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect(HOST, username=USER, password=PASS, timeout=30)

sftp = c.open_sftp()
with sftp.file("/tmp/recon13.sh", "w") as f:
    f.write(REMOTE_SCRIPT)
sftp.close()

stdin, stdout, stderr = c.exec_command("bash /tmp/recon13.sh", timeout=1800)
out = stdout.read().decode("utf-8", errors="replace")
err = stderr.read().decode("utf-8", errors="replace")
import sys
sys.stdout.buffer.write(out.encode("utf-8", errors="replace"))
if err:
    sys.stdout.buffer.write(("\n--- STDERR ---\n" + err).encode("utf-8", errors="replace"))
sys.stdout.buffer.write(b"\n")
c.close()
