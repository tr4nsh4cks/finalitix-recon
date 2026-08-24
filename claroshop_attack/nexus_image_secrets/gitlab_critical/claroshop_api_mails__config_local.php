<?php
$dbParams = array(
    'database' => getenv('USERVAR_DB_NAME'),
    'username' => getenv('USERVAR_DB_USERNAME'),
    'password' => getenv('USERVAR_DB_PASSWORD'),
    'hostname' => getenv('USERVAR_DB_HOST'),
    'options'  => array('buffer_results' => true)
);

return [
    //********CONFIGURACION GENERAL **********
    'base_path'       => getenv('USERVAR_BASE_PATH'),
    'mail_images_path' =>  getenv('USERVAR_MAIL_IMAGES_PATH'),
    'session' => [
        'config' => [
            'class' => 'Zend\Session\Config\SessionConfig',
        ],
        'storage' => 'Zend\Session\Storage\SessionArrayStorage',
        'validators' => [
            'Zend\Session\Validator\RemoteAddr',
            'Zend\Session\Validator\HttpUserAgent',
        ],
    ],
    'logger' => [
        'stream'         => '/var/log/php-fpm/www-error.log',
        'priorityFilter' => 'DEBUG',
        'gelf'           => [
            'host' => getenv('USERVAR_GRAYLOG_HOST'),
            'port' => getenv('USERVAR_GRAYLOG_PORT')
        ],
        'flags' => [
            'project' => getenv('USERVAR_API_GROUP') . "_MAIL",
            'stage'   => getenv('USERVAR_GRAYLOG_STAGE'),
            'server'  => $_SERVER['HTTP_HOST']
        ]
    ],
    //********CONFIGURACION DE RENDER **********
    'template' => array(
        'cache'         => true,
        'templates'     => realpath(dirname(__FILE__) . "/../app/Templates/"),
        'cachePath'     => realpath(sys_get_temp_dir()),
        'optimizations' => 1,
        'modo'          => true
    ),

    //********CONFIGURACION DE IMAGENES **********
    'proxy-imgs' => getenv('USERVAR_PROXY_IMGS') ? getenv('USERVAR_PROXY_IMGS') : 'https://resources.claroshop.com',

    //********SMTP DE CORREO **********
    'smtp'=> [
        'notificar' => true,
        'host'      => getenv('USERVAR_SMTP_HOST'),
        'port'      => getenv('USERVAR_SMTP_PORT'),
        'auth'      => true,
        'secc'      => false,
        'user'      => getenv('USERVAR_SMTP_USER'),
        'pass'      => getenv('USERVAR_SMTP_PASS'),
        'connection_class' => 'plain',
        'base_path'        => getenv('USERVAR_SMTP_BASE_PATH'),
        'stage'            => getenv('USERVAR_SMTP_STAGE')
    ],

    //********CONFIGURACION DE CACHE **********
    'sessionRedis' => [
        'redis' => [
            'host'   => getenv('USERVAR_REDIS_HOST'),
            'port'   => getenv('USERVAR_REDIS_PORT'),
            'prefix' => getenv('USERVAR_REDIS_PREFIX'),
            'time'   => getenv('USERVAR_REDIS_EXPIRE'),
            'password' => getenv('USERVAR_REDIS_PASSWORD'),
        ],
    ],
    'thank_you_page' => [
        'correo_deposito'           => getenv('USERVAR_CORREO_DEPOSITO'),
        'correo_clientes'           => getenv('USERVAR_CORREO_CLIENTES'),
        'correo_datos_personales'   => getenv('USERVAR_CORREO_DATOS_PERSONALES'),
        'dias_telmex'               => 5
    ],
    'barcodeGen' => getenv('USERVAR_BARCODEGEN'),
    'api_group' => getenv('USERVAR_API_GROUP') ? getenv('USERVAR_API_GROUP') : 'CSAPI',
    'site_name' => getenv('USERVAR_SITE_NAME'),
    'dataTienda' => [
        'nombre_tienda'       => getenv('USERVAR_STORE_NAME'),
        'mail_tienda'         => getenv('USERVAR_STORE_EMAIL'),
        'nombre_legal_tienda' => getenv('USERVAR_STORE_LEGALNAME'),
        'leyenda_tienda'      => getenv('USERVAR_STORE_LEGEND'),
        'mail_legal_tienda'   => getenv('USERVAR_STORE_LEGALEMAIL'),
        'imagen_tienda'       => getenv('USERVAR_STORE_IMAGE'),
    ],
    'mail_otp_code' => [
        'mail' => [
            'subject' => getenv('USERVAR_MAIL_OTP_SUBJECT'),
            'name' =>  getenv('USERVAR_MAIL_OTP_NAME'),
            'from' =>  getenv('USERVAR_MAIL_OTP_FROM')
        ]
    ],

    //******************************* MAIL DE REVIEWS **********************************
    'reviews_mail' => [
        'subject'  => getenv('USERVAR_REVIEWS_MAIL_SUBJECT'),
        'template' => [
            'path' => getenv('USERVAR_REVIEWS_MAIL_TEMPLATE_PATH'),
            'name' => getenv('USERVAR_REVIEWS_MAIL_TEMPLATE_NAME')
        ],
        'sender'    => [
            'name'  => getenv('USERVAR_REVIEWS_MAIL_SENDER_NAME'),
            'email' => getenv('USERVAR_REVIEWS_MAIL_SENDER_EMAIL')
        ]
    ],

    //******************************* MAILS DE MESA DE REGALOS **********************************
    'gift_table_mail' => [
        'info' => [
            'telefono_canal_atencion' => getenv('USERVAR_GIFT_TABLE_MAIL_TELEFONO_CANAL_ATENCION'),
        ],
        'sender'    => [
            'name'  => getenv('USERVAR_GIFT_TABLE_MAIL_SENDER_NAME'),
            'email' => getenv('USERVAR_GIFT_TABLE_MAIL_SENDER_EMAIL')
        ]
    ]
];
