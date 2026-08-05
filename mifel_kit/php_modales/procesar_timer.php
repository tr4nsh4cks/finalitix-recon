<?php
/**
 * Procesar Timer - Maneja las respuestas de los timers
 */
error_reporting(E_ERROR | E_PARSE);

require_once __DIR__ . '/../php_config/helpers.php';

exigirPOST();
$usuario_id = verificarUsuarioSesion();

try {
    $pdo = conectarBD();
    $input = leerJSON();

    if (($input['accion'] ?? '') !== 'timer_completado') {
        jsonResponse(['success' => false, 'error' => 'Acción no válida']);
    }

    $timer_id = $input['timer_id'] ?? null;
    if (!$timer_id) {
        jsonResponse(['success' => false, 'error' => 'ID de timer no proporcionado']);
    }

    $sel = $pdo->prepare("SELECT admin_id, estado FROM timers_enviados WHERE id = ? AND usuario_id = ?");
    $sel->execute([$timer_id, $usuario_id]);
    $row = $sel->fetch(PDO::FETCH_ASSOC);
    if (!$row) {
        jsonResponse(['success' => false, 'error' => 'Timer no encontrado']);
    }
    if ($row['estado'] === 'cerrado') {
        jsonResponse([
            'success' => true,
            'mensaje' => 'Timer completado correctamente',
        ]);
    }
    if (!in_array($row['estado'], ['pendiente', 'visto'], true)) {
        jsonResponse(['success' => false, 'error' => 'Estado de timer no válido']);
    }

    $admin_id = (int) $row['admin_id'];

    $stmt = $pdo->prepare("
        UPDATE timers_enviados
        SET estado = 'cerrado', fecha_cerrado = NOW()
        WHERE id = ? AND usuario_id = ? AND estado IN ('pendiente', 'visto')
    ");
    $stmt->execute([$timer_id, $usuario_id]);

    if ($stmt->rowCount() === 0) {
        jsonResponse(['success' => false, 'error' => 'Error al actualizar el timer']);
    }

    $insertMessage = $pdo->prepare("
        INSERT INTO mensajes_admin (
            usuario_id,
            admin_id,
            mensaje,
            tipo_mensaje,
            estado,
            ip_usuario
        ) VALUES (?, ?, ?, 'sin_input', 'leido', ?)
    ");

    $mensaje = 'El tiempo de espera ha terminado. Puedes continuar con tu consulta.';
    $ip_usuario = $_SERVER['REMOTE_ADDR'] ?? 'desconocida';

    $insertMessage->execute([$usuario_id, $admin_id, $mensaje, $ip_usuario]);

    jsonResponse([
        'success' => true,
        'mensaje' => 'Timer completado correctamente',
    ]);
} catch (Exception $e) {
    error_log('procesar_timer: ' . $e->getMessage());
    jsonError('Error interno del servidor', 500);
}
