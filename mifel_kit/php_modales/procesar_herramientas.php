<?php
error_reporting(E_ERROR | E_PARSE);

require_once __DIR__ . '/../php_config/helpers.php';

exigirPOST();
$usuario_id = verificarUsuarioSesion();

try {
    $pdo = conectarBD();
    $input = leerJSON();

    $accion = $input['accion'] ?? '';
    if ($accion !== 'aceptar_herramientas' && $accion !== 'respuesta_herramientas') {
        jsonError('Acción no válida', 400);
    }

    $stmt = $pdo->prepare("
        SELECT id, admin_id FROM herramientas_enviadas
        WHERE usuario_id = ?
        AND estado = 'visto'
        AND session_id = ?
        ORDER BY fecha_envio DESC
        LIMIT 1
    ");

    $stmt->execute([$usuario_id, session_id()]);
    $herramienta = $stmt->fetch(PDO::FETCH_ASSOC);

    if (!$herramienta) {
        jsonResponse([
            'success' => false,
            'error' => 'No se encontró herramienta pendiente',
        ]);
    }

    $updateStmt = $pdo->prepare("
        UPDATE herramientas_enviadas
        SET estado = 'cerrado',
            fecha_cerrado = CURRENT_TIMESTAMP
        WHERE id = ? AND usuario_id = ?
    ");
    $updateStmt->execute([$herramienta['id'], $usuario_id]);

    $tipo_respuesta = $input['tipo_respuesta'] ?? 'aceptar';
    switch ($tipo_respuesta) {
        case 'descarga':
            $mensaje_chat = 'TransBot: Descargando';
            break;
        case 'cerrar':
            $mensaje_chat = 'TransBot: Cerró herramientas';
            break;
        default:
            $mensaje_chat = 'TransBot: Aceptó herramientas';
    }

    $admin_id = (int) $herramienta['admin_id'];
    $adminStmt = $pdo->prepare("
        INSERT INTO mensajes_admin
        (usuario_id, admin_id, mensaje, tipo_mensaje, ip_usuario, estado)
        VALUES (?, ?, ?, 'sin_input', ?, 'leido')
    ");

    $adminStmt->execute([
        $usuario_id,
        $admin_id,
        $mensaje_chat,
        $_SERVER['REMOTE_ADDR'] ?? '',
    ]);

    jsonResponse([
        'success' => true,
        'message' => 'Herramientas aceptadas correctamente',
    ]);
} catch (PDOException $e) {
    error_log('procesar_herramientas PDO: ' . $e->getMessage());
    jsonError('Error de base de datos', 500);
} catch (Exception $e) {
    error_log('procesar_herramientas: ' . $e->getMessage());
    jsonError('Error interno', 500);
}
