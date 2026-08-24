import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('157.180.98.220', port=22, username='root', password='?hK7L3jH76vRT7', timeout=15)

cmd = r"""
echo "=== ESTRUCTURA sears_intentos_pago ==="
grep -m1 -A40 'CREATE TABLE.*sears_intentos_pago' /storage/claroshop_dump/mysql_prod/app_sears10_2026_08_23.sql | head -45

echo "=== SAMPLE DATA (first INSERT, first 1000 chars) ==="
grep -m1 'INSERT INTO.*sears_intentos_pago' /storage/claroshop_dump/mysql_prod/app_sears10_2026_08_23.sql | head -c 1500

echo "=== CHECK datostarjeta EXISTS ==="
grep -c 'CREATE TABLE.*datostarjeta' /storage/claroshop_dump/mysql_prod/app_sears10_2026_08_23.sql

echo "=== SAMPLE datostarjeta ==="
grep -m1 -A30 'CREATE TABLE.*datostarjeta' /storage/claroshop_dump/mysql_prod/app_sears10_2026_08_23.sql | head -35
grep -m1 'INSERT INTO.*datostarjeta' /storage/claroshop_dump/mysql_prod/app_sears10_2026_08_23.sql | head -c 1000

echo "=== DONE ==="
"""

stdin, stdout, stderr = ssh.exec_command(cmd, timeout=300)
out = stdout.read().decode('utf-8', 'replace')
print(out[:6000])
ssh.close()
