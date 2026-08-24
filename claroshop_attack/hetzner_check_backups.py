import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('157.180.98.220', port=22, username='root', password='?hK7L3jH76vRT7', timeout=15)

cmd = """export PATH=/usr/local/bin:$PATH
echo "=== SEARS-BACKUPS TOP LEVEL ==="
aws s3 ls s3://sears-backups/ 2>&1 | head -30
echo "=== SQL/DUMP FILES ==="
aws s3 ls s3://sears-backups/ --recursive 2>&1 | grep -i 'sql\|dump\|backup\|mysql\|\.gz\|\.tar' | head -30
echo "=== TOTAL SIZE ==="
aws s3 ls s3://sears-backups/ --recursive --summarize 2>&1 | tail -3
echo "=== RESPALDO-SERVERS ==="
aws s3 ls s3://respaldo-servers/ 2>&1 | head -20
"""

stdin, stdout, stderr = ssh.exec_command(cmd, timeout=60)
print(stdout.read().decode())
err = stderr.read().decode()
if err: print("ERR:", err[:200])
ssh.close()
