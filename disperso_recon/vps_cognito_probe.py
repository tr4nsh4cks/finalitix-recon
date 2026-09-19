"""Run Cognito probes from VPS via SSH"""
import paramiko, json, sys, time

VPS = '64.177.88.10'
PW = r'5F.jyTK$D6%.F{a='

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(VPS, username='root', password=PW, timeout=10)
print(f'Connected to {VPS}')

# Upload the probe script
sftp = ssh.open_sftp()
sftp.put(r'c:\xampp\htdocs\pentagi\disperso_recon\cognito_probe.py', '/tmp/cognito_probe.py')
sftp.close()
print('Uploaded cognito_probe.py')

# Ensure requests is installed
stdin, stdout, stderr = ssh.exec_command('pip3 install requests -q 2>&1', timeout=30)
stdout.channel.recv_exit_status()
print('requests installed')

# Run the probe
stdin, stdout, stderr = ssh.exec_command('python3 /tmp/cognito_probe.py 2>&1', timeout=60)
out = stdout.read().decode()
err = stderr.read().decode()
print(out)
if err:
    print(f'STDERR: {err}')

ssh.close()
