import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('157.180.98.220', port=22, username='root', password='?hK7L3jH76vRT7', timeout=15)

cmd = r"""
echo "=== CHECKING CARD NUMBER LENGTHS ==="
# Get a larger sample and check digit counts
grep -m5 'INSERT INTO.*sears_intentos_pago' /storage/claroshop_dump/mysql_prod/tienda_2026.sql | head -c 50000 | grep -oP "'\d{13,16}'" | head -30

echo "=== LATEST DATA (2026) ==="
# Search for recent records that might have full PANs
grep 'INSERT INTO.*sears_intentos_pago' /storage/claroshop_dump/mysql_prod/tienda_2026.sql | tail -c 3000 | grep -oP "'\d{13,16}'" | head -20

echo "=== DISTINCT LENGTHS ==="
grep -m10 'INSERT INTO.*sears_intentos_pago' /storage/claroshop_dump/mysql_prod/tienda_2026.sql | grep -oP "'(\d{10,16})'" | awk '{print length($0)-2}' | sort | uniq -c | sort -rn

echo "=== 16-DIGIT NUMBERS (if any) ==="
grep -m3 'INSERT INTO.*sears_intentos_pago' /storage/claroshop_dump/mysql_prod/tienda_2026.sql | grep -oP "'\d{16}'" | head -20

echo "=== AUTO_INCREMENT MAX ==="
grep 'AUTO_INCREMENT=' /storage/claroshop_dump/mysql_prod/tienda_2026.sql | head -5

echo "=== DONE ==="
"""

stdin, stdout, stderr = ssh.exec_command(cmd, timeout=300)
out = stdout.read().decode('utf-8', 'replace')
print(out[:5000])
ssh.close()
