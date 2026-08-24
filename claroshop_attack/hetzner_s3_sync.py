import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('157.180.98.220', port=22, username='root', password='?hK7L3jH76vRT7', timeout=15)

sync_script = """#!/bin/bash
export PATH=/usr/local/bin:$PATH
mkdir -p /root/claroshop_dump/s3

cat > /root/sync_all_s3.sh << 'SCRIPT'
#!/bin/bash
export PATH=/usr/local/bin:$PATH
LOG=/root/claroshop_dump/s3_sync.log
echo "=== S3 SYNC START $(date) ===" > $LOG

BUCKETS=$(aws s3 ls | awk '{print $3}')
TOTAL=$(echo "$BUCKETS" | wc -l)
COUNT=0

for b in $BUCKETS; do
    COUNT=$((COUNT+1))
    echo "[$COUNT/$TOTAL] Syncing s3://$b ..." | tee -a $LOG
    mkdir -p /root/claroshop_dump/s3/$b
    aws s3 sync s3://$b /root/claroshop_dump/s3/$b --no-sign-request 2>/dev/null || \
    aws s3 sync s3://$b /root/claroshop_dump/s3/$b 2>&1 | tail -3 | tee -a $LOG
    echo "[$COUNT/$TOTAL] DONE: $b ($(du -sh /root/claroshop_dump/s3/$b 2>/dev/null | cut -f1))" | tee -a $LOG
done

echo "=== S3 SYNC COMPLETE $(date) ===" | tee -a $LOG
echo "TOTAL SIZE:" | tee -a $LOG
du -sh /root/claroshop_dump/s3/ | tee -a $LOG
SCRIPT

chmod +x /root/sync_all_s3.sh
screen -dmS s3sync bash -c '/root/sync_all_s3.sh'
sleep 2
screen -ls
echo "=== SYNC LAUNCHED ==="
"""

stdin, stdout, stderr = ssh.exec_command(sync_script, timeout=30)
print(stdout.read().decode())
err = stderr.read().decode()
if err:
    print("STDERR:", err[:300])
ssh.close()
print("S3 sync running in background on Hetzner (screen session: s3sync)")
