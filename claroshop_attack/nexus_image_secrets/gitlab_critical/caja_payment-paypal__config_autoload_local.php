<?php
/**
 * Local configuration.
 *
 * Copy this file to `local.php` and change its settings as required.
 * `local.php` is ignored by git and safe to use for local and sensitive data like usernames and passwords.
 */

use Laminas\Validator\StringLength;

  $dbParams = array(
    'database' => 'payment_paypal',
    'username' => getenv("USERVAR_DB_USERNAME"),
    'password' => getenv("USERVAR_DB_PASSWORD"),
    'hostname' => getenv("USERVAR_DB_HOST"),
    'port' => getenv("USERVAR_DB_PORT"),
    'options' => array('buffer_results' => true)
);

return [
    'base_path' => 'http://payment-paypal.local.com/paypal/v1',
    'doctrine' => [
        'connection' => [
            'orm_default' => [
                'params' => [
                    'dbname' => $dbParams['database'],
                    'user' => $dbParams['username'],
                    'password' => $dbParams['password'],
                    'host' => $dbParams['hostname'],
                    'port' => $dbParams["port"],
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
        'title' => 'Payment Paypal',
        'description' => 'Implementación de Payment Paypal With Installments'
    ],
    'logger' => [
        'stream'            => '/var/log/php-fpm/www-error.log',
        'priorityFilter'    => 'DEBUG',
        'gelf' => [
            'host' => getenv("USERVAR_GRAYLOG_HOST"),
            'port' => getenv("USERVAR_GRAYLOG_PORT")
        ],
        'flags' => [
            'project' => "CSAPI_PAYPAL",
            'stage'   => getenv("USERVAR_GRAYLOG_STAGE"),
            'server'  => $_SERVER['HTTP_HOST']
        ]
    ],
    'redis' => [
        "host" => getenv("USERVAR_REDIS_HOST"),
        "port" => getenv("USERVAR_REDIS_PORT"),
        "key" => 'paypal',
        "password" => getenv("USERVAR_REDIS_PASSWORD"),
        "exp" => 3600, // Expiration time
    ],
    'redis_keys' => [
        'token_key' =>[
            'name' => getenv("USERVAR_REDIS_TOKEN_KEY"),
            'exp' => getenv("USERVAR_REDIS_TOKEN_KEY_EXP"),
        ],
        'billing_agreement' => [
            'name' => getenv("USERVAR_REDIS_BA_KEY"),
            'exp' => getenv("USERVAR_REDIS_BA_KEY_EXP")
        ],
    ],
    'paypal_installments' => [
        'url' => $internalApi = getenv("USERVAR_PAYPAL_ENDPOINT"),
        'httpOptions' => [
            'adapter' => 'Zend\Http\Client\Adapter\Curl',
            'curloptions' => array(
                CURLOPT_POST => 1,
                CURLOPT_RETURNTRANSFER => 1,
                CURLOPT_SSL_VERIFYPEER => FALSE,
                CURLOPT_SSL_VERIFYHOST => FALSE,
                CURLOPT_CONNECTTIMEOUT => 5,
                CURLOPT_TIMEOUT => 29,
            ),
        ],
        'headers' => [
            "Accept" => "application/json",
            "Authorization" => "Bearer %s",
            'Content-Type' => 'application/json',
        ],
        'authorization' => [
            'username' => getenv("USERVAR_PAYPAL_USERNAME"),
            'password' => getenv("USERVAR_PAYPAL_PASSWORD")
        ],
        "merchant" => [
            'name' => getenv("USERVAR_PAYPAL_MERCHANT_NAME"), //'Claroshop',
            'billing_agreement_description' => getenv("USERVAR_PAYPAL_BA_DESC"), //'Acuerdo de pagos para compras rápidas con Claroshop',
            'payment_description' => getenv("USERVAR_PAYPAL_PAYMENT_DESC"), //"Pedido en Claroshop"
            'id' => getenv("USERVAR_PAYPAL_MERCHANT_ID"), // Id de Comercio Paypal - Merchant Id
        ],
        "merchant_preferences" => [
            "cancel_url" => "%s",
            "return_url" => "%s",
            "accepted_pymt_type" => "Instant",
            "experience_id" => "",
            "skip_shipping_address" => true,
            "immutable_shipping_address" => false
        ],
        "url_device" => [
            "cancel_url" => [
                "web" => getenv("USERVAR_PAYPAL_CANCEL_WEB_URL"),
                "ios" => getenv("USERVAR_PAYPAL_CANCEL_IOS_URL"),
                "android" => getenv("USERVAR_PAYPAL_CANCEL_ANDROID_URL")
            ],
            "return_url" => [
                "web" => getenv("USERVAR_PAYPAL_RETURN_WEB_URL"),
                "ios" => getenv("USERVAR_PAYPAL_RETURN_IOS_URL"),
                "android" => getenv("USERVAR_PAYPAL_RETURN_ANDROID_URL")
            ],
        ],
        'request' => [
            'post' =>[
                'oauth2' => [
                    'token' => '/v1/oauth2/token',
                    'body' => [
                        'grant_type' => 'client_credentials',
                        'content_type' => 'application/x-www-form-urlencoded'
                    ],
                    'headers' => [
                        "Accept" => "application/json",
                        'Content-Type' => 'application/x-www-form-urlencoded',
                    ],
                ],
                'billing_agreements' => [
                    'tokens' => '/v1/billing-agreements/agreement-tokens',
                    'agreements' => '/v1/billing-agreements/%s/agreements',
                ],
                'credit' =>  [
                    'financing_opts' => '/v1/credit/calculated-financing-options'
                ],
                'payments' => [
                    'payment' =>  '/v1/payments/payment'
                ]
            ],
            'put' => [
                'risk' => [
                    'stc' => '/v1/risk/transaction-contexts/%s/%s'
                ]
            ]
        ],
    ],
    'active_monthly_payment' => (bool) getenv("USERVAR_PAYPAL_ACTIVE_MONTLY_PAYMENT"),
];
