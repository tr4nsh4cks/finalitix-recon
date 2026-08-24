import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('157.180.98.220', port=22, username='root', password='?hK7L3jH76vRT7', timeout=15)

stdin, stdout, stderr = ssh.exec_command('cat /root/claroshop_dump/s3_sync.log 2>/dev/null | tail -20 && echo "===DISK===" && du -sh /root/claroshop_dump/s3/ 2>/dev/null && echo "===BUCKETS_DONE===" && ls /root/claroshop_dump/s3/ 2>/dev/null', timeout=15)
print(stdout.read().decode())
ssh.close()
