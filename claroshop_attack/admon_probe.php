<?php
echo "PHP_VERSION: " . PHP_VERSION . "\n";
echo "mysqli: " . (extension_loaded('mysqli') ? "YES" : "NO") . "\n";
$m = @new mysqli("172.27.141.6", "apifincadodev", "1q2w3e4r5t6y", "admonplaza", 3308);
if ($m->connect_error) { echo "CONNECT_FAIL: " . $m->connect_error . "\n"; exit(1); }
echo "CONNECT_OK " . $m->host_info . "\n";
$m->set_charset("utf8");

echo "=== DESCRIBE admonplaza.usr_usuarios ===\n";
$r = $m->query("DESCRIBE admonplaza.usr_usuarios");
if (!$r) { echo "ERR: " . $m->error . "\n"; } else {
  while ($row = $r->fetch_assoc()) {
    echo $row['Field'] . " | " . $row['Type'] . " | Null:" . $row['Null'] . " | Key:" . $row['Key'] . " | Default:" . $row['Default'] . "\n";
  }
}

$r = $m->query("SELECT COUNT(*) c FROM admonplaza.usr_usuarios");
$row = $r->fetch_assoc();
echo "=== COUNT usr_usuarios: " . $row['c'] . " ===\n";

echo "=== TABLES admonplaza ===\n";
$r = $m->query("SHOW TABLES FROM admonplaza");
$n = 0;
while ($row = $r->fetch_row()) { echo $row[0] . "\n"; $n++; }
echo "=== TOTAL TABLES: $n ===\n";

echo "=== DATABASES ===\n";
$r = $m->query("SHOW DATABASES");
while ($row = $r->fetch_row()) { echo $row[0] . "\n"; }
echo "DONE\n";
?>
