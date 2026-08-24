<?php
$configParams = array(
    'APP_NAME' => 'Cron de conciliación de pagos',
    'APP_ENV' => 'loc',  // local | dev | prod

    'DB' => array(
        'mysql' => array(
            'DB_HOST' => '172.27.140.151',
            'DB_PORT' => 3320,
            'DB_DATABASE' => 'app_sears',
            'DB_USERNAME' => 'federico.michell',
            'DB_PASSWORD' => 'Ay)f=Zm9mY6x[e5]'
        )
    ),

    'REDIS' => array(
        'HOST' => '%REDISHOST%',
        'PASSWORD' => '%REDISPASSWORD%',
        'REDIS_PORT' => '%REDISPORT%',
    ),

    'SMTP' => array(
        'HOST' => 'ssl://email-smtp.us-east-1.amazonaws.com',
        'USER' => 'AKIAJ7JDS52XV5CLN7VQ',
        'PASSWORD' => 'AnegzYehwmFBVAtP+bR/SMlYZue2Ad54qCVEAnz2eiPY',
        'PORT' => 465,
        'FROMADDRESS' => 'sears.internet@sears.com.mx' // Direccion email desde donde se envian los correos
    ),

    'FTP' => array(
        'HOST' => 'desa01.plazavip.com',
        'USER' => 'fmichell',
        'PASSWORD' => 'NocJwQ9qXTjUgZdfUhVR',
        'PATH' => '/labs_fm.d.plazavip.com/web/archivos_conciliacion/'
    ),

    'GELF' => array(
        'HOST' => '%GELFHOST%',
        'PORT' => '%GELFPORT%'
    )
);