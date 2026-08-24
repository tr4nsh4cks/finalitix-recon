cat > /tmp/mon.php << 'PHPEOF'
<?php
error_reporting(0);
$conn = @mysqli_init();
@mysqli_options($conn, MYSQLI_OPT_CONNECT_TIMEOUT, 6);
if (!@mysqli_real_connect($conn, "172.27.140.151", "dbapipedidoscsb", "YF8v{%dvupN3V1%T", "monedero", 3306)) {
    echo "FAIL\n"; exit(1);
}
mysqli_set_charset($conn, "utf8");
echo "=== monedero TABLES ===\n";
$r = mysqli_query($conn, "SHOW TABLES");
$tables = array();
while ($row = mysqli_fetch_row($r)) { $tables[] = $row[0]; }
echo implode(",", $tables)."\n";
foreach ($tables as $tb) {
    $rc = mysqli_query($conn, "SELECT COUNT(*) FROM `$tb`");
    $cnt = $rc ? mysqli_fetch_row($rc)[0] : "?";
    echo "COUNT $tb = $cnt\n";
}
echo "=== payment_t1 TABLES (141.26 has it too) ===\n";
mysqli_select_db($conn, "payment_t1");
$r = mysqli_query($conn, "SHOW TABLES");
$tables = array();
while ($row = mysqli_fetch_row($r)) { $tables[] = $row[0]; }
echo implode(",", $tables)."\n";
foreach ($tables as $tb) {
    $rc = mysqli_query($conn, "SELECT COUNT(*) FROM `$tb`");
    $cnt = $rc ? mysqli_fetch_row($rc)[0] : "?";
    echo "COUNT $tb = $cnt\n";
}
echo "DONE\n";
?>
PHPEOF
php /tmp/mon.php
rm -f /tmp/mon.php
