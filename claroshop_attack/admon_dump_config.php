<?php
$m = @new mysqli("172.27.141.6", "apifincadodev", "1q2w3e4r5t6y", "admonplaza", 3308);
if ($m->connect_error) { echo "CONNECT_FAIL\n"; exit(1); }
$m->set_charset("utf8");
$tables = array(
  "mod_portales","usr_perfiles","usr_perfiles_permisos","permisos_acciones",
  "mnu_menu","mod_modulos","mod_secciones","ctg_depto_personal","ctg_familia_admon",
  "ctg_log","ctg_secciones_tipo","mod_familia_estatus","usr_estatus","usr_alias_estatus",
  "usr_motivos_estatus","mod_solicitudes_ctg_estatus","mod_solicitudes_notificaciones"
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
