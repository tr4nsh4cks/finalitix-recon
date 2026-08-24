"""Recon phase 7: bucket list + sample data from sears payment tables."""
import paramiko

HOST = "157.180.98.220"
USER = "root"
PASS = "?hK7L3jH76vRT7"

REMOTE_SCRIPT = r'''
#!/bin/bash
TIENDA=/storage/claroshop_dump/mysql_prod/tienda_2026.sql

echo "=== BUCKET LIST (sync script) ==="
cat /storage/sync_all_s3.sh
echo ""
echo "=== SAMPLE: sears_intentos_pago (first INSERT, 1500 chars) ==="
grep -m1 'INSERT INTO `sears_intentos_pago`' "$TIENDA" | head -c 1500
echo ""
echo ""
echo "=== SAMPLE: sears_pago_audit (first INSERT, 1200 chars) ==="
grep -m1 'INSERT INTO `sears_pago_audit`' "$TIENDA" | head -c 1200
echo ""
echo ""
echo "=== SAMPLE: sears_vtas_internet (first INSERT, 800 chars) ==="
grep -m1 'INSERT INTO `sears_vtas_internet`' "$TIENDA" | head -c 800
echo ""
echo ""
echo "=== ROW COUNTS (INSERT statements per table) ==="
for t in sears_intentos_pago sears_pago_audit sears_pago_audit_referencias sears_pago_audit_referencias_usadas sears_secuencia sears_vtas_internet tmp_salesaudit tmp_salesaudit_2013_2016; do
  n=$(grep -c "INSERT INTO \`$t\`" "$TIENDA")
  echo "$t: $n INSERT statements"
done
'''

c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect(HOST, username=USER, password=PASS, timeout=30)

sftp = c.open_sftp()
with sftp.file("/tmp/recon7.sh", "w") as f:
    f.write(REMOTE_SCRIPT)
sftp.close()

stdin, stdout, stderr = c.exec_command("bash /tmp/recon7.sh", timeout=1800)
out = stdout.read().decode("utf-8", errors="replace")
err = stderr.read().decode("utf-8", errors="replace")
print(out)
if err:
    print("--- STDERR ---")
    print(err)
c.close()
