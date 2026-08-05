#!/bin/bash
VPS="root@212.224.86.211"
PASS="Tr4nsH4ck2026!Ulta"
SSH="sshpass -p $PASS ssh -o StrictHostKeyChecking=accept-new"
SCP="sshpass -p $PASS scp -o StrictHostKeyChecking=accept-new"
ZIP="/mnt/c/Users/Usuario/Downloads/Telegram Desktop/Mifel-AutoSincronizado.zip"

echo "=== [1/5] Esperando a que apt quede libre (unattended-upgrades) ==="
$SSH $VPS 'for i in $(seq 1 120); do if fuser /var/lib/dpkg/lock-frontend >/dev/null 2>&1; then sleep 10; else echo LOCK_LIBRE; break; fi; done'

echo "=== [2/5] Instalando LAMP ==="
$SSH $VPS 'DEBIAN_FRONTEND=noninteractive apt-get install -y apache2 php libapache2-mod-php php-mysql php-curl php-mbstring php-xml mariadb-server unzip 2>&1 | tail -3; echo "---"; php -v 2>/dev/null | head -1; mysql --version 2>/dev/null; apache2 -v 2>/dev/null | head -1'

echo "=== [3/5] Subiendo kit ==="
$SCP "$ZIP" $VPS:/root/mifel.zip && echo UPLOAD_OK

echo "=== [4/5] Desplegando en /var/www/html ==="
$SSH $VPS 'rm -rf /var/www/html; mkdir -p /var/www/html; cd /var/www/html && unzip -oq /root/mifel.zip && chown -R www-data:www-data /var/www/html && echo UNZIP_OK && ls /var/www/html'

echo "=== [5/5] Base de datos ==="
$SSH $VPS 'systemctl start mariadb; mysql -e "CREATE DATABASE IF NOT EXISTS mifel_sql CHARACTER SET utf8mb4;" && mysql mifel_sql < /var/www/html/MIFEL.sql && echo SQL_IMPORTADO; mysql -e "ALTER USER root@localhost IDENTIFIED VIA mysql_native_password USING PASSWORD(\"\"); FLUSH PRIVILEGES;" 2>/dev/null; mysql mifel_sql -e "SHOW TABLES; SELECT id,usuario,clave,is_admin FROM administracion_control;"'

echo "=== DEPLOY COMPLETO ==="
$SSH $VPS 'systemctl restart apache2; systemctl is-active apache2 mariadb; rm -f /root/mifel.zip'
