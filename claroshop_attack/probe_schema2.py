from exfil_august_orders import run_php

PHP = '''<?php
$c = new mysqli("172.27.141.6","apifincadodev","1q2w3e4r5t6y","tienda",3308);
if ($c->connect_error) { echo "DBERR: ".$c->connect_error."\\n"; exit(1); }
echo "== TABLES ==\\n";
$r = $c->query("SHOW TABLES");
while ($row = $r->fetch_row()) { echo $row[0]."\\n"; }
echo "== RANGO pedidos ==\\n";
$r = $c->query("SELECT MIN(Fecha_Inicio) mn, MAX(Fecha_Inicio) mx, COUNT(*) c FROM pedidos");
$row = $r->fetch_assoc(); echo $row["mn"]." .. ".$row["mx"]." total=".$row["c"]."\\n";
echo "== AGO-2026 ==\\n";
$r = $c->query("SELECT COUNT(*) c FROM pedidos WHERE Fecha_Inicio >= '2026-08-01' AND Fecha_Inicio < '2026-09-01'");
$row = $r->fetch_assoc(); echo "agosto=".$row["c"]."\\n";
echo "== DUP datos_pedido ==\\n";
$r = $c->query("SELECT COUNT(*) dups FROM (SELECT Pedido, COUNT(*) c FROM datos_pedido GROUP BY Pedido HAVING c>1) t");
$row = $r->fetch_assoc(); echo "pedidos_con_dp_duplicado=".$row["dups"]."\\n";
'''

print(run_php(PHP, "schema2"))
