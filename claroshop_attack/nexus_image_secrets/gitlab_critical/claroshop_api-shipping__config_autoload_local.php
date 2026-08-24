<?php
/**
 * Local configuration.
 *
 * Copy this file to `local.php` and change its settings as required.
 * `local.php` is ignored by git and safe to use for local and sensitive data like usernames and passwords.
 */

declare(strict_types=1);
use Doctrine\ODM\MongoDB\Configuration;
use Doctrine\ODM\MongoDB\Repository\DocumentRepository as DefaultDocumentRepository;
use DoctrineMongoODMModule\Service\DoctrineObjectHydratorFactory;

/**
 * El valor de work_weekend en el config map es 1 en caso de ser verdadero o 0 en caso de ser falso
 */

const TE_LLEGA_ENTRE_EL = 'Te llega entre el ';
const HOY_Y_MANANA = 'hoy y mañana';
const TE_LLEGA_MANANA = 'Te llega mañana';
const TE_LLEGA_HOY      = 'Te llega hoy';
const TE_LLEGA_EL = 'Te llega el ';
const GRATIS = 'GRATIS';

$dbParams = array(
    'database' => getenv('USERVAR_DB_NAME'),
    'username' => getenv('USERVAR_DB_USERNAME'),
    'password' => getenv('USERVAR_DB_PASSWORD'),
    'hostname' => getenv('USERVAR_DB_HOST'),
    'port' => getenv('USERVAR_DB_PORT') ? getenv('USERVAR_DB_PORT') : '3306',
    'options'  => array('buffer_results' => true)
);

$mongodb = [
    "server" => getenv('USERVAR_MONGO_HOST'),
    "port" => getenv('USERVAR_MONGO_PORT'),
    "user" => getenv('USERVAR_MONGO_USERNAME'),
    "password" => urlencode(getenv('USERVAR_MONGO_PASSWORD')),
    "dbname" => getenv('USERVAR_MONGO_DATABASE') ?: null,
    "uri" => getenv('USERVAR_MONGO_URI'),
    "replicaset" => getenv('USERVAR_MONGO_REPLICASET'), //rs0
];

