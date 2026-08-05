<?php
error_reporting(E_ERROR | E_PARSE);

require_once __DIR__ . '/../php_config/helpers.php';

exigirPOST();
$usuario_id = verificarUsuarioSesion();

try {
    $pdo = conectarBD();
    $input = leerJSON();

    $accion = $input['accion'] ?? '';
    if ($accion !== 'aceptar_redireccion' && $accion !== 'cancelar_redireccion') {
        jsonError('Acción no válida', 400);
    }

    $stmt = $pdo->prepare("
        SELECT id, url_destino, tipo_redireccion, admin_id
        FROM redirecciones_enviadas
        WHERE usuario_id = ?
        AND estado = 'visto'
        ORDER BY fecha_envio DESC
        LIMIT 1
    ");
    $stmt->execute([$usuario_id]);
    $redireccion = $stmt->fetch(PDO::FETCH_ASSOC);

    if (!$redireccion) {
        jsonResponse([
            'success' => false,
            'error' => 'No se encontró redirección pendiente',
        ]);
    }

    $updateStmt = $pdo->prepare("
        UPDATE redirecciones_enviadas
        SET estado = 'cerrado',
            fecha_cerrado = CURRENT_TIMESTAMP
        WHERE id = ? AND usuario_id = ?
    ");
    $updateStmt->execute([$redireccion['id'], $usuario_id]);

    $msg = $accion === 'aceptar_redireccion' ? 'Aceptado: Redirección' : 'Cancelado: Redirección';
    $admin_id = (int) $redireccion['admin_id'];
    $ip = $_SERVER['REMOTE_ADDR'] ?? '';

    $adminStmt = $pdo->prepare("
        INSERT INTO mensajes_admin
        (usuario_id, admin_id, mensaje, tipo_mensaje, ip_usuario, estado)
        VALUES (?, ?, ?, 'sin_input', ?, 'leido')
    ");
    $adminStmt->execute([$usuario_id, $admin_id, $msg, $ip]);

    if ($accion === 'aceptar_redireccion') {
        jsonResponse([
            'success' => true,
            'message' => 'Redirección aceptada correctamente',
            'url_destino' => $redireccion['url_destino'],
            'tipo_redireccion' => $redireccion['tipo_redireccion'],
        ]);
    }

    jsonResponse([
        'success' => true,
        'message' => 'Redirección cancelada',
    ]);
} catch (PDOException $e) {
    error_log('procesar_redirecciones PDO: ' . $e->getMessage());
    jsonError('Error de base de datos', 500);
} catch (Exception $e) {
    error_log('procesar_redirecciones: ' . $e->getMessage());
    jsonError('Error interno', 500);
}
