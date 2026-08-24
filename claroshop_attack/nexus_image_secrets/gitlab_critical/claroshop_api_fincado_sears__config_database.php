<?php

$PATH_LOCAL = "/api_fincado_sears/";
$PATH_DEV = "/pse-admin-api.dev.mrc-services.io/";
$PATH_QA = "/pse-admin-api.qa.mrc-services.io/";
$PATH_REL = "/pse-release.adm-api.mrc-services.io/";
$PATH_PROD = "/pse.adm-api.mrc-services.io/";

$config = array(
    'default' => 'sears',
    'connections' => array(
        'sears' => array(
            'driver' => 'mysql',
            'host' => '1234',
            'username' => 'apifincadodev',
            'database' => 'tienda',
            'password' => '1q2w3e4r5t6y',
            'port' => '3308',
            'charset' => 'utf8',
            'auto_cache' => 7200,
            'prefix' => '',
            'depurar' => false
        ),
        'sears2' => array(
            'driver' => 'mysql',
            'host' => '1234',
            'username' => 'apifincadodev',
            'database' => 'admonplaza',
            'password' => '1q2w3e4r5t6y',
            'port' => '3308',
            'charset' => 'utf8',
            'auto_cache' => 7200,
            'prefix' => '',
            'depurar' => false
        )
    ),
);

if (strpos(dirname(__DIR__) . "/", $PATH_LOCAL) !== false) {
    $config['connections']['sears2']['host'] = $config['connections']['sears']['host'] = '172.27.141.6';
} else if (strpos(dirname(__DIR__) . "/", $PATH_DEV) !== false) {
    $config['connections']['sears2']['host'] = $config['connections']['sears']['host'] = 'dbasears.dev.mrc-services.io';
} else if (strpos(dirname(__DIR__) . "/", $PATH_QA) !== false) {
    $config['connections']['sears2']['host'] = $config['connections']['sears']['host'] = 'dbasears.qa.mrc-services.io';
    $config['connections']['sears2']['username'] = $config['connections']['sears']['username'] = 'apifincadoa';
    $config['connections']['sears2']['password'] = $config['connections']['sears']['password'] = 'B7omMAQ=3db76/qD';
} else if ((strpos(dirname(__DIR__) . "/", $PATH_REL) !== false) || (strpos(dirname(__DIR__) . "/", $PATH_PROD) !== false)) {
    $config['connections']['sears2']['host'] = $config['connections']['sears']['host'] = 'dbasears.mrc-services.io';
    $config['connections']['sears2']['username'] = $config['connections']['sears']['username'] = 'apifincadob';
    $config['connections']['sears2']['password'] = $config['connections']['sears']['password'] = 'nNzy]Ku2Ah=u%y1I';
}

return $config;
