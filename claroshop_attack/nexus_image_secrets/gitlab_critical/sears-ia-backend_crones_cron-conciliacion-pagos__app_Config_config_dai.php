<?php
/**
 * Created by PhpStorm.
 * User: Federico @fmichell
 * Date/Time: 6/7/2019/9:50 PM
 * Description: Archivo de configuracion para almacenar parametros de conexion a bases de datos.
 * DAI = Data Access Interface
 */

/*
 * ===============================================================
 * Accesos a la base de datos
 * ===============================================================
 */

// MYSQL
if (in_array(AMBIENTE, array('loc', 'dev', 'console', 'prod'))) {
    define('BD_HOST', $configParams['DB']['mysql']['DB_HOST']);
    define('BD_PORT', $configParams['DB']['mysql']['DB_PORT']);
    define('BD_USER', $configParams['DB']['mysql']['DB_USERNAME']);
    define('BD_PW', $configParams['DB']['mysql']['DB_PASSWORD']);
    define('BD_NAME', $configParams['DB']['mysql']['DB_DATABASE']);
} else {
    throw new ErrorException('Ambiente de desarrollo indeterminado');
    exit;
}