import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('157.180.98.220', port=22, username='root', password='?hK7L3jH76vRT7', timeout=15)

cmd = r"""
echo "=== ALL TABLES IN app_sears10_2026_08_23.sql ==="
grep 'CREATE TABLE' /storage/claroshop_dump/mysql_prod/app_sears10_2026_08_23.sql | sed 's/.*`\([^`]*\)`.*/\1/' | sort

echo "=== TOTAL COUNT app_sears10 ==="
grep -c 'CREATE TABLE' /storage/claroshop_dump/mysql_prod/app_sears10_2026_08_23.sql

echo "=== ALL TABLES IN tienda_2026.sql ==="
grep 'CREATE TABLE' /storage/claroshop_dump/mysql_prod/tienda_2026.sql | sed 's/.*`\([^`]*\)`.*/\1/' | sort

echo "=== TOTAL COUNT tienda ==="
grep -c 'CREATE TABLE' /storage/claroshop_dump/mysql_prod/tienda_2026.sql

echo "=== FIRST 100 LINES OF DUMP (to see DB name/format) ==="
head -20 /storage/claroshop_dump/mysql_prod/app_sears10_2026_08_23.sql

echo "=== DONE ==="
"""

stdin, stdout, stderr = ssh.exec_command(cmd, timeout=600)
out = stdout.read().decode('utf-8', 'replace')
print(out[:15000])
ssh.close()
