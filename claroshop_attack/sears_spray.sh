cat > /tmp/ss.php << 'PHPEOF'
<?php
error_reporting(0);
$tests = array(
    array("SEARS_141.6_tienda", "172.27.141.6", 3308, "dbpetapimkp", "N3iUendbBbKpxFgk", "tienda"),
    array("SEARS_141.6_nodb",   "172.27.141.6", 3308, "dbpetapimkp", "N3iUendbBbKpxFgk", ""),
    array("DEV_140.151",        "172.27.140.151", 3306, "dbpetapimkp", "N3iUendbBbKpxFgk", ""),
    array("SEARS_141.24_3308",  "172.27.141.24", 3308, "dbpetapimkp", "N3iUendbBbKpxFgk", "tienda"),
);
foreach ($tests as $t) {
    list($label,$h,$p,$u,$pw,$db) = $t;
    $conn = @mysqli_init();
    @mysqli_options($conn, MYSQLI_OPT_CONNECT_TIMEOUT, 5);
    $ok = @mysqli_real_connect($conn, $h, $u, $pw, $db, $p);
    if ($ok) {
        echo "AUTH_OK|$label|$h:$p|$u|$db\n";
        $r = @mysqli_query($conn, "SELECT VERSION() v, CURRENT_USER() cu");
        if ($r) { $row = mysqli_fetch_row($r); echo "  VERSION=".$row[0]." USER=".$row[1]."\n"; }
        $r = @mysqli_query($conn, "SHOW DATABASES");
        if ($r) { while ($row = mysqli_fetch_row($r)) { echo "  DB: ".$row[0]."\n"; } }
        mysqli_close($conn);
    } else {
        echo "AUTH_FAIL|$label|$h:$p|$u|".mysqli_connect_error()."\n";
    }
}
echo "DONE\n";
?>
PHPEOF
php /tmp/ss.php
rm -f /tmp/ss.php
