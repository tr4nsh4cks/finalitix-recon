<?php
/**
 * Verificar Timer - Verifica si hay timers pendientes para el usuario
 */
error_reporting(E_ERROR | E_PARSE);

require_once __DIR__ . '/../php_config/helpers.php';

$usuario_id = verificarUsuarioSesion();

try {
    $pdo = conectarBD();

    $stmt = $pdo->prepare("
        SELECT id, tiempo_segundos, mensaje_personalizado, fecha_envio
        FROM timers_enviados
        WHERE usuario_id = ?
        AND estado = 'pendiente'
        ORDER BY fecha_envio ASC
        LIMIT 1
    ");

    $stmt->execute([$usuario_id]);
    $timer = $stmt->fetch(PDO::FETCH_ASSOC);

    if ($timer) {
        $updateStmt = $pdo->prepare("
            UPDATE timers_enviados
            SET estado = 'visto', fecha_visto = NOW()
            WHERE id = ? AND usuario_id = ?
        ");
        $updateStmt->execute([$timer['id'], $usuario_id]);

        jsonResponse([
            'success' => true,
            'tiene_timer' => true,
            'id' => $timer['id'],
            'tiempo_segundos' => $timer['tiempo_segundos'],
            'mensaje_personalizado' => $timer['mensaje_personalizado'],
            'fecha_envio' => $timer['fecha_envio'],
        ]);
    }

    jsonResponse([
        'success' => true,
        'tiene_timer' => false,
    ]);
} catch (Exception $e) {
    error_log('verificar_timer: ' . $e->getMessage());
    jsonError('Error interno del servidor', 500);
}
