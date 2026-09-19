"""Run full Cognito probe suite from VPS"""
import paramiko, json

VPS = '216.238.69.202'
PW = r'hL@4xY@k)Nt6z_CE'

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(VPS, username='root', password=PW, timeout=10)
print(f'Connected to {VPS}')

# Upload
sftp = ssh.open_sftp()
sftp.put(r'c:\xampp\htdocs\pentagi\disperso_recon\cognito_probe.py', '/tmp/cognito_probe.py')
sftp.close()
print('Uploaded')

# Install + run
stdin, stdout, stderr = ssh.exec_command('pip3 install requests -q 2>&1 && python3 /tmp/cognito_probe.py 2>&1', timeout=90)
out = stdout.read().decode()
err_out = stderr.read().decode()
print(out)
if err_out:
    print(f'STDERR: {err_out}')

ssh.close()
