<?php

/*echo $_SERVER['HTTP_HOST'];
echo "<br><br><br>";*/

date_default_timezone_set("America/Mexico_City");

if($_SERVER['HTTP_HOST'] == "axii.qa.sears.com.mx"){
	define('HOSTDB', 'dbasears.qa.mrc-services.io');
	define('PASSDB', '72nsY[qu6Aud=Y)D3');
	define('PERMITEHORARIO', true);
}elseif($_SERVER['HTTP_HOST'] == "axii.admin.sears.com.mx"){
	define('HOSTDB', 'dbasears.mrc-services.io');
	define('PASSDB', 'Mh54/dPK-aZ469mbR');
	define('PERMITEHORARIO', false);
}elseif($_SERVER['HTTP_HOST'] == "axii.release.admin.sears.com.mx"){
	define('HOSTDB', 'dbasears.mrc-services.io');
	define('PASSDB', 'Mh54/dPK-aZ469mbR');
	define('PERMITEHORARIO', true);
}else{
	define('HOSTDB', 'dbasears.dev.mrc-services.io');
	define('PASSDB', 'Mh54/dPK-aZ469mbR');
	define('PERMITEHORARIO', true);
}

/*if(PERMITEHORARIO){
	echo "Si se permite horario desde config<br><br>";
}else{
	echo "No se permite horario desde config<br><br>";
}*/

define('USERDB', 'dbreportes');
define('NOMBREDB', 'tienda');
define('PUERTO', '3308');

/*define('HOSTDB', 'dbasears.claroshop-services.net');
define('USERDB', 'adaxsedb');
define('PASSDB', 'f9uPLFEIicN2cKJA');
define('NOMBREDB', 'tienda');*/

//hash('md5', 'finanzas:apiclaroshop:reportepedidos', false); genera token
define('TOKEN', 'f0ebcc112606ac5fadc1cb672416644a');

//hash('md5', 'finanzas:apiclaroshop:reportepedidosconciliacargos', false); genera token concilia
define('TOKEN_CONCILIA', '80f56244e6b1af95945e3ca0c88fad57');

define('KEY_ENCRYPT_CONCILIA', 'reportesConcilia');
define('KEY_ENCRYPT', 'reportesFinanzas');
define('BLOCK_SIZE', 128);

//define('RANGO_FECHA', 2678400); //un mes
define('RANGO_FECHA', 1382400); //16 días
define('INICIO_HISTORIA', 1447023600);// = 09-11-2015

define('TIPO_DATOS', 'xml');
define('TIPO_DATOS_CONCILIA', 'xml');

//VERIFICACION DE HORA PARA EJECUCION DE WS
$horario = getdate(time());

define('HORA_SERVIDOR', $horario['hours']);
define('HORA_INICIO_RESTRINGIDA', '9');
define('HORA_FINAL_RESTRINGIDA', '23');

?>