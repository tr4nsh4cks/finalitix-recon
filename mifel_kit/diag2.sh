#!/bin/bash
VPS="root@212.224.86.211"
PASS="Tr4nsH4ck2026!Ulta"
SSH="sshpass -p $PASS ssh -o StrictHostKeyChecking=accept-new"
$SSH $VPS 'echo "--- uptime:"; uptime; echo "--- sites-enabled:"; ls -la /etc/apache2/sites-enabled/ /etc/apache2/sites-available/ 2>/dev/null; echo "--- zip en root:"; ls -la /root/ | grep -i zip; echo "--- apache conf:"; ls /etc/apache2/ 2>/dev/null; echo "--- agentes raros:"; ps aux | grep -iE "ulta|agent|cloud-init|provision" | grep -v grep; echo "--- cloud-init status:"; cloud-init status 2>/dev/null; echo "--- ultimos logins:"; last -5 2>/dev/null; echo "--- journal apache (ultimas 5):"; journalctl -u apache2 --no-pager -n 5 2>/dev/null | tail -5'
