import paramiko, sys

vps = '64.177.88.10'
password = r'5F.jyTK$D6%.F{a='
local_file = r'C:\xampp\htdocs\pentagi\independencia_attack\fisa_probe_infra.py'

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
try:
    ssh.connect(vps, username='root', password=password, timeout=10)
    print(f'Connected to {vps}')
    
    sftp = ssh.open_sftp()
    sftp.put(local_file, '/root/fisa_probe_infra.py')
    print('Uploaded fisa_probe_infra.py')
    sftp.close()
    
    # Install requests if needed, then run
    stdin, stdout, stderr = ssh.exec_command('pip3 install requests -q 2>/dev/null; python3 /root/fisa_probe_infra.py 2>&1', timeout=300)
    for line in stdout:
        print(line.strip())
    for line in stderr:
        print(f'ERR: {line.strip()}')
    ssh.close()
    print('\nDone.')
except Exception as e:
    print(f'Error: {e}')
    sys.exit(1)
