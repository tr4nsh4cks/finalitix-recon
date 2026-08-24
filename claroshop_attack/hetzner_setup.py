import paramiko, sys

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('157.180.98.220', port=22, username='root', password='?hK7L3jH76vRT7', timeout=15)

setup_script = """#!/bin/bash
set -e
pip3 install --break-system-packages awscli 2>&1 | tail -5
export PATH=/usr/local/bin:$PATH
mkdir -p /root/.aws /root/claroshop_dump/s3

cat > /root/.aws/credentials << 'EOF'
[default]
aws_access_key_id = AKIA4QYKCQNRTB3RPOG5
aws_secret_access_key = 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
EOF

cat > /root/.aws/config << 'EOF'
[default]
region = us-east-1
output = json
EOF

aws --version
echo "=== BUCKETS ==="
aws s3 ls
echo "=== BUCKET COUNT ==="
aws s3 ls | wc -l
"""

stdin, stdout, stderr = ssh.exec_command(setup_script, timeout=180)
out = stdout.read().decode()
err = stderr.read().decode()
print(out)
if err:
    print("STDERR:", err[:500])
ssh.close()
