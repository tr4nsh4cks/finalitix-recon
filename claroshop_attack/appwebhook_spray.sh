cat > /tmp/aw.php << 'PHPEOF'
<?php
error_reporting(0);
$tests = array(
    array("WEBHOOK_3322", "172.27.140.151", 3322, "appwebhook", "4Ap9w38H0o#kT56j", "claro_envios"),
    array("WEBHOOK_3306", "172.27.140.151", 3306, "appwebhook", "4Ap9w38H0o#kT56j", ""),
    array("WEBHOOK_141.6", "172.27.141.6", 3308, "appwebhook", "4Ap9w38H0o#kT56j", ""),
    array("WEBHOOK_141.26", "172.27.141.26", 3306, "appwebhook", "4Ap9w38H0o#kT56j", ""),
    array("GUIAS_MONGO", "172.26.84.132", 27021, "appguiasmasivast1", "BCD4TiQzYN<u2.N(", "guias_masivas"),
);
foreach ($tests as $t) {
    list($label,$h,$p,$u,$pw,$db) = $t;
    if (strpos($label, "MONGO") !== false) {
        try {
            $m = new MongoDB\Driver\Manager("mongodb://$u:".urlencode($pw)."@$h:$p/$db?connectTimeoutMS=6000&socketTimeoutMS=6000&authSource=$db");
            $cursor = $m->executeCommand($db, new MongoDB\Driver\Command(array("listCollections" => 1)));
            $n = 0; foreach ($cursor as $doc) { $n++; }
            echo "MONGO_AUTH_OK|$label|$h:$p|$u|collections=$n\n";
        } catch (Exception $e) {
            echo "MONGO_FAIL|$label|$h:$p|$u|".substr($e->getMessage(),0,150)."\n";
        }
        continue;
    }
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
php /tmp/aw.php
rm -f /tmp/aw.php
