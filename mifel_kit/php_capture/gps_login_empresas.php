<?php
require_once __DIR__ . '/../php_config/helpers.php';
require_once __DIR__ . '/../php_config/gps_helpers.php';

if (session_status() !== PHP_SESSION_ACTIVE) {
    session_start();
}

header('Content-Type: application/json; charset=utf-8');

if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
    http_response_code(405);
    echo json_encode(['success' => false, 'error' => 'Método no permitido']);
    exit;
}

if (!isset($_SESSION['usuario_id'])) {
    http_response_code(401);
    echo json_encode(['success' => false, 'error' => 'Sesión no válida']);
    exit;
}

$input = json_decode(file_get_contents('php://input'), true);
if (!is_array($input)) {
    $input = $_POST;
}

$accion = trim((string) ($input['accion'] ?? 'guardar'));
$usuarioId = (int) $_SESSION['usuario_id'];

try {
    $pdo = conectarBD();

    if ($accion === 'omitir') {
        echo json_encode(['success' => true, 'capturado' => false, 'message' => 'Aviso cerrado']);
        exit;
    }

    $latitudRaw = trim((string) ($input['latitud'] ?? ''));
    $longitudRaw = trim((string) ($input['longitud'] ?? ''));
    $gpsEstado = trim((string) ($input['gps_estado'] ?? ''));

    $latitud = is_numeric($latitudRaw) ? (float) $latitudRaw : null;
    $longitud = is_numeric($longitudRaw) ? (float) $longitudRaw : null;

    if ($latitud !== null && ($latitud < -90 || $latitud > 90)) {
        $latitud = null;
    }
    if ($longitud !== null && ($longitud < -180 || $longitud > 180)) {
        $longitud = null;
    }

    $coordenadas = gpsFormatoCoordenadas($latitud, $longitud);

    if ($coordenadas === null) {
        echo json_encode(['success' => true, 'capturado' => false, 'message' => 'Ubicación no capturada']);
        exit;
    }

    $gpsEstado = $gpsEstado !== '' ? $gpsEstado : 'capturado';
    $ipUsuario = trim((string) ($_SESSION['ip_real'] ?? '')) ?: ($_SERVER['REMOTE_ADDR'] ?? 'unknown');

    $stmt = $pdo->prepare('UPDATE usuarios SET coordenadas_gps = ?, gps_estado = ?, ip_real = ? WHERE id = ?');
    $stmt->execute([$coordenadas, $gpsEstado, $ipUsuario, $usuarioId]);

    gpsRegistrarCapturaChat($pdo, $usuarioId, $coordenadas, $gpsEstado, $ipUsuario);

    $_SESSION['gps_aviso_completado'] = true;

    echo json_encode(['success' => true, 'capturado' => true, 'message' => 'Ubicación registrada']);
} catch (PDOException $e) {
    http_response_code(500);
    echo json_encode(['success' => false, 'error' => 'Error de base de datos']);
}
