#!/bin/bash
# HTTPS para el IP via sslip.io (dominio gratis que resuelve al IP) + certbot
VPS="root@212.224.86.211"
PASS="Tr4nsH4ck2026!Ulta"
SSH="sshpass -p $PASS ssh -o StrictHostKeyChecking=accept-new"
DOM="212.224.86.211.sslip.io"

echo "=== Verificando que $DOM resuelve ==="
$SSH $VPS "getent hosts $DOM || nslookup $DOM 2>/dev/null | tail -3"

echo "=== Instalando certbot ==="
$SSH $VPS 'for i in $(seq 1 60); do if fuser /var/lib/dpkg/lock-frontend >/dev/null 2>&1; then sleep 10; else break; fi; done; DEBIAN_FRONTEND=noninteractive apt-get install -y certbot python3-certbot-apache 2>&1 | tail -2'

echo "=== Generando certificado ==="
$SSH $VPS "certbot --apache -d $DOM --agree-tos -m tr4nsh4cks@gmail.com --redirect --no-eff-email 2>&1 | tail -15"

echo "=== Verificando vhost SSL ==="
$SSH $VPS 'apache2ctl -S 2>/dev/null | grep -i ssl; ls /etc/letsencrypt/live/ 2>/dev/null'

echo "=== HTTPS_LISTO: https://$DOM ==="
