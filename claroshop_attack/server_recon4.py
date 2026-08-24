"""Recon phase 4: explore S3 source code folders for AES class + locate nTarjeta context."""
import paramiko

HOST = "157.180.98.220"
USER = "root"
PASS = "?hK7L3jH76vRT7"

REMOTE_SCRIPT = r'''
#!/bin/bash
echo "=== ats.sears.com.mx content ==="
ls -la /storage/claroshop_dump/s3/axii-pedidos/ats.sears.com.mx/ 2>/dev/null
echo ""
echo "=== ats.dev.sears.com.mx content ==="
ls -la /storage/claroshop_dump/s3/axii-pedidos/ats.dev.sears.com.mx/ 2>/dev/null
echo ""
echo "=== Search for AesCtr / Aes.php / Veness in S3 folder ==="
grep -rli 'veness\|AesCtr\|class Aes' /storage/claroshop_dump/s3/ 2>/dev/null | head -20
echo ""
echo "=== Search for the key itself in S3 ==="
grep -rl '8L84j3x3yZY894gyEwFNhDSPSrfyHf9WA' /storage/claroshop_dump/s3/ 2>/dev/null | head -10
echo ""
echo "=== Search encrypt/decrypt PHP files ==="
find /storage/claroshop_dump/s3/ -iname '*aes*' -o -iname '*crypt*' -o -iname '*cipher*' 2>/dev/null | head -20
echo ""
echo "=== nTarjeta context in app_sears10 (first 3 matches, 200 chars) ==="
grep -o -i '.\{80\}ntarjeta.\{120\}' /storage/claroshop_dump/mysql_prod/app_sears10_2026_08_23.sql | head -3
echo ""
echo "=== INCOMMTARJETAS context ==="
grep -o -i '.\{60\}INCOMMTARJETAS.\{80\}' /storage/claroshop_dump/mysql_prod/app_sears10_2026_08_23.sql | head -3
'''

c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect(HOST, username=USER, password=PASS, timeout=30)

sftp = c.open_sftp()
with sftp.file("/tmp/recon4.sh", "w") as f:
    f.write(REMOTE_SCRIPT)
sftp.close()

stdin, stdout, stderr = c.exec_command("bash /tmp/recon4.sh", timeout=1800)
out = stdout.read().decode("utf-8", errors="replace")
err = stderr.read().decode("utf-8", errors="replace")
print(out)
if err:
    print("--- STDERR ---")
    print(err)
c.close()
