<?php
/**
 * Local configuration.
 *
 * Copy this file to `local.php` and change its settings as required.
 * `local.php` is ignored by git and safe to use for local and sensitive data like usernames and passwords.
 */

declare(strict_types=1);

return [
    'doctrine' => [
        'connection' => [
            'orm_default' => [
                'params' => [
                    'dbname' => 'payment_t1',
                    'user' => getenv('USERVAR_DB_USERNAME'),
                    'password' => getenv('USERVAR_DB_PASSWORD'),
                    'host' => getenv('USERVAR_DB_HOST'),
                    'port' => getenv('USERVAR_DB_PORT'),
                    'driver' => 'pdo_mysql',
                    'charset' => 'utf8',
                    'driverOptions' => array(1002=>'SET NAMES utf8')
                ],
            ],
        ],
        'driver' => [
            'orm_default' => [
                'class' => \Doctrine\Common\Persistence\Mapping\Driver\MappingDriverChain::class,
                'drivers' => [
                    'App\Entity' => 'my_entity',
                ],
            ],
            'my_entity' => [
                'class' => \Doctrine\ORM\Mapping\Driver\AnnotationDriver::class,
                'cache' => 'array',
                'paths' => __DIR__ . '/../../src/App/src/Entity',
            ],
        ],
        'configuration' => [
            'orm_default' => [
                'proxy_dir' => '/tmp/DoctrineORM/Proxy',
            ]
        ]
    ],

    'documentation' => [
        'html' => $_SERVER['DOCUMENT_ROOT'] . '/' . 'documentation.phtml',
        'title' => 'Payment T1 Pagos',
        'description' => 'Microservicio para pago con Tarjetas de Crédito / Débito por medio de T1 Pagos.',
        'base_path' => getenv('USERVAR_URI_PROJECT') . "/v1",
    ],
    'documentation-v2' => [
        'html' => $_SERVER['DOCUMENT_ROOT'] . '/' . 'documentation.phtml',
        'title' => 'Payment T1 Pagos V2',
        'description' => 'Microservicio para pago con Tarjetas de Crédito / Débito por medio de T1 Pagos.',
        'base_path' => getenv('USERVAR_URI_PROJECT'),
    ],
    'logger' => [
        'stream'            => '/var/log/php-fpm/www-error.log',
        'writer'            => getenv('USERVAR_GRAYLOG_WRITER') ? \Laminas\Log\Writer\Syslog::class : null,
        'priorityFilter'    => 'DEBUG',
        'gelf' => [
            'host' => getenv('USERVAR_GRAYLOG_HOST'),
            'port' => getenv('USERVAR_GRAYLOG_PORT'),
        ],
        'flags' => [
            'project' => "T1Pagos",
            'stage'   => getenv('USERVAR_GRAYLOG_STAGE'),
            'server'  => $_SERVER['HTTP_HOST'],
        ]
    ],
    'redis' => [
        "host" => getenv('USERVAR_REDIS_HOST'),
        "port" => getenv('USERVAR_REDIS_PORT'),
        "password" => getenv('USERVAR_REDIS_PASSWORD') ?? '',
        "keys" => [
            "t1pagos" => [
                "key" => getenv('USERVAR_REDIS_KEYS_T1'), //"t1_sears_dev",
                "exp" => getenv('USERVAR_REDIS_KEYS_EXP') ?: 30,
            ],
        ],
    ],
    "payment_departamental" => [
        "name" => getenv("USERVAR_DEPARTAMENTAL_PORTAL_NAME"),
        "description" => getenv("USERVAR_DEPARTAMENTAL_DESCRIPTION"),
        "sku" => getenv("USERVAR_DEPARTAMENTAL_SKU"),
        "type" => "servicio",
        "cypher_key" => getenv("USERVAR_DEPARTAMENTAL_CYPHER_KEY"),
        "prefix" => getenv("USERVAR_DEPARTAMENTAL_PREFIX"),
        "spei" => [
            "monto_minimo" => 1,
            "monto_maximo" => 99999,
        ],
    ],
];
