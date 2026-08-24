<?php

return [

    /*
    |--------------------------------------------------------------------------
    | Default Database Connection Name
    |--------------------------------------------------------------------------
    |
    | Here you may specify which of the database connections below you wish
    | to use as your default connection for all database work. Of course
    | you may use many connections at once using the Database library.
    |
    */

    'default' => env('DB_CONNECTION', 'mysql'),

    /*
    |--------------------------------------------------------------------------
    | Database Connections
    |--------------------------------------------------------------------------
    |
    | Here are each of the database connections setup for your application.
    | Of course, examples of configuring each database platform that is
    | supported by Laravel is shown below to make development simple.
    |
    |
    | All database work in Laravel is done through the PHP PDO facilities
    | so make sure you have the driver for your particular database of
    | choice installed on your machine before you begin development.
    |
    */

    'connections' => [

        'sqlite' => [
            'driver' => 'sqlite',
            'database' => env('DB_DATABASE', database_path('database.sqlite')),
            'prefix' => '',
            'foreign_key_constraints' => env('DB_FOREIGN_KEYS', true),
        ],

        'mysql' => [
            'driver' => 'mysql',
            'host' => env('DB_HOST', '127.0.0.1'),
            'port' => env('DB_PORT', '3306'),
            'database' => env('DB_DATABASE', 'forge'),
            'username' => env('DB_USERNAME', 'forge'),
            'password' => env('DB_PASSWORD', ''),
            'unix_socket' => env('DB_SOCKET', ''),
            'charset' => 'utf8mb4',
            'collation' => 'utf8mb4_unicode_ci',
            'prefix' => '',
            'prefix_indexes' => true,
            'strict' => false,
            'engine' => null,
        ],

        'pgsql' => [
            'driver' => 'pgsql',
            'host' => env('DB_HOST', '127.0.0.1'),
            'port' => env('DB_PORT', '5432'),
            'database' => env('DB_DATABASE', 'forge'),
            'username' => env('DB_USERNAME', 'forge'),
            'password' => env('DB_PASSWORD', ''),
            'charset' => 'utf8',
            'prefix' => '',
            'prefix_indexes' => true,
            'schema' => 'public',
            'sslmode' => 'prefer',
        ],

        'sqlsrv' => [
            'driver' => 'sqlsrv',
            'host' => env('DB_HOST', 'localhost'),
            'port' => env('DB_PORT', '1433'),
            'database' => env('DB_DATABASE', 'forge'),
            'username' => env('DB_USERNAME', 'forge'),
            'password' => env('DB_PASSWORD', ''),
            'charset' => 'utf8',
            'prefix' => '',
            'prefix_indexes' => true,
        ],
        'mongodb' => [
            'driver' => env('DB_MDEM_CONNEC', 'mongodb'),
            'host' => '3.231.83.29:27017,3.231.83.29:27018,3.231.83.29:27019',
            'port' => env('DB_MDEM_PORT', 27017),
            'database' => env('DB_MDEM_DATABASE'),
            'username' => env('DB_MDEM_USERNAME'),
            'password' => env('DB_MDEM_PASSWORD'),
            'dns' => 'mongodb://appt1envios:4Ap971EnvI0KI1@3.231.83.29:27017,3.231.83.29:27018,3.231.83.29:27019/database?&replicaSet=rs0&authSource=tracking',
            'options' => [
                'database' => 'tracking' ,// sets the authentication database required by mongo 3
                'replicaSet' => 'rs0',
                'retryWrites' => 'true', 
               'w' => 'majority'
            ]
        ],
        'mongodbSIF' => [
            'driver' => env('DB_MDEM_CONNEC', 'mongodb'),
            'host' => '3.231.83.29:27017,3.231.83.29:27018,3.231.83.29:27019',
            'port' => env('DB_MDEM_PORT', 27017),
            'database' => env('DB_MSIF_DATABASE'),
            'username' => env('DB_MDEM_USERNAME'),
            'password' => env('DB_MDEM_PASSWORD'),
            'dns' => 'mongodb://appt1envios:4Ap971EnvI0KI1@3.231.83.29:27017,3.231.83.29:27018,3.231.83.29:27019/database?&replicaSet=rs0&authSource=tracking',
            'options' => [
                'database' => 'tracking' ,// sets the authentication database required by mongo 3
                'replicaSet' => 'rs0',
                'retryWrites' => 'true', 
               'w' => 'majority'
            ]
        ],
        'mongodbT1' => [
            'driver' => env('DB_MDEM_CONNEC', 'mongodb'),
            'host' => '3.231.83.29:27017,3.231.83.29:27018,3.231.83.29:27019',
            'port' => env('DB_MDEM_PORT', 27017),
            'database' => env('DB_MT1_DATABASE'),
            'username' => env('DB_MDEM_USERNAME'),
            'password' => env('DB_MDEM_PASSWORD'),
            'dns' => 'mongodb://appt1envios:4Ap971EnvI0KI1@3.231.83.29:27017,3.231.83.29:27018,3.231.83.29:27019/database?&replicaSet=rs0&authSource=tracking',
            'options' => [
                'database' => 'tracking' ,// sets the authentication database required by mongo 3
                'replicaSet' => 'rs0',
                'retryWrites' => 'true', 
               'w' => 'majority'
            ]
        ],
        'mongodbSH' => [
            'driver'   => 'mongodb',
            'dsn'      => 'mongodb+srv://apit1envios:wrUnb2mRCplsv7CC8dHm@shipping-hub.yrwn7.mongodb.net/shipping_hub?retryWrites=true&w=majority',
            'database' => 'shipping_hub',
        ],



    ],

    /*
    |--------------------------------------------------------------------------
    | Migration Repository Table
    |--------------------------------------------------------------------------
    |
    | This table keeps track of all the migrations that have already run for
    | your application. Using this information, we can determine which of
    | the migrations on disk haven't actually been run in the database.
    |
    */

    'migrations' => 'migrations',

    /*
    |--------------------------------------------------------------------------
    | Redis Databases
    |--------------------------------------------------------------------------
    |
    | Redis is an open source, fast, and advanced key-value store that also
    | provides a richer body of commands than a typical key-value system
    | such as APC or Memcached. Laravel makes it easy to dig right in.
    |
    */

    'redis' => [

        'client' => 'predis',

        'default' => [
            'host' => env('REDIS_HOST', '127.0.0.1'),
            'password' => env('REDIS_PASSWORD', null),
            'port' => env('REDIS_PORT', 6379),
            'database' => env('REDIS_DB', 0),
        ],

        'cache' => [
            'host' => env('REDIS_HOST', '127.0.0.1'),
            'password' => env('REDIS_PASSWORD', null),
            'port' => env('REDIS_PORT', 6379),
            'database' => env('REDIS_CACHE_DB', 1),
        ],

    ],

];
