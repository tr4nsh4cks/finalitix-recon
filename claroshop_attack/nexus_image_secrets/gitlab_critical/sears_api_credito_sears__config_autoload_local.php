<?php
return array(
    'doctrine' => array(
        'configuration' => array(
            'orm_default' => array(
                //'proxy_dir' => sys_get_temp_dir().'/DoctrineORMModuleV2/Proxy',
                'proxy_dir' => '/tmp',
                'proxy_namespace' => 'DoctrineORMModule\Proxy',
            )
        ),
        'connection' => array(
            'orm_default' => array(
                'driverClass' => 'Doctrine\DBAL\Driver\PDOMySql\Driver',
                'params' => array(
                    'host'     => getenv('USERVAR_DB_HOST'),
                    'port'     => getenv('USERVAR_DB_PORT'),
                    'user'     => getenv('USERVAR_DB_USER'),
                    'password' => getenv('USERVAR_DB_PASSWORD'),
                    'dbname'   => getenv('USERVAR_DB_NAME'),
                    'charset' => 'utf8',
                    'driverOptions' => array(1002=>'SET NAMES utf8')
                )
            )
        ),
    ),

    'logger' => array (
        'stream' => '/var/log/php-fpm/www-error.log',
        // Valores permitidos para el priorityFilter
        // EMERG : system is unusable
        // ALERT : action must be taken immediately
        // CRIT : critical conditions
        // ERR : error conditions
        // WARN : warning conditions
        // NOTICE: normal but significant condition
        // INFO : informational messages
        // DEBUG : Debug: debug messages
        'priorityFilter' => 'DEBUG'
    ),
    'phpSettings' => array(
        'display_startup_errors' => true,
        'display_errors' => true,
    ),

    'llave_encriptacion_tdc'=>getenv('USERVAR_TDC_KEY_ENCRYPTION'),
    'llave_encriptacion'=>getenv('USERVAR_KEY_ENCRYPTION'),
    'stage'=>'dev',
    'redisSession' => array(
        'password' => getenv('USERVAR_REDIS_SESSION_PASSWORD'),
        'cookie' => array(
            'key'       => getenv('USERVAR_REDIS_KEY'), //llave para encriptado de token
            'name'      => getenv('USERVAR_REDIS_NAME_COOKIE'), //Nombre que se implementara la cookie
            'domain'    => getenv('USERVAR_URL_STORE'), //Dominio al que se asociara la cookie
            'path'      => '/', //Limitar el acceso de la cookie
            'secure'    => FALSE, //Limitar el accesoa solo https
            'httponly'  => TRUE, //limitar el acceso solo por protocolo http
            'expirePersist'    => 15552000, //cantidad en segundos para definir el tiempo de vida de la cookie
            'expire'    => 18000 //Cantidad en segundos para definir el tiempo de vida de la cookie sin persistencia
        )
    ),
    'redisClient' => array(
        'host'   => getenv('USERVAR_REDIS_HOST'),
        'port'   => getenv('USERVAR_REDIS_PORT'),
        'password' => getenv('USERVAR_REDIS_PASSWORD'),
        'prefix' => getenv('USERVAR_REDIS_PREFIX'),
        'time'   => 15552000
    )
);