import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('157.180.98.220', port=22, username='root', password='?hK7L3jH76vRT7', timeout=15)

cmd = "export PATH=/usr/local/bin:$PATH && echo '=== DOWNLOAD STATUS ===' && ls -lh /storage/claroshop_dump/mysql_prod/ 2>/dev/null && echo '=== ALL BUCKETS ===' && aws s3 ls && echo '=== CONFIG FILES IN SEARS-BACKUPS ===' && aws s3 ls s3://sears-backups/ --recursive | grep -iE 'local\\.php|config|env|\\.yml|\\.properties|secret' | head -30"

stdin, stdout, stderr = ssh.exec_command(cmd, timeout=60)
out = stdout.read().decode('utf-8', 'replace')
err = stderr.read().decode('utf-8', 'replace')
print(out)
if err.strip():
    print("ERR:", err[:300])
ssh.close()
