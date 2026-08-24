cat > /tmp/me.php << 'PHPEOF'
<?php
error_reporting(0);
try {
    $m = new MongoDB\Driver\Manager("mongodb://appt1envios:4Ap971EnvI0KI1@3.231.83.29:27017/tracking?connectTimeoutMS=8000&socketTimeoutMS=8000&authSource=tracking&replicaSet=rs0");
    $cursor = $m->executeCommand("tracking", new MongoDB\Driver\Command(array("listCollections" => 1)));
    $cols = array();
    foreach ($cursor as $doc) { foreach ($doc as $c) { $cols[] = $c->name; } }
    echo "MONGO_EXT_AUTH_OK collections=".count($cols)."\n";
    echo implode(",", array_slice($cols, 0, 30))."\n";
} catch (Exception $e) {
    echo "MONGO_EXT_FAIL: ".substr($e->getMessage(),0,250)."\n";
}
echo "DONE\n";
?>
PHPEOF
php /tmp/me.php
rm -f /tmp/me.php
