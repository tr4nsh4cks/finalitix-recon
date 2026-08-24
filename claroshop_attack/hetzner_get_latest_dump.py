import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('157.180.98.220', port=22, username='root', password='?hK7L3jH76vRT7', timeout=15)

cmd = """export PATH=/usr/local/bin:$PATH
mkdir -p /storage/claroshop_dump/mysql_prod

echo "=== DOWNLOADING LATEST PROD DUMP (6.8 GB) ==="
screen -dmS sqldump bash -c 'export PATH=/usr/local/bin:$PATH; aws s3 cp s3://sears-backups/mysql/app_sears10_2026_08_23.sql /storage/claroshop_dump/mysql_prod/app_sears10_2026_08_23.sql 2>&1 | tee /storage/claroshop_dump/mysql_prod/download.log; echo DONE >> /storage/claroshop_dump/mysql_prod/download.log'

echo "=== ALSO GETTING tienda_2026.sql (5.6 GB) ==="
screen -dmS tienda bash -c 'export PATH=/usr/local/bin:$PATH; aws s3 cp s3://sears-backups/mysql/tienda_2026.sql /storage/claroshop_dump/mysql_prod/tienda_2026.sql 2>&1 | tee /storage/claroshop_dump/mysql_prod/tienda_download.log; echo DONE >> /storage/claroshop_dump/mysql_prod/tienda_download.log'

sleep 2
screen -ls
echo "=== 2 downloads launched: app_sears10 (6.8G) + tienda (5.6G) ==="
"""

stdin, stdout, stderr = ssh.exec_command(cmd, timeout=30)
print(stdout.read().decode('utf-8', 'replace'))
ssh.close()
