import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('157.180.98.220', port=22, username='root', password='?hK7L3jH76vRT7', timeout=15)

cmd = r"""
echo "=== TABLAS CLIENTES/PII ==="
grep -oP 'CREATE TABLE.*?`\K[^`]+' /storage/claroshop_dump/mysql_prod/app_sears10_2026_08_23.sql | grep -iE 'client|custom|user|person|cuenta|direccion|address|email|telefon|phone|tarjeta|card|pago|payment|pedido|order|factur|invoice|token|credit|saldo|wallet' | sort

echo "=== ROW COUNTS (INSERT lines) ==="
for t in clientes cliente customer customers users usuario usuarios datostarjeta direcciones addresses pedidos orders facturas; do
  c=$(grep -c "INSERT INTO.*\`$t\`" /storage/claroshop_dump/mysql_prod/app_sears10_2026_08_23.sql 2>/dev/null)
  if [ "$c" != "0" ]; then
    echo "$t: $c INSERT statements"
  fi
done

echo "=== SAMPLE CLIENTES TABLE STRUCTURE ==="
grep -m1 -A2 'CREATE TABLE.*`clientes`' /storage/claroshop_dump/mysql_prod/app_sears10_2026_08_23.sql | head -30
grep -m1 -A2 'CREATE TABLE.*`cliente`' /storage/claroshop_dump/mysql_prod/app_sears10_2026_08_23.sql | head -30

echo "=== SAMPLE USERS TABLE ==="
grep -m1 -A2 'CREATE TABLE.*`users`' /storage/claroshop_dump/mysql_prod/app_sears10_2026_08_23.sql | head -30

echo "=== DATOSTARJETA STRUCTURE ==="
grep -m1 'CREATE TABLE' /storage/claroshop_dump/mysql_prod/app_sears10_2026_08_23.sql | head -1
grep -B1 -A30 'CREATE TABLE.*`datostarjeta`' /storage/claroshop_dump/mysql_prod/app_sears10_2026_08_23.sql | head -35

echo "=== DONE ==="
"""

stdin, stdout, stderr = ssh.exec_command(cmd, timeout=300)
out = stdout.read().decode('utf-8', 'replace')
print(out[:8000])
ssh.close()
