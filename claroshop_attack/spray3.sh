cat > /tmp/s3.php << 'PHPEOF'
<?php
error_reporting(0);
$tests = array(
    array("dbclaroe_141.26",  "172.27.141.26", 3306, "dbclaroe", "NHygr43Dr*Enq[JYq5", ""),
    array("dbclaroe_140.151", "172.27.140.151", 3306, "dbclaroe", "NHygr43Dr*Enq[JYq5", ""),
    array("dbclaroe_141.6",   "172.27.141.6", 3308, "dbclaroe", "NHygr43Dr*Enq[JYq5", ""),
    array("pedidos_140.151",  "172.27.140.151", 3306, "dbapipedidoscsb", "YF8v{%dvupN3V1%T", ""),
    array("pedidos_141.26",   "172.27.141.26", 3306, "dbapipedidoscsb", "YF8v{%dvupN3V1%T", ""),
    array("alibaba_141.4",    "172.27.141.4", 3308, "dbapialibaba", 'ZfK"%CfA\\ke@kQ:', ""),
    array("federico_140.151", "172.27.140.151", 3306, "federico.michell", "Ay)f=Zm9mY6x[e5]", ""),
    array("petapimkp_141.26", "172.27.141.26", 3306, "dbpetapimkp", "N3iUendbBbKpxFgk", ""),
    array("appclaroenvios_141.26", "172.27.141.26", 3306, "appclaroenvios", "Za85.ry/ffLS*e73k", ""),
);
foreach ($tests as $t) {
    list($label,$h,$p,$u,$pw,$db) = $t;
    $conn = @mysqli_init();
    @mysqli_options($conn, MYSQLI_OPT_CONNECT_TIMEOUT, 5);
    $ok = @mysqli_real_connect($conn, $h, $u, $pw, $db, $p);
    if ($ok) {
        echo "AUTH_OK|$label|$h:$p|$u\n";
        $r = @mysqli_query($conn, "SELECT VERSION() v, CURRENT_USER() cu");
        if ($r) { $row = mysqli_fetch_row($r); echo "  V=".$row[0]." U=".$row[1]."\n"; }
        $r = @mysqli_query($conn, "SHOW DATABASES");
        if ($r) { $dbs=array(); while ($row = mysqli_fetch_row($r)) { $dbs[]=$row[0]; } echo "  DBS: ".implode(",", $dbs)."\n"; }
        mysqli_close($conn);
    } else {
        echo "AUTH_FAIL|$label|$h:$p|$u|".substr(mysqli_connect_error(),0,90)."\n";
    }
}
// redis test
echo "--- REDIS 172.27.140.151:6379 ---\n";
$redis = @fsockopen("172.27.140.151", 6379, $en, $es, 5);
if ($redis) {
    fwrite($redis, "AUTH @st0rAg3K3Y\r\n");
    echo "AUTH_RESP: ".fgets($redis);
    fwrite($redis, "INFO server\r\n");
    $resp = fread($redis, 400);
    echo "INFO_RESP: ".substr($resp,0,200)."\n";
    fclose($redis);
} else { echo "REDIS closed: $es\n"; }
echo "DONE\n";
?>
PHPEOF
php /tmp/s3.php
rm -f /tmp/s3.php
