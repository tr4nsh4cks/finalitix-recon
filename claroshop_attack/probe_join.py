from exfil_august_orders import run_php

PHP = '''<?php
$c = new mysqli("172.27.141.6","apifincadodev","1q2w3e4r5t6y","tienda",3308);
if ($c->connect_error) { echo "DBERR: ".$c->connect_error."\\n"; exit(1); }
echo "== SAMPLE AGO ==\\n";
$r = $c->query("SELECT Id, Cliente, Num_pedido, num_externo, Fecha_Inicio FROM pedidos WHERE Fecha_Inicio>='2026-08-01' ORDER BY Id DESC LIMIT 5");
while ($row = $r->fetch_assoc()) { echo $row["Id"]." | ".$row["Cliente"]." | ".$row["Num_pedido"]." | ".$row["num_externo"]." | ".$row["Fecha_Inicio"]."\\n"; }
echo "== RANGOS ==\\n";
$r = $c->query("SELECT MAX(Id) mi FROM pedidos"); $row=$r->fetch_assoc(); echo "max pedidos.Id=".$row["mi"]."\\n";
$r = $c->query("SELECT MAX(Pedido) mp, MIN(Pedido) mn, COUNT(*) c FROM datos_pedido"); $row=$r->fetch_assoc(); echo "datos_pedido.Pedido: min=".$row["mn"]." max=".$row["mp"]." count=".$row["c"]."\\n";
echo "== JOIN NUM_PEDIDO ==\\n";
$r = $c->query("SELECT COUNT(*) c FROM pedidos p INNER JOIN datos_pedido dp ON p.Num_pedido=dp.Pedido WHERE p.Fecha_Inicio>='2026-08-01' AND p.Fecha_Inicio<'2026-09-01'");
$row=$r->fetch_assoc(); echo "join_num_pedido=".$row["c"]."\\n";
echo "== JOIN NUM_EXTERNO ==\\n";
$r = $c->query("SELECT COUNT(*) c FROM pedidos p INNER JOIN datos_pedido dp ON p.num_externo=dp.Pedido WHERE p.Fecha_Inicio>='2026-08-01' AND p.Fecha_Inicio<'2026-09-01'");
$row=$r->fetch_assoc(); echo "join_num_externo=".$row["c"]."\\n";
echo "== datosenvio cols ==\\n";
$r = $c->query("SHOW COLUMNS FROM datosenvio");
while ($row = $r->fetch_assoc()) { echo $row["Field"]." | ".$row["Type"]."\\n"; }
echo "== datos_pedido_historial cols ==\\n";
$r = $c->query("SHOW COLUMNS FROM datos_pedido_historial");
if (!$r) { echo "QERR: ".$c->error."\\n"; } else { while ($row = $r->fetch_assoc()) { echo $row["Field"]." | ".$row["Type"]."\\n"; } }
'''

print(run_php(PHP, "joinprobe"))
