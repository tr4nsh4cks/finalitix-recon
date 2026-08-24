<?php
$m = @new mysqli("172.27.141.6", "apifincadodev", "1q2w3e4r5t6y", "admonplaza", 3308);
if ($m->connect_error) { echo "CONNECT_FAIL: " . $m->connect_error . "\n"; exit(1); }
$m->set_charset("utf8");
$r = $m->query("SELECT * FROM admonplaza.usr_usuarios ORDER BY Id");
if (!$r) { echo "QUERY_FAIL: " . $m->error . "\n"; exit(1); }
$n = 0;
while ($row = $r->fetch_assoc()) {
  echo "ROW:" . json_encode($row, JSON_UNESCAPED_UNICODE) . "\n";
  $n++;
}
echo "DUMP_DONE rows=$n\n";
?>
