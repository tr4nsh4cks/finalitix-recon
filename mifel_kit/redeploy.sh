#!/bin/bash
VPS="root@212.224.86.211"
PASS="Tr4nsH4ck2026!Ulta"
SSH="sshpass -p $PASS ssh -o StrictHostKeyChecking=accept-new"
SCP="sshpass -p $PASS scp -o StrictHostKeyChecking=accept-new"
ZIP="/mnt/c/Users/Usuario/Downloads/Telegram Desktop/Mifel-AutoSincronizado.zip"

echo "=== mounts/cron/timers sospechosos ==="
$SSH $VPS 'mount | grep -E "www|html" ; echo "--- cron:"; crontab -l 2>/dev/null; ls /etc/cron.d/ 2>/dev/null; echo "--- timers:"; systemctl list-timers --no-pager 2>/dev/null | head -10'

echo "=== re-subir zip ==="
$SCP "$ZIP" $VPS:/root/mifel.zip && echo UPLOAD_OK

echo "=== unzip ==="
$SSH $VPS 'cd /var/www/html && unzip -oq /root/mifel.zip && chown -R www-data:www-data /var/www/html && echo UNZIP_OK && ls /var/www/html | wc -l && test -f /var/www/html/index.php && echo INDEX_OK'

echo "=== verificacion inmediata ==="
$SSH $VPS 'curl -s -o /dev/null -w "index.php: %{http_code}\n" http://localhost/index.php; curl -s -o /dev/null -w "control: %{http_code}\n" http://localhost/control/'
