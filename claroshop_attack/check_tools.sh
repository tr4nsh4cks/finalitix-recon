which mysql php python python3 nc 2>/dev/null
echo "---PHP---"
php -v 2>/dev/null | head -1
echo "---PHP_MODULES---"
php -m 2>/dev/null | grep -iE "mysql|pdo|mongodb|redis"
echo "---DONE---"
