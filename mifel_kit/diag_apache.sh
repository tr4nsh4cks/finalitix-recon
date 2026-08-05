#!/bin/bash
VPS="root@212.224.86.211"
PASS="Tr4nsH4ck2026!Ulta"
SSH="sshpass -p $PASS ssh -o StrictHostKeyChecking=accept-new"
$SSH $VPS 'echo "--- DocumentRoot:"; grep -r DocumentRoot /etc/apache2/sites-enabled/; echo "--- files:"; ls -la /var/www/html/ | head -12; echo "--- index.php:"; test -f /var/www/html/index.php && echo SI || echo NO; echo "--- curl index.php:"; curl -s -o /dev/null -w "%{http_code}\n" http://localhost/index.php; echo "--- php mod:"; apache2ctl -M 2>/dev/null | grep -i php; echo "--- puertos:"; ss -tlnp | grep -E ":80 |:443 "'
