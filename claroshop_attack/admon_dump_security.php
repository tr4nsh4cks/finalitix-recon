<?php
$m = @new mysqli("172.27.141.6", "apifincadodev", "1q2w3e4r5t6y", "admonplaza", 3308);
if ($m->connect_error) { echo "CONNECT_FAIL\n"; exit(1); }
$m->set_charset("utf8");
$tables = array(
  "historico_psw_axii","codigo_login_axii","usr_accesos","usuario_accion","historial_usuario_axii"
);
foreach ($tables as $t) {
  $r = $m->query("SELECT * FROM admonplaza.`$t`");
  if (!$r) { echo "ERR:$t:" . $m->error . "\n"; continue; }
  while ($row = $r->fetch_assoc()) {
    echo "ROW:$t|" . json_encode($row, JSON_UNESCAPED_UNICODE) . "\n";
  }
}
echo "DUMP_DONE\n";
?>
