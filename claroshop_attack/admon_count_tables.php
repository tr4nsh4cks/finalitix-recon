<?php
$m = @new mysqli("172.27.141.6", "apifincadodev", "1q2w3e4r5t6y", "admonplaza", 3308);
if ($m->connect_error) { echo "CONNECT_FAIL\n"; exit(1); }
$m->set_charset("utf8");
$tables = array("codigo_login_axii","ctg_depto_personal","ctg_familia_admon","ctg_log","ctg_secciones_tipo","historial_usuario_axii","historico_psw_axii","log_asignacion_evento","log_asignacion_evento_info","log_mod_sesion","log_sesion","mnu_menu","mod_familia_estatus","mod_modulos","mod_portales","mod_secciones","mod_solicitudes","mod_solicitudes_archivos","mod_solicitudes_comprobantes","mod_solicitudes_ctg_estatus","mod_solicitudes_notificaciones","permisos_acciones","usr_accesos","usr_alias_estatus","usr_estatus","usr_estatus_permisos","usr_log","usr_motivos_estatus","usr_perfiles","usr_perfiles_permisos","usr_permisos","usr_usuarios","usuario_accion");
foreach ($tables as $t) {
  $r = $m->query("SELECT COUNT(*) c FROM admonplaza.`$t`");
  if (!$r) { echo "CNT:$t=ERR:" . $m->error . "\n"; continue; }
  $row = $r->fetch_assoc();
  echo "CNT:$t=" . $row['c'] . "\n";
}
echo "DONE\n";
?>
