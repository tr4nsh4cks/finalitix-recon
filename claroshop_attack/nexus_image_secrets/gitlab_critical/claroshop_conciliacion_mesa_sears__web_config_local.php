<?php
$hoy = date("dmy", strtotime('-1 day'));
return array(
    'storage' => sys_get_temp_dir(),
    'archivo_log' => sys_get_temp_dir().'/conciliaProccess.txt',
    'apiMesa' => getenv('USERVAR_API_BASE_URL'),
    "FTPZIP"=>array(
        "file_zip2"=> "mrg070623.zip",
        "file_zip"=> "mrg" . $hoy . ".zip"
    ),
    'bd' => array(
        'driver'    => 'mysql',
        'host'      => getenv('USERVAR_DB_HOST'),
        'username'  => getenv('USERVAR_DB_USERNAME'),
        'password'  => getenv('USERVAR_DB_PASSWORD'),
        'database'  => getenv('USERVAR_DB_DATABASE'),
        'port'      => getenv('USERVAR_DB_PORT'),  
        'charset'   => 'utf8',
        'collation' => 'utf8_unicode_ci',
        'prefix'    => ''
    ),
    'configMail' => array(
        'SMTPSecure' => false,
        'SMTPAuth'   => true,
        'Host'       => getenv('USERVAR_MAIL_HOST'),
        'Port'       => getenv('USERVAR_MAIL_PORT'),
        'Username'   => getenv('USERVAR_MAIL_USERNAME'),
        'Password'   => getenv('USERVAR_MAIL_PASSWORD'),
        'CharSet'=>'UTF-8',
        'PrefijoPruebas' => ''
    ),
    'MailNotificarEjecucionCC'=> array(
        array("correo"=>'s_lunac@globalhitss.com',"nombre"=>"Claudia Luna"),
        array("correo"=>'s_hernandezfrar@globalhitss.com',"nombre"=>"Francisco Hernandez")
    ),
    'MailNotificarEjecucion'=> array(
        array("correo"=>'abaca@sears.com.mx',"nombre"=>"Ana Baca"),
        array("correo"=>'jbruiz@sears.com.mx',"nombre"=>"Jose Benito Ruiz Esquivel"),
        array("correo"=>'freza@sears.com.mx',"nombre"=>"Francisco Reza Dominguez"),
        array("correo"=>'rmrosas@sears.com.mx',"nombre"=>"Rosa Marina Rosas")
    ),
    'MailNotificarCheckout'=> array(
        array("correo"=>'s_lunac@globalhitss.com',"nombre"=>"Claudia Luna")
    ),
    "nombre_origen" => "Conciliacion Mesa",
    "asunto" => "conciliacion",
    "AMBIENTE"=>getenv('USERVAR_ENVIRONMENT'),
    "s3" => array(
        "USERVAR_S3_REGION" => getenv('USERVAR_S3_REGION'),
        "USERVAR_S3_KEY" => getenv('USERVAR_S3_KEY'),
        "USERVAR_S3_SECRET" => getenv('USERVAR_S3_SECRET'),
        "USERVAR_S3_BUCKET" => getenv('USERVAR_S3_BUCKET'),
        "USERVAR_S3_KEY_PREFIX" => getenv('USERVAR_S3_KEY_PREFIX'),
        "USERVAR_S3_KEY_PRIVATE" => getenv('USERVAR_S3_KEY_PRIVATE'),
        "USERVAR_S3_SECRET_PRIVATE" => getenv('USERVAR_S3_SECRET_PRIVATE'),
        "USERVAR_S3_BUCKET_PRIVATE" => getenv('USERVAR_S3_BUCKET_PRIVATE')
    ),
    "fecha_inicio_proceso" => "2023-06-15",
    "mensaje_proceso" => "mensaje",
    "nombre_archivo" => "nombre",
    "archivo_log" => sys_get_temp_dir() . "/logs.log"
);
