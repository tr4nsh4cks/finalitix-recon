<?php
$m = @new mysqli("172.27.141.6", "apifincadodev", "1q2w3e4r5t6y", "admonplaza", 3308);
if ($m->connect_error) { echo "CONNECT_FAIL\n"; exit(1); }
$m->set_charset("utf8");
// Logs recientes (ultimos 1000 de cada uno)
$queries = array(
  "log_sesion" => "SELECT * FROM admonplaza.log_sesion ORDER BY 1 DESC LIMIT 1000",
  "log_mod_sesion" => "SELECT * FROM admonplaza.log_mod_sesion ORDER BY 1 DESC LIMIT 1000",
  "usr_log" => "SELECT * FROM admonplaza.usr_log ORDER BY 1 DESC LIMIT 1000",
  "log_asignacion_evento" => "SELECT * FROM admonplaza.log_asignacion_evento ORDER BY 1 DESC LIMIT 300",
  "mod_solicitudes" => "SELECT * FROM admonplaza.mod_solicitudes ORDER BY 1 DESC LIMIT 200"
);
foreach ($queries as $t => $q) {
  $r = $m->query($q);
  if (!$r) { echo "ERR:$t:" . $m->error . "\n"; continue; }
  while ($row = $r->fetch_assoc()) {
    echo "ROW:$t|" . json_encode($row, JSON_UNESCAPED_UNICODE) . "\n";
  }
}
echo "DUMP_DONE\n";
?>
