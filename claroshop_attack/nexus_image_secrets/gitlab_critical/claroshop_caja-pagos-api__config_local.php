<?php
return array(
    'template' => array(
        'cache'         => false,
        'templates'     => realpath(dirname(__FILE__) . "/../app/Templates/"),
        'cachePath'     => realpath(sys_get_temp_dir()),
        'optimizations' => 1,
        'modo'          => true
    ),

    'gigya'=> array(
        'key'=>getenv('USERVAR_GIGYA_KEY'), // release.claroshop.com
        'secret'=>getenv('USERVAR_GIGYA_SECRET')
    ),

    'cache' => array(
        'consistente' => (bool)getenv('USERVAR_CACHE_CONSISTENTE'),
    ),

    'imgs_cache' => array(
        'consistente' => (bool)getenv('USERVAR_IMGS_CACHE_CONSISTENTE'),
        'servidores' => array(
            array(getenv('USERVAR_IMGS_CACHE_SERVIDORES_IP'), getenv('USERVAR_IMGS_CACHE_SERVIDORES_NUMBER')),
            array(getenv('USERVAR_IMGS_CACHE_SERVIDORES_IP'), getenv('USERVAR_IMGS_CACHE_SERVIDORES_NUMBER')),
        )
    ),

    'inbursa'=> array(
        "username" => getenv('USERVAR_INBURSA_USERNAME'),
        "password" => getenv('USERVAR_INBURSA_PASSWORD'),
        "httpGateway" => getenv('USERVAR_INBURSA_GATEWAY')
    ),

    'imgs_decompras' => getenv('USERVAR_IMGS_DECOMPRAS'),
    'endpoint_recibo_telmex' => getenv('USERVAR_RECIBO_TELMEX'),
    'endpoint_telmex' => getenv('USERVAR_TELMEX'),
    'forma_pago_recibo_telmex' => getenv('USERVAR_FORMAS_PAGO_RECIBO_TELMEX'),
    'categorias_sin_recibo_telmex' => getenv('USERVAR_CATEGORIAS_SIN_RECIBO_TELMEX'),
    'precioRDD' => getenv('USERVAR_PRECIO_RDD'),

    'cyber'=> array(
        "TRANSACTION_KEY"   => getenv('USERVAR_CYBER_TRANSACTION_KEY'),
        "MERCHANT_ID"       => getenv('USERVAR_CYBER_MERCHANT_ID'),
        "WSDL_URL"          => getenv('USERVAR_CYBER_WSDL_URL'),
        "TRANSACCION_UPDATE"=> getenv('USERVAR_CYBER_TRANSACCION_UPDATE')
    ),

    "pagos"=>array(
        'netpay'=>array(
            "httpGateway"       => getenv('USERVAR_NETPAY_GATEWAY'),
            "storeID"           => getenv('USERVAR_NETPAY_STORE_ID'),
            "username"          => getenv('USERVAR_NETPAY_USERNAME'),
            "password"          => getenv('USERVAR_NETPAY_PASSWORD'),
            "mode"              => getenv('USERVAR_NETPAY_MODE')
        ),
    ),

    'login_sears' => array(
        'api_endpoit'   => getenv('USERVAR_LOGIN_SEARS_API_ENDPOINT'),
        'auth_user'     => getenv('USERVAR_LOGIN_SEARS_AUTH_USER'),
        'auth_pasword'  => getenv('USERVAR_LOGIN_SEARS_AUTH_PASSWORD'),
        'semilla'       => getenv('USERVAR_LOGIN_SEARS_AUTH_SEMILLA'),
        'mode'          => getenv('USERVAR_LOGIN_SEARS_AUTH_MODE')
    ),

    'paypal_express'=> array(
        'url'               => getenv('USERVAR_PAYPAL_EXPRESS_URL'),
        'api_user'          => getenv('USERVAR_PAYPAL_EXPRESS_API_USER'),
        'api_password'      => getenv('USERVAR_PAYPAL_EXPRESS_API_PASSWORD'),
        'api_signature'     => getenv('USERVAR_PAYPAL_EXPRESS_API_SIGNATURE'),
        'api_endpoint'      => getenv('USERVAR_PAYPAL_EXPRESS_API_ENDPOINT'),
        'api_version'       => getenv('USERVAR_PAYPAL_EXPRESS_API_VERSION'),
        'api_return_url'    => getenv('USERVAR_PAYPAL_EXPRESS_API_RETURN_URL'),
        'api_cancel_url'    => getenv('USERVAR_PAYPAL_EXPRESS_API_CANCEL_URL'),
        'api_brand_logo'    => getenv('USERVAR_PAYPAL_EXPRESS_API_BRAND_LOGO'),
    ),

    'paypal_service'=>array(
        'url'      => getenv('USERVAR_PAYPAL_SERVICE_URL'),
        'clientId' => getenv('USERVAR_PAYPAL_SERVICE_CLIENT_ID'),
        'password' => getenv('USERVAR_PAYPAL_SERVICE_PASSWORD'),
        'payPalEnv'=> getenv('USERVAR_PAYPAL_SERVICE_ENV'),
        'payPalShopName' => getenv('USERVAR_PAYPAL_SERVICE_SHOP_NAME'),
        'payPalMerchantPrivacyPolicyURL' => getenv('USERVAR_PAYPAL_SERVICE_PRIVACY_POLICY'),
        'payPalMerchantUserAgreementURL' => getenv('USERVAR_PAYPAL_SERVICE_USER_AGREEMENT')
    ),

    'captcha'=>array(
        'KEY'=> getenv('USERVAR_CAPTCHA_KEY'),
        'KEY_SECRET'=> getenv('USERVAR_CAPTCHA_KEY_SECRET'),
        'URL_CAPTCHA'=> getenv('USERVAR_CAPTCHA_URL')
    ),

    'boxpay'=> array(
        "TRANSACTION_KEY"   => getenv('USERVAR_BOXPAY_KEY'),  //id_pos
        "VAK"               => getenv('USERVAR_BOXPAY_VAK'),
        "MERCHANT_ID"       => getenv('USERVAR_BOXPAY_MERCHANT_ID'),
        "CURL_URL"          => getenv('USERVAR_BOXPAY_MERCHANT_URL')
    ),

    'bd' => array(
        'servidores' => array(
            array(
                'host' => getenv('USERVAR_DB_HOST'),
                'peso' => 1
            )
        ),
        'usuario' => getenv('USERVAR_DB_USERNAME'),
        'contrasena' => getenv('USERVAR_DB_PASSWORD'),
        'basedatos' => 'tienda',
        'charset' => 'UTF-8',
        'auto_cache' => 7200,
        'depurar'=> false,
        'port' => getenv('USERVAR_DB_PORT')
    ),

    'olark'=> array(
        'identify'=> getenv('USERVAR_OLARK_IDENTIFY'),
        'system_group' => getenv('USERVAR_OLARK_SYSTEM_GROUP')
    ),

    'doctrine' => array(
        'connection' => array(
            // default connection name
            'orm_default' => array(
                'driverClass' => 'Doctrine\DBAL\Driver\PDOMySql\Driver',
                'params' => array(
                    'host'     => getenv('USERVAR_DB_HOST'),
                    'port'     => getenv('USERVAR_DB_PORT'),
                    'user'     => getenv('USERVAR_DB_USERNAME'),
                    'password' => getenv('USERVAR_DB_PASSWORD'),
                    'dbname'   => 'tienda',
                    'charset' => 'utf8',
                    'driverOptions' => array(1002=>'SET NAMES utf8'),
                )
            )
        ),
        'configuration' => array(
            'orm_default' => array(
                'proxy_dir' => '/tmp/Proxy',
                'proxy_namespace' => 'DoctrineORMModule\Proxy',
                'result_cache'      => 'mycache',
            )
        )
    ),

    'amdocs' => array(
        'endpoint'      => 'http://200.57.158.26:1701/search/?sei=MexDeComprasSystem',
        'endpointA'     => 'http://200.57.158.26:1701/search/?sei=AutoSuggestionSystem',
    ),

    'imgs_servicio'=> getenv('USERVAR_IMGS_SERVICE'),
    'app_environment'=> 'desa',
    'base_path' => getenv('USERVAR_BASEPATH_CLAROSHOP'),
    'llave_encriptacion_tdc'=> getenv('USERVAR_KEY_ENCRYPT_TDC'),

    'tcSears'=> array(
        'seed'  => getenv('USERVAR_TC_SEARS_SEED'),
        'url'   => getenv('USERVAR_TC_SEARS_URL'),
        'credentials' => array(
            'user'=> getenv('USERVAR_TC_SEARS_USER'),
            'pass'=> getenv('USERVAR_TC_SEARS_PASS')
        ),
        'mode'=>'D'
    ),

    'tiendas'=> array(
        'bannerHome' => array(
            '3509'=>'242',//Telmex
            '2626'=>'245',//Telcel
            '2430'=>'246',//Sears
            '3496'=>'244',//Sanborns
            '3571'=>'320',//Samsung
            '3562' => '365',//BOXBANNER_MABE -PROD
            '3574' => '366',//BOXBANNER_PHILOSOPHY
            '3575' => '367',//BOXBANNER_HASBRO
            '3576' => '368',//BOXBANNER_FLEXI
            '3577' => '369',//BOXBANNER_ENTIENDAS
            '3578' => '388',//BOXBANNER_CRAFTMAN
        ),

        'dbBannerHome' => array(
            '3509'=>'247',//Telmex
            '2626'=>'248',//Telcel
            '2430'=>'249',//Sears
            '3496'=>'250',//Sanborns
            '3562' => '370', //REC_PRODUCTOS_MABE
            '3574' => '371', //REC_PRODUCTOS_PHILOSOPHY
            '3575' => '372', //REC_PRODUCTOS_HASBRO'
            '3576' => '373', //REC_PRODUCTOS_FLEXI'
            '3577' => '374', //REC_PRODUCTOS_ENTIENDAS'
            '3578' => '389', //REC_PRODUCTOS_CRAFTMAN'
        ),

        'recomendadosHome' => array(
            '3509'=>'247',//Telmex
            '2626'=>'248',//Telcel
            '2430'=>'249',//Sears
            '3496'=>'250',//Sanborns
            '3562' => 'RECOMENDADOS_MABE',//mabe
            '3574' => 'RECOMENDADOS_PHILOSOPHY',//philosophy
            '3575' => 'RECOMENDADOS_HASBRO',//hasbro
            '3576' => 'RECOMENDADOS_FLEXI',//flexi
            '3577' => 'RECOMENDADOS_ENTIENDAS',//entiendas
            '3578' => 'RECOMENDADOS_CRAFTMAN',//entiendas
        ),

        'recomendadosProductos' => array(
            '3509'=>'322',//Telmex
            '2626'=>'324',//Telcel
            '2430'=>'325',//Sears
            '3496'=>'323',//Sanborns
        ),

        'buscadosProductos' => array(
            '3509'=>'326',//Telmex
            '2626'=>'328',//Telcel
            '2430'=>'329',//Sears
            '3496'=>'327',//Sanborns
        ),

        'logosTienda'=>array(
            '3509' => 'telmex', //Telmex
            '2626' => 'telcel', //Telcel
            '2430' => 'sears',//Sears
            '3496' => 'sanborns',//Sanborns
            '3571' => 'samsung',//Samsung
            '3572' => 'piagui',//piagui
            '16197'=>'ninewest',
            '16199'=>'guess',
            '16200'=>'cat',
            '16201'=>'anneklein',
            '3562'=> 'mabe', //mabe
            '3574'=> 'philosophy', //philosophy
            '3575'=> 'hasbro', //hasbro
            '3576'=> 'flexi', //flexi
            '3577'=> 'entiendas', //entiendas
            '3578'=> 'craftman', //craftman
        ),

        'colorTienda' => array(
            '3509' => 'menuTiendaTelmex', //Telmex
            '2626' => 'menuTiendaTelcel', //Telcel
            '2430' => 'menuTiendaSears',//Sears
            '3496' => 'menuTiendaSanborns',//Sanborns
            '3571' => 'menuTiendaSamsung',//Fancy
            '3562' => '#686664',//mabe
            '3574' => '#000000',//philosophy
            '3575' => '#DCE3E9',//hasbro
            '3576' => '#C4262E',//flexi
            '3577' => '#67BF03',//entiendas
            '3578' => '#000000',//entiendas
        ),

        'piagui' => array(
            array('id'=>'16197','dep'=>'ninewest'),
            array('id'=>'16199','dep'=>'guess'),
            array('id'=>'16200','dep'=>'cat'),
            array('id'=>'16201','dep'=>'anneklein')
        ),

        'artes_laterales' =>array(
            '3562' => '383',//mabe          LATERALES_MABE
            '3574' => '384',//philosophy 	LATERALES_HASBRO
            '3575' => '385',//hasbro        LATERALES_ENTIENDAS
            '3576' => '386',//flexi         LATERALES_PHILOSOPHY
            '3577' => '387',//entiendas     LATERALES_FLEXI
            '3578' => '390',//craftman      LATERALES_CRAFTMAN
        ),
    ),

    'categorias' => array(
        'bannerHome' =>array(
            '13527'=>'233',//celulares
            '13531'=>'234',//computacion
            '13538'=>'235',//deportes
            '13537'=>'236',//electro
            '13543'=>'237',//entretenimiento
            '13539'=>'238',//electronica
            '13540'=>'239',//moda
            '13541'=>'240',//ninios
            '13542'=>'241',//salud
        ),

        'recomendadosProductos' =>array(
            '13527'=>'303',//celulares
            '13531'=>'304',//computacion
            '13538'=>'305',//deportes
            '13537'=>'306',//electro
            '13543'=>'307',//entretenimiento
            '13539'=>'308',//electronica
            '13540'=>'309',//moda
            '13541'=>'310',//ninios
            '13542'=>'311',//salud
        ),

        'buscadosProductos' =>array(
            '13527'=>'312',//celulares
            '13531'=>'313',//computacion
            '13538'=>'314',//deportes
            '13537'=>'315',//electro
            '13543'=>'316',//entretenimiento
            '13539'=>'317',//electronica
            '13540'=>'318',//moda
            '13541'=>'319',//ninios
            '13542'=>'320',//salud
        )
    ),

    'landing' => array(
        'rebajas'=> array(
            'leaderboard'   => '253',
            'productos'     => '336',
        ),

        'outlet'=> array(
            'leaderboard'   => '254',
            'productos'     => '337',
        ),

        'backtoschool'=> array(
            'leaderboard'   => '255',
            'productos'     => '338',
        ),

        'ofertadeldia'=> array(
            'leaderboard'   => '252',
            'productos'     => '335',
        ),
    ),

    'smtp' => array(
        'notificar' => true,
        'host'      => getenv('USERVAR_SMTP_HOST'),
        'port'      => getenv('USERVAR_SMTP_PORT'),
        'auth'      => (bool)getenv('USERVAR_SMTP_AUTH'),
        'secc'      => false,
        'user'      => getenv('USERVAR_SMTP_USER'),
        'pass'      => getenv('USERVAR_SMTP_PASS'),
        'connection_class'      => "plain",
        'base_path' => getenv('USERVAR_BASEPATH_CLAROSHOP'),
        'stage' => getenv('USERVAR_SMTP_STAGE')
    ),

    'facebook' => array(
        'appId'     => getenv('USERVAR_FACEBOOK_APP_ID'),//@fixme ver donde se usan y ver si podemos quitarlos
        'appSecret' => getenv('USERVAR_FACEBOOK_APP_SECRET'),////@fixme ver donde se usan y ver si podemos quitarlos
        'purchase' => array(
            'appId' => getenv('USERVAR_FACEBOOK_PURCHASE_APP_ID'),//Ver cual es el de desarrollo
            'currency' => 'MXN'
        ),
        'ambiente' => getenv('USERVAR_FACEBOOK_STAGE'),//Estas banderas estan por no tener el control en desarrollo
        'origen' => getenv('USERVAR_FACEBOOK_ORIGIN')
    ),

    'fancy' => array(
        'urlPrecioDolar'=> getenv('USERVAR_FANCY_URL_DOLLAR_PRICE'),
        'urlCalculate'  => getenv('USERVAR_FANCY_URL_CALCULATE'),
        'urlCheckout'   => getenv('USERVAR_FANCY_URL_CHECKOUT'),
        'urlStatus' => getenv('USERVAR_FANCY_URL_STATUS'),
        'urlCancel' => getenv('USERVAR_FANCY_URL_CANCEL'),
        'mode'          => 'P'
    ),

    'single' => array(
        'provider_id' => getenv('USERVAR_SINGLE_PROVIDER_ID'),
        'user'        => getenv('USERVAR_SINGLE_USER'),
        'pass'        => getenv('USERVAR_SINGLE_PASS'),
        'key'         => getenv('USERVAR_SINGLE_KEY'),
        'url'         => getenv('USERVAR_SINGLE_URL')
    ),

    'endpoint_stock_sears' => array(
        "endpoint"  => getenv('USERVAR_STOCK_SEARS_ENDPOINT'),
        "user"  =>  getenv('USERVAR_STOCK_SEARS_USER'),
        "pass" => getenv('USERVAR_STOCK_SEARS_PASS'),
        "mode" => getenv('USERVAR_STOCK_SEARS_MODE')
    ),
    'transfer' => array(
        'endpoint' => getenv('USERVAR_TRANSFER_ENDPOINT'),
        'merchantId' => getenv('USERVAR_TRANSFER_MERCHANT_ID'),
        'opciones' => [
            'soapMap'        => getenv('USERVAR_TRANSFER_OPTIONS_SOAP_MAP'),
            'invoke'         => getenv('USERVAR_TRANSFER_OPTIONS_INVOKE'),
            'soapMapValue'   => getenv('USERVAR_TRANSFER_OPTIONS_SOAP_MAP_VALUE'),
            'invokeResponse' => getenv('USERVAR_TRANSFER_OPTIONS_INVOKE_RESPONSE'),
            'trace'=> true,
            'soap_version'=> getenv('USERVAR_TRANSFER_OPTIONS_SOAP_VERSION')
        ],
        'IdFormaPago' => getenv('USERVAR_TRANSFER_ID_FORMA_PAGO'),
    ),

    'logger' => [
        'stream'            => '/var/log/php-fpm/www-error.log',
        'priorityFilter'    => 'DEBUG',
        'gelf' => [
            'host' => getenv('USERVAR_GRAYLOG_HOST'),
            'port' => getenv('USERVAR_GRAYLOG_PORT'),
        ],
        'flags' => [
            'project' => "MS_CAJA",
            'stage'   => getenv('USERVAR_GRAYLOG_STAGE'),
            'server'  => $_SERVER['HTTP_HOST']
        ]
    ],

    'loggerFront' => [
        'stream'            => '/var/log/php-fpm/www-error.log',
        'priorityFilter'    => 'DEBUG',
        'gelf' => [
            'host' => getenv('USERVAR_GRAYLOG_FRONT_HOST'),
            'port' => getenv('USERVAR_GRAYLOG_FRONT_PORT'),
        ],
        'flags' => [
            'project' => "CSAPI_CAJA",
            'stage'   => getenv('USERVAR_GRAYLOG_FRONT_STAGE'),
            'server'  => $_SERVER['HTTP_HOST']
        ]
    ],

    'cuenta_claro' => array(
        'user' => getenv('USERVAR_CUENTA_CLARO_USER'),
        'pass' => getenv('USERVAR_CUENTA_CLARO_PASS'),
        'empresa' => "073",
        'tipo' => 1,
        'endpoint' => getenv('USERVAR_CUENTA_CLARO_ENDPOINT'),
        "mode" => getenv('USERVAR_CUENTA_CLARO_MODE'), /*P - Producción, D - Desarrollo, T - Test*/
    ),

    'col_lab' => array(
        'endpoint' => getenv('USERVAR_COLAB_ENDPOINT'),
        "mode" => getenv('USERVAR_COLAB_MODE'),
    ),

    '3d_secure' => array(
        'KEY_SECRET'=> getenv('USERVAR_3DSECURE_KEY_SECRET'),
        'SID'=> getenv('USERVAR_3DSECURE_SID'),
        'RETURN_URL'=> getenv('USERVAR_3DSECURE_URL_RETURN'),
        'CANCEL_URL'=> getenv('USERVAR_3DSECURE_URL_CANCEL'),
        'TANK_PAGE'=> getenv('USERVAR_3DSECURE_URL_TANK_PAGE')
    ),

    'puntossinfin' => array(
        'opciones' => array(),
        'habilitado'=> (bool)getenv('USERVAR_PUNTOS_SIN_FIN_HABILITADO'),
        'IdFormaPago' => getenv('USERVAR_PUNTOS_SIN_FIN_ID_FORMA_PAGO'), //desarrollo
        'endpoint' => getenv('USERVAR_PUNTOS_SIN_FIN_ENDPOINT')    //desarrollo
    ),

    'session' => array(
        'config' => array(
            'class' => 'Zend\Session\Config\SessionConfig',
            'options' => [
                'remember_me_seconds' => getenv('USERVAR_SESSION_REMEMBER_SECONDS'),
                'use_cookies'         => (bool)getenv('USERVAR_SESSION_USE_COOKIES'),
                'use_only_cookies'    => getenv('USERVAR_SESSION_USE_ONLY_COOKIES')
            ]
        ),
        'storage' => 'Zend\Session\Storage\SessionArrayStorage',
        'validators' => array(
            'Zend\Session\Validator\RemoteAddr',
            'Zend\Session\Validator\HttpUserAgent',
        ),
    ),
    'tagManagerId' => getenv('USERVAR_TAGMANAGER_ID'), //dev

    'emarsysAPI'=>array(
        'username'      => getenv('USERVAR_EMARSYS_USERNAME'),
        'secret'        => getenv('USERVAR_EMARSYS_SECRET'),
        'endpoint'      => getenv('USERVAR_EMARSYS_ENDPOINT'),
        'listaClientes' => getenv('USERVAR_EMARSYS_LISTA_CLIENTES'),
        'curloptions'   => [
            CURLOPT_RETURNTRANSFER => TRUE,
            CURLOPT_HEADER         => FALSE,
            CURLOPT_CONNECTTIMEOUT => 10,
            CURLINFO_HEADER_OUT    => TRUE
        ]
    ),

    'GigyaService'=>array(
        'username'      => getenv('USERVAR_GIGYA_SERVICE_USERNAME'),
        'secret'        => getenv('USERVAR_GIGYA_SERVICE_SECRET'),
        'apiMethod'     => getenv('USERVAR_GIGYA_SERVICE_API_METHOD')
    ),

    'visualizarTiendasRelease' => true,
    'purchaseEventsMkt' => getenv('USERVAR_PURCHASE_EVENTS_MKT'),  //"Dev" desarrollo y qa; "Prod" release y produccion
    'emarsysTest'       => getenv('USERVAR_EMARSYS_TEST'),
    'compra_compra'=> array(557095,557096,557097,577379,604144,613598),

    'telmexLogin'=>array(
        'endpoint' => getenv('USERVAR_TELMEX_LOGIN_ENDPOINT')//desarrollo
    ),
    'endpoint_recibo_telmex' => getenv('USERVAR_RECIBO_TELMEX_ENDPOINT'),

    'ApiRestSelfService' => array(
        'url'  => getenv('USERVAR_SELFSERVICE_URL'),
        'user' => getenv('USERVAR_SELFSERVICE_USER'),
        'pass' => getenv('USERVAR_SELFSERVICE_PASS'),
        'options' => array(
            'sslverifypeer' => false,
            'sslallowselfsigned' => true,
        )
    ),

    'LoginSelfService' => array(
        'url'  => getenv('USERVAR_SELFSERVICE_LOGIN_URL'),
    ),

    'fedex'             => array(
        'prod'           => TRUE,
        'key'            => getenv('USERVAR_FEDEX_KEY'),
        'password'       => getenv('USERVAR_FEDEX_PASS'),
        'accountNumber' => getenv('USERVAR_FEDEX_ACCOUNT_NUMBER'),
        'meterNumber'   => getenv('USERVAR_FEDEX_METER_NUMBER'),
        'dropOffType'   => getenv('USERVAR_FEDEX_DROPOFF_TIME'),
        'approvedCodes'  => [
            'FEDEX_EXPRESS_SAVER',  // 1-3 business days
            'STANDARD_OVERNIGHT',   // overnight
        ],
    ),

    'google'=>array(
        'key_shortener' => getenv('USERVAR_GOOGLE_KEY_SHORTENER'),
        'GoogleUrlApiService' => getenv('USERVAR_GOOGLE_URL_API_SERVICE'),
        'adwords' => array(
            'conversion' =>array(
                'id' => getenv('USERVAR_GOOGLE_CONVERSION_ID'), //Ver cual es el de desarrollo
                'lenguaje' => 'en', //Ver si es lo correcto el lenguaje
                'formato' => '3', //Ver que es esto del formato
                'color' => 'ffffff',
                'label' => getenv('USERVAR_GOOGLE_CONVERSION_LABEL'),
                'currency' => 'MXN',
                'origen' => 'web',
                'ambiente' => getenv('USERVAR_GOOGLE_CONVERSION_AMBIENTE')
            )
        ),
    ),

    'diasCancelacion' => array(
        'deposito' => getenv('USERVAR_DIAS_CANCELACION_DEPOSITO'),
        'pagoTienda' => getenv('USERVAR_DIAS_CANCELACION_PAGO_TIENDA'),
        'conekta' => getenv('USERVAR_DIAS_CANCELACION_CONEKTA'),
        'copy' => [ // Solo son copys del thankyoupage y correos
            'conekta' => getenv('USERVAR_DIAS_CANCELACION_COPY_CONEKTA'),
            'payu' => getenv('USERVAR_DIAS_CANCELACION_COPY_PAYU'),
        ]
    ),

    'apiSms' => array(
        'endpoint' => getenv('USERVAR_API_SMS_ENDPOINT'),
        'username' => getenv('USERVAR_API_SMS_USERNAME')
    ),

    'recibo_telmex' => array(
        "login" => [
            'endpoint' => getenv('USERVAR_RECIBO_TELMEX_MOCKS_LOGIN_ENDPOINT'),
            'options' => [
                //'cache_wsdl' => getenv('USERVAR_RECIBO_TELMEX_MOCKS_OPTIONS_CACHE')
            ]
        ],

        "credito" => [
            'endpoint' => getenv('USERVAR_RECIBO_TELMEX_CREDITO_ENDPOINT'),
            'options' => [
                // 'cache_wsdl' => getenv('USERVAR_RECIBO_TELMEX_MOCKS_OPTIONS_CACHE')
            ]
        ],

        "antifraude" => [
            'endpoint' => getenv('USERVAR_RECIBO_TELMEX_ANTIFRAUDE_ENDPOINT'),
            'options' => [
                //'cache_wsdl' => getenv('USERVAR_RECIBO_TELMEX_MOCKS_OPTIONS_CACHE')
            ]
        ],

        "cuestionario" =>[
            'endpoint' => getenv('USERVAR_RECIBO_TELMEX_CUESTIONARIO_ENDPOINT'),
            'options' => [
                "login"=> getenv('USERVAR_RECIBO_TELMEX_MOCKS_OPTIONS_CUESTIONARIO_LOGIN'),
                "password"=> getenv('USERVAR_RECIBO_TELMEX_MOCKS_OPTIONS_CUESTIONARIO_PASS'),
                "soap_version"=> getenv('USERVAR_RECIBO_TELMEX_MOCKS_OPTIONS_CUESTIONARIO_SOAP_VERSION')
            ]
        ],

        "saldos" => [
            'endpoint' => getenv('USERVAR_RECIBO_TELMEX_MOCKS_SALDOS_ENDPOINT'),
            'options' => [
                // 'cache_wsdl' => [] //getenv('USERVAR_RECIBO_TELMEX_MOCKS_OPTIONS_CACHE')
            ]
        ],
    ),

    'CR' => array(
        'endPoint' => getenv('USERVAR_CR_ENDPOINT'),
        'location' => getenv('USERVAR_CR_LOCATION'),//Parametro solo para ambientes locales Reverse proxy
        'httpUser' => getenv('USERVAR_CR_HTTP_USER'),//Usuario http Parametro solo para ambientes locales Reverse Proxy
        'httpPass' => getenv('USERVAR_CR_HTTP_PASS'),//Contraseña http Parametro solo para ambientes locales Reverse Proxu
        'options' => array(
            "cache_wsdl" => getenv('USERVAR_CR_OPTIONS_CACHE'),
            "soap_version" => getenv('USERVAR_CR_OPTIONS_SOAP_VERSION'),
        ),
        'max_stock' => getenv('USERVAR_CR_MAX_STOCK'),
        'credencial' => array(
            'usuario' => getenv('USERVAR_CR_CREDENCIAL_USERNAME'),
            'password' => getenv('USERVAR_CR_CREDENCIAL_PASS'),
            'id_empresa' => getenv('USERVAR_CR_CREDENCIAL_ID_EMPRESA')
        ),
        'entrada' => array(
            'usuario'  => getenv('USERVAR_CR_ENTRADA_USERNAME'),
            'password' => getenv('USERVAR_CR_ENTRADA_PASS')
        ),
    ),

    'thank_you_page' => array(
        'from' => getenv('USERVAR_THANKYOUPAGE_FROM'),
        'correo_deposito' => getenv('USERVAR_THANKYOUPAGE_CORREO_DEPOSITO'),
        'correo_clientes' => getenv('USERVAR_THANKYOUPAGE_CORREO_CLIENTES'),
        'correo_datos_personales' => getenv('USERVAR_THANKYOUPAGE_CORREO_DATOS_PERSONALES'),
        'dias_telmex' => getenv('USERVAR_THANKYOUPAGE_DIAS_TELMEX')
    ),

    'sears_tiempo_entrega' => array(
        'stage' => true,
        'endpoint' => getenv('USERVAR_TIEMPO_ENTREGA_SEARS_ENDPOINT'),
        'usuario'=> getenv('USERVAR_TIEMPO_ENTREGA_SEARS_USER'),
        'password'=> getenv('USERVAR_TIEMPO_ENTREGA_SEARS_PASS'),
        'codEmp'=>'1',
        'tienda'=>'104',
        'bandera_big_ticket' => 'S',
        'httpuser'=> getenv('USERVAR_TIEMPO_ENTREGA_SEARS_HTTP_USER'),
        'httppassword'=> getenv('USERVAR_TIEMPO_ENTREGA_SEARS_HTTP_PASS'),
        'location'=> getenv('USERVAR_TIEMPO_ENTREGA_SEARS_LOCATION')
    ),

    'amex' => array(
        'urlWSDL' => getenv('USERVAR_AMEX_URL_WSLD'),
        /*'options' => array(
            'location' => getenv('USERVAR_AMEX_OPTIONS_LOCATION'),
            'login' => getenv('USERVAR_AMEX_OPTIONS_LOGIN'),
            'password' => getenv('USERVAR_AMEX_OPTIONS_PASS')
        ),*/
        'credencial' => array(
            'usuario' => getenv('USERVAR_AMEX_CREDENCIAL_USER'),
            'password' => getenv('USERVAR_AMEX_CREDENCIAL_PASS'),
            'id_empresa' => getenv('USERVAR_AMEX_CREDENCIAL_ID_EMPRESA')
        ),
        'entrada' => array(
            'usuario'  => getenv('USERVAR_AMEX_ENTRADA_USER'),
            'password' => getenv('USERVAR_AMEX_ENTRADA_PASS')
        ),
        'encryptkeys' => array(
            'key' => getenv('USERVAR_AMEX_ENCRYPT_KEY')
        ),
        'data' => array(
            'id_tienda' => '1',
            'num_compania' => '006',
            'whiteList' => array(
                'num_tienda' => '6575',
                'tipo_transaccion' => '9'
            ),
            'accepted' => array(
                'num_tienda'   => '6574',
                'tipo_transaccion'   => '8',
            ),
            'review' => array(
                'num_tienda' => '6573',
                'tipo_transaccion' => '1'
            ),
            'departamentales' => array(
                'num_tienda' => '6573',
                'sears' => array(
                    'tipo_transaccion' => '6'
                ),
                'sanborns' => array(
                    'tipo_transaccion' => getenv('USERVAR_AMEX_DATA_DEPARTAMENTALES_SANBORNS') ?: '3' // '3' claroshop sanborns, '4' en sanborns.com.mx,
                ),
                'certificados' => array(
                    'num_tienda' => '6573',
                    'tipo_transaccion' => '3'
                ),
                'puntosSears' => array(
                    'num_tienda' => '6573',
                    'tipo_transaccion' => '5'
                ),
            ),
            'amex' => array(
                'num_tienda' => '6573',
                'tipo_transaccion' => '2'
            ),
        ),
    ),

    'microsoft' => array(
        'url' => getenv('USERVAR_MICROSOFT_URL'),
        'apiKey'     => getenv('USERVAR_MICROSOFT_API_KEY'),
        'accessKey'   => getenv('USERVAR_MICROSOFT_ACCESS_KEY'),
    ),

    'tiendaCruzRoja' => getenv('USERVAR_TIENDA_CRUZ_ROJA'),

    'telmexBuro' => array(
        'url' => getenv('USERVAR_TELMEX_BURO_URL'),
    ),

    'apiNipTarjeta' => array(
        'url' => getenv('USERVAR_API_NIP_TARJETA_URL'),
        'idServicio' => '06',
        'options' => array(
            'trace' => 1
        ),
    ),

    'mercadoPago' => array(
        'PUBLIC_KEY'   => getenv('USERVAR_MERCADO_PAGO_PUBLIC_KEY'),
        'ACCESS_TOKEN' => getenv('USERVAR_MERCADO_PAGO_ACCESS_TOKEN'),
    ),

    's3'  => array(
        'user'=> getenv('USERVAR_S3_USER'),
        'pass'=> getenv('USERVAR_S3_PASS'),
        'mode'=> (bool)getenv('USERVAR_S3_MODE'),
        'bucket' => getenv('USERVAR_S3_BUCKET'),
        'ruta'   => getenv('USERVAR_S3_ROUTE')
    ),

    'wsSearsStatus' => getenv('USERVAR_WS_SEARS_STATUS_URL'),
    'proxy-imgs' => getenv('USERVAR_PROXY_IMGS_URL'),

    'sessionRedis' => [
        'redis' => [
            'host'   => getenv('USERVAR_REDIS_HOST'),
            'port'   => getenv('USERVAR_REDIS_PORT'),
            'prefix' => getenv('USERVAR_REDIS_PREFIX'),
            'pass' => getenv('USERVAR_REDIS_PASSWORD'),
            'time'   => getenv('USERVAR_REDIS_TIME')
        ],
        'token' => [
            'expire' => 1800,
            'key'    => getenv('USERVAR_REDIS_TOKEN_KEY'),
        ],
        'header' => [
            'name' => 'CSC-KEY',
            'app'  => 'isWebApp',
            'isApp'  => 'isApp',
            'isPwa' => 'isPwa',
        ],
        //se agrego llave
        'cyr' => [
            'header' => [
                'name' => 'CSC-CYR'
            ],
        ],
        'container' => [
            'name'        => getenv('USERVAR_REDIS_CONTAINER_NAME'),
            'cliente'     => 'cliente',
            'carrito'     => 'carrito',
            'multipedido' => 'multipedido',
            'attempts'    => 'attempts',
            'session'     => 'session'
        ],
        'setDefaultVersions' => [
            'androidVersion' => getenv('USERVAR_REDIS_DEFAULT_VERSION_ANDROID'),
            'iosVersion'     => getenv('USERVAR_REDIS_DEFAULT_VERSION_IOS'),
            'default'        => getenv('USERVAR_REDIS_DEFAULT_VERSION_WEB'),
            'defaultIsWebTrue' => 'unknown|unknown'
        ],
        'plataforms' => [
            'android' => 'android',
            'ios'     => 'ios'
        ],
    ],

    'redisClient' => array(
        'host'   => '',
    ),

    //se agrego llave
    'encrypted_keys' => [
        'cyr' => getenv('USERVAR_ENCRYPTED_KEYS_CYR')
    ],
    'tiendaOrigen' => 2468,
    'emarsysRecommendations' => [
        'items'      => 10,
        'contenedor' => 'agregarRecomendaciones'
    ],
    'redis' => [],

    'conekta' => [
        'keyPrivada' => getenv('USERVAR_CONEKTA_PRIVATE_KEY'),
        'httpOptions' => [
            'curloptions' => array(
                CURLOPT_CAINFO => '/etc/pki/tls/certs/ca-bundle.crt',
                CURLOPT_RETURNTRANSFER => true,
                CURLOPT_CONNECTTIMEOUT => getenv('USERVAR_CONEKTA_CURLOPT_CONNECTTIMEOUT'),
                CURLOPT_TIMEOUT => getenv('USERVAR_CONEKTA_CURLOPT_TIMEOUT'),
                CURLOPT_RETURNTRANSFER => true,
                CURLOPT_SSLVERSION => 6,
                CURLOPT_SSL_VERIFYPEER => FALSE,
                CURLOPT_SSL_VERIFYHOST => FALSE,
            )
        ],
    ],

    'listaNegraTiendas'=> "",

    'monedero' => array(
        'urlApiMonedero' => getenv('USERVAR_MONEDERO_URL'),
        'ocultarFpMonedero' => (bool)getenv('USERVAR_MONEDERO_HIDEN_MONEDERO'),
        'httpOptions' => [
            'adapter'   => 'Zend\Http\Client\Adapter\Curl',
            'curloptions' => array(
                CURLOPT_RETURNTRANSFER => 1,
                CURLOPT_SSL_VERIFYPEER => FALSE,
                CURLOPT_SSL_VERIFYHOST => FALSE,
                CURLOPT_CONNECTTIMEOUT => 10,
                CURLOPT_TIMEOUT => 10
            ),
            'headers' => array(
                "Accept" => "application/json",
                "Content-Type" => "application/json",
                "x-api-key" => getenv('USERVAR_MONEDERO_API_KEY'),
            ),
        ],
    ),

    'inactiva_forma_pago' => explode(",", getenv('USERVAR_FORMAS_DE_PAGO_INACTIVAS')),
    'inactiva_apps' => [
        'ios' => [
            "zip" => 6.11,
            "credito" => 6.12,
        ],
        'android' => [
            "zip" => 8.7,
            "credito" => 9.2,
        ],
    ],

    'formas_pago' => [
        'conekta'       => (int) getenv('USERVAR_FORMAS_PAGO_CONEKTA'),
        'monedero'      => (int) getenv('USERVAR_FORMAS_PAGO_MONEDERO'),
        'monedero_sears' => (int) getenv('USERVAR_FORMAS_PAGO_MONEDERO_SEARS'),
        'tarjetaStratus'=> (int) getenv('USERVAR_FORMAS_PAGO_TARJETA_STRATUS'),
        'tarjetaPagos'  => (int) getenv('USERVAR_FORMAS_PAGO_TARJETA_PAGOS'),
        'tarjetaAmex'   => (int) getenv('USERVAR_FORMAS_PAGO_TARJETA_AMEX'),
        'tarjetaPagosAmex' =>(int) getenv('USERVAR_FORMAS_PAGO_TARJETA_PAGO_AMEX'),
        'pagoTienda'    => getenv('USERVAR_FORMAS_PAGO_PAGO_TIENDA'),
        'claropay' => (int) getenv('USERVAR_FORMAS_PAGO_CLAROPAY'),
        'deposito' => (int) getenv('USERVAR_FORMAS_PAGO_DEPOSITO'),
        'zip' => (int) getenv('USERVAR_FORMAS_PAGO_ZIP'),
        'credito' => (int) getenv('USERVAR_FORMAS_PAGO_CREDITO'),
        "mejor_plan_credito_claroshop" => (int) getenv('USERVAR_FORMAS_PAGO_CREDITO_MEJOR_PLAN'),
        "revolvente_credito_claroshop" => (int) getenv('USERVAR_FORMAS_PAGO_CREDITO_REVOLVENTE_CLAROSHOP'),
        'conveniencia'=> (int) getenv('USERVAR_FORMAS_PAGO_TIENDAS_CONVENIENCIA'),
    ],

    'formas_pago_click_recoge' => explode(",", getenv("USERVAR_FORMA_PAGO_CLICK_RECOGE")),

    'envioGratis' => (bool) getenv('USERVAR_ENVIO_GRATIS'),
    "min_shipping_cost" => getenv('USERVAR_MIN_SHIPPING_COST'),
    "tiendaEnvioGratis"  => getenv('USERVAR_TIENDA_ENVIO_GRATIS'),
    "categoriasEnvioGratis" =>  getenv('USERVAR_CATEGORIAS_ENVIO_GRATIS'),
    "productosEnvioGratis"  => [],

    'dashboard' => array(
        "time_cache" => 3600
    ),

    'documentation' => [
        "base_path" => getenv('USERVAR_DOCUMENTATION_PATH')
    ],

    "paypal_soap_app_cs_versions" => [
        "android" => [
            "7.0.3",
            "7.3",
            "7.4",
            "7.5",
            "7.6",
            "7.7",
            "7.8",
        ],
        "ios" =>  [
            "6.0.1",
            "6.2.0",
            "6.2.1",
            "6.2.2",
            "6.3.0",
            "6.3.1",
        ],
    ],

    "android_app" => [
        "hide_forma_pago" => [
            "claropay" => getenv('USERVAR_ANDROID_APP_HIDEN_FORMA_PAGO_CLAROPAY') // Versiones menores o iguales se oculta claropay
        ]
    ],

    "ios_app" => [
        "hide_forma_pago" => [
            "claropay" => getenv('USERVAR_IOS_APP_HIDEN_FORMA_PAGO_CLAROPAY')// Versiones menores o iguales se oculta claropay
        ]
    ],

    "telmex" => [
        "error_detail" => [
            19 => [
                "message" => getenv('USERVAR_TELMEX_ERRORS_DETAILS_MESSAGE'),
                "title_apps" => getenv('USERVAR_TELMEX_ERRORS_DETAILS_TITLE_APPS'),
                "title_web" => getenv('USERVAR_TELMEX_ERRORS_DETAILS_TITLE_WEB'),
                "bullets" => [
                    "La línea Telmex debe contar con un Paquete Infinitum de $389 o mayor.",
                    "Contar con un historial de pago excelente o bueno.",
                    "No contar con ningún saldo vencido en telecomunicaciones, ventas financiadas o terceros.",
                    "Antigüedad mínima de 6 meses.",
                    "No tener orden de servicio abierta (Fallo en la línea Telmex o internet)",
                    "Contar con cuenta Mi Telmex"
                ],
                "ack" => "Enterado",
            ],
        ],

        "icons" => [
            2 => './assets/error/T_Telmex@2x.png',
            3 =>'./assets/error/T_Telmex@2x.png',
            5 =>'./assets/error/T_Telmex@2x.png',
            17 =>'./assets/error/T_Telmex@2x.png',
            22 =>'./assets/error/T_Telmex@2x.png',
            16 =>'./assets/error/T_Telmex@2x.png',
            20 =>'./assets/error/T_Telmex@2x.png',
            23 =>'./assets/error/T_Telmex@2x.png',
            21 =>'./assets/error/T_Telmex@2x.png',
            25 =>'./assets/error/T_Telmex@2x.png',
            27 =>'./assets/error/T_Telmex@2x.png',

            6 => './assets/error/Telmex_no@2x.png',
            7 => './assets/error/Telmex_no@2x.png',

            8=> './assets/error/Card@2x.png',
            9=> './assets/error/Card@2x.png',
            14=> './assets/error/Card@2x.png',
            15=> './assets/error/Card@2x.png',
            18=> './assets/error/Card@2x.png',
            19=> './assets/error/T_Telmex@2x.png',
            24=> './assets/error/Card@2x.png',
            26=> './assets/error/Card@2x.png',
            28=> './assets/error/Card@2x.png',
            29=> './assets/error/Card@2x.png',

            10 => './assets/error/Telmex_2@2x.png',
            11 => './assets/error/Telmex_2@2x.png',
            13 => './assets/error/Telmex_2@2x.png',

            12 => './assets/error/Claro@2x.png',

            1 => './assets/error/Datos@2x.png',
        ],
        "errors" => [
            4   => getenv('USERVAR_TELMEX_ERRORS_04'),
            1   => getenv('USERVAR_TELMEX_ERRORS_01'),
            14  => getenv('USERVAR_TELMEX_ERRORS_14'),
            9   => getenv('USERVAR_TELMEX_ERRORS_09'),
            8   => getenv('USERVAR_TELMEX_ERRORS_08'),
            10  => getenv('USERVAR_TELMEX_ERRORS_10'),
            11  => getenv('USERVAR_TELMEX_ERRORS_11'),
            12  => getenv('USERVAR_TELMEX_ERRORS_12'),
            24  => getenv('USERVAR_TELMEX_ERRORS_24'),
            26  => getenv('USERVAR_TELMEX_ERRORS_26'),
            2   => getenv('USERVAR_TELMEX_ERRORS_02'),
            3   => getenv('USERVAR_TELMEX_ERRORS_03'),
            17  => getenv('USERVAR_TELMEX_ERRORS_17'),
            19  => getenv('USERVAR_TELMEX_ERRORS_19'),
            25  => getenv('USERVAR_TELMEX_ERRORS_25'),
            21  => getenv('USERVAR_TELMEX_ERRORS_21'),
            27  => getenv('USERVAR_TELMEX_ERRORS_27'),
            18  => getenv('USERVAR_TELMEX_ERRORS_18'),
            28  => getenv('USERVAR_TELMEX_ERRORS_28'),
            29  => getenv('USERVAR_TELMEX_ERRORS_29'),
            15  => getenv('USERVAR_TELMEX_ERRORS_15'),
            16  => getenv('USERVAR_TELMEX_ERRORS_16'),
            20  => getenv('USERVAR_TELMEX_ERRORS_20'),
            5   => getenv('USERVAR_TELMEX_ERRORS_05'),
            6   => getenv('USERVAR_TELMEX_ERRORS_06'),
            7   => getenv('USERVAR_TELMEX_ERRORS_07'),
        ],
        "monto_min" => getenv('USERVAR_TELMEX_MONTO_MIN') ?: 200,
        "msi" => explode(",", getenv('USERVAR_TELMEX_ACTIVE_MONTHS_MSI')),
    ],
    'factores_mejor_plan' => [
        '6'     => getenv('USERVAR_FACTORES_TCSEARS_06'),
        '13'    => getenv('USERVAR_FACTORES_TCSEARS_13'),
        '18'    => getenv('USERVAR_FACTORES_TCSEARS_18'),
        '24'    => getenv('USERVAR_FACTORES_TCSEARS_24'),
        '36'    => getenv('USERVAR_FACTORES_TCSEARS_36'),
        '48'    => getenv('USERVAR_FACTORES_TCSEARS_48')
    ],
    'telmex_primera_compra' => [
        'porcentaje_descuento' => getenv('USERVAR_TELMEX_PRIMERACOMPRA_DESCUENTO'), //0 para apagar primera compra
        'monto_minimo' => getenv('USERVAR_TELMEX_PRIMERACOMPRA_MONTO_MINIMO'),
        'endpoint' => getenv('USERVAR_TELMEX_PRIMERACOMPRA_ENDPOINT'), // https://csapi.dev.claroshop.com/pcl/telmex/get-sin-promocion-aprobado/
        'httpOptions' => [
            'adapter'   => 'Zend\Http\Client\Adapter\Curl',
            'curloptions' => [
                CURLOPT_RETURNTRANSFER => 1,
                CURLOPT_SSL_VERIFYPEER => FALSE,
                CURLOPT_SSL_VERIFYHOST => FALSE,
                CURLOPT_CONNECTTIMEOUT => getenv('USERVAR_TELMEX_PRIMERACOMPRA_CONNECTTIMEOUT'), //60,
                CURLOPT_TIMEOUT => getenv('USERVAR_TELMEX_PRIMERACOMPRA_TIMEOUT'), //60
            ],
        ],
    ],
    'inactiva_version_zip_ios' => 6.11,
    'inactiva_version_zip_android' => 8.7,
    'mesa_regalos' => [
        'redirect_caja' => getenv('USERVAR_MESA_REGALOS_REDIRECT_CAJA'),
    ],
    'api_manager_service' => [
        'endpoint' => getenv('USERVAR_API_MANAGER_SERVICE_ENDPOINT'),
        'options' => [
            'curloptions' => [
                CURLOPT_POST => 1,
                CURLOPT_DNS_CACHE_TIMEOUT => -1,
                CURLOPT_RETURNTRANSFER => 1,
                CURLOPT_SSL_VERIFYPEER => FALSE,
                CURLOPT_SSL_VERIFYHOST => FALSE,
                CURLOPT_CONNECTTIMEOUT => 10,
                CURLOPT_TIMEOUT => 10
            ]
        ],
    ],

    'pago_tienda_barcode' => [
        'identificador' => getenv("USERVAR_PAGO_TIENDA_BARCODE_IDENTIFICADOR"),
        'num_tienda' 	=> getenv("USERVAR_PAGO_TIENDA_BARCODE_TIENDA"),
    ],
    'payment_limit' => [
        'telmex' => [
            "min" => (float) getenv('USERVAR_PAYMENT_LIMIT_TELMEX_MIN'),
        ],
        'efectivo' => [
            "max" => (float) getenv('USERVAR_PAYMENT_LIMIT_EFECTIVO_MAX'),
        ],
        'pago_tienda' => [
            "max" => (float) getenv('USERVAR_PAYMENT_LIMIT_TIENDA_MAX'),
        ],
        'deposito' => [
            "max" => (float) getenv('USERVAR_PAYMENT_LIMIT_DEPOSITO_MAX'),
        ],
        'claropay' => [
            "max" => (float) getenv('USERVAR_PAYMENT_LIMIT_CLAROPAY_MAX'),
        ],
    ],
    'apiNipTarjeta' => [
        'url' => getenv('USERVAR_SEARS_VALIDA_TARJETA'),
        'options' => [
            'cache_wsdl'=>WSDL_CACHE_NONE
        ]
    ],
    'apiNipSears' => [
        'url' => getenv('USERVAR_SEARS_VALIDA_NIP_SEARS'),
        'options' => [
            'cache_wsdl'=>WSDL_CACHE_NONE
        ],
    ],
    "tarjetas_departamentales" => [
        "encryptkeys" => getenv('USERVAR_TARJETAS_DEPARTAMENTALES_DECRYPT_KEY'),
    ],
    "pago-departamental-portal-origen"=> getenv('USERVAR_PAGO_DEPARTAMENTAL_PORTAL_ORIGEN')?? "Sears",
    "channel_sale_id" => getenv('USERVAR_CHANNEL_SALE_ID'),
);
