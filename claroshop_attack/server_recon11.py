"""Recon phase 11: deep search for key/AesCtr/datostarjeta across dumps and buckets."""
import paramiko

HOST = "157.180.98.220"
USER = "root"
PASS = "?hK7L3jH76vRT7"

REMOTE_SCRIPT = r'''
#!/bin/bash
APP=/storage/claroshop_dump/mysql_prod/app_sears10_2026_08_23.sql
TIENDA=/storage/claroshop_dump/mysql_prod/tienda_2026.sql

echo "=== 1. Key 8L84j3x3 in app_sears10 dump ==="
grep -m2 -o '.\{0,50\}8L84j3x3.\{0,50\}' "$APP" || echo "NOT FOUND"
echo ""
echo "=== 2. Key in tienda dump ==="
grep -m2 -o '.\{0,50\}8L84j3x3.\{0,50\}' "$TIENDA" || echo "NOT FOUND"
echo ""
echo "=== 3. AesCtr / Veness / aes_ctr in app dump ==="
grep -m3 -oi '.\{0,40\}\(aesctr\|veness\|aes_ctr\).\{0,60\}' "$APP" || echo "NOT FOUND"
echo ""
echo "=== 4. datos + tarjeta combined search in app (any order) ==="
grep -m3 -oi '.\{0,30\}datos.\{0,20\}tarjeta.\{0,40\}' "$APP" | head -5 || echo "NOT FOUND"
echo ""
echo "=== 5. dev latest dump: tables list ==="
aws s3 cp s3://sears-backups/mysql/app_sears10_dev_2026_w33.sql - 2>/dev/null | grep -o 'CREATE TABLE `[^`]*`' | head -100
echo ""
echo "=== 6. dev dump: datostarjeta/tarjeta search ==="
aws s3 cp s3://sears-backups/mysql/app_sears10_dev_2026_w33.sql - 2>/dev/null | grep -m3 -oi '.\{0,40\}tarjeta.\{0,60\}' | head -5 || echo "NOT FOUND"
echo ""
echo "=== 7. app_sears10_recent.sql: datostarjeta stream-grep (4 min max) ==="
timeout 240 aws s3 cp s3://sears-backups/mysql/app_sears10_recent.sql - 2>/dev/null | grep -m2 -oi '.\{0,60\}datostarjeta.\{0,80\}' || echo "NO MATCH in streamed portion"
echo ""
echo "=== 8. portales-cs config ==="
aws s3 ls s3://portales-cs/config/ --recursive 2>&1 | head -20
'''

c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect(HOST, username=USER, password=PASS, timeout=30)

sftp = c.open_sftp()
with sftp.file("/tmp/recon11.sh", "w") as f:
    f.write(REMOTE_SCRIPT)
sftp.close()

stdin, stdout, stderr = c.exec_command("bash /tmp/recon11.sh", timeout=1200)
out = stdout.read().decode("utf-8", errors="replace")
err = stderr.read().decode("utf-8", errors="replace")
print(out)
if err:
    print("--- STDERR ---")
    print(err)
c.close()
