<?php

return [
    'db' => [
        'driver' => 'PDO_MYSQL',
        'host'   => getenv('USERVAR_DB_HOST'),
        'username' => getenv('USERVAR_DB_USER'),
        'password' => getenv('USERVAR_DB_PASSWORD'),
        'dbname' => getenv('USERVAR_DB_NAME')
    ],
];
