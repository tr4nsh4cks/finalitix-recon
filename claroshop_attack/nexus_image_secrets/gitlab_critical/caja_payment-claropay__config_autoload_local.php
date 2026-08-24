<?php
/**
 * Local configuration.
 *
 * Copy this file to `local.php` and change its settings as required.
 * `local.php` is ignored by git and safe to use for local and sensitive data like usernames and passwords.
 */

declare(strict_types=1);

$dbParams = array(
    'database' => 'payment_claropay',
    'username' => getenv("USERVAR_DB_USERNAME"),
    'password' => getenv("USERVAR_DB_PASSWORD"),
    'hostname' => getenv("USERVAR_DB_HOST"),
    'options' => array('buffer_results' => true)
);

return [
    'base_path' => getenv("USERVAR_BASE_PATH"),
    'doctrine' => [
        'connection' => [
            'orm_default' => [
                'params' => [
                    'dbname' => $dbParams['database'],
                    'user' => $dbParams['username'],
                    'password' => $dbParams['password'],
                    'host' => $dbParams['hostname'],
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
    ],

    'documentation' => [
        'html' => $_SERVER['DOCUMENT_ROOT'] . '/' . 'documentation.phtml',
        'title' => 'Payment ClaroPay',
        'description' => 'Implementación de Payment ClaroPay'
    ],

    'internal-api' => (
        //$internalApi = 'https://seapi.release.sears.com.mx'
        //$internalApi = 'https://snapi.dev.sanborns.com.mx'
    $internalApi = 'https://csapi.dev.claroshop.com'
    ),
    'claropay_external_service' => [
        'localWsdl' => [
            'status' => true,
            'name' => '/claropayuat.wsdl'
        ],
        'endpoint' => getenv("USERVAR_CLAROPAY_ENDPOINT"),
        //'endpoint' => 'https://microcks-adm.dev-ng.claroshop.com/api/resources/PaymentServiceSoap11MockService-1.0.wsdl',
        'options' => [
            "soap_version"=> SOAP_1_1,
            'location' => getenv("USERVAR_CLAROPAY_ENDPOINT"),
        ],
        'auth' => [
            'username' => getenv("USERVAR_CLAROPAY_USERNAME"),
            'password' => getenv("USERVAR_CLAROPAY_PASSWORD"),
            'ns' => 'http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-secext-1.0.xsd'
        ],
        'classmap' => [
            'paymentRequest' => '\App\ExternalService\ClaroPay\PaymentRequest',
            'cancelRequest' => '\App\ExternalService\ClaroPay\CancelRequest',
            'fullRefundRequest' => '\App\ExternalService\ClaroPay\FullRefundRequest',
            'partialRefundRequest' => '\App\ExternalService\ClaroPay\PartialRefundRequest',
            'paymentReversalRequest' => '\App\ExternalService\ClaroPay\PaymentReversalRequest',
            'cancelReversalRequest' => '\App\ExternalService\ClaroPay\CancelReversalRequest',
            'WSResponse' => '\App\ExternalService\ClaroPay\WSResponse',
        ]
    ],
    'logger' => [
        'stream'            => '/var/log/php-fpm/www-error.log',
        'priorityFilter'    => 'DEBUG',
        'gelf' => [
            'host' => getenv("USERVAR_GRAYLOG_HOST"),
            'port' => getenv("USERVAR_GRAYLOG_PORT")
        ],
        'flags' => [
            'project' => "CSAPI_CLAROPAY",
            'stage'   => getenv("USERVAR_GRAYLOG_STAGE"),
            'server'  => $_SERVER['HTTP_HOST']
        ]
    ],
    'redis' => [
        "host" => getenv("USERVAR_REDIS_HOST"),
        "port" => getenv("USERVAR_REDIS_PORT"),
        "key" => 'claropay_dev',
        "password" => getenv("USERVAR_REDIS_PASSWORD"),
        "exp" => 3600, // Expiration time
    ],
];