return [
    'fullfilment_red_code_active' => false,
    'minimum_shipping_cost_free' => 499,
    'doctrine' => [
        'connection' => [
            'odm_default'   => [
                'server'    => $mongodb["server"],
                'port'      => $mongodb["port"],
                'user'      => $mongodb["user"],
                'password'  => $mongodb["password"],
                'connectionString' => $mongodb['uri'] ? $mongodb["uri"] : "mongodb://{$mongodb["user"]}:{$mongodb["password"]}@{$mongodb["server"]}/{$mongodb["dbname"]}?replicaSet={$mongodb["replicaset"]}&readPreference=primary",
                'dbname'    => $mongodb["dbname"],
                'options'   => []
            ],

            'orm_default' => [
                'params' => [
                    'dbname'   => $dbParams['database'],
                    'user'     => $dbParams['username'],
                    'password' => $dbParams['password'],
                    'host'     => $dbParams['hostname'],
                    'port'     => $dbParams['port'],
                    'driver'   => 'pdo_mysql',
                    'charset'  => 'utf8',
                ],
            ],
        ],

        'configuration' => [
            'odm_default' => [
                'metadata_cache'    => 'array',
                'driver'            => 'odm_default',
                'generate_proxies'  => Configuration::AUTOGENERATE_FILE_NOT_EXISTS,
                'proxy_dir'         => '/var/cache/php-fpm/DoctrineMongoODMModule/Proxy',
                'proxy_namespace'   => 'DoctrineMongoODMModule\Proxy',
                'generate_hydrators'=> Configuration::AUTOGENERATE_ALWAYS,
                'hydrator_dir'      => '/var/cache/php-fpm/DoctrineMongoODMModule/Hydrator',
                'hydrator_namespace'=> 'DoctrineMongoODMModule\Hydrator',
                'generate_persistent_collections'   => Configuration::AUTOGENERATE_ALWAYS,
                'persistent_collection_dir'         => '/var/cache/php-fpm/DoctrineMongoODMModule/PersistentCollection',
                'persistent_collection_namespace'   => 'DoctrineMongoODMModule\PersistentCollection',
                'persistent_collection_factory'     => null,
                'persistent_collection_generator'   => null,
                'default_db' => $mongodb["dbname"],
                'filters' => [],
                'types' => [],
                'default_document_repository_class_name' => DefaultDocumentRepository::class,
            ]
        ],

        'driver' => [
            'odm_default' => [
                'class' => Doctrine\ODM\MongoDB\Mapping\Driver\AnnotationDriver::class,
                'drivers' => [
                    'App\Document' => 'documentmanager'
                ]
            ],
            'orm_default' => [
                'class' => \Doctrine\Common\Persistence\Mapping\Driver\MappingDriverChain::class,
                'drivers' => [
                    'App\Entity' => 'my_entity',
                ],
            ],
            'my_entity' => [
                'class' => \Doctrine\ORM\Mapping\Driver\AnnotationDriver::class,
                'cache' => 'array',
                'paths' => [ __DIR__ . '/../../src/App/src/Entity'],
            ]
        ],

        'documentmanager' => [
            'odm_default' => [
                'connection' => 'odm_default',
                'configuration' => 'odm_default',
                'eventmanager' => 'odm_default',
            ]
        ],

        'eventmanager' => [
            'odm_default' => [
                'subscribers' => []
            ]
        ],

        'hydrators' => [
            'factories' => [
                'Doctrine\Laminas\Hydrator\DoctrineObject' => DoctrineObjectHydratorFactory::class,
            ],
        ],
    ],

    'documentation' => [
        'html' => $_SERVER['DOCUMENT_ROOT'] . '/' . 'documentation.phtml'
    ],

    'internal-api' => (
        $internalApi = getenv('USERVAR_INTERNALAPI')
    ),
    'products_micro_service' => [
        'url' => $internalApi . '/producto',
        'httpOptions' => [
            'adapter'   => 'Zend\Http\Client\Adapter\Curl',
            'curloptions' => array(
                CURLOPT_RETURNTRANSFER => 1,
                CURLOPT_SSL_VERIFYPEER => false,
                CURLOPT_SSL_VERIFYHOST => false,
                CURLOPT_CONNECTTIMEOUT => 4,
                CURLOPT_TIMEOUT => 10
            )
        ],
        'request' => [
            'get' => $internalApi . '/producto',
        ]
    ],

    'sellers_micro_service' => [
        'url' => $internalApi . '/sellers/v1',
        'httpOptions' => [
            'adapter'   => 'Zend\Http\Client\Adapter\Curl',
            'curloptions' => array(
                CURLOPT_RETURNTRANSFER => 1,
                CURLOPT_SSL_VERIFYPEER => false,
                CURLOPT_SSL_VERIFYHOST => false,
                CURLOPT_CONNECTTIMEOUT => 15,
                CURLOPT_TIMEOUT => 15
            )
        ],
        'request' => [
            'getSubsidiaries' => '/sellers/',
        ]
    ],

    'logger' => [
        'stream'         => '/var/log/php-fpm/www-error.log',
        'priorityFilter' => 'DEBUG',
        'gelf'           => [
            'host' => getenv('USERVAR_GRAYLOG_HOST'),
            'port' => getenv('USERVAR_GRAYLOG_PORT')
        ],
        'flags' => [
            'project' => "CSAPI_SHIPPING",
            'stage'   => getenv('USERVAR_GRAYLOG_STAGE'),
            'server'  => $_SERVER['HTTP_HOST']
        ]
    ],
    'redis' => [
        "host"     => getenv('USERVAR_REDIS_HOST'),             //IP FOR THE REDIS CONTAINER,
        "port"     => getenv('USERVAR_REDIS_PORT'),             // PORT FOR THE REDIS CONTAINER,
        "key"      => getenv('USERVAR_REDIS_KEY'),
        "password" => getenv('USERVAR_REDIS_PASSWORD') ?? '',
        "exp"      => 3600,                                     // Expiration time
    ],
    'shipping_micro_service' => [
        'url' => $internalApi . '/shipping/v1',
        'httpOptions' => [
            'adapter'     => 'Zend\Http\Client\Adapter\Curl',
            'curloptions' => array(
                CURLOPT_POST           => 1,
                CURLOPT_RETURNTRANSFER => 1,
                CURLOPT_SSL_VERIFYPEER => false,
                CURLOPT_SSL_VERIFYHOST => false,

            ),
            'persistent' => false,

            'sslverifypeer'      => false,
            'sslallowselfsigned' => true,
            'sslusecontext'      => true,

            'ssl' => array(
                'verify_peer'       => false,
                'allow_self_signed' => true,
                'capture_peer_cert' => true,
            ),
        ],
        'request' => [
            'post' => $internalApi . '/shipping/v1/delivery',
        ]
    ],
    'base_path' => $internalApi . '/shipping/v1',
    'delivery_days' => [
        'fulfillment' => [
            'flag_delivery_tomorrow' => (bool)getenv('USERVAR_FLAG_DELIVERY_TOMORROW'),
            'flag_delivery_today' => (bool)getenv('USERVAR_FLAG_DELIVERY_TODAY'),
        ],
    ],
    'sears_tiempo_entrega' => [
        'stage'               => getenv('USERVAR_STE_STAGE'),
        'endpoint'            => getenv('USERVAR_STE_ENDPOINT'),
        'location'            => getenv('USERVAR_STE_LOCATION'),
        'usuario'             => getenv('USERVAR_STE_USERNAME'),
        'password'            => getenv('USERVAR_STE_PASSWORD'),
        'codEmp'              => '1',
        'tienda'              => '104',
        'bandera_big_ticket'  => 'S',
        'dias_entrega'        => getenv('USERVAR_STE_DIAS_ENTREGA') ?? 10,
        'httpuser'            => getenv('USERVAR_STE_HTTP_USER') ?? '', # Usuario http
        'httppassword'        => getenv('USERVAR_STE_HTTP_PASS') ?? '', # contraseña http
        'activate_month_name' => true,
        'activate_days_name'  => true,
    ],
    'redis_keys' => [
        'shipping_key' => [
            'name'  => getenv('USERVAR_REDIS_SHIPPING_KEY'),
            'exp'   => 3600,
            'count' => 100
        ],
        'cp_key' => [
            'name' => getenv('USERVAR_REDIS_CP_KEY'),
            'exp'  => 86400,
        ],
        'holidays_key' => [
            'name' => getenv('USERVAR_REDIS_HOLIDAYS_KEY'),
            'exp'  => 86400
        ],
        'super_express' => [
            'name' => getenv('USERVAR_SUPER_EXPRESS_KEY'),
            'exp' => 100
        ]
    ],

    'delivery_free' => [
        'copy' => GRATIS,
        'amount' => getenv('USERVAR_DELIVERY_FREE_AMOUNT')
    ],
    'sellers_pcr' => explode(",", getenv("USERVAR_SELLERS_PCR")),
    'flag_super_express' => (bool)getenv('USERVAR_FLAG_SUPER_EXPRESS'),
];
