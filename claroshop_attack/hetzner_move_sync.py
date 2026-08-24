import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('157.180.98.220', port=22, username='root', password='?hK7L3jH76vRT7', timeout=15)

cmd = """export PATH=/usr/local/bin:$PATH
# Kill old sync and move to /storage
screen -X -S s3sync quit 2>/dev/null
mkdir -p /storage/claroshop_dump/s3
mv /root/claroshop_dump/s3/* /storage/claroshop_dump/s3/ 2>/dev/null

# New sync script targeting /storage
cat > /storage/sync_all_s3.sh << 'SCRIPT'
#!/bin/bash
export PATH=/usr/local/bin:$PATH
LOG=/storage/claroshop_dump/s3_sync.log
echo "=== S3 SYNC START $(date) ===" > $LOG

BUCKETS=$(aws s3 ls | awk '{print $3}')
TOTAL=$(echo "$BUCKETS" | wc -l)
COUNT=0

for b in $BUCKETS; do
    COUNT=$((COUNT+1))
    echo "[$COUNT/$TOTAL] Syncing s3://$b ..." | tee -a $LOG
    mkdir -p /storage/claroshop_dump/s3/$b
    aws s3 sync s3://$b /storage/claroshop_dump/s3/$b 2>&1 | tail -5 | tee -a $LOG
    echo "[$COUNT/$TOTAL] DONE: $b ($(du -sh /storage/claroshop_dump/s3/$b 2>/dev/null | cut -f1))" | tee -a $LOG
done

echo "=== S3 SYNC COMPLETE $(date) ===" | tee -a $LOG
du -sh /storage/claroshop_dump/s3/ | tee -a $LOG
SCRIPT

chmod +x /storage/sync_all_s3.sh
screen -dmS s3sync bash -c '/storage/sync_all_s3.sh'
sleep 2
screen -ls
echo "=== RELAUNCHED TO /storage (58TB free) ==="
"""

stdin, stdout, stderr = ssh.exec_command(cmd, timeout=30)
print(stdout.read().decode('utf-8', 'replace'))
ssh.close()
