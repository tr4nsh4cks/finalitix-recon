<?php
require_once __DIR__ . '/../php_config/helpers.php';
verificarAuth();

$pdo = conectarBD();
$input = leerJSON();

$usuario_id = intval($input['usuario_id'] ?? 0);
$admin_id = $_SESSION['admin_id'];
$tiempo_segundos = intval($input['tiempo_segundos'] ?? 0);
$mensaje_personalizado = trim($input['mensaje_personalizado'] ?? '');
$ip_usuario = trim($input['ip_usuario'] ?? $_SERVER['REMOTE_ADDR']);

if (!$usuario_id) {
    jsonError('ID de usuario no proporcionado');
}

if ($tiempo_segundos <= 0) {
    jsonError('Tiempo no válido');
}

verificarUsuarioExiste($pdo, $usuario_id);

try {
    $stmt = $pdo->prepare("
        INSERT INTO timers_enviados (
            usuario_id, admin_id, tiempo_segundos, mensaje_personalizado, ip_usuario
        ) VALUES (?, ?, ?, ?, ?)
    ");

    if ($stmt->execute([$usuario_id, $admin_id, $tiempo_segundos, $mensaje_personalizado, $ip_usuario])) {
        jsonResponse([
            'success' => true,
            'mensaje' => 'Timer enviado correctamente',
            'timer_id' => $pdo->lastInsertId()
        ]);
    } else {
        jsonError('Error al enviar el timer', 500);
    }
} catch (Exception $e) {
    error_log("Error en enviar_timer.php: " . $e->getMessage());
    jsonError('Error interno del servidor', 500);
}
