import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('157.180.98.220', port=22, username='root', password='?hK7L3jH76vRT7', timeout=15)

cmd = r"""
echo "=== CREATE TABLE sears_intentos_pago ==="
grep -A50 'CREATE TABLE.*sears_intentos_pago' /storage/claroshop_dump/mysql_prod/tienda_2026.sql | head -55

echo "=== SAMPLE DATA (first 2000 chars of first INSERT) ==="
grep -m1 'INSERT INTO.*sears_intentos_pago' /storage/claroshop_dump/mysql_prod/tienda_2026.sql | head -c 2000

echo ""
echo "=== CREATE TABLE sears_pago_audit ==="
grep -A40 'CREATE TABLE.*sears_pago_audit' /storage/claroshop_dump/mysql_prod/tienda_2026.sql | head -45

echo "=== CREATE TABLE sears_vtas_internet ==="
grep -A40 'CREATE TABLE.*sears_vtas_internet' /storage/claroshop_dump/mysql_prod/tienda_2026.sql | head -45

echo "=== ROW COUNTS ==="
echo -n "sears_intentos_pago INSERTs: "; grep -c 'INSERT INTO.*sears_intentos_pago' /storage/claroshop_dump/mysql_prod/tienda_2026.sql
echo -n "sears_pago_audit INSERTs: "; grep -c 'INSERT INTO.*sears_pago_audit' /storage/claroshop_dump/mysql_prod/tienda_2026.sql
echo -n "sears_vtas_internet INSERTs: "; grep -c 'INSERT INTO.*sears_vtas_internet' /storage/claroshop_dump/mysql_prod/tienda_2026.sql

echo "=== DONE ==="
"""

stdin, stdout, stderr = ssh.exec_command(cmd, timeout=600)
out = stdout.read().decode('utf-8', 'replace')
print(out[:8000])
ssh.close()
