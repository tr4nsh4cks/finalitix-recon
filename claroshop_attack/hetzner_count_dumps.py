import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('157.180.98.220', port=22, username='root', password='?hK7L3jH76vRT7', timeout=15)

cmd = """export PATH=/usr/local/bin:$PATH
echo "=== COUNT SQL FILES ==="
aws s3 ls s3://sears-backups/ --recursive --human-readable | grep -i "\\.sql" | wc -l

echo "=== LATEST 20 ==="
aws s3 ls s3://sears-backups/ --recursive --human-readable | grep -i "\\.sql" | sort -k1,2 | tail -20

echo "=== TOTAL BUCKET SIZE ==="
aws s3 ls s3://sears-backups/ --recursive --human-readable --summarize | tail -3
"""

stdin, stdout, stderr = ssh.exec_command(cmd, timeout=120)
print(stdout.read().decode('utf-8', 'replace'))
err = stderr.read().decode('utf-8', 'replace')
if err.strip():
    print("STDERR:", err[:500])
ssh.close()
