import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('157.180.98.220', port=22, username='root', password='?hK7L3jH76vRT7', timeout=15)

stdin, stdout, stderr = ssh.exec_command('df -h && echo "===LSBLK===" && lsblk && echo "===MOUNTS===" && mount | grep -v tmpfs | grep -v proc | grep -v sys', timeout=15)
print(stdout.read().decode())
ssh.close()
