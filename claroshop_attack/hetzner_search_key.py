import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('157.180.98.220', port=22, username='root', password='?hK7L3jH76vRT7', timeout=15)

cmd = """export PATH=/usr/local/bin:$PATH

echo "=== RESPALDO-SERVERS BUCKET ==="
aws s3 ls s3://respaldo-servers/ --recursive | grep -iE 'local\\.php|config|env|\\.properties|secret|encrypt|key' | head -20

echo "=== PORTALES-CS BUCKET ==="
aws s3 ls s3://portales-cs/ --recursive | grep -iE 'local\\.php|config|env|secret' | head -20

echo "=== SEARCHING SQL DUMP FOR CONFIG TABLE ==="
grep -m5 'CREATE TABLE.*config' /storage/claroshop_dump/mysql_prod/app_sears10_2026_08_23.sql | head -10

echo "=== SEARCHING FOR ENCRYPTION KEY REFERENCE ==="
grep -m10 -i 'llave_encriptacion\|encrypt.*key\|KEY_AES\|tdc.*key' /storage/claroshop_dump/mysql_prod/app_sears10_2026_08_23.sql | head -10

echo "=== SEARCHING FOR core_config_data TABLE ==="
grep -m3 'CREATE TABLE.*core_config' /storage/claroshop_dump/mysql_prod/app_sears10_2026_08_23.sql

echo "=== TABLES IN DUMP (first 100) ==="
grep -oP 'CREATE TABLE.*?`\\K[^`]+' /storage/claroshop_dump/mysql_prod/app_sears10_2026_08_23.sql | head -100

echo "=== DONE ==="
"""

stdin, stdout, stderr = ssh.exec_command(cmd, timeout=300)
out = stdout.read().decode('utf-8', 'replace')
print(out[:5000])
ssh.close()
